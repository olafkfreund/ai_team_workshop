# Workshop Instructor Guide

## Pre-Workshop Setup (30 minutes)

### Environment Preparation
1. **Azure Resources Setup**
   ```bash
   cd workshop/deployment
   ./deploy.sh --environment workshop --resource-group workshop-demo
   ```

2. **Validate Workshop Environment**
   ```bash
   cd workshop
   python test-workshop.py --comprehensive
   ```

3. **Prepare Demo Data**
   - Upload sample prompts to Azure Blob Storage
   - Create demo agent configurations
   - Set up monitoring dashboards

### Participant Preparation
- Send environment setup instructions 1 week before
- Provide Azure subscription access
- Share prerequisite installation guide
- Test participant environment connectivity

## Workshop Flow

### Module 1: Architecture & Setup (20 mins)
**Objectives:**
- Understand enterprise MCP architecture
- Set up local development environment
- Build and run the MCP server

**Key Points:**
- Emphasize production-ready patterns
- Explain Azure integration benefits
- Show live dashboard and monitoring

**Hands-on Activity:**
```bash
# Participants follow along
docker build -t workshop-mcp .
docker run -p 8080:8080 workshop-mcp
python test-workshop.py --quick
```

**Common Issues & Solutions:**
- Port 8080 already in use: Use `docker run -p 8081:8080`
- Docker build fails: Check Docker Desktop is running
- Health check fails: Wait 30 seconds for container startup

### Module 2: Agent Development (25 mins)
**Objectives:**
- Create custom agents with Azure integration
- Implement advanced prompt patterns
- Handle context and multi-tenancy

**Demo Script:**
1. Show existing agent in action
2. Create new agent live
3. Test with different contexts
4. Explain prompt engineering best practices

**Hands-on Activity:**
```bash
# Create custom agent
cp agents/azureVmMetricsAgent.json agents/customAgent.json
# Edit agent configuration
# Test the new agent
curl -X POST http://localhost:8080/agent/customAgent \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Custom test"}'
```

### Module 3: Production Features (30 mins)
**Objectives:**
- Implement authentication and caching
- Set up monitoring and metrics
- Configure rate limiting

**Key Demonstrations:**
1. **Authentication Flow:**
   ```bash
   # Generate token
   TOKEN=$(curl -X POST http://localhost:8080/auth/token \
     -H "Content-Type: application/json" \
     -d '{"user_id": "demo"}' | jq -r '.token')
   
   # Use authenticated request
   curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8080/agent/azureVmMetricsAgent
   ```

2. **Caching Demonstration:**
   - Show response time difference with/without cache
   - Explain cache invalidation strategies

3. **Monitoring Dashboard:**
   - Open live dashboard at `/dashboard`
   - Show real-time metrics and events
   - Explain monitoring best practices

### Module 4: Testing & Quality (20 mins)
**Objectives:**
- Run comprehensive test suites
- Understand performance benchmarks
- Implement security testing

**Demo Flow:**
1. **Unit Tests:**
   ```bash
   cd mpc-server
   pytest test_mcp_server.py -v --cov=.
   ```

2. **Load Testing:**
   ```bash
   python test-workshop.py --load-test
   ```

3. **Security Scanning:**
   ```bash
   # If available
   trivy image workshop-mcp:latest
   ```

### Module 5: Deployment & CI/CD (20 mins)
**Objectives:**
- Deploy to Azure with Infrastructure as Code
- Set up CI/CD pipeline
- Configure monitoring and alerting

**Live Deployment:**
```bash
cd deployment
# Show Bicep template
code main.bicep

# Deploy to Azure
az deployment group create \
  --resource-group workshop-demo \
  --template-file main.bicep \
  --parameters environment=demo
```

**CI/CD Pipeline:**
- Show GitHub Actions workflow
- Explain multi-environment strategy
- Demonstrate automated testing

### Module 6: Q&A & Next Steps (5 mins)
**Key Topics:**
- Enterprise adoption strategies
- Scaling considerations
- Security and compliance
- Integration with existing systems

## Troubleshooting Guide

### Common Issues

1. **"Container won't start"**
   ```bash
   # Check logs
   docker logs $(docker ps -lq)
   
   # Check port conflicts
   netstat -an | grep 8080
   
   # Restart with different port
   docker run -p 8081:8080 workshop-mcp
   ```

2. **"Health check fails"**
   ```bash
   # Wait for startup
   sleep 30
   
   # Check container status
   docker ps
   
   # Test manually
   curl http://localhost:8080/health
   ```

3. **"Agent requests timeout"**
   - Check Redis connection
   - Verify Azure credentials
   - Reduce request complexity

4. **"Dashboard not loading"**
   - Check if templates directory exists
   - Verify Flask-SocketIO installation
   - Clear browser cache

### Performance Issues

1. **Slow response times**
   - Enable Redis caching
   - Check Azure service latency
   - Optimize agent prompts

2. **High memory usage**
   - Reduce worker count
   - Implement request queuing
   - Monitor memory leaks

### Azure Integration Issues

1. **Authentication failures**
   - Verify Azure CLI login
   - Check service principal permissions
   - Validate connection strings

2. **Storage access denied**
   - Check blob container permissions
   - Verify storage account access keys
   - Test connection string format

## Assessment & Validation

### Participant Success Criteria
- [ ] Successfully build and run MCP server
- [ ] Create at least one custom agent
- [ ] Demonstrate understanding of caching and authentication
- [ ] Pass workshop validation tests (>85% success rate)
- [ ] Deploy to Azure (optional advanced)

### Workshop Quality Metrics
- Participant engagement (feedback forms)
- Technical success rate (validation results)
- Time management (staying on schedule)
- Q&A quality (relevant questions)

## Post-Workshop Follow-up

### Immediate (1 week)
- Send complete code repository
- Provide access to deployed demo environment
- Share additional resources and documentation

### Medium-term (1 month)
- Follow-up survey on implementation
- Office hours for technical questions
- Community forum access

### Long-term (3 months)
- Case study development
- Advanced workshop opportunities
- Enterprise consulting options

## Instructor Tips

### Preparation
- Test all demos 24 hours before workshop
- Have backup environments ready
- Prepare troubleshooting scenarios
- Review participant skill levels

### Delivery
- Start with working examples before theory
- Use live coding whenever possible
- Encourage questions throughout
- Adapt pace based on participant understanding

### Management
- Monitor participant progress actively
- Provide individual help when needed
- Keep track of time boundaries
- Have extension activities for fast learners

## Resources for Instructors

### Technical Documentation
- [Azure MCP Integration Guide](./AZURE_INTEGRATION.md)
- [Security Best Practices](./SECURITY_GUIDE.md)
- [Performance Optimization](./PERFORMANCE_GUIDE.md)

### Presentation Materials
- Workshop slides (PowerPoint/PDF)
- Architecture diagrams
- Demo scripts and recordings
- Hands-on exercise templates

### Support Tools
- Participant environment checker
- Common error solutions
- Emergency contact procedures
- Backup demonstration videos
