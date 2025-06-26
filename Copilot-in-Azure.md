# Copilot in Azure: Step-by-Step Guide for Enterprise Developer Enablement

## Overview
This guide provides a practical, step-by-step approach to managing Azure Copilot instances, sharing agents, MCP servers, and reusable functions for enterprise developer teams. It includes real-life examples, benefits, drawbacks, and recommended tools for both Windows and Linux environments.

---

## 1. Project Structure Example

```text
/enterprise-copilot
├── agents/
│   ├── agent1.json
│   └── agent2.json
├── prompts/
│   ├── onboarding.md
│   └── troubleshooting.md
├── mcp-servers/
│   ├── server1/
│   └── server2/
├── shared-functions/
│   ├── summarize.py
│   └── translate.py
└── deployment/
    ├── bicep/
    └── scripts/
```

---

## 2. Step-by-Step Guide

### Step 1: Set Up Azure Copilot (OpenAI) Instance

1. Go to [Azure AI Studio](https://ai.azure.com/) or [Azure Portal](https://portal.azure.com/).
2. Create a new Azure OpenAI resource.
3. Assign RBAC roles (e.g., Contributor, Reader) to your developer teams.
4. Configure network and security settings (VNet, Private Endpoints if needed).

### Step 2: Centralize Prompts and Agent Instructions

Centralizing prompts and agent instructions means storing all prompt templates and agent configuration files in a single, accessible location (such as Azure Blob Storage, Azure Key Vault, or a shared Git repository). This approach ensures consistency, reusability, and easy updates across all projects and teams.

#### Purpose
- **For Developers:**
  - Quickly access, update, and reuse prompt templates and agent configs for different projects.
  - Collaborate with other developers by sharing improvements and best practices.
  - Integrate prompts and agent configs directly into code or CI/CD pipelines using VS Code on Windows or Linux.
- **For Operations:**
  - Enforce version control, access policies, and audit trails for all prompt and agent changes.
  - Automate deployment and updates to production environments.
  - Monitor usage and ensure compliance with organizational standards.

#### How It Works in Visual Studio Code (Windows & Linux)
- Developers clone or pull the shared Git repository containing prompts and agent configs.
- They edit files using VS Code, leveraging features like Git integration, markdown preview, and JSON validation.
- Changes are committed and pushed, triggering CI/CD pipelines or manual reviews as needed.
- On both Windows and Linux, the workflow is identical—VS Code and Git work the same way on both platforms.

#### Developer Example: Adding a New Prompt and Agent

1. **Create a new prompt file:**

`prompts/faq-support.md`
```markdown
# FAQ Support Copilot Prompt
You are a support assistant. Answer frequently asked questions clearly and concisely. If unsure, escalate to a human agent.
```

2. **Create a new agent config:**

`agents/faqAgent.json`
```json
{
  "name": "FAQAgent",
  "description": "Answers common support questions.",
  "prompt_path": "prompts/faq-support.md",
  "model": "gpt-4",
  "temperature": 0.3,
  "functions": ["summarize"]
}
```

3. **Edit, commit, and push using VS Code:**
```sh
# In the VS Code terminal (Windows or Linux)
git add prompts/faq-support.md agents/faqAgent.json
git commit -m "Add FAQ support prompt and agent config"
git push
```

#### Operations Example: Deploying Updated Prompts and Agents

1. **Monitor the repository for changes:**
   - Use a CI/CD pipeline (e.g., GitHub Actions, Azure DevOps) to detect new or updated prompt/agent files.

2. **Automate deployment to Azure Blob Storage:**
```yaml
# Example GitHub Actions workflow step
- name: Upload prompts to Azure Blob Storage
  uses: azure/CLI@v1
  with:
    inlineScript: |
      az storage blob upload-batch -d copilot-prompts --account-name <storage-account> -s prompts/
```

3. **Update MCP server configuration:**
   - Reload or redeploy MCP servers to pick up new/changed agent configs.
   - Example (Linux/Windows PowerShell):
```sh
# Restart MCP server container (Linux)
docker restart mcp-server
# Or trigger a redeploy in Azure
az container restart --name mcp-server-instance --resource-group copilot-rg
```

#### Summary
- **Developers** benefit from fast iteration, collaboration, and easy integration in their local environment (Windows or Linux, using VS Code).
- **Operations** gain control, automation, and compliance by centralizing and automating prompt/agent management.
- This approach ensures all teams use the latest, approved prompts and agent instructions, reducing errors and improving quality across the organization.

---

## 3. Real-Life Example: Onboarding a New Project

- **Scenario:** Team A needs a Copilot agent for onboarding new employees.
- **Steps:**
  1. Team A creates a prompt in `prompts/onboarding.md` (see above).
  2. Registers the prompt in the central repo or Blob Storage.
  3. Updates the agent config in `agents/agent1.json` to use the new prompt.
  4. Updates the MCP server config to include the new agent.
  5. Builds and pushes the MCP server Docker image to Azure Container Registry (ACR).
  6. Deploys the MCP server to Azure Container Instances (ACI) (see below).
  7. Shares the endpoint and usage guide with the team via the developer portal.

---

## 4. Example: Deploying a Containerized MCP Server to Azure Container Instances (ACI)

### Prerequisites
- Azure CLI installed
- Docker installed
- Access to Azure subscription

### Steps

1. **Build and Push Docker Image to Azure Container Registry (ACR):**

```sh
# Log in to Azure
az login

# Create a resource group (if needed)
az group create --name copilot-rg --location westeurope

# Create an Azure Container Registry
az acr create --resource-group copilot-rg --name mycopilotacr --sku Basic

# Log in to ACR
az acr login --name mycopilotacr

# Build and push the Docker image
az acr build --registry mycopilotacr --image mcp-server:latest .
```

2. **Deploy the Container to Azure Container Instances:**

```sh
az container create \
  --resource-group copilot-rg \
  --name mcp-server-instance \
  --image mycopilotacr.azurecr.io/mcp-server:latest \
  --cpu 1 --memory 2 \
  --ports 8080 \
  --environment-variables OPENAI_API_KEY=<your-api-key> \
  --restart-policy OnFailure
```

3. **Get the Public IP and Test the Endpoint:**

```sh
az container show --resource-group copilot-rg --name mcp-server-instance --query ipAddress.ip --output tsv
# Test with curl or Postman
```

---

## 5. Benefits

- **Centralized Management:**
  - All Copilot agents, prompts, and MCP servers are managed in one place, making updates and governance straightforward.
  - Easier to enforce organizational standards and policies.
- **Reusability:**
  - Prompts, agent configurations, and functions can be shared across multiple teams and projects, reducing duplication and speeding up onboarding for new projects.
  - Common use cases (e.g., summarization, translation, onboarding) can be standardized and improved over time.
- **Security:**
  - Azure AD and RBAC provide enterprise-grade access control, ensuring only authorized users can access or modify resources.
  - Integration with Azure Key Vault for secrets management and secure storage of API keys and credentials.
- **Scalability:**
  - Azure services (Container Instances, App Service, AKS) scale automatically with demand, supporting both small teams and large enterprises.
  - Easy to deploy new agents or scale up MCP servers as usage grows.
- **Compliance:**
  - Azure Policy and monitoring help enforce regulatory and organizational compliance (e.g., data residency, encryption, audit logging).
  - Built-in support for GDPR, HIPAA, and other compliance frameworks.
- **Operational Efficiency:**
  - Automated deployment pipelines (CI/CD) and infrastructure-as-code (Bicep, ARM) reduce manual work and errors.
  - Centralized monitoring and logging with Azure Monitor and Application Insights.
- **Developer Experience:**
  - Developers can focus on building solutions, not infrastructure, thanks to shared, managed resources and clear documentation.
  - SDKs, APIs, and CLI tools make integration easy for both Windows and Linux users.
- **Rapid Innovation:**
  - New features, agents, or prompts can be rolled out quickly to all teams.
  - Experimentation is safer and faster with isolated, containerized deployments.

---

## 6. Drawbacks

- **Complexity:**
  - Initial setup of Azure resources, networking, security, and governance can be complex and require specialized knowledge.
  - Ongoing management of multiple Azure services (OpenAI, ACR, ACI, API Management, etc.) can be challenging for small teams.
- **Cost:**
  - Azure services (especially OpenAI, compute, and storage) can incur significant costs, especially at scale or with high usage.
  - Monitoring, logging, and compliance features may add to operational expenses.
- **Latency:**
  - Network hops (e.g., API Management, VNet, container endpoints) can introduce latency, impacting real-time or interactive use cases.
  - Cold starts for serverless/containerized MCP servers may affect response times.
- **Learning Curve:**
  - Teams must learn Azure-specific tools, best practices, and security/compliance requirements.
  - Developers may need to adapt to new workflows (e.g., using shared prompts, APIs, or containerized agents).
- **Vendor Lock-in:**
  - Heavy reliance on Azure-specific services and APIs can make migration to other clouds or on-premises solutions more difficult.
- **Governance Overhead:**
  - Maintaining RBAC, policies, and compliance across multiple teams and projects requires ongoing attention and process discipline.
- **Debugging and Troubleshooting:**
  - Distributed, containerized, and API-driven architectures can make debugging more complex compared to monolithic or local solutions.
- **Resource Quotas and Limits:**
  - Azure OpenAI and other services may have usage quotas, rate limits, or regional restrictions that can impact scaling or global deployments.

---

## 7. Recommended Tools

| Task                        | Windows Tools                | Linux Tools                  |
|-----------------------------|------------------------------|------------------------------|
| Azure Management            | Azure Portal, Azure CLI      | Azure CLI, Azure Portal      |
| Code/Repo Management        | VS Code, Git, GitHub Desktop | VS Code, Git                 |
| Containerization            | Docker Desktop               | Docker                       |
| API Testing                 | Postman                      | Postman, curl                |
| Monitoring                  | Azure Monitor, App Insights  | Azure Monitor, App Insights  |
| CI/CD                       | GitHub Actions, Azure DevOps | GitHub Actions, Azure DevOps |

---

## 8. References

- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [Azure AI Studio](https://ai.azure.com/)
- [Azure Policy](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Azure API Management](https://learn.microsoft.com/en-us/azure/api-management/)
- [Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/)
- [Azure Container Instances](https://learn.microsoft.com/en-us/azure/container-instances/)

---

## 9. Instruction Prompt Examples for Multiple Languages

Below are example prompt templates for Copilot agents to assist developers in different programming languages. These can be stored in the `prompts/` directory and referenced by agent configurations.

### .NET (C#)
```markdown
# .NET Copilot Instruction
You are a .NET expert. Help the user write, debug, and optimize C# code for ASP.NET Core applications. Provide code samples, explain best practices, and suggest improvements.
```

### TypeScript
```markdown
# TypeScript Copilot Instruction
You are a TypeScript specialist. Assist with writing type-safe code, configuring tsconfig, and integrating with React or Node.js. Offer concise code examples and explain type errors.
```

### Java
```markdown
# Java Copilot Instruction
You are a Java mentor. Guide the user in writing, refactoring, and testing Java code for Spring Boot applications. Provide code snippets, explain OOP concepts, and help with Maven/Gradle.
```

### C#
```markdown
# C# Copilot Instruction
You are a C# developer assistant. Help with LINQ queries, async programming, and .NET libraries. Offer clear code examples and troubleshooting tips.
```

### C++
```markdown
# C++ Copilot Instruction
You are a C++ guru. Assist with memory management, STL usage, and cross-platform development. Provide code samples and explain complex concepts like templates and smart pointers.
```

### Node.js
```markdown
# Node.js Copilot Instruction
You are a Node.js backend expert. Help with Express.js, asynchronous code, and npm package management. Provide code snippets and explain event-driven programming.
```

### Python
```markdown
# Python Copilot Instruction
You are a Python guide. Assist with data analysis, web development (Flask/Django), and scripting. Provide code examples, explain errors, and suggest best practices for readability.
```

### Go (Golang)
```markdown
# Go Copilot Instruction
You are a Go language assistant. Help with writing idiomatic Go code, managing goroutines, and using Go modules. Provide code samples and explain concurrency patterns.
```

---

These instruction prompts can be referenced in agent configs to tailor Copilot’s behavior for each language and use case.

---

## 10. Example: Agent for Checking Azure VM Metrics

This example demonstrates how to create a Copilot agent that helps users check and interpret metrics for Azure Virtual Machines (VMs). The agent can guide developers or operations teams in monitoring VM health, performance, and troubleshooting issues.

### Example Prompt (`prompts/azure-vm-metrics.md`)
```markdown
# Azure VM Metrics Copilot Prompt
You are an Azure infrastructure assistant. Help users check, interpret, and troubleshoot metrics for Azure Virtual Machines. Provide guidance on using Azure CLI, Portal, and REST APIs to retrieve metrics such as CPU usage, memory, disk I/O, and network traffic. Suggest best practices for monitoring and alerting.
```

### Example Agent Config (`agents/azureVmMetricsAgent.json`)
```json
{
  "name": "AzureVmMetricsAgent",
  "description": "Assists with checking and interpreting Azure VM metrics.",
  "prompt_path": "prompts/azure-vm-metrics.md",
  "model": "gpt-4",
  "temperature": 0.2,
  "functions": ["getAzureVmMetrics"]
}
```

### Example Function (Python, can be deployed as Azure Function or used in MCP server)
```python
def getAzureVmMetrics(vm_name, resource_group):
    import subprocess
    cmd = [
        "az", "monitor", "metrics", "list",
        "--resource", f"/subscriptions/<sub-id>/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}",
        "--metric", "Percentage CPU,Network In,Network Out,Disk Read Bytes,Disk Write Bytes",
        "--interval", "PT1H"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout
```

### Usage Scenario
- **Developer/Operations:**
  - Ask the agent: "Check the CPU and network metrics for VM 'webserver01' in resource group 'prod-rg'."
  - The agent responds with Azure CLI commands, interprets the output, and suggests actions if metrics are outside normal ranges.
  - The agent can also recommend setting up alerts or dashboards in Azure Monitor for ongoing visibility.

### Benefits
- **Developers** can quickly diagnose performance issues without deep Azure expertise.
- **Operations** can automate routine monitoring and get actionable insights from natural language queries.

---

## 11. Example: Agent for Generating Documentation for Terraform Code in Azure DevOps

This example demonstrates how to create a Copilot agent that helps generate and maintain documentation for Terraform infrastructure-as-code (IaC) projects managed in Azure DevOps. The agent can analyze Terraform files, extract resource information, and produce human-readable documentation.

### Example Prompt (`prompts/terraform-docs.md`)
```markdown
# Terraform Documentation Copilot Prompt
You are an infrastructure documentation assistant. Analyze Terraform code and generate clear, concise documentation for each resource, variable, and output. Follow best practices for Azure DevOps projects. Format documentation in markdown and include usage examples where possible.
```

### Example Agent Config (`agents/terraformDocsAgent.json`)
```json
{
  "name": "TerraformDocsAgent",
  "description": "Generates documentation for Terraform code in Azure DevOps projects.",
  "prompt_path": "prompts/terraform-docs.md",
  "model": "gpt-4",
  "temperature": 0.2,
  "functions": ["generateTerraformDocs"]
}
```

### Example Function (Node.js, can be used in MCP server or as Azure Function)
```javascript
const fs = require('fs');
const path = require('path');

function generateTerraformDocs(terraformDir) {
  const files = fs.readdirSync(terraformDir).filter(f => f.endsWith('.tf'));
  let docs = '# Terraform Documentation\n\n';
  files.forEach(file => {
    const content = fs.readFileSync(path.join(terraformDir, file), 'utf8');
    // Simple example: extract resource blocks
    const resources = content.match(/resource ".*?" ".*?" {[^}]*}/gs) || [];
    resources.forEach(res => {
      docs += '## ' + res.split(' ')[1].replace(/"/g, '') + '\n';
      docs += '```hcl\n' + res + '\n```\n';
    });
  });
  return docs;
}
```

### Usage Scenario
- **Developer/Operations:**
  - Ask the agent: "Generate documentation for the Terraform code in the 'infra' directory."
  - The agent scans the directory, extracts resource definitions, and produces markdown documentation.
  - The documentation can be committed to the Azure DevOps repo or published as a wiki page for team reference.

### Benefits
- **Developers** save time and ensure up-to-date documentation for IaC projects.
- **Operations** improve compliance, onboarding, and knowledge sharing by automating documentation.

---
