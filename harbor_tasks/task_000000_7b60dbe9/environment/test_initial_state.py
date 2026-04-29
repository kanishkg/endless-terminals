# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the debugging task for the health-check dashboard.
"""

import json
import os
import subprocess
import stat
import socket
import urllib.request
import urllib.error
import pytest


class TestMonitorDirectoryAndScript:
    """Tests for the monitor directory and check_all.py script."""

    def test_monitor_directory_exists(self):
        """Verify /home/user/monitor/ directory exists."""
        monitor_dir = "/home/user/monitor"
        assert os.path.isdir(monitor_dir), (
            f"Directory {monitor_dir} does not exist. "
            "The monitor directory should be present."
        )

    def test_check_all_script_exists(self):
        """Verify check_all.py exists in the monitor directory."""
        script_path = "/home/user/monitor/check_all.py"
        assert os.path.isfile(script_path), (
            f"File {script_path} does not exist. "
            "The check_all.py script should be present."
        )

    def test_check_all_script_is_readable(self):
        """Verify check_all.py is readable."""
        script_path = "/home/user/monitor/check_all.py"
        assert os.access(script_path, os.R_OK), (
            f"File {script_path} is not readable. "
            "The script should be readable."
        )

    def test_check_all_script_is_valid_python(self):
        """Verify check_all.py is valid Python syntax."""
        script_path = "/home/user/monitor/check_all.py"
        result = subprocess.run(
            ["python3", "-m", "py_compile", script_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"File {script_path} has Python syntax errors: {result.stderr}"
        )

    def test_monitor_directory_is_writable(self):
        """Verify /home/user/monitor/ directory is writable."""
        monitor_dir = "/home/user/monitor"
        assert os.access(monitor_dir, os.W_OK), (
            f"Directory {monitor_dir} is not writable. "
            "The monitor directory should be writable for status.json output."
        )


class TestServicesRunning:
    """Tests to verify the three Flask services are running."""

    def test_inventory_service_listening_on_8081(self):
        """Verify inventory service is listening on port 8081."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert ":8081" in result.stdout, (
            "No service is listening on port 8081. "
            "The inventory service should be running on 127.0.0.1:8081."
        )

    def test_pricing_service_listening_on_8082(self):
        """Verify pricing service is listening on port 8082."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert ":8082" in result.stdout, (
            "No service is listening on port 8082. "
            "The pricing service should be running on 127.0.0.1:8082."
        )

    def test_fulfillment_service_listening_on_8083(self):
        """Verify fulfillment service is listening on port 8083."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert ":8083" in result.stdout, (
            "No service is listening on port 8083. "
            "The fulfillment service should be running on 127.0.0.1:8083."
        )


class TestServiceHealthEndpoints:
    """Tests to verify each service responds correctly to health checks."""

    def test_inventory_health_returns_200(self):
        """Verify inventory service /health endpoint returns 200."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8081/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, (
                    f"Inventory service returned status {response.status}, expected 200."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to inventory service on 8081: {e}")

    def test_inventory_health_returns_status_ok(self):
        """Verify inventory service /health returns {"status":"ok"}."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8081/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                body = json.loads(response.read().decode())
                assert body.get("status") == "ok", (
                    f"Inventory service returned {body}, expected {{'status': 'ok'}}."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to inventory service on 8081: {e}")

    def test_inventory_health_has_ready_header(self):
        """Verify inventory service /health returns X-Service-Ready header."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8081/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                header_value = response.getheader("X-Service-Ready")
                assert header_value == "true", (
                    f"Inventory service X-Service-Ready header is '{header_value}', expected 'true'."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to inventory service on 8081: {e}")

    def test_pricing_health_returns_200(self):
        """Verify pricing service /health endpoint returns 200."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8082/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, (
                    f"Pricing service returned status {response.status}, expected 200."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to pricing service on 8082: {e}")

    def test_pricing_health_returns_status_ok(self):
        """Verify pricing service /health returns {"status":"ok"}."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8082/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                body = json.loads(response.read().decode())
                assert body.get("status") == "ok", (
                    f"Pricing service returned {body}, expected {{'status': 'ok'}}."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to pricing service on 8082: {e}")

    def test_pricing_health_has_ready_header(self):
        """Verify pricing service /health returns X-Service-Ready header."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8082/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                header_value = response.getheader("X-Service-Ready")
                assert header_value == "true", (
                    f"Pricing service X-Service-Ready header is '{header_value}', expected 'true'."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to pricing service on 8082: {e}")

    def test_fulfillment_health_returns_200(self):
        """Verify fulfillment service /health endpoint returns 200."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8083/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, (
                    f"Fulfillment service returned status {response.status}, expected 200."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to fulfillment service on 8083: {e}")

    def test_fulfillment_health_returns_status_ok(self):
        """Verify fulfillment service /health returns {"status":"ok"}."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8083/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                body = json.loads(response.read().decode())
                assert body.get("status") == "ok", (
                    f"Fulfillment service returned {body}, expected {{'status': 'ok'}}."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to fulfillment service on 8083: {e}")

    def test_fulfillment_health_has_ready_header(self):
        """Verify fulfillment service /health returns X-Service-Ready header."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8083/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                header_value = response.getheader("X-Service-Ready")
                assert header_value == "true", (
                    f"Fulfillment service X-Service-Ready header is '{header_value}', expected 'true'."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to fulfillment service on 8083: {e}")


class TestCurrentBuggyState:
    """Tests to verify the script currently has the bug (produces wrong output)."""

    def test_status_json_exists(self):
        """Verify status.json exists (from previous buggy run)."""
        status_path = "/home/user/monitor/status.json"
        assert os.path.isfile(status_path), (
            f"File {status_path} does not exist. "
            "The status.json should exist from a previous run of check_all.py."
        )

    def test_status_json_shows_degraded_services(self):
        """Verify current status.json shows services as degraded (the bug)."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)

        services = data.get("services", {})
        # Check that at least one service shows degraded
        degraded_count = sum(
            1 for svc in services.values() 
            if isinstance(svc, dict) and svc.get("status") == "degraded"
        )
        assert degraded_count > 0, (
            "Expected status.json to show services as 'degraded' due to the bug, "
            f"but found: {services}"
        )

    def test_status_json_shows_healthy_false(self):
        """Verify current status.json shows healthy as false (the bug)."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)

        assert data.get("healthy") is False, (
            f"Expected status.json 'healthy' to be false due to the bug, "
            f"but found: {data.get('healthy')}"
        )

    def test_script_contains_state_key_bug(self):
        """Verify check_all.py contains the bug - checking 'state' instead of 'status'."""
        script_path = "/home/user/monitor/check_all.py"
        with open(script_path, "r") as f:
            content = f.read()

        # The bug is using "state" instead of "status"
        assert '"state"' in content or "'state'" in content, (
            "Expected check_all.py to contain the bug: checking for 'state' key "
            "instead of 'status' key in the JSON response."
        )

    def test_script_contains_header_todo_comment(self):
        """Verify check_all.py contains the red herring TODO comment about headers."""
        script_path = "/home/user/monitor/check_all.py"
        with open(script_path, "r") as f:
            content = f.read()

        assert "X-Service-Ready" in content, (
            "Expected check_all.py to contain reference to X-Service-Ready header "
            "(the red herring TODO comment)."
        )


class TestPythonEnvironment:
    """Tests to verify Python environment is properly set up."""

    def test_python3_available(self):
        """Verify python3 is available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "python3 is not available or not working properly."
        )

    def test_requests_library_installed(self):
        """Verify requests library is installed."""
        result = subprocess.run(
            ["python3", "-c", "import requests; print(requests.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python 'requests' library is not installed. "
            f"Error: {result.stderr}"
        )

    def test_script_can_be_executed(self):
        """Verify check_all.py can be executed without import errors."""
        # Just check imports work, don't run the full script
        result = subprocess.run(
            ["python3", "-c", 
             "import sys; sys.path.insert(0, '/home/user/monitor'); "
             "import ast; ast.parse(open('/home/user/monitor/check_all.py').read())"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"check_all.py cannot be parsed: {result.stderr}"
        )
