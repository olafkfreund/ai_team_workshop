const axios = require('axios');

const AGENT = 'terraformDocsAgent';
const MPC_SERVER = 'http://localhost:8080';

const prompt = 'Generate documentation for the Terraform code in the infra directory.';

axios.post(`${MPC_SERVER}/agent/${AGENT}`, { prompt })
  .then(res => console.log(res.data))
  .catch(err => console.error(err));
