# 🏗️ Enterprise MCP Workshop - Module Tasks & Challenges

## 📚 Workshop Overview

**Duration:** 120 minutes across 6 focused modules  
**Approach:** Hands-on learning with real Azure integration  
**Outcome:** Production-ready MCP server deployment

---

## 🎯 Module 1: Architecture & Setup (20 minutes)

### **Learning Objectives**
- Understand enterprise MCP server architecture patterns
- Set up production-ready development environment
- Build and deploy containerized MCP server
- Validate comprehensive testing framework

### **Hands-on Tasks**

#### **Task 1.1: Environment Validation** (5 mins)
```bash
# Validate your complete environment setup
cd workshop
python test-workshop.py --pre-workshop

# Expected: 95%+ validation success rate
# ✅ Azure CLI authenticated and accessible
# ✅ Docker running with enterprise features
# ✅ All required Python dependencies installed
# ✅ Redis cache accessible for performance features
```

#### **Task 1.2: Enterprise MCP Server Build** (10 mins)
```bash
# Build production-ready multi-stage Docker image
cd mpc-server
docker build -t workshop-mcp .

# Launch with full enterprise features enabled
docker run -d -p 8080:8080 \
  -e MCP_DEBUG=true \
  -e ENABLE_AUTHENTICATION=true \
  -e ENABLE_CACHING=true \
  -e ENABLE_MONITORING=true \
  --name workshop-mcp workshop-mcp

# Validate health and feature endpoints
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

#### **Task 1.3: Live Dashboard Access** (5 mins)
- **Action**: Open real-time monitoring dashboard
- **URL**: `http://localhost:8080/dashboard`
- **Validation**: See live metrics, WebSocket connections, request counts
- **Success Criteria**: Dashboard loads with real-time data updates

---

## 🤖 Module 2: Agent Development (25 minutes)

### **Learning Objectives**
- Build intelligent agents with real Azure API integration
- Implement advanced context handling and multi-tenancy
- Master prompt engineering for production scenarios
- Test agents with actual Azure resources

### **Hands-on Tasks**

#### **Task 2.1: Azure VM Monitoring Agent Analysis** (8 mins)
```bash
# Examine the production Azure VM monitoring agent
cat agents/azureVmMetricsAgent.json

# Test with real Azure VM data
curl -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me the status of virtual machines in my subscription", "context": {"subscription_id": "your-subscription-id"}}'
```

#### **Task 2.2: Custom Storage Analytics Agent** (12 mins)
- **Objective**: Create an agent that analyzes Azure Storage account usage
- **Requirements**:
  - Query real Azure Storage metrics
  - Provide usage recommendations
  - Handle multiple storage accounts
  - Include cost optimization suggestions

```bash
# Create your custom agent configuration
cp agents/azureVmMetricsAgent.json agents/storageAnalyticsAgent.json

# Edit the agent for storage analytics
code agents/storageAnalyticsAgent.json

# Test your custom agent
curl -X POST http://localhost:8080/agent/storageAnalyticsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze storage usage and provide cost optimization recommendations"}'
```

#### **Task 2.3: Multi-tenant Context Handling** (5 mins)
```bash
# Test agent with different subscription contexts
curl -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "VM status", "context": {"subscription_id": "sub-1", "resource_group": "prod"}}'

curl -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "VM status", "context": {"subscription_id": "sub-2", "resource_group": "dev"}}'
```

**Success Criteria**: Custom agent responds with real Azure data and appropriate recommendations.

---

## 🔐 Module 3: Production Features (30 minutes)

### **Learning Objectives**
- Implement JWT authentication with security best practices
- Configure Redis caching for optimal performance
- Set up rate limiting and abuse prevention
- Enable comprehensive monitoring and audit logging

### **Hands-on Tasks**

#### **Task 3.1: Authentication Implementation** (10 mins)
```bash
# Generate authentication token
TOKEN=$(curl -X POST http://localhost:8080/auth/token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "workshop-participant", "roles": ["developer"]}' | jq -r '.token')

echo "Your JWT Token: $TOKEN"

# Use authenticated requests
curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show VM performance metrics"}'

# Test authentication validation
curl -H "Authorization: Bearer invalid-token" \
  http://localhost:8080/agent/azureVmMetricsAgent
```

#### **Task 3.2: Redis Caching Performance** (10 mins)
```bash
# Test response times without cache (first request)
time curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List all VMs with status"}'

# Test response times with cache (subsequent request)
time curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "List all VMs with status"}'

# Verify cache statistics
curl http://localhost:8080/metrics | grep cache
```

#### **Task 3.3: Rate Limiting & Monitoring** (10 mins)
```bash
# Test rate limiting (generate multiple requests)
for i in {1..15}; do
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8080/health &
done
wait

# Check rate limit headers and responses
curl -I -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/health

# Monitor real-time metrics on dashboard
# Open: http://localhost:8080/dashboard
# Observe: Request rates, error counts, cache hit ratios
```

**Success Criteria**: Authentication working, caching improves performance by >50%, rate limiting prevents abuse.

---

## 🧪 Module 4: Testing & Quality (20 minutes)

### **Learning Objectives**
- Execute comprehensive test suites with coverage analysis
- Perform load testing and performance validation
- Implement security testing and vulnerability scanning
- Establish quality gates and automated validation

### **Hands-on Tasks**

#### **Task 4.1: Unit & Integration Testing** (8 mins)
```bash
# Run comprehensive test suite with coverage
cd mpc-server
pytest test_mcp_server.py -v --cov=. --cov-report=html

# View coverage report
# open htmlcov/index.html

# Run specific test categories
pytest test_mcp_server.py::test_authentication -v
pytest test_mcp_server.py::test_azure_integration -v
pytest test_mcp_server.py::test_caching -v
```

#### **Task 4.2: Performance & Load Testing** (8 mins)
```bash
# Run comprehensive workshop validation
cd ..
python test-workshop.py --load-test

# Expected results:
# ✅ 50+ test scenarios executed
# ✅ Load test: 100 concurrent requests handled
# ✅ Average response time < 500ms
# ✅ Zero critical failures
# ✅ Performance benchmarks met
```

#### **Task 4.3: Security Validation** (4 mins)
```bash
# Test input validation and sanitization
curl -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<script>alert(\"xss\")</script>", "context": {"malicious": "../../etc/passwd"}}'

# Test authentication bypass attempts
curl -X POST http://localhost:8080/agent/azureVmMetricsAgent \
  -H "Authorization: Bearer fake-token" \
  -d '{"prompt": "test"}'

# Review security audit logs
curl http://localhost:8080/logs | jq '.[] | select(.level == "SECURITY")'
```

**Success Criteria**: All tests pass, performance benchmarks met, security vulnerabilities prevented.

---

## 🚀 Module 5: Deployment & CI/CD (20 minutes)

### **Learning Objectives**
- Deploy to Azure using Infrastructure as Code (Bicep)
- Configure automated CI/CD pipelines with GitHub Actions
- Set up production monitoring and alerting
- Implement multi-environment deployment strategies

### **Hands-on Tasks**

#### **Task 5.1: Infrastructure as Code Review** (8 mins)
```bash
# Examine Bicep template for Azure deployment
cd deployment
cat main.bicep

# Review deployment parameters
cat parameters.json

# Validate template syntax
az bicep build --file main.bicep
```

#### **Task 5.2: CI/CD Pipeline Configuration** (7 mins)
```bash
# Review GitHub Actions workflow
cat .github/workflows/mcp-server.yml

# Key features to understand:
# - Multi-stage builds (test → build → deploy)
# - Environment-specific deployments
# - Automated testing integration
# - Security scanning
# - Container registry publishing
```

#### **Task 5.3: Azure Deployment (Optional)** (5 mins)
```bash
# Deploy to Azure Container Instances (if subscription permits)
cd deployment
./deploy.sh --environment workshop --resource-group workshop-rg

# Monitor deployment progress
az container show --name workshop-mcp --resource-group workshop-rg
```

**Success Criteria**: Understanding of IaC templates, CI/CD pipeline configured, deployment process validated.

---

## 🎯 Module 6: Real-World Scenarios & Q&A (5 minutes)

### **Challenge Scenarios** (Choose One)

#### **Scenario A: Enterprise Onboarding Assistant**
Create an agent that helps new developers with:
- Azure resource discovery and permissions
- Code repository setup and cloning
- Development environment configuration
- Team contact information and escalation paths

#### **Scenario B: Production Incident Response**
Build an agent that assists with:
- Azure service health status checking
- Log analysis and error pattern detection
- Runbook guidance for common issues
- Escalation procedures and contact information

#### **Scenario C: Cost Optimization Advisor**
Develop an agent that provides:
- Azure resource cost analysis
- Optimization recommendations
- Sizing and scaling suggestions
- Budget alerts and forecasting

### **Implementation Challenge** (3 mins)
```bash
# Implement your chosen scenario
cp agents/azureVmMetricsAgent.json agents/yourScenarioAgent.json
# Edit and customize for your scenario
# Test with realistic queries
```

### **Q&A & Next Steps** (2 mins)
- **Enterprise Adoption Strategies**
- **Scaling Considerations**
- **Security and Compliance Requirements**
- **Integration with Existing Systems**
- **ROI Measurement and Success Metrics**

---

## 📊 Workshop Success Validation

### **Final Validation Checklist**
```bash
# Run comprehensive workshop validation
python test-workshop.py --final-validation

# Expected comprehensive results:
# ✅ All 6 modules completed successfully
# ✅ Custom agents created and functional
# ✅ Authentication and security features working
# ✅ Performance benchmarks exceeded
# ✅ Production-ready deployment understanding
# ✅ 95%+ overall workshop success rate
```

### **Knowledge Assessment Questions**

#### **Technical Understanding**
1. Explain the benefits of Redis caching in MCP server architecture
2. Describe how JWT authentication enhances security in production
3. What are the key components of enterprise monitoring and observability?
4. How does Infrastructure as Code improve deployment reliability?

#### **Implementation Planning**
1. What steps would you take to deploy this in your organization?
2. How would you customize agents for your specific business needs?
3. What security considerations are critical for production deployment?
4. How would you measure the success and ROI of MCP implementation?

### **Success Criteria Achievement**
- [ ] **Technical Mastery**: All hands-on tasks completed successfully
- [ ] **Understanding**: Can explain enterprise architecture patterns
- [ ] **Application**: Can adapt concepts to organizational needs
- [ ] **Planning**: Has concrete next steps for implementation

---

## 🏆 Workshop Excellence Achieved!

Congratulations on completing the Enterprise MCP Workshop! You've successfully:

✅ **Built production-ready MCP servers** with real Azure integration  
✅ **Implemented enterprise security** with authentication and monitoring  
✅ **Deployed using modern DevOps practices** with IaC and CI/CD  
✅ **Mastered comprehensive testing** strategies and quality gates  
✅ **Gained strategic understanding** of enterprise adoption approaches  

**You're now ready to lead MCP implementations in your organization!** 🚀

---

## 📞 Continued Learning & Support

- **Documentation**: Complete guides in `/docs/` folder
- **Community**: GitHub Discussions for ongoing questions
- **Advanced Training**: Contact us for enterprise consulting
- **Best Practices**: Continue following the patterns learned today

*The journey to MCP excellence continues beyond this workshop!*
