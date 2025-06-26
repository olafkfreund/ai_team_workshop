import os
import json
from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)

# Helper to fetch resource from Azure Blob Storage
def fetch_resource(resource_type, language, filename):
    conn_str = os.environ['AZURE_STORAGE_CONNECTION_STRING']
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container = blob_service.get_container_client('copilot-resources')
    blob = container.get_blob_client(f'{resource_type}/{language}/{filename}')
    return blob.download_blob().readall().decode()

# Helper to get project language from metadata
def get_project_language(project_id):
    # For demo: expects a local file, but could be from DB or API
    with open(f'projects/{project_id}/project-config.json') as f:
        return json.load(f)['language']

@app.route('/agent/<project_id>/<agent_name>', methods=['POST'])
def run_agent(project_id, agent_name):
    try:
        language = get_project_language(project_id)
        prompt = fetch_resource('prompts', language, 'onboarding.md')
        agent_config = fetch_resource('agents', language, f'{agent_name}.json')
        # Simulate agent response
        user_prompt = request.json.get('prompt', '')
        return jsonify({
            'project': project_id,
            'language': language,
            'agent': agent_name,
            'prompt': prompt,
            'agent_config': json.loads(agent_config),
            'user_prompt': user_prompt,
            'result': f"[Simulated response for {agent_name} in {language}]"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
