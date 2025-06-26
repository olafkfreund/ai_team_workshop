import requests

AGENT = "azureVmMetricsAgent"
MPC_SERVER = "http://localhost:8080"

prompt = "Check the CPU and network metrics for VM 'webserver01' in resource group 'prod-rg'."

response = requests.post(f"{MPC_SERVER}/agent/{AGENT}", json={"prompt": prompt})
print(response.json())
