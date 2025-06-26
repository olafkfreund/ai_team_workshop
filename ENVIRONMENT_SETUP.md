# 🔧 Enterprise MCP Workshop Environment Configuration

## 🎯 Environment Overview

This workshop requires a comprehensive environment setup to support enterprise-grade features including real Azure integration, authentication, caching, monitoring, and production deployment capabilities.

## 📋 Environment Variables Configuration

### **Required Environment File**

Create a `.env` file in the workshop root directory:

```bash
# Azure Authentication & Core Services
AZURE_SUBSCRIPTION_ID="your-subscription-id"
AZURE_TENANT_ID="your-tenant-id"
AZURE_CLIENT_ID="your-client-id"
AZURE_CLIENT_SECRET="your-client-secret"
AZURE_RESOURCE_GROUP="workshop-resources"

# Azure Storage (for centralized resources)
AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=..."
AZURE_STORAGE_ACCOUNT_NAME="workshopstorage"
AZURE_STORAGE_CONTAINER_NAME="copilot-resources"

# Azure Key Vault (for production scenarios)
AZURE_KEY_VAULT_URL="https://workshop-kv.vault.azure.net/"

# MCP Server Configuration
MCP_SERVER_HOST="0.0.0.0"
MCP_SERVER_PORT="8080"
MCP_SERVER_DEBUG="true"
MCP_SERVER_LOG_LEVEL="INFO"

# Authentication & Security
JWT_SECRET_KEY="your-jwt-secret-key-minimum-32-characters"
JWT_ALGORITHM="HS256"
JWT_EXPIRATION_HOURS="24"

# Redis Configuration (for caching)
REDIS_URL="redis://localhost:6379"
REDIS_PASSWORD=""
REDIS_DB="0"
REDIS_TTL="300"

# Rate Limiting
RATE_LIMIT_REQUESTS="100"
RATE_LIMIT_WINDOW="3600"

# Monitoring & Observability
PROMETHEUS_PORT="9090"
APPLICATION_INSIGHTS_CONNECTION_STRING="InstrumentationKey=..."

# Workshop Settings
WORKSHOP_MODE="enterprise"  # basic, enterprise, production
ENABLE_REAL_AZURE_CALLS="true"
ENABLE_AUTHENTICATION="true"
ENABLE_CACHING="true"
ENABLE_MONITORING="true"

# Development Settings
PYTHONPATH="/workshop"
FLASK_ENV="development"
FLASK_DEBUG="true"
```

### **Production Environment Variables**

For production deployments, use these additional settings:

```bash
# Production Security
MCP_SERVER_DEBUG="false"
MCP_SERVER_LOG_LEVEL="WARNING"
FLASK_ENV="production"
FLASK_DEBUG="false"

# Enhanced Security
ENABLE_CORS="false"
ALLOWED_ORIGINS="https://your-domain.com"
ENABLE_HTTPS="true"
SSL_CERT_PATH="/certs/server.crt"
SSL_KEY_PATH="/certs/server.key"

# Production Monitoring
ENABLE_DETAILED_METRICS="true"
LOG_TO_FILE="true"
LOG_FILE_PATH="/logs/mcp-server.log"

# Azure Production Services
AZURE_ENVIRONMENT="production"
AZURE_LOCATION="eastus"
```

## 🏗️ Infrastructure Requirements

### **Azure Resources Needed**

#### **Required for Workshop:**
1. **Azure Subscription** with Contributor role
2. **Resource Group** for workshop resources
3. **Storage Account** for blob storage and resource management
4. **Virtual Machines** (any existing VMs for monitoring demos)
5. **Azure Monitor** access for metrics querying

#### **Optional for Advanced Features:**
1. **Azure Key Vault** for secret management
2. **Azure Container Registry** for image storage
3. **Azure Container Instances** for deployment
4. **Azure Cosmos DB** for advanced data scenarios
5. **Azure Application Insights** for monitoring

### **Local Development Infrastructure**

#### **Required Services:**
```bash
# Redis for caching (using Docker)
docker run -d --name workshop-redis -p 6379:6379 redis:alpine

# Optional: Prometheus for metrics
docker run -d --name workshop-prometheus -p 9090:9090 prom/prometheus
```

## 🔐 Security Configuration

### **Authentication Setup**

1. **Azure Service Principal Creation:**
```bash
# Create service principal for workshop
az ad sp create-for-rbac --name "workshop-mcp-sp" \
  --role "Contributor" \
  --scopes "/subscriptions/{subscription-id}"
```

2. **JWT Secret Generation:**
```bash
# Generate secure JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **Azure Key Vault Setup (Optional)**

```bash
# Create Key Vault
az keyvault create --name workshop-kv \
  --resource-group workshop-resources \
  --location eastus

# Store secrets
az keyvault secret set --vault-name workshop-kv \
  --name "jwt-secret" --value "your-jwt-secret"
```

## 📊 Development vs Production Configurations

### **Development Environment**
- Local Redis instance
- Debug logging enabled
- Simulated Azure responses for some endpoints
- No HTTPS required
- Relaxed CORS policies

### **Production Environment**
- Azure Redis Cache
- Production logging levels
- Real Azure API calls only
- HTTPS/TLS required
- Strict CORS and security policies

## 🧪 Environment Validation

### **Pre-Workshop Validation Script**

```bash
# Run comprehensive environment validation
python test-workshop.py --validate-environment

# Expected checks:
# ✅ Azure CLI authenticated
# ✅ Environment variables loaded
# ✅ Azure services accessible
# ✅ Docker services running
# ✅ Network connectivity verified
```

### **Manual Validation Steps**

```bash
# Test Azure connectivity
az account show
az vm list --output table

# Test Redis connectivity
redis-cli ping

# Test environment variables
python -c "import os; print('Azure Sub:', os.getenv('AZURE_SUBSCRIPTION_ID'))"

# Test Docker build
cd mpc-server
docker build -t workshop-mcp .
```

## 🐛 Troubleshooting Common Issues

### **Azure Authentication Issues**

```bash
# Clear cached credentials
az account clear
az login --tenant <tenant-id>

# Verify permissions
az role assignment list --assignee <your-user-id>
```

### **Redis Connection Issues**

```bash
# Check Redis container
docker ps | grep redis
docker logs workshop-redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

### **Environment Variable Issues**

```bash
# Load .env file manually
set -o allexport
source .env
set +o allexport

# Verify variables
env | grep AZURE
```

### **Network and Firewall Issues**

```bash
# Test Azure endpoint connectivity
curl -s "https://management.azure.com/" -o /dev/null && echo "Azure reachable"

# Test local ports
netstat -tlnp | grep :8080
```

## 🚀 Quick Environment Setup Script

Create this script for rapid environment setup:

```bash
#!/bin/bash
# setup-workshop-env.sh

echo "🔧 Setting up Enterprise MCP Workshop Environment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start Redis container
echo "🚀 Starting Redis container..."
docker run -d --name workshop-redis -p 6379:6379 redis:alpine

# Validate Azure CLI
echo "☁️ Validating Azure CLI..."
az account show > /dev/null || (echo "❌ Azure CLI not authenticated" && exit 1)

# Load environment variables
echo "🔐 Loading environment variables..."
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

# Build Docker image
echo "🐳 Building Docker image..."
cd mpc-server
docker build -t workshop-mcp . || (echo "❌ Docker build failed" && exit 1)

# Run validation
echo "✅ Running environment validation..."
cd ..
python test-workshop.py --quick

echo "🎉 Environment setup complete! Ready for workshop."
```

## 🏆 Environment Readiness Criteria

Your environment is ready when:
- [ ] All Azure services accessible
- [ ] Docker image builds successfully
- [ ] Redis cache running locally
- [ ] Environment variables loaded
- [ ] Validation script passes with >90% success
- [ ] Network connectivity confirmed
- [ ] Authentication working properly

## 📞 Support & Resources

- **Environment Issues**: Check troubleshooting section above
- **Azure Service Issues**: Contact your Azure administrator
- **Workshop Questions**: Ask during the session
- **Technical Documentation**: See `/docs/` folder

---

*A properly configured environment ensures a smooth workshop experience and successful learning outcomes.* 🚀

## Docker Compose for Advanced Workshop

If you want to run multiple services, create a `docker-compose.yml`:

```yaml
version: '3.8'
services:
  mcp-server:
    build: ./mpc-server
    ports:
      - "8080:8080"
    environment:
      - WORKSHOP_MODE=basic
      - LOG_LEVEL=INFO
    volumes:
      - ./prompts:/app/prompts:ro
      - ./agents:/app/agents:ro
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
```

## Troubleshooting

### Common Issues

1. **Docker build fails**
   - Check Docker is running: `docker --version`
   - Ensure you're in the correct directory
   - Try: `docker system prune` to clean up

2. **Port 8080 already in use**
   - Kill existing process: `lsof -ti:8080 | xargs kill`
   - Or use different port: `docker run -p 8081:8080 workshop-mcp`

3. **Python import errors**
   - Check requirements.txt includes all dependencies
   - Rebuild Docker image after changes

4. **Agent responses are empty**
   - Check server logs: `docker logs <container_id>`
   - Verify JSON payload format in client calls
