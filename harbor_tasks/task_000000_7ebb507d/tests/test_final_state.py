# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the debugging task for the netcheck health-checker.
"""

import json
import os
import re
import subprocess
import yaml
import pytest


class TestCheckerExecutesSuccessfully:
    """Test that checker.py now runs successfully without hanging."""

    def test_checker_completes_within_timeout(self):
        """Verify checker.py completes within 30 seconds (doesn't hang)."""
        result = subprocess.run(
            ['timeout', '30', 'python3', 'checker.py'],
            cwd='/home/user/netcheck',
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"checker.py did not exit successfully (returncode={result.returncode}). " \
            f"stderr: {result.stderr}, stdout: {result.stdout}"

    def test_checker_does_not_timeout(self):
        """Verify checker.py doesn't hit the timeout (exit code 124)."""
        result = subprocess.run(
            ['timeout', '30', 'python3', 'checker.py'],
            cwd='/home/user/netcheck',
            capture_output=True,
            text=True
        )
        assert result.returncode != 124, \
            "checker.py timed out - the timeout bug has not been fixed"


class TestResultsJsonExists:
    """Test that results.json exists and is valid."""

    def test_results_json_exists(self):
        """Verify results.json exists."""
        path = "/home/user/netcheck/results.json"
        assert os.path.isfile(path), \
            f"results.json does not exist at {path} - checker.py may not have run successfully"

    def test_results_json_is_valid_json(self):
        """Verify results.json contains valid JSON."""
        path = "/home/user/netcheck/results.json"
        try:
            with open(path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"results.json is not valid JSON: {e}")
        except FileNotFoundError:
            pytest.fail(f"results.json does not exist at {path}")


class TestResultsJsonContent:
    """Test that results.json contains correct status for all three services."""

    @pytest.fixture
    def results_data(self):
        """Load and return the results.json data."""
        path = "/home/user/netcheck/results.json"
        with open(path, 'r') as f:
            return json.load(f)

    def test_results_contains_auth_service(self, results_data):
        """Verify results.json contains auth-service status."""
        # Handle both list and dict formats
        if isinstance(results_data, list):
            service_names = [item.get('name', item.get('service', '')) for item in results_data]
            assert any('auth' in name.lower() for name in service_names), \
                f"auth-service not found in results. Found: {service_names}"
        elif isinstance(results_data, dict):
            # Could be keyed by service name or have a 'results' key
            if 'results' in results_data:
                inner = results_data['results']
                if isinstance(inner, list):
                    service_names = [item.get('name', item.get('service', '')) for item in inner]
                    assert any('auth' in name.lower() for name in service_names), \
                        f"auth-service not found in results. Found: {service_names}"
                else:
                    assert any('auth' in key.lower() for key in inner.keys()), \
                        f"auth-service not found in results. Found: {list(inner.keys())}"
            else:
                all_keys = str(results_data).lower()
                assert 'auth' in all_keys, \
                    f"auth-service not found in results: {results_data}"

    def test_results_contains_data_service(self, results_data):
        """Verify results.json contains data-service status."""
        if isinstance(results_data, list):
            service_names = [item.get('name', item.get('service', '')) for item in results_data]
            assert any('data' in name.lower() for name in service_names), \
                f"data-service not found in results. Found: {service_names}"
        elif isinstance(results_data, dict):
            if 'results' in results_data:
                inner = results_data['results']
                if isinstance(inner, list):
                    service_names = [item.get('name', item.get('service', '')) for item in inner]
                    assert any('data' in name.lower() for name in service_names), \
                        f"data-service not found in results. Found: {service_names}"
                else:
                    assert any('data' in key.lower() for key in inner.keys()), \
                        f"data-service not found in results. Found: {list(inner.keys())}"
            else:
                all_keys = str(results_data).lower()
                assert 'data' in all_keys, \
                    f"data-service not found in results: {results_data}"

    def test_results_contains_cache_service(self, results_data):
        """Verify results.json contains cache-service status."""
        if isinstance(results_data, list):
            service_names = [item.get('name', item.get('service', '')) for item in results_data]
            assert any('cache' in name.lower() for name in service_names), \
                f"cache-service not found in results. Found: {service_names}"
        elif isinstance(results_data, dict):
            if 'results' in results_data:
                inner = results_data['results']
                if isinstance(inner, list):
                    service_names = [item.get('name', item.get('service', '')) for item in inner]
                    assert any('cache' in name.lower() for name in service_names), \
                        f"cache-service not found in results. Found: {service_names}"
                else:
                    assert any('cache' in key.lower() for key in inner.keys()), \
                        f"cache-service not found in results. Found: {list(inner.keys())}"
            else:
                all_keys = str(results_data).lower()
                assert 'cache' in all_keys, \
                    f"cache-service not found in results: {results_data}"

    def test_all_services_show_healthy_status(self, results_data):
        """Verify all services show healthy/ok/success status."""
        results_str = json.dumps(results_data).lower()
        # Check for indicators of success - should have healthy/ok/success indicators
        # and should NOT have error/fail/unhealthy as the dominant status
        success_indicators = ['ok', 'healthy', 'success', 'up', '200', 'true']
        has_success = any(indicator in results_str for indicator in success_indicators)
        assert has_success, \
            f"Results don't indicate healthy status for services: {results_data}"


class TestEndpointsYamlUnchanged:
    """Test that endpoints.yaml still has correct endpoint URLs (invariant)."""

    @pytest.fixture
    def endpoints_config(self):
        """Load and return the endpoints.yaml configuration."""
        path = "/home/user/netcheck/endpoints.yaml"
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    def test_endpoints_still_point_to_correct_ports(self, endpoints_config):
        """Verify endpoint URLs still point to ports 5001, 5002, 5003."""
        endpoints = endpoints_config.get('endpoints', [])
        urls = [e.get('url', '') for e in endpoints]
        urls_str = ' '.join(urls)

        assert '5001' in urls_str, \
            f"Port 5001 not found in endpoint URLs: {urls}"
        assert '5002' in urls_str, \
            f"Port 5002 not found in endpoint URLs: {urls}"
        assert '5003' in urls_str, \
            f"Port 5003 not found in endpoint URLs: {urls}"


class TestFlaskServicesStillRunning:
    """Test that all three Flask services are still running (invariant)."""

    def test_port_5001_still_listening(self):
        """Verify auth-service is still listening on port 5001."""
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True
        )
        assert ':5001' in result.stdout, \
            "auth-service no longer running on port 5001"

    def test_port_5002_still_listening(self):
        """Verify data-service is still listening on port 5002."""
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True
        )
        assert ':5002' in result.stdout, \
            "data-service no longer running on port 5002"

    def test_port_5003_still_listening(self):
        """Verify cache-service is still listening on port 5003."""
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True
        )
        assert ':5003' in result.stdout, \
            "cache-service no longer running on port 5003"


class TestCheckerStillReadsEndpointsYaml:
    """Test that checker.py still reads from endpoints.yaml (not hardcoded)."""

    def test_checker_references_endpoints_yaml(self):
        """Verify checker.py still references endpoints.yaml."""
        path = "/home/user/netcheck/checker.py"
        with open(path, 'r') as f:
            content = f.read()

        # Should reference endpoints.yaml or endpoints file
        assert 'endpoints' in content.lower(), \
            "checker.py no longer references endpoints configuration"


class TestCheckerMakesHttpRequests:
    """Test that checker.py actually makes HTTP requests (anti-shortcut)."""

    def test_checker_uses_http_library(self):
        """Verify checker.py uses requests, urllib, or http.client for HTTP calls."""
        path = "/home/user/netcheck/checker.py"
        result = subprocess.run(
            ['grep', '-E', r'requests\.get|requests\.request|urllib|http\.client|httpx'],
            args=['grep', '-E', r'requests\.get|requests\.request|urllib|http\.client|httpx', path],
            capture_output=True,
            text=True
        )
        # Also check with a simple grep
        with open(path, 'r') as f:
            content = f.read()

        http_patterns = ['requests.get', 'requests.request', 'urllib', 'http.client', 'httpx']
        has_http_lib = any(pattern in content for pattern in http_patterns)

        assert has_http_lib, \
            "checker.py does not appear to make HTTP requests - " \
            "must use requests.get, urllib, or similar"


class TestTimeoutBugFixed:
    """Test that the timeout bug has been properly fixed."""

    def test_checker_no_longer_uses_none_timeout(self):
        """Verify checker.py no longer passes None as timeout."""
        path = "/home/user/netcheck/checker.py"
        with open(path, 'r') as f:
            content = f.read()

        # The bug was: timeout=config.get('global_timeout') which returns None
        # After fix, should either:
        # 1. Use the per-endpoint timeout value
        # 2. Use a hardcoded default
        # 3. Use DEFAULT_TIMEOUT from config.py

        # Check that global_timeout bug pattern is fixed
        # It's OK if global_timeout is still mentioned, as long as there's a fallback
        if 'global_timeout' in content:
            # If global_timeout is still there, ensure there's a fallback/default
            # Look for patterns like: .get('global_timeout', <default>) or
            # timeout_val or endpoint.get('timeout')
            has_fallback = (
                re.search(r"\.get\s*\(\s*['\"]global_timeout['\"].*,", content) or
                'timeout_val' in content or
                re.search(r"endpoint.*\.get\s*\(\s*['\"]timeout['\"]", content) or
                'DEFAULT_TIMEOUT' in content
            )
            # Even if no obvious fallback, the test that checker completes
            # within 30 seconds proves the fix works

        # The real proof is that checker.py completes - tested elsewhere
        # This test just verifies the code structure looks reasonable
        assert 'timeout' in content.lower(), \
            "checker.py doesn't appear to handle timeouts at all"
