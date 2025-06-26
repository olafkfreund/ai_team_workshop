#!/usr/bin/env python3
"""
Comprehensive Workshop Validation Suite
Tests all aspects of the MCP server and validates enterprise readiness
"""
import requests
import json
import sys
import time
import asyncio
import threading
import statistics
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import os
import socket

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class WorkshopValidator:
    """Comprehensive workshop validation with enterprise features"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "warnings": 0,
            "start_time": datetime.now(),
            "test_results": []
        }
        self.agents = ["azureVmMetricsAgent", "terraformDocsAgent", "onboardingAgent"]
    
    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with colors and timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = {
            "INFO": Colors.BLUE,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "HEADER": Colors.HEADER
        }.get(level, Colors.ENDC)
        
        print(f"{color}[{timestamp}] {level}: {message}{Colors.ENDC}")
    
    def test_result(self, test_name: str, passed: bool, details: str = "", response_time: float = 0):
        """Record test result"""
        self.results["total_tests"] += 1
        if passed:
            self.results["passed_tests"] += 1
            self.log(f"✅ {test_name}", "SUCCESS")
        else:
            self.results["failed_tests"] += 1
            self.log(f"❌ {test_name}", "ERROR")
        
        self.results["test_results"].append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "response_time_ms": response_time,
            "timestamp": datetime.now().isoformat()
        })
        
        if details:
            self.log(f"   Details: {details}", "INFO")

    def check_prerequisites(self) -> bool:
        """Check all prerequisites for the workshop"""
        self.log("Checking Prerequisites", "HEADER")
        
        prerequisites = [
            ("Docker", ["docker", "--version"]),
            ("Python 3.8+", ["python3", "--version"]),
            ("curl", ["curl", "--version"]),
            ("jq (optional)", ["jq", "--version"])
        ]
        
        all_good = True
        for name, cmd in prerequisites:
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.test_result(f"Prerequisite: {name}", True, version)
                else:
                    self.test_result(f"Prerequisite: {name}", False, "Not found or error")
                    if name != "jq (optional)":
                        all_good = False
            except FileNotFoundError:
                self.test_result(f"Prerequisite: {name}", False, "Command not found")
                if name != "jq (optional)":
                    all_good = False
        
        return all_good

    def check_files_and_structure(self) -> bool:
        """Validate workshop file structure"""
        self.log("Validating File Structure", "HEADER")
        
        required_files = [
            "Dockerfile",
            "requirements.txt",
            "app.py",
            "config.py",
            "../test-workshop.py",
            "templates/dashboard.html"
        ]
        
        optional_files = [
            "server.py",
            "dashboard.py",
            "test_mcp_server.py"
        ]
        
        all_required = True
        for file_path in required_files:
            if os.path.exists(file_path):
                # Check file size and basic content
                size = os.path.getsize(file_path)
                self.test_result(f"Required file: {file_path}", True, f"Size: {size} bytes")
            else:
                self.test_result(f"Required file: {file_path}", False, "Missing")
                all_required = False
        
        for file_path in optional_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                self.test_result(f"Optional file: {file_path}", True, f"Size: {size} bytes")
        
        return all_required

    def check_docker_setup(self) -> bool:
        """Validate Docker setup and image build"""
        self.log("Validating Docker Setup", "HEADER")
        
        # Check if Docker is running
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                self.test_result("Docker daemon", True, "Running")
            else:
                self.test_result("Docker daemon", False, "Not running")
                return False
        except Exception as e:
            self.test_result("Docker daemon", False, str(e))
            return False
        
        # Check if image exists or can be built
        try:
            result = subprocess.run(["docker", "images", "-q", "workshop-mcp"], capture_output=True, text=True)
            if result.stdout.strip():
                self.test_result("Docker image", True, "Image exists")
                return True
            else:
                self.log("Docker image not found, attempting to build...", "INFO")
                build_result = subprocess.run(["docker", "build", "-t", "workshop-mcp", "."], 
                                            capture_output=True, text=True)
                if build_result.returncode == 0:
                    self.test_result("Docker image build", True, "Built successfully")
                    return True
                else:
                    self.test_result("Docker image build", False, build_result.stderr[:200])
                    return False
        except Exception as e:
            self.test_result("Docker image", False, str(e))
            return False

    def check_server_connectivity(self) -> bool:
        """Check if MCP server is accessible"""
        self.log("Testing Server Connectivity", "HEADER")
        
        # Check if port is open
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 8080))
            sock.close()
            
            if result == 0:
                self.test_result("Port 8080 connectivity", True, "Port is open")
            else:
                self.test_result("Port 8080 connectivity", False, "Port is closed")
                return False
        except Exception as e:
            self.test_result("Port 8080 connectivity", False, str(e))
            return False
        
        # Test basic HTTP connectivity
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.test_result("Health endpoint", True, 
                               f"Status: {data.get('status', 'unknown')}", response_time)
                return True
            else:
                self.test_result("Health endpoint", False, 
                               f"HTTP {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.test_result("Health endpoint", False, str(e))
            self.log("💡 Hint: Make sure to run 'docker run -p 8080:8080 workshop-mcp'", "WARNING")
            return False

    def test_health_endpoint_detailed(self):
        """Detailed health endpoint testing"""
        self.log("Testing Health Endpoint Details", "HEADER")
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["status", "timestamp", "version"]
                for field in required_fields:
                    if field in data:
                        self.test_result(f"Health field: {field}", True, str(data[field]))
                    else:
                        self.test_result(f"Health field: {field}", False, "Missing")
                
                # Check optional enterprise fields
                optional_fields = ["services", "features"]
                for field in optional_fields:
                    if field in data:
                        self.test_result(f"Enterprise field: {field}", True, 
                                       f"Count: {len(data[field])}")
                    else:
                        self.results["warnings"] += 1
                        self.log(f"⚠️  Optional enterprise field missing: {field}", "WARNING")
                
                # Performance check
                if response_time < 100:
                    self.test_result("Health response time", True, f"{response_time:.1f}ms")
                elif response_time < 500:
                    self.test_result("Health response time", True, 
                                   f"{response_time:.1f}ms (acceptable)")
                else:
                    self.test_result("Health response time", False, 
                                   f"{response_time:.1f}ms (too slow)")
            else:
                self.test_result("Health endpoint detailed", False, 
                               f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("Health endpoint detailed", False, str(e))

    def test_agents_comprehensive(self):
        """Comprehensive agent testing"""
        self.log("Testing Agents Comprehensively", "HEADER")
        
        # Test agent listing
        try:
            response = requests.get(f"{self.base_url}/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                agent_count = len(data.get('agents', []))
                self.test_result("Agents listing", True, f"Found {agent_count} agents")
                
                # Validate agent structure
                for agent in data.get('agents', []):
                    required_fields = ["name", "description", "capabilities"]
                    agent_name = agent.get('name', 'Unknown')
                    
                    for field in required_fields:
                        if field in agent:
                            self.test_result(f"Agent {agent_name} field: {field}", True)
                        else:
                            self.test_result(f"Agent {agent_name} field: {field}", False)
            else:
                self.test_result("Agents listing", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("Agents listing", False, str(e))
        
        # Test each agent with multiple scenarios
        test_scenarios = {
            "azureVmMetricsAgent": [
                {
                    "prompt": "Check CPU and memory usage for VM 'web-server-01'",
                    "context": {"resource_group": "production", "vm_name": "web-server-01"}
                },
                {
                    "prompt": "Analyze disk performance for database server",
                    "context": {"resource_group": "database", "vm_name": "db-server-01"}
                }
            ],
            "terraformDocsAgent": [
                {
                    "prompt": "Generate documentation for main.tf",
                    "context": {"project_path": "./infrastructure"}
                },
                {
                    "prompt": "Create cost analysis for Azure resources",
                    "context": {"project_path": "./terraform", "include_costs": True}
                }
            ],
            "onboardingAgent": [
                {
                    "prompt": "Help me get started as a new developer",
                    "context": {"role": "developer", "team": "platform"}
                },
                {
                    "prompt": "What's my first week checklist?",
                    "context": {"role": "devops", "team": "infrastructure"}
                }
            ]
        }
        
        for agent_name, scenarios in test_scenarios.items():
            for i, scenario in enumerate(scenarios):
                try:
                    start_time = time.time()
                    response = requests.post(
                        f"{self.base_url}/agent/{agent_name}",
                        json=scenario,
                        timeout=15
                    )
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        data = response.json()
                        result_length = len(data.get('result', ''))
                        
                        # Check response structure
                        if all(field in data for field in ['agent', 'status', 'result']):
                            self.test_result(
                                f"{agent_name} scenario {i+1}", 
                                True, 
                                f"Response: {result_length} chars", 
                                response_time
                            )
                            
                            # Check for meaningful content
                            result_text = data.get('result', '')
                            if len(result_text) > 50 and any(keyword in result_text.lower() 
                                                           for keyword in ['azure', 'vm', 'cpu', 'terraform', 'onboarding']):
                                self.test_result(f"{agent_name} content quality", True, 
                                               "Contains relevant keywords")
                            else:
                                self.test_result(f"{agent_name} content quality", False, 
                                               "Generic or empty response")
                        else:
                            self.test_result(f"{agent_name} scenario {i+1}", False, 
                                           "Missing required fields")
                    else:
                        self.test_result(f"{agent_name} scenario {i+1}", False, 
                                       f"HTTP {response.status_code}")
                        
                except Exception as e:
                    self.test_result(f"{agent_name} scenario {i+1}", False, str(e))

    def test_performance_and_load(self):
        """Performance and load testing"""
        self.log("Testing Performance & Load", "HEADER")
        
        # Single request performance
        response_times = []
        for i in range(10):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/agent/azureVmMetricsAgent",
                    json={"prompt": f"Performance test {i}"},
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append((end_time - start_time) * 1000)
                    
            except Exception:
                pass
        
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            self.test_result("Single request performance", True, 
                           f"Avg: {avg_time:.1f}ms, Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")
            
            # Performance thresholds
            if avg_time < 1000:
                self.test_result("Performance threshold", True, "Under 1 second average")
            elif avg_time < 2000:
                self.test_result("Performance threshold", True, "Under 2 seconds (acceptable)")
            else:
                self.test_result("Performance threshold", False, f"Too slow: {avg_time:.1f}ms")
        
        # Concurrent requests test
        def make_concurrent_request():
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.base_url}/agent/azureVmMetricsAgent",
                    json={"prompt": "Concurrent test"},
                    timeout=15
                )
                end_time = time.time()
                return response.status_code == 200, (end_time - start_time) * 1000
            except Exception:
                return False, 0
        
        # Test with 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_concurrent_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        successful_requests = sum(1 for success, _ in results if success)
        concurrent_times = [time for success, time in results if success]
        
        if successful_requests == 5:
            avg_concurrent_time = statistics.mean(concurrent_times)
            self.test_result("Concurrent requests", True, 
                           f"5/5 successful, avg: {avg_concurrent_time:.1f}ms")
        else:
            self.test_result("Concurrent requests", False, 
                           f"Only {successful_requests}/5 successful")

    def test_api_documentation(self):
        """Test API documentation endpoints"""
        self.log("Testing API Documentation", "HEADER")
        
        # Test Swagger documentation
        try:
            response = requests.get(f"{self.base_url}/docs/", timeout=10)
            if response.status_code == 200:
                self.test_result("Swagger documentation", True, "Accessible")
            else:
                self.test_result("Swagger documentation", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("Swagger documentation", False, str(e))
        
        # Test API spec
        try:
            response = requests.get(f"{self.base_url}/apispec.json", timeout=10)
            if response.status_code == 200:
                spec = response.json()
                self.test_result("API specification", True, 
                               f"Paths: {len(spec.get('paths', {}))}")
            else:
                self.test_result("API specification", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("API specification", False, str(e))

    def test_enterprise_features(self):
        """Test enterprise features"""
        self.log("Testing Enterprise Features", "HEADER")
        
        # Test metrics endpoint
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200:
                metrics_text = response.text
                if "mcp_requests_total" in metrics_text:
                    self.test_result("Prometheus metrics", True, "Available with counters")
                else:
                    self.test_result("Prometheus metrics", False, "Missing expected metrics")
            else:
                self.test_result("Prometheus metrics", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("Prometheus metrics", False, str(e))
        
        # Test authentication endpoint
        try:
            response = requests.post(f"{self.base_url}/auth/token", 
                                   json={"user_id": "test", "tenant_id": "test"}, 
                                   timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.test_result("JWT authentication", True, "Token generated")
                else:
                    self.test_result("JWT authentication", False, "No token in response")
            else:
                self.test_result("JWT authentication", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("JWT authentication", False, str(e))
        
        # Test dashboard
        try:
            response = requests.get(f"{self.base_url}/dashboard", timeout=10)
            if response.status_code == 200:
                self.test_result("Dashboard interface", True, "Accessible")
            else:
                self.test_result("Dashboard interface", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("Dashboard interface", False, str(e))

    def test_error_handling(self):
        """Test error handling scenarios"""
        self.log("Testing Error Handling", "HEADER")
        
        # Test invalid endpoint
        try:
            response = requests.get(f"{self.base_url}/invalid-endpoint", timeout=5)
            if response.status_code == 404:
                data = response.json()
                if "error" in data and "available_endpoints" in data:
                    self.test_result("404 error handling", True, "Proper error response")
                else:
                    self.test_result("404 error handling", False, "Poor error response")
            else:
                self.test_result("404 error handling", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.test_result("404 error handling", False, str(e))
        
        # Test invalid agent request
        try:
            response = requests.post(f"{self.base_url}/agent/invalidAgent", 
                                   json={"prompt": "test"}, timeout=5)
            if response.status_code == 200:
                # This is OK - the server handles unknown agents gracefully
                self.test_result("Invalid agent handling", True, "Graceful handling")
            elif 400 <= response.status_code < 500:
                self.test_result("Invalid agent handling", True, f"Proper error {response.status_code}")
            else:
                self.test_result("Invalid agent handling", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.test_result("Invalid agent handling", False, str(e))
        
        # Test malformed request
        try:
            response = requests.post(f"{self.base_url}/agent/azureVmMetricsAgent", 
                                   json={"invalid": "request"}, timeout=5)
            if 400 <= response.status_code < 500:
                self.test_result("Malformed request handling", True, f"HTTP {response.status_code}")
            else:
                self.test_result("Malformed request handling", False, 
                               f"Expected 4xx, got {response.status_code}")
        except Exception as e:
            self.test_result("Malformed request handling", False, str(e))

    def generate_report(self):
        """Generate comprehensive test report"""
        self.log("Generating Test Report", "HEADER")
        
        end_time = datetime.now()
        duration = end_time - self.results["start_time"]
        
        # Summary statistics
        total = self.results["total_tests"]
        passed = self.results["passed_tests"]
        failed = self.results["failed_tests"]
        warnings = self.results["warnings"]
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("\n" + "="*80)
        print(f"{Colors.HEADER}{Colors.BOLD}🧪 WORKSHOP VALIDATION REPORT{Colors.ENDC}")
        print("="*80)
        
        print(f"\n📊 {Colors.BOLD}SUMMARY{Colors.ENDC}")
        print(f"   Total Tests: {total}")
        print(f"   {Colors.GREEN}✅ Passed: {passed}{Colors.ENDC}")
        print(f"   {Colors.RED}❌ Failed: {failed}{Colors.ENDC}")
        print(f"   {Colors.YELLOW}⚠️  Warnings: {warnings}{Colors.ENDC}")
        print(f"   Success Rate: {Colors.GREEN if success_rate >= 90 else Colors.YELLOW if success_rate >= 70 else Colors.RED}{success_rate:.1f}%{Colors.ENDC}")
        print(f"   Duration: {duration.total_seconds():.1f} seconds")
        
        # Performance statistics
        response_times = [r["response_time_ms"] for r in self.results["test_results"] 
                         if r["response_time_ms"] > 0]
        if response_times:
            avg_response = statistics.mean(response_times)
            print(f"   Avg Response Time: {avg_response:.1f}ms")
        
        # Category breakdown
        categories = {}
        for result in self.results["test_results"]:
            category = result["test"].split(":")[0] if ":" in result["test"] else result["test"].split()[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            if result["passed"]:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        print(f"\n📋 {Colors.BOLD}CATEGORY BREAKDOWN{Colors.ENDC}")
        for category, counts in categories.items():
            total_cat = counts["passed"] + counts["failed"]
            rate = (counts["passed"] / total_cat * 100) if total_cat > 0 else 0
            color = Colors.GREEN if rate >= 90 else Colors.YELLOW if rate >= 70 else Colors.RED
            print(f"   {category}: {color}{counts['passed']}/{total_cat} ({rate:.0f}%){Colors.ENDC}")
        
        # Failed tests details
        failed_tests = [r for r in self.results["test_results"] if not r["passed"]]
        if failed_tests:
            print(f"\n❌ {Colors.BOLD}FAILED TESTS{Colors.ENDC}")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['details']}")
        
        # Recommendations
        print(f"\n💡 {Colors.BOLD}RECOMMENDATIONS{Colors.ENDC}")
        
        if success_rate >= 95:
            print(f"   {Colors.GREEN}🎉 Excellent! Workshop is ready for participants.{Colors.ENDC}")
        elif success_rate >= 85:
            print(f"   {Colors.YELLOW}✨ Good! Address failed tests before workshop.{Colors.ENDC}")
        elif success_rate >= 70:
            print(f"   {Colors.YELLOW}⚡ Fair. Several issues need attention.{Colors.ENDC}")
        else:
            print(f"   {Colors.RED}🚨 Poor. Significant issues must be resolved.{Colors.ENDC}")
        
        if failed > 0:
            print("   • Review and fix failed tests above")
        if warnings > 0:
            print("   • Consider implementing enterprise features with warnings")
        if not response_times or statistics.mean(response_times) > 2000:
            print("   • Optimize server performance")
        
        print("\n" + "="*80)
        
        # Return overall success
        return success_rate >= 85

    def run_all_tests(self) -> bool:
        """Run comprehensive test suite"""
        print(f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                    🧪 Workshop Validator v2.0                ║
║              Enterprise-Grade Validation Suite               ║
╚══════════════════════════════════════════════════════════════╝
{Colors.ENDC}""")
        
        # Run all test categories
        test_methods = [
            self.check_prerequisites,
            self.check_files_and_structure,
            self.check_docker_setup,
            self.check_server_connectivity,
            self.test_health_endpoint_detailed,
            self.test_agents_comprehensive,
            self.test_performance_and_load,
            self.test_api_documentation,
            self.test_enterprise_features,
            self.test_error_handling
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log(f"Test method {test_method.__name__} failed: {e}", "ERROR")
            print()  # Add spacing between test categories
        
        # Generate final report
        return self.generate_report()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Workshop Validation Suite")
    parser.add_argument("--url", default="http://localhost:8080", 
                       help="MCP Server URL (default: http://localhost:8080)")
    parser.add_argument("--quick", action="store_true", 
                       help="Run quick tests only")
    
    args = parser.parse_args()
    
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    validator = WorkshopValidator(args.url)
    
    try:
        if args.quick:
            # Quick validation
            success = (validator.check_server_connectivity() and 
                      validator.test_health_endpoint_detailed())
            print(f"\n{'✅ Quick validation passed!' if success else '❌ Quick validation failed!'}")
        else:
            # Full validation
            success = validator.run_all_tests()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Validation interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}💥 Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
