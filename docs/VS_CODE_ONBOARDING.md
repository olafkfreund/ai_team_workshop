# 🚀 VS Code Configuration for Enterprise MCP Development## OverviewThis guide helps you configure Visual Studio Code for enterprise-grade MCP server development with full Azure integration, comprehensive debugging, and production-ready workflows.## 📋 Prerequisites### **Required Extensions**Install these VS Code extensions for optimal development experience:```bash# Core Azure Development Extensionscode --install-extension ms-azuretools.vscode-azureappservicecode --install-extension ms-azuretools.vscode-azurefunctionscode --install-extension ms-azuretools.vscode-azureresourcegroupscode --install-extension ms-azuretools.vscode-azurestoragecode --install-extension ms-azuretools.vscode-docker# Python Developmentcode --install-extension ms-python.pythoncode --install-extension ms-python.pylintcode --install-extension ms-python.black-formattercode --install-extension ms-python.isort# Testing & Qualitycode --install-extension ms-python.pytestcode --install-extension hbenl.vscode-test-explorercode --install-extension ms-vscode.test-adapter-converter# DevOps & Automationcode --install-extension github.vscode-github-actionscode --install-extension ms-azuretools.vscode-bicepcode --install-extension redhat.vscode-yaml# Monitoring & Debuggingcode --install-extension ms-vscode.vscode-jsoncode --install-extension davidanson.vscode-markdownlint```## 🔧 Workspace Configuration### **1. Workspace Settings**Create `.vscode/settings.json` in your workshop directory:```json{    "python.defaultInterpreterPath": "./venv/bin/python",    "python.testing.pytestEnabled": true,    "python.testing.pytestArgs": ["mpc-server"],    "python.linting.enabled": true,    "python.linting.pylintEnabled": true,    "python.formatting.provider": "black",    "python.sortImports.args": ["--profile", "black"],        "docker.defaultRegistryPath": "your-registry.azurecr.io",    "azure.subscription": "${env:AZURE_SUBSCRIPTION_ID}",    "azure.resourceGroups": "workshop-resources",        "files.associations": {        "*.bicep": "bicep",        "Dockerfile*": "dockerfile"    },        "editor.formatOnSave": true,    "editor.codeActionsOnSave": {        "source.organizeImports": true
    },
    
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}",
        "MCP_DEBUG": "true"
    },
    
    "yaml.schemas": {
        "https://raw.githubusercontent.com/Azure/azure-pipelines-vscode/master/service-schema.json": [
            ".github/workflows/*.yml"
        ]
    }
}
```

### **2. Launch Configuration**

Create `.vscode/launch.json` for debugging:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "MCP Server Debug",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/mpc-server/app.py",
            "console": "integratedTerminal",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "true",
                "MCP_DEBUG": "true",
                "PYTHONPATH": "${workspaceFolder}"
            },
            "args": []
        },
        {
            "name": "Test Suite Debug",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${workspaceFolder}/mpc-server/test_mcp_server.py",
                "-v",
                "--tb=short"
            ],
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        },
        {
            "name": "Workshop Validation",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test-workshop.py",
            "args": ["--comprehensive"],
            "console": "integratedTerminal"
        }
    ]
}
```

### **3. Tasks Configuration**

Create `.vscode/tasks.json` for automation:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build MCP Server",
            "type": "shell",
            "command": "docker",
            "args": ["build", "-t", "workshop-mcp", "./mpc-server"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Run MCP Server",
            "type": "shell",
            "command": "docker",
            "args": [
                "run", "-d", "-p", "8080:8080",
                "-e", "MCP_DEBUG=true",
                "-e", "ENABLE_AUTHENTICATION=true",
                "-e", "ENABLE_CACHING=true",
                "--name", "workshop-mcp",
                "workshop-mcp"
            ],
            "group": "build",
            "presentation": {
                "reveal": "always"
            },
            "dependsOn": "Build MCP Server"
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "python",
            "args": ["-m", "pytest", "mpc-server/test_mcp_server.py", "-v", "--cov=."],
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": ["$python"]
        },
        {
            "label": "Workshop Validation",
            "type": "shell",
            "command": "python",
            "args": ["test-workshop.py", "--comprehensive"],
            "group": "test",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Deploy to Azure",
            "type": "shell",
            "command": "./deployment/deploy.sh",
            "args": ["--environment", "dev"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Azure Login",
            "type": "shell",
            "command": "az",
            "args": ["login"],
            "group": "build"
        }
    ]
}
```

## 🐛 Debugging Configuration

### **Python Debugging**
- Set breakpoints in your MCP server code
- Use the "MCP Server Debug" configuration
- Monitor variables and request flow
- Debug Azure integration points

### **Docker Debugging**
```json
{
    "name": "Docker Debug",
    "type": "docker",
    "request": "launch",
    "preLaunchTask": "docker-build",
    "python": {
        "pathMappings": [
            {
                "localRoot": "${workspaceFolder}/mpc-server",
                "remoteRoot": "/app"
            }
        ],
        "projectType": "flask"
    }
}
```

## 🔍 Code Quality Integration

### **Linting Configuration**

Create `.pylintrc` in the mpc-server directory:

```ini
[MASTER]
load-plugins=pylint_flask

[MESSAGES CONTROL]
disable=C0103,R0903,W0613,C0114,C0115,C0116

[FORMAT]
max-line-length=100
```

### **Code Formatting**

Create `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 100
```

## 🧪 Testing Integration

### **Test Discovery**
- VS Code will automatically discover pytest tests
- Use Test Explorer for visual test management
- Run individual tests or full suites
- View coverage reports inline

### **Test Configuration**

Update `pytest.ini`:

```ini
[tool:pytest]
testpaths = mpc-server
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov=. --cov-report=html
```

## ☁️ Azure Integration

### **Azure Account Setup**
1. Sign in to Azure through VS Code
2. Select your subscription
3. Configure resource group access
4. Set up storage account connections

### **Environment Variables**
Create `.vscode/.env` for local development:

```bash
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_RESOURCE_GROUP=workshop-resources
AZURE_STORAGE_ACCOUNT=workshopstorage
```

## 🚀 Development Workflow

### **Daily Development Process**

1. **Start Development Session:**
   ```bash
   # Open VS Code
   code .
   
   # Run Azure login task
   Ctrl+Shift+P -> Tasks: Run Task -> Azure Login
   ```

2. **Code Development:**
   - Use IntelliSense for Azure SDK APIs
   - Set breakpoints and debug
   - Format code on save
   - Run tests continuously

3. **Testing & Validation:**
   ```bash
   # Run specific tests
   Ctrl+Shift+P -> Test: Run Test at Cursor
   
   # Run full validation
   Ctrl+Shift+P -> Tasks: Run Task -> Workshop Validation
   ```

4. **Docker Operations:**
   ```bash
   # Build and run
   Ctrl+Shift+P -> Tasks: Run Task -> Run MCP Server
   
   # View container logs
   Ctrl+Shift+` -> docker logs workshop-mcp
   ```

## 📊 Monitoring & Observability

### **Live Dashboard Integration**
- Open `http://localhost:8080/dashboard` in Simple Browser
- Monitor real-time metrics
- View WebSocket connections
- Track performance metrics

### **Log Monitoring**
```json
{
    "name": "View Server Logs",
    "type": "shell",
    "command": "docker",
    "args": ["logs", "-f", "workshop-mcp"],
    "presentation": {
        "reveal": "always",
        "panel": "dedicated"
    }
}
```

## 🔐 Security Best Practices

### **Secrets Management**
- Never commit `.env` files
- Use Azure Key Vault extension
- Rotate JWT secrets regularly
- Monitor authentication logs

### **Code Security**
```json
{
    "label": "Security Scan",
    "type": "shell",
    "command": "bandit",
    "args": ["-r", "mpc-server/", "-f", "json"],
    "group": "test"
}
```

## 📚 Documentation Integration

### **Live Documentation**
- Auto-generated Swagger docs at `/docs/`
- Markdown preview for documentation
- IntelliSense for docstrings
- Automatic API documentation

### **Code Documentation**
```python
def create_agent_response(prompt: str, context: dict) -> dict:
    """
    Create intelligent agent response with Azure integration.
    
    Args:
        prompt: User input prompt
        context: Azure context and metadata
        
    Returns:
        dict: Formatted agent response
        
    Raises:
        AuthenticationError: If Azure authentication fails
        ValidationError: If input validation fails
    """
```

## 🚀 Deployment Integration

### **CI/CD Integration**
- GitHub Actions workflow visible in VS Code
- Deployment status monitoring
- Environment-specific configurations
- Automated testing on commit

### **Infrastructure as Code**
- Bicep syntax highlighting
- Template validation
- Parameter file editing
- Deployment monitoring

## 📞 Troubleshooting

### **Common Issues**

**Azure Authentication:**
```bash
# Clear VS Code Azure cache
Ctrl+Shift+P -> Azure: Sign Out
# Sign in again
Ctrl+Shift+P -> Azure: Sign In
```

**Python Path Issues:**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "${workspaceFolder}"
    }
}
```

**Docker Integration:**
```bash
# Reset Docker extension
Ctrl+Shift+P -> Docker: Refresh
# Restart Docker Desktop if needed
```

## 🎓 Learning Resources

### **VS Code Resources**
- [Azure Extensions Documentation](https://docs.microsoft.com/en-us/azure/developer/vscode/)
- [Python Development Guide](https://code.visualstudio.com/docs/python/python-tutorial)
- [Docker Integration](https://code.visualstudio.com/docs/containers/overview)

### **Workshop-Specific**
- Use integrated terminal for all commands
- Leverage IntelliSense for Azure APIs
- Debug with breakpoints and watch expressions
- Monitor performance through integrated tools

---

## 🏆 VS Code Excellence Achieved!

With this configuration, you have a professional enterprise-grade development environment that supports:

✅ **Full Azure Integration** with authentication and resource management  
✅ **Advanced Debugging** for both local and containerized applications  
✅ **Comprehensive Testing** with coverage and quality metrics  
✅ **Production Deployment** with Infrastructure as Code support  
✅ **Real-time Monitoring** with integrated dashboard access  
✅ **Security Best Practices** with automated scanning and validation  

**You're now equipped with a world-class development environment for MCP excellence!** 🚀
