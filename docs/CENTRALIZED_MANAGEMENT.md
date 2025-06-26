# Centralizing Prompts, Agents, and Instructions in Azure

Centralizing your Copilot prompts, agent configurations, and instruction templates in Azure ensures consistency, security, and easy sharing across teams. The recommended approach is to use Azure Blob Storage for file storage and optionally Azure Key Vault for secrets.

## Step-by-Step Guide

### 1. Create an Azure Storage Account

```sh
az storage account create \
  --name <yourstorageaccount> \
  --resource-group <yourresourcegroup> \
  --location <region> \
  --sku Standard_LRS
```

### 2. Create a Blob Container

```sh
az storage container create \
  --account-name <yourstorageaccount> \
  --name copilot-resources \
  --public-access off
```

### 3. Upload Prompts, Agents, and Instructions

```sh
az storage blob upload-batch \
  --account-name <yourstorageaccount> \
  -d copilot-resources \
  -s ./prompts
az storage blob upload-batch \
  --account-name <yourstorageaccount> \
  -d copilot-resources/agents \
  -s ./agents
```

### 4. Accessing Files from MCP Server or Clients
- Use Azure SDKs (Python, Node.js, etc.) or REST API to download the latest prompts and agent configs at runtime.
- Example (Python):

```python
from azure.storage.blob import BlobServiceClient
blob_service = BlobServiceClient.from_connection_string('<connection-string>')
container = blob_service.get_container_client('copilot-resources')
blob = container.get_blob_client('onboarding.md')
prompt = blob.download_blob().readall().decode()
```

### 5. Secure Access
- Use Azure AD or SAS tokens to restrict access to storage.
- Store sensitive data (API keys, secrets) in Azure Key Vault and reference them in your agent configs.

### 6. Configure MCP Server to Use Centralized Resources
- Add environment variables or config options to your MCP server to point to the Azure Blob Storage container and Key Vault.
- On startup, the server fetches the latest prompts and agent configs from Azure.

#### Example MCP Server Config Snippet
```yaml
storage:
  type: azure-blob
  account: <yourstorageaccount>
  container: copilot-resources
  key_vault: <your-keyvault-name>
```

## Benefits
- **Consistency:** All teams use the latest, approved prompts and configs.
- **Security:** Centralized access control and audit logging.
- **Scalability:** Easy to update and distribute new resources to all MCP servers and clients.

---

For more advanced automation, integrate uploads into your CI/CD pipeline (e.g., GitHub Actions, Azure DevOps) to keep Azure resources in sync with your repository.
