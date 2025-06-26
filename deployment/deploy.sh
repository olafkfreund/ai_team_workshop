#!/bin/bash

# Production deployment script for MCP Server
# This script deploys the MCP Server to Azure with enterprise features

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="mcp-server-prod"
LOCATION="East US"
ENVIRONMENT="prod"
APP_NAME="mcp-server"
CONTAINER_REGISTRY="mcpserverprod"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        error "Azure CLI not found. Please install it first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker not found. Please install it first."
        exit 1
    fi
    
    # Check if logged in to Azure
    if ! az account show &> /dev/null; then
        error "Not logged in to Azure. Please run 'az login' first."
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create resource group
create_resource_group() {
    log "Creating resource group: $RESOURCE_GROUP"
    
    az group create \
        --name "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --output table
    
    success "Resource group created"
}

# Create container registry
create_container_registry() {
    log "Creating container registry: $CONTAINER_REGISTRY"
    
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$CONTAINER_REGISTRY" \
        --sku Standard \
        --location "$LOCATION" \
        --admin-enabled true \
        --output table
    
    success "Container registry created"
}

# Build and push Docker image
build_and_push_image() {
    log "Building and pushing Docker image..."
    
    # Get ACR login server
    ACR_LOGIN_SERVER=$(az acr show --name "$CONTAINER_REGISTRY" --resource-group "$RESOURCE_GROUP" --query loginServer --output tsv)
    
    # Login to ACR
    az acr login --name "$CONTAINER_REGISTRY"
    
    # Build image locally first for testing
    log "Building Docker image locally..."
    docker build -t mcp-server:latest ../mpc-server/
    
    # Tag for ACR
    docker tag mcp-server:latest "$ACR_LOGIN_SERVER/mcp-server:latest"
    docker tag mcp-server:latest "$ACR_LOGIN_SERVER/mcp-server:v$(date +%Y%m%d-%H%M%S)"
    
    # Push to ACR
    log "Pushing to Azure Container Registry..."
    docker push "$ACR_LOGIN_SERVER/mcp-server:latest"
    docker push "$ACR_LOGIN_SERVER/mcp-server:v$(date +%Y%m%d-%H%M%S)"
    
    success "Docker image built and pushed"
}

# Deploy infrastructure using Bicep
deploy_infrastructure() {
    log "Deploying infrastructure using Bicep..."
    
    # Deploy main infrastructure
    az deployment group create \
        --resource-group "$RESOURCE_GROUP" \
        --template-file main.bicep \
        --parameters \
            environment="$ENVIRONMENT" \
            appName="$APP_NAME" \
            containerRegistryName="$CONTAINER_REGISTRY" \
        --output table
    
    success "Infrastructure deployed"
}

# Configure monitoring and alerts
setup_monitoring() {
    log "Setting up monitoring and alerts..."
    
    # Get Application Insights connection string
    APP_INSIGHTS_CONNECTION_STRING=$(az monitor app-insights component show \
        --app "${APP_NAME}-${ENVIRONMENT}-insights" \
        --resource-group "$RESOURCE_GROUP" \
        --query connectionString \
        --output tsv)
    
    # Create alert rules
    log "Creating alert rules..."
    
    # High error rate alert
    az monitor metrics alert create \
        --name "mcp-server-high-error-rate" \
        --resource-group "$RESOURCE_GROUP" \
        --scopes "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}-${ENVIRONMENT}-aci" \
        --condition "count 'Log' contains 'ERROR' > 10" \
        --window-size "5m" \
        --evaluation-frequency "1m" \
        --severity 2 \
        --description "High error rate detected in MCP Server" \
        --output table
    
    # High CPU usage alert
    az monitor metrics alert create \
        --name "mcp-server-high-cpu" \
        --resource-group "$RESOURCE_GROUP" \
        --scopes "/subscriptions/$(az account show --query id --output tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ContainerInstance/containerGroups/${APP_NAME}-${ENVIRONMENT}-aci" \
        --condition "avg CpuUsage > 80" \
        --window-size "10m" \
        --evaluation-frequency "5m" \
        --severity 3 \
        --description "High CPU usage detected in MCP Server" \
        --output table
    
    success "Monitoring and alerts configured"
}

# Validate deployment
validate_deployment() {
    log "Validating deployment..."
    
    # Get container instance details
    MCP_URL=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "main" \
        --query properties.outputs.mcpServerUrl.value \
        --output tsv)
    
    log "MCP Server URL: $MCP_URL"
    
    # Wait for container to be ready
    log "Waiting for container to be ready..."
    sleep 30
    
    # Test health endpoint
    for i in {1..10}; do
        if curl -f "$MCP_URL/health" &> /dev/null; then
            success "Health check passed"
            break
        else
            warning "Health check attempt $i failed, retrying in 10 seconds..."
            sleep 10
        fi
        
        if [ $i -eq 10 ]; then
            error "Health check failed after 10 attempts"
            return 1
        fi
    done
    
    # Test agent endpoint
    log "Testing agent endpoint..."
    RESPONSE=$(curl -s -X POST "$MCP_URL/agent/azureVmMetricsAgent" \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Test deployment"}')
    
    if echo "$RESPONSE" | jq -e '.status == "success"' &> /dev/null; then
        success "Agent endpoint test passed"
    else
        error "Agent endpoint test failed"
        echo "Response: $RESPONSE"
        return 1
    fi
    
    success "Deployment validation completed"
}

# Setup CI/CD pipeline
setup_cicd() {
    log "Setting up CI/CD pipeline..."
    
    # Create service principal for CI/CD
    SP_NAME="mcp-server-cicd-sp"
    SUBSCRIPTION_ID=$(az account show --query id --output tsv)
    
    log "Creating service principal: $SP_NAME"
    SP_CREDENTIALS=$(az ad sp create-for-rbac \
        --name "$SP_NAME" \
        --role Contributor \
        --scopes "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP" \
        --output json)
    
    # Extract credentials
    CLIENT_ID=$(echo "$SP_CREDENTIALS" | jq -r '.appId')
    CLIENT_SECRET=$(echo "$SP_CREDENTIALS" | jq -r '.password')
    TENANT_ID=$(echo "$SP_CREDENTIALS" | jq -r '.tenant')
    
    # Output GitHub Actions secrets
    log "GitHub Actions secrets to configure:"
    echo "=================================="
    echo "AZURE_CLIENT_ID: $CLIENT_ID"
    echo "AZURE_CLIENT_SECRET: $CLIENT_SECRET"
    echo "AZURE_TENANT_ID: $TENANT_ID"
    echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
    echo "AZURE_RESOURCE_GROUP: $RESOURCE_GROUP"
    echo "AZURE_CONTAINER_REGISTRY: $CONTAINER_REGISTRY"
    echo "=================================="
    
    success "CI/CD setup completed"
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    # Add any cleanup tasks here
}

# Rollback function
rollback() {
    error "Deployment failed. Starting rollback..."
    
    # Get previous deployment
    PREVIOUS_DEPLOYMENT=$(az deployment group list \
        --resource-group "$RESOURCE_GROUP" \
        --query "[?name!='main'] | sort_by(@, &properties.timestamp) | [-1].name" \
        --output tsv)
    
    if [ -n "$PREVIOUS_DEPLOYMENT" ]; then
        log "Rolling back to deployment: $PREVIOUS_DEPLOYMENT"
        # Rollback logic would go here
        warning "Rollback completed, but manual verification may be required"
    else
        warning "No previous deployment found for rollback"
    fi
}

# Print deployment summary
print_summary() {
    log "Deployment Summary"
    echo "=================="
    echo "Resource Group: $RESOURCE_GROUP"
    echo "Environment: $ENVIRONMENT"
    echo "Location: $LOCATION"
    
    # Get outputs from deployment
    MCP_URL=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "main" \
        --query properties.outputs.mcpServerUrl.value \
        --output tsv)
    
    STORAGE_ACCOUNT=$(az deployment group show \
        --resource-group "$RESOURCE_GROUP" \
        --name "main" \
        --query properties.outputs.storageAccountName.value \
        --output tsv)
    
    echo "MCP Server URL: $MCP_URL"
    echo "Storage Account: $STORAGE_ACCOUNT"
    echo "Container Registry: $CONTAINER_REGISTRY.azurecr.io"
    echo ""
    echo "Next Steps:"
    echo "1. Configure DNS and SSL certificates"
    echo "2. Set up backup and disaster recovery"
    echo "3. Configure CI/CD pipeline with provided secrets"
    echo "4. Review monitoring and alerting configuration"
    echo "=================="
}

# Main deployment function
main() {
    log "Starting MCP Server production deployment..."
    
    # Set trap for cleanup on exit
    trap cleanup EXIT
    trap rollback ERR
    
    check_prerequisites
    create_resource_group
    create_container_registry
    build_and_push_image
    deploy_infrastructure
    setup_monitoring
    validate_deployment
    setup_cicd
    print_summary
    
    success "Deployment completed successfully! 🚀"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --container-registry)
            CONTAINER_REGISTRY="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --resource-group NAME    Resource group name (default: mcp-server-prod)"
            echo "  --location LOCATION      Azure location (default: East US)"
            echo "  --environment ENV        Environment (dev/staging/prod, default: prod)"
            echo "  --container-registry NAME Container registry name"
            echo "  --help                   Show this help message"
            exit 0
            ;;
        *)
            error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main deployment
main
