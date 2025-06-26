# Configuring Modules to Use Centralized Prompts, Agents, and Instructions in Azure

To enable your MCP server and agent modules to use centralized resources in Azure Blob Storage (and optionally Key Vault), you need to:
- Add configuration options to your MCP server and client modules
- Implement logic to fetch the latest files from Azure at startup or on demand
- Securely manage access credentials

## 1. Example MCP Server Configuration (YAML)

```yaml
storage:
  type: azure-blob
  account: <yourstorageaccount>
  container: copilot-resources
  connection_string: <env:AZURE_STORAGE_CONNECTION_STRING>
key_vault:
  name: <your-keyvault-name>
  client_id: <env:AZURE_CLIENT_ID>
  client_secret: <env:AZURE_CLIENT_SECRET>
  tenant_id: <env:AZURE_TENANT_ID>
```

- Use environment variables for secrets and connection strings.
- The server reads this config on startup and uses it to connect to Azure services.

## 2. Example Python Code to Fetch Prompts/Agents

```python
import os
from azure.storage.blob import BlobServiceClient

def fetch_prompt(prompt_name):
    conn_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container = blob_service.get_container_client('copilot-resources')
    blob = container.get_blob_client(prompt_name)
    return blob.download_blob().readall().decode()

prompt = fetch_prompt('onboarding.md')
```

## 3. Example Node.js Code to Fetch Prompts/Agents

```javascript
const { BlobServiceClient } = require('@azure/storage-blob');
const connStr = process.env.AZURE_STORAGE_CONNECTION_STRING;
const containerName = 'copilot-resources';

async function fetchPrompt(promptName) {
  const blobService = BlobServiceClient.fromConnectionString(connStr);
  const container = blobService.getContainerClient(containerName);
  const blob = container.getBlobClient(promptName);
  const downloadBlockBlobResponse = await blob.download();
  return (await streamToBuffer(downloadBlockBlobResponse.readableStreamBody)).toString();
}

// Helper to convert stream to buffer
async function streamToBuffer(readableStream) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    readableStream.on('data', (data) => {
      chunks.push(data instanceof Buffer ? data : Buffer.from(data));
    });
    readableStream.on('end', () => {
      resolve(Buffer.concat(chunks));
    });
    readableStream.on('error', reject);
  });
}

fetchPrompt('onboarding.md').then(console.log);
```

## 4. Using in Agent Modules
- When an agent is initialized, it loads its prompt and config from Azure Blob Storage using the above logic.
- For secrets (API keys, etc.), use Azure Key Vault SDKs to fetch them securely at runtime.
- You can cache prompts/configs locally and refresh them on a schedule or on demand.

## 5. Secure Access
- Use managed identities or service principals for authentication.
- Never hard-code secrets; always use environment variables or managed identity.

## 6. CI/CD Integration
- Add steps in your pipeline to upload new/updated prompts and agent configs to Azure Blob Storage after code review/merge.

---

By following this approach, all modules (MCP server, agents, clients) will always use the latest, centrally managed resources, ensuring consistency and security across your organization.
