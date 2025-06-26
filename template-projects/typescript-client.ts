import axios from 'axios';

const PROJECT_ID = 'sample-python-app'; // Change to your project id
const AGENT = 'azureVmMetricsAgent';
const MPC_SERVER = 'http://localhost:8080';

const prompt = "Check the CPU and network metrics for VM 'webserver01' in resource group 'prod-rg'.";

axios.post(`${MPC_SERVER}/agent/${PROJECT_ID}/${AGENT}`, { prompt })
  .then(res => console.log(res.data))
  .catch(err => console.error(err));
