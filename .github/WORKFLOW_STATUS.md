# GitHub Actions Workflow Status

## ⚠️ AUTO-RUN DISABLED

Both MCP Server CI/CD Pipeline workflow files have been configured to **only run manually** to prevent automatic execution.

### Current Configuration

**Files affected:**
- `mcp-server.yml` - Main workflow file
- `mcp-server-clean.yml` - Clean backup version

**Status:**
- ❌ **Push triggers**: Disabled (commented out)
- ❌ **Pull request triggers**: Disabled (commented out)  
- ✅ **Manual dispatch**: Enabled

### How to Run the Workflow

1. Navigate to the **Actions** tab in your GitHub repository
2. Select **"MCP Server CI/CD Pipeline"** from the workflow list
3. Click **"Run workflow"** button
4. Choose your target environment:
   - `dev` - Development environment
   - `staging` - Staging environment  
   - `prod` - Production environment
5. Click **"Run workflow"** to start execution

### Re-enabling Auto-Run

To restore automatic workflow execution, edit `.github/workflows/mcp-server.yml` and:

1. Uncomment the `push:` and `pull_request:` trigger sections
2. Update the job conditions to include the appropriate branch checks
3. Commit the changes

### Workflow Jobs

The workflow includes the following jobs (all manual-only):

- **quality-checks**: Code formatting, linting, security scanning
- **test**: Unit tests with coverage reporting
- **build**: Docker image build and vulnerability scanning
- **deploy-dev**: Development environment deployment
- **deploy-staging**: Staging environment deployment  
- **deploy-production**: Production environment deployment
- **performance-test**: Load testing against staging
- **security-scan**: OWASP ZAP security testing
- **cleanup**: Resource cleanup and maintenance

---
*Last updated: $(date)*
