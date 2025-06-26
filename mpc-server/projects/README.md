# Using MCP Server Projects with Visual Studio Code

This guide explains how to enable and use language-based project configuration with the MCP server in Visual Studio Code (VS Code).

## How It Works

- Each project folder (e.g., `sample-python-app`, `sample-node-app`) contains a `project-config.json` specifying the main development language.
- The MCP server uses this file to dynamically load the correct prompts, agent configs, and instructions for the project’s language from Azure Blob Storage.
- This enables language-specific onboarding, documentation, and agent behavior for every project.

---

## How the MCP Server Pulls Resources from Azure Blob Storage

1. **Project Metadata**: Each project has a `project-config.json` file specifying its language:
   ```json
   {
     "projectName": "sample-python-app",
     "language": "python"
   }
   ```
2. **Request Flow**: When a client sends a request to the MCP server endpoint:
   ```
   POST /agent/sample-python-app/<agent_name>
   ```
   the server reads the project config to determine the language (e.g., `python`).
3. **Resource Fetching**: The server builds the Azure Blob Storage path for each resource:
   - Prompts: `prompts/python/onboarding.md`
   - Agents: `agents/python/<agent_name>.json`
   - Instructions: `instructions/python/<instruction_file>`
4. **Azure Blob Storage Access**: The server uses the Azure SDK to download the files:
   ```python
   from azure.storage.blob import BlobServiceClient
   def fetch_resource(resource_type, language, filename):
       conn_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
       blob_service = BlobServiceClient.from_connection_string(conn_str)
       container = blob_service.get_container_client('copilot-resources')
       blob = container.get_blob_client(f'{resource_type}/{language}/{filename}')
       return blob.download_blob().readall().decode()
   ```
5. **Result**: The server returns the language-specific prompt, agent config, and instructions to the client.

---

## How to Upload Instructions, Agents, and Prompts to Azure Blob Storage

1. **Set up your Azure Storage account and container** (see main workshop docs).
2. **Upload files using Azure CLI:**
   ```sh
   # Upload all Python prompts
   az storage blob upload-batch \
     --account-name <yourstorageaccount> \
     -d copilot-resources/prompts/python \
     -s ./prompts/python

   # Upload all Python agent configs
   az storage blob upload-batch \
     --account-name <yourstorageaccount> \
     -d copilot-resources/agents/python \
     -s ./agents/python

   # Upload all Python instructions
   az storage blob upload-batch \
     --account-name <yourstorageaccount> \
     -d copilot-resources/instructions/python \
     -s ./instructions/python
   ```
3. **Repeat for other languages** by changing the folder and destination path.

---

## Enabling in Visual Studio Code

### 1. Clone the Repository and Open in VS Code
```sh
git clone <your-repo-url>
cd workshop/mpc-server/projects
code .
```

### 2. Review and Edit `project-config.json`
- Open the relevant project folder (e.g., `sample-python-app`).
- Edit `project-config.json` to set the correct language for your project:
```json
{
  "projectName": "sample-python-app",
  "language": "python"
}
```

### 3. Start the MCP Server
- Make sure your Azure Storage connection string is set in your environment:
```sh
export AZURE_STORAGE_CONNECTION_STRING="<your-connection-string>"
```
- Start the server (from the `mpc-server` folder):
```sh
python mcp_server.py
```

### 4. Real-Life Example: Using a Python Project
- The MCP server will read `projects/sample-python-app/project-config.json` and detect the language as `python`.
- When you POST to `/agent/sample-python-app/<agent_name>`, the server will fetch the correct prompts and agent configs for Python from Azure Blob Storage.
- Example client request (Python):
```python
import requests
response = requests.post(
    "http://localhost:8080/agent/sample-python-app/defaultAgent",
    json={"prompt": "How do I use async in Python?"}
)
print(response.json())
```
- The response will include the Python-specific prompt, agent config, and a simulated result.

### 5. Switching Languages
- To use a different language, create or edit a project folder and set the `language` field in `project-config.json` (e.g., `"node"`, `"go"`, `"java"`).
- The MCP server will automatically use the correct resources for that language.

---

## Best Practices
- Use the VS Code Azure Storage extension to browse and update prompts/agents in Azure.
- Use Git for version control of your project configs.
- Document your project’s language and agent requirements in a local README.

---

By following this approach, your team can easily onboard new projects in VS Code, with the MCP server providing the right Copilot experience for every language and project.
