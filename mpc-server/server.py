from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

@app.route('/agent/<agent_name>', methods=['POST'])
def run_agent(agent_name):
    """Simple workshop version - simulate agent responses"""
    data = request.json
    user_prompt = data.get('prompt', '')
    
    # For workshop: simulate different responses based on agent name
    responses = {
        'azureVmMetricsAgent': f"✅ VM Metrics Analysis:\nCPU: 45%, Memory: 62%, Disk I/O: Normal\nRecommendation: Monitor during peak hours",
        'terraformDocsAgent': f"📋 Generated Terraform Documentation:\n# Infrastructure Overview\nResources: 5 VMs, 2 Load Balancers\nEstimated cost: $340/month",
        'onboardingAgent': f"🎯 Welcome! Here's your onboarding checklist:\n1. Setup Azure CLI\n2. Clone repositories\n3. Configure VS Code"
    }
    
    response_text = responses.get(agent_name, f"[Simulated response for {agent_name}]")
    
    return jsonify({
        'agent': agent_name,
        'prompt': user_prompt,
        'result': response_text,
        'status': 'success'
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'version': 'workshop-1.0'})

if __name__ == '__main__':
    print("🚀 Workshop MCP Server starting on http://localhost:8080")
    print("📖 Available agents: azureVmMetricsAgent, terraformDocsAgent, onboardingAgent")
    app.run(host='0.0.0.0', port=8080, debug=True)
