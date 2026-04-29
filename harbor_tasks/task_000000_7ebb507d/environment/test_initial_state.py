# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the debugging task for the netcheck health-checker.
"""

import os
import subprocess
import yaml
import pytest


class TestNetcheckDirectoryStructure:
    """Test that the netcheck directory and required files exist."""

    def test_netcheck_directory_exists(self):
        """Verify /home/user/netcheck directory exists."""
        path = "/home/user/netcheck"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_checker_py_exists(self):
        """Verify checker.py exists and is a file."""
        path = "/home/user/netcheck/checker.py"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_endpoints_yaml_exists(self):
        """Verify endpoints.yaml exists and is a file."""
        path = "/home/user/netcheck/endpoints.yaml"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_config_py_exists(self):
        """Verify config.py exists (the red herring file from reorganization)."""
        path = "/home/user/netcheck/config.py"
        assert os.path.isfile(path), f"File {path} does not exist (this was added during reorganization)"

    def test_netcheck_directory_is_writable(self):
        """Verify /home/user/netcheck is writable."""
        path = "/home/user/netcheck"
        assert os.access(path, os.W_OK), f"Directory {path} is not writable"


class TestEndpointsYamlConfiguration:
    """Test that endpoints.yaml has the correct configuration."""

    @pytest.fixture
    def endpoints_config(self):
        """Load and return the endpoints.yaml configuration."""
        path = "/home/user/netcheck/endpoints.yaml"
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def test_endpoints_yaml_is_valid_yaml(self):
        """Verify endpoints.yaml is valid YAML."""
        path = "/home/user/netcheck/endpoints.yaml"
        try:
            with open(path, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"endpoints.yaml is not valid YAML: {e}")

    def test_endpoints_key_exists(self, endpoints_config):
        """Verify 'endpoints' key exists in config."""
        assert 'endpoints' in endpoints_config, "endpoints.yaml missing 'endpoints' key"

    def test_three_endpoints_configured(self, endpoints_config):
        """Verify exactly three endpoints are configured."""
        endpoints = endpoints_config.get('endpoints', [])
        assert len(endpoints) == 3, f"Expected 3 endpoints, found {len(endpoints)}"

    def test_auth_service_endpoint(self, endpoints_config):
        """Verify auth-service endpoint is configured correctly."""
        endpoints = endpoints_config.get('endpoints', [])
        auth_service = next((e for e in endpoints if e.get('name') == 'auth-service'), None)
        assert auth_service is not None, "auth-service endpoint not found"
        assert auth_service.get('url') == 'http://127.0.0.1:5001/health', \
            f"auth-service URL incorrect: {auth_service.get('url')}"
        assert auth_service.get('timeout') == 5, \
            f"auth-service timeout incorrect: {auth_service.get('timeout')}"

    def test_data_service_endpoint(self, endpoints_config):
        """Verify data-service endpoint is configured correctly."""
        endpoints = endpoints_config.get('endpoints', [])
        data_service = next((e for e in endpoints if e.get('name') == 'data-service'), None)
        assert data_service is not None, "data-service endpoint not found"
        assert data_service.get('url') == 'http://127.0.0.1:5002/health', \
            f"data-service URL incorrect: {data_service.get('url')}"
        assert data_service.get('timeout') == 5, \
            f"data-service timeout incorrect: {data_service.get('timeout')}"

    def test_cache_service_endpoint(self, endpoints_config):
        """Verify cache-service endpoint is configured correctly."""
        endpoints = endpoints_config.get('endpoints', [])
        cache_service = next((e for e in endpoints if e.get('name') == 'cache-service'), None)
        assert cache_service is not None, "cache-service endpoint not found"
        assert cache_service.get('url') == 'http://127.0.0.1:5003/health', \
            f"cache-service URL incorrect: {cache_service.get('url')}"
        assert cache_service.get('timeout') == 5, \
            f"cache-service timeout incorrect: {cache_service.get('timeout')}"


class TestCheckerPyContent:
    """Test that checker.py has the expected content and bug."""

    @pytest.fixture
    def checker_content(self):
        """Load and return the checker.py content."""
        path = "/home/user/netcheck/checker.py"
        with open(path, 'r') as f:
            return f.read()

    def test_checker_uses_requests_library(self, checker_content):
        """Verify checker.py uses requests library for HTTP calls."""
        assert 'requests' in checker_content, \
            "checker.py does not appear to use the requests library"

    def test_checker_reads_endpoints_yaml(self, checker_content):
        """Verify checker.py reads from endpoints.yaml."""
        assert 'endpoints.yaml' in checker_content or 'endpoints' in checker_content.lower(), \
            "checker.py does not appear to read endpoints.yaml"

    def test_checker_writes_results_json(self, checker_content):
        """Verify checker.py writes to results.json."""
        assert 'results.json' in checker_content or 'results' in checker_content.lower(), \
            "checker.py does not appear to write results.json"

    def test_checker_has_timeout_bug(self, checker_content):
        """Verify the timeout bug exists (references global_timeout which doesn't exist)."""
        assert 'global_timeout' in checker_content, \
            "checker.py does not contain the expected 'global_timeout' bug reference"


class TestConfigPyContent:
    """Test that config.py exists with the red herring DEFAULT_TIMEOUT."""

    def test_config_py_has_default_timeout(self):
        """Verify config.py has DEFAULT_TIMEOUT constant."""
        path = "/home/user/netcheck/config.py"
        with open(path, 'r') as f:
            content = f.read()
        assert 'DEFAULT_TIMEOUT' in content, \
            "config.py does not contain DEFAULT_TIMEOUT constant"


class TestFlaskServicesRunning:
    """Test that all three Flask mock services are running."""

    def test_port_5001_listening(self):
        """Verify auth-service is listening on port 5001."""
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True
        )
        assert ':5001' in result.stdout, \
            "No service listening on port 5001 (auth-service should be running)"

    def test_port_5002_listening(self):
        """Verify data-service is listening on port 5002."""
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True
        )
        assert ':5002' in result.stdout, \
            "No service listening on port 5002 (data-service should be running)"

    def test_port_5003_listening(self):
        """Verify cache-service is listening on port 5003."""
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True
        )
        assert ':5003' in result.stdout, \
            "No service listening on port 5003 (cache-service should be running)"

    def test_auth_service_responds_to_curl(self):
        """Verify auth-service responds to health check."""
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
             'http://127.0.0.1:5001/health'],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.stdout == '200', \
            f"auth-service health check failed with status {result.stdout}"

    def test_data_service_responds_to_curl(self):
        """Verify data-service responds to health check."""
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             'http://127.0.0.1:5002/health'],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.stdout == '200', \
            f"data-service health check failed with status {result.stdout}"

    def test_cache_service_responds_to_curl(self):
        """Verify cache-service responds to health check."""
        result = subprocess.run(
            ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
             'http://127.0.0.1:5003/health'],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.stdout == '200', \
            f"cache-service health check failed with status {result.stdout}"


class TestResultsJsonNotExists:
    """Test that results.json does not exist yet (checker hangs before writing it)."""

    def test_results_json_does_not_exist(self):
        """Verify results.json does not exist (because checker hangs)."""
        path = "/home/user/netcheck/results.json"
        assert not os.path.exists(path), \
            f"results.json already exists at {path} - it should not exist yet (checker should hang before creating it)"


class TestPythonEnvironment:
    """Test that Python and required libraries are available."""

    def test_python3_available(self):
        """Verify Python 3 is available."""
        result = subprocess.run(
            ['python3', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python 3 is not available"
        assert 'Python 3' in result.stdout, f"Unexpected Python version: {result.stdout}"

    def test_requests_library_installed(self):
        """Verify requests library is installed."""
        result = subprocess.run(
            ['python3', '-c', 'import requests; print(requests.__version__)'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"requests library is not installed: {result.stderr}"

    def test_pyyaml_library_installed(self):
        """Verify PyYAML library is installed (needed to read endpoints.yaml)."""
        result = subprocess.run(
            ['python3', '-c', 'import yaml; print(yaml.__version__)'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"PyYAML library is not installed: {result.stderr}"
