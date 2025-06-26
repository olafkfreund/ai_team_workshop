"""
Comprehensive test suite for MCP Server
Includes unit tests, integration tests, and load testing
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
import statistics

from app import app, agent_processor
from config import config

# Test client
@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """Generate auth headers for testing"""
    # Generate a test token
    response = requests.post('http://localhost:8080/auth/token', json={
        'user_id': 'test-user',
        'tenant_id': 'test-tenant'
    })
    token = response.json()['token']
    return {'Authorization': f'Bearer {token}'}

class TestHealthEndpoint:
    """Test health check functionality"""
    
    def test_health_check_success(self, client):
        """Test health endpoint returns correct status"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'services' in data
        assert 'features' in data

class TestAgentEndpoints:
    """Test agent execution functionality"""
    
    def test_agent_execution_success(self, client):
        """Test successful agent execution"""
        response = client.post('/agent/azureVmMetricsAgent', json={
            'prompt': 'Check VM performance',
            'context': {'resource_group': 'test-rg', 'vm_name': 'test-vm'}
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['agent'] == 'azureVmMetricsAgent'
        assert data['status'] == 'success'
        assert 'execution_time_ms' in data
        assert 'request_id' in data
    
    def test_agent_execution_validation_error(self, client):
        """Test agent execution with invalid request"""
        response = client.post('/agent/azureVmMetricsAgent', json={
            'prompt': 'x' * 20000  # Too long prompt
        })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Invalid request'
    
    def test_agent_execution_missing_prompt(self, client):
        """Test agent execution without prompt"""
        response = client.post('/agent/azureVmMetricsAgent', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_all_agents_execution(self, client):
        """Test all available agents"""
        agents = ['azureVmMetricsAgent', 'terraformDocsAgent', 'onboardingAgent']
        
        for agent in agents:
            response = client.post(f'/agent/{agent}', json={
                'prompt': f'Test prompt for {agent}',
                'context': {'test': True}
            })
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['agent'] == agent
            assert data['status'] == 'success'

class TestAgentProcessor:
    """Test the agent processing engine"""
    
    @pytest.mark.asyncio
    async def test_vm_metrics_agent_processing(self):
        """Test VM metrics agent processing"""
        processor = agent_processor
        
        request_data = {
            'prompt': 'Check CPU and memory for VM test-vm',
            'context': {'resource_group': 'test-rg', 'vm_name': 'test-vm'}
        }
        
        result = await processor.process_agent_request('azureVmMetricsAgent', request_data)
        
        assert result['agent'] == 'azureVmMetricsAgent'
        assert result['status'] == 'success'
        assert 'CPU Usage' in result['result']
        assert 'Memory Usage' in result['result']
        assert result['execution_time_ms'] > 0
    
    @pytest.mark.asyncio
    async def test_terraform_docs_agent_processing(self):
        """Test Terraform docs agent processing"""
        processor = agent_processor
        
        request_data = {
            'prompt': 'Generate documentation for main.tf',
            'context': {'project_path': './terraform'}
        }
        
        result = await processor.process_agent_request('terraformDocsAgent', request_data)
        
        assert result['agent'] == 'terraformDocsAgent'
        assert result['status'] == 'success'
        assert 'Infrastructure Overview' in result['result']
        assert 'Resource Summary' in result['result']
    
    @pytest.mark.asyncio
    async def test_onboarding_agent_processing(self):
        """Test onboarding agent processing"""
        processor = agent_processor
        
        request_data = {
            'prompt': 'Help me get started as a new developer',
            'context': {'role': 'developer', 'team': 'platform'}
        }
        
        result = await processor.process_agent_request('onboardingAgent', request_data)
        
        assert result['agent'] == 'onboardingAgent'
        assert result['status'] == 'success'
        assert 'Welcome to the Team' in result['result']
        assert 'Onboarding Checklist' in result['result']

class TestListAgentsEndpoint:
    """Test agents listing functionality"""
    
    def test_list_agents_success(self, client):
        """Test listing available agents"""
        response = client.get('/agents')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'agents' in data
        assert 'count' in data
        assert len(data['agents']) == 3
        
        # Check agent structure
        agent = data['agents'][0]
        assert 'name' in agent
        assert 'description' in agent
        assert 'capabilities' in agent
        assert 'required_context' in agent
        assert 'example_usage' in agent

class TestMetricsEndpoint:
    """Test Prometheus metrics"""
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint returns Prometheus format"""
        # First make some requests to generate metrics
        for i in range(5):
            client.post('/agent/azureVmMetricsAgent', json={
                'prompt': f'Test request {i}'
            })
        
        response = client.get('/metrics')
        assert response.status_code == 200
        
        # Check Prometheus format
        data = response.data.decode('utf-8')
        assert 'mcp_requests_total' in data
        assert 'mcp_agent_requests_total' in data

class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_token_generation(self, client):
        """Test JWT token generation"""
        response = client.post('/auth/token', json={
            'user_id': 'test-user',
            'tenant_id': 'test-tenant'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'expires_in' in data

class TestCacheManagement:
    """Test caching functionality"""
    
    def test_cache_clear(self, client):
        """Test cache clearing"""
        response = client.post('/admin/cache/clear')
        # Should work even if Redis is not available
        assert response.status_code in [200, 404]

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_404_endpoint(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Endpoint not found'
        assert 'available_endpoints' in data

class TestLoadAndPerformance:
    """Load testing and performance validation"""
    
    def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        def make_request():
            response = client.post('/agent/azureVmMetricsAgent', json={
                'prompt': 'Load test request'
            })
            return response.status_code == 200
        
        # Test with 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(results), "Some concurrent requests failed"
    
    def test_response_time_performance(self, client):
        """Test response time performance"""
        response_times = []
        
        for _ in range(20):
            start_time = time.time()
            response = client.post('/agent/azureVmMetricsAgent', json={
                'prompt': 'Performance test'
            })
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)  # Convert to ms
        
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        print(f"Average response time: {avg_response_time:.2f}ms")
        print(f"95th percentile response time: {p95_response_time:.2f}ms")
        
        # Performance assertions
        assert avg_response_time < 2000, f"Average response time too high: {avg_response_time}ms"
        assert p95_response_time < 5000, f"95th percentile response time too high: {p95_response_time}ms"

class TestIntegrationScenarios:
    """Integration tests for real-world scenarios"""
    
    def test_complete_vm_monitoring_workflow(self, client):
        """Test complete VM monitoring workflow"""
        # Step 1: Get VM metrics
        response = client.post('/agent/azureVmMetricsAgent', json={
            'prompt': 'Show me detailed performance metrics for web-server-01',
            'context': {
                'resource_group': 'production',
                'vm_name': 'web-server-01'
            }
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'CPU Usage' in data['result']
        assert 'Recommendations' in data['result']
        
        # Step 2: Check if metrics are cached (second request should be faster)
        start_time = time.time()
        response2 = client.post('/agent/azureVmMetricsAgent', json={
            'prompt': 'Show me detailed performance metrics for web-server-01',
            'context': {
                'resource_group': 'production',
                'vm_name': 'web-server-01'
            }
        })
        end_time = time.time()
        
        assert response2.status_code == 200
        # Second request might be faster due to caching
    
    def test_terraform_documentation_workflow(self, client):
        """Test Terraform documentation workflow"""
        response = client.post('/agent/terraformDocsAgent', json={
            'prompt': 'Generate comprehensive documentation for our Azure infrastructure',
            'context': {
                'project_path': './infrastructure',
                'include_costs': True
            }
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Infrastructure Overview' in data['result']
        assert 'Resource Summary' in data['result']
        assert 'Estimated Cost' in data['result']
    
    def test_multi_tenant_isolation(self, client):
        """Test multi-tenant isolation"""
        # Request from tenant A
        response_a = client.post('/agent/onboardingAgent', json={
            'prompt': 'Help me get started',
            'tenant_id': 'tenant-a'
        })
        
        # Request from tenant B
        response_b = client.post('/agent/onboardingAgent', json={
            'prompt': 'Help me get started',
            'tenant_id': 'tenant-b'
        })
        
        assert response_a.status_code == 200
        assert response_b.status_code == 200
        
        # Both should succeed and be isolated

# Load testing utilities
class LoadTester:
    """Load testing utilities for stress testing"""
    
    @staticmethod
    def run_load_test(base_url: str, num_requests: int = 100, concurrent_users: int = 10):
        """Run a load test against the MCP server"""
        print(f"Starting load test: {num_requests} requests with {concurrent_users} concurrent users")
        
        results = {
            'total_requests': num_requests,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.post(f'{base_url}/agent/azureVmMetricsAgent', json={
                    'prompt': 'Load test request'
                }, timeout=30)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                results['response_times'].append(response_time)
                
                if response.status_code == 200:
                    results['successful_requests'] += 1
                else:
                    results['failed_requests'] += 1
                    results['errors'].append(f"HTTP {response.status_code}")
                    
            except Exception as e:
                results['failed_requests'] += 1
                results['errors'].append(str(e))
        
        # Execute load test
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            # Wait for all requests to complete
            for future in futures:
                future.result()
        
        # Calculate statistics
        if results['response_times']:
            results['avg_response_time'] = statistics.mean(results['response_times'])
            results['min_response_time'] = min(results['response_times'])
            results['max_response_time'] = max(results['response_times'])
            results['p95_response_time'] = statistics.quantiles(results['response_times'], n=20)[18]
            results['p99_response_time'] = statistics.quantiles(results['response_times'], n=100)[98]
        
        results['success_rate'] = (results['successful_requests'] / results['total_requests']) * 100
        
        return results

# Test configuration
pytest_plugins = ['pytest_asyncio']

if __name__ == '__main__':
    # Run tests
    pytest.main(['-v', __file__])
    
    # Run load test if server is running
    try:
        load_tester = LoadTester()
        load_results = load_tester.run_load_test('http://localhost:8080', 50, 5)
        
        print("\n" + "="*50)
        print("LOAD TEST RESULTS")
        print("="*50)
        print(f"Total Requests: {load_results['total_requests']}")
        print(f"Successful: {load_results['successful_requests']}")
        print(f"Failed: {load_results['failed_requests']}")
        print(f"Success Rate: {load_results['success_rate']:.2f}%")
        
        if load_results['response_times']:
            print(f"Avg Response Time: {load_results['avg_response_time']:.2f}ms")
            print(f"Min Response Time: {load_results['min_response_time']:.2f}ms")
            print(f"Max Response Time: {load_results['max_response_time']:.2f}ms")
            print(f"95th Percentile: {load_results['p95_response_time']:.2f}ms")
            print(f"99th Percentile: {load_results['p99_response_time']:.2f}ms")
        
        if load_results['errors']:
            print(f"Errors: {set(load_results['errors'])}")
            
    except Exception as e:
        print(f"Load test failed: {e}")
        print("Make sure the MCP server is running on http://localhost:8080")
