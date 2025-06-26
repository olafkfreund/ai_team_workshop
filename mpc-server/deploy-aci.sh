#!/bin/bash
# Deploy MCP server to Azure Container Instance
RESOURCE_GROUP="copilot-rg"
ACI_NAME="mcp-server-instance"
IMAGE_NAME="mcp-server:latest"
ACR_NAME="<your-acr-name>"
STORAGE_CONN_STRING="<your-azure-storage-connection-string>"

# Build and push Docker image to Azure Container Registry (ACR)
# az acr build --registry $ACR_NAME --image $IMAGE_NAME .
# Uncomment above and set up ACR if you want to use ACR

# Deploy to Azure Container Instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $ACI_NAME \
  --image $ACR_NAME.azurecr.io/$IMAGE_NAME \
  --cpu 1 --memory 2 \
  --ports 8080 \
  --environment-variables AZURE_STORAGE_CONNECTION_STRING="$STORAGE_CONN_STRING" \
  --restart-policy OnFailure

# Get public IP
az container show --resource-group $RESOURCE_GROUP --name $ACI_NAME --query ipAddress.ip --output tsv
