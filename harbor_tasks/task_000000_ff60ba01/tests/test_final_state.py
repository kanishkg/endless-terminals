# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the ETL dashboard issue.
"""

import os
import subprocess
import json
import time
import socket
import pytest


HOME = "/home/user"
ETL_MONITOR = f"{HOME}/etl-monitor"


class TestYAMLConfigFixed:
    """Verify the YAML configuration file is now valid."""

    def test_app_yaml_exists(self):
        """config/app.yaml should still exist."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        assert os.path.isfile(app_yaml), f"{app_yaml} does not exist"

    def test_app_yaml_no_tabs(self):
        """config/app.yaml should not contain any tab characters."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        with open(app_yaml, 'rb') as f:
            content = f.read()
        assert b'\t' not in content, \
            "config/app.yaml still contains tab characters - tabs must be replaced with spaces"

    def test_app_yaml_is_valid_yaml(self):
        """config/app.yaml should be valid YAML that can be parsed."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        result = subprocess.run(
            ["python3", "-c", f"import yaml; yaml.safe_load(open('{app_yaml}'))"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"config/app.yaml is not valid YAML: {result.stderr}"

    def test_app_yaml_has_server_port(self):
        """config/app.yaml should have server.port configuration."""
        app_yaml = f"{ETL_MONITOR}/config/app.yaml"
        result = subprocess.run(
            ["python3", "-c", 
             f"import yaml; c=yaml.safe_load(open('{app_yaml}')); print(c.get('server',{{}}).get('port',''))"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to parse app.yaml: {result.stderr}"
        port = result.stdout.strip()
        assert port == "3000", \
            f"config/app.yaml should specify server.port as 3000, got: {port}"


class TestRoutesUnchanged:
    """Verify routes/status.js was not modified."""

    def test_status_route_exists(self):
        """routes/status.js should still exist."""
        status_js = f"{ETL_MONITOR}/routes/status.js"
        assert os.path.isfile(status_js), f"{status_js} does not exist"

    def test_status_route_has_status_endpoint(self):
        """routes/status.js should still have a /status endpoint."""
        status_js = f"{ETL_MONITOR}/routes/status.js"
        with open(status_js, 'r') as f:
            content = f.read()
        assert "status" in content.lower(), \
            "routes/status.js should define a status endpoint"


class TestPackageJsonUnchanged:
    """Verify package.json dependencies were not modified."""

    def test_package_json_exists(self):
        """package.json should still exist."""
        package_json = f"{ETL_MONITOR}/package.json"
        assert os.path.isfile(package_json), f"{package_json} does not exist"

    def test_package_json_has_express(self):
        """package.json should still have express dependency."""
        package_json = f"{ETL_MONITOR}/package.json"
        with open(package_json, 'r') as f:
            data = json.load(f)
        assert "dependencies" in data, "package.json missing 'dependencies' section"
        assert "express" in data["dependencies"], "express not in dependencies"


class TestServerJsNotHardcoded:
    """Verify server.js was not modified to hardcode port 3000."""

    def test_server_js_exists(self):
        """server.js should still exist."""
        server_js = f"{ETL_MONITOR}/server.js"
        assert os.path.isfile(server_js), f"{server_js} does not exist"

    def test_server_js_not_hardcoded_port(self):
        """server.js should not have port 3000 hardcoded directly."""
        server_js = f"{ETL_MONITOR}/server.js"
        with open(server_js, 'r') as f:
            content = f.read()
        # Check that server.js still uses config for port, not hardcoded
        # It should still reference config.server.port or similar
        assert "config" in content.lower(), \
            "server.js should still use config for port configuration"


class TestPortEnvironmentFixed:
    """Verify the PORT environment variable issue is addressed."""

    def test_bashrc_no_invalid_port(self):
        """.bashrc should not have PORT=65540 (or it should be fixed/commented)."""
        bashrc = f"{HOME}/.bashrc"
        if os.path.isfile(bashrc):
            with open(bashrc, 'r') as f:
                content = f.read()
            # Check that the invalid port is either removed or commented out
            lines = content.split('\n')
            for line in lines:
                stripped = line.strip()
                # Skip comments
                if stripped.startswith('#'):
                    continue
                # Check for the problematic export
                if 'PORT' in stripped and '65540' in stripped and 'export' in stripped:
                    pytest.fail(
                        ".bashrc still has 'export PORT=65540' active - "
                        "this invalid port must be removed or commented out"
                    )


class TestServerRunsSuccessfully:
    """Verify the server can start and respond on port 3000."""

    def test_npm_start_succeeds(self):
        """npm start should be able to run without immediate failure."""
        # Start the server in background
        env = os.environ.copy()
        # Clear any problematic PORT from environment
        if 'PORT' in env:
            del env['PORT']

        proc = subprocess.Popen(
            ["npm", "start"],
            cwd=ETL_MONITOR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        # Give server time to start
        time.sleep(3)

        # Check if process is still running
        poll_result = proc.poll()

        if poll_result is not None:
            # Process exited - get output for debugging
            stdout, stderr = proc.communicate()
            pytest.fail(
                f"npm start exited with code {poll_result}.\n"
                f"stdout: {stdout.decode()}\n"
                f"stderr: {stderr.decode()}"
            )

        # Clean up
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    def test_server_listens_on_port_3000(self):
        """Server should be listening on port 3000."""
        env = os.environ.copy()
        if 'PORT' in env:
            del env['PORT']

        proc = subprocess.Popen(
            ["npm", "start"],
            cwd=ETL_MONITOR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        try:
            # Give server time to start
            time.sleep(3)

            # Try to connect to port 3000
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 3000))
            sock.close()

            assert result == 0, \
                f"Could not connect to port 3000 - server not listening (error code: {result})"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    def test_status_endpoint_returns_200(self):
        """GET /status should return HTTP 200."""
        env = os.environ.copy()
        if 'PORT' in env:
            del env['PORT']

        proc = subprocess.Popen(
            ["npm", "start"],
            cwd=ETL_MONITOR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        try:
            # Give server time to start
            time.sleep(3)

            # Use curl to check the endpoint
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "http://localhost:3000/status"],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert result.stdout == "200", \
                f"Expected HTTP 200 from /status, got {result.stdout}"
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    def test_status_endpoint_returns_json_with_status_ok(self):
        """GET /status should return JSON with status: ok."""
        env = os.environ.copy()
        if 'PORT' in env:
            del env['PORT']

        proc = subprocess.Popen(
            ["npm", "start"],
            cwd=ETL_MONITOR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        try:
            # Give server time to start
            time.sleep(3)

            # Use curl to get the response
            result = subprocess.run(
                ["curl", "-s", "http://localhost:3000/status"],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert result.returncode == 0, \
                f"curl failed: {result.stderr}"

            # Parse JSON response
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                pytest.fail(f"Response is not valid JSON: {result.stdout}\nError: {e}")

            assert "status" in data, \
                f"Response JSON missing 'status' key: {data}"
            assert data["status"] == "ok", \
                f"Expected status 'ok', got '{data['status']}'"

        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    def test_status_endpoint_has_pipelines(self):
        """GET /status should return JSON with pipelines field."""
        env = os.environ.copy()
        if 'PORT' in env:
            del env['PORT']

        proc = subprocess.Popen(
            ["npm", "start"],
            cwd=ETL_MONITOR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        try:
            # Give server time to start
            time.sleep(3)

            # Use curl to get the response
            result = subprocess.run(
                ["curl", "-s", "http://localhost:3000/status"],
                capture_output=True,
                text=True,
                timeout=10
            )

            assert result.returncode == 0, \
                f"curl failed: {result.stderr}"

            # Parse JSON response
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                pytest.fail(f"Response is not valid JSON: {result.stdout}\nError: {e}")

            assert "pipelines" in data, \
                f"Response JSON missing 'pipelines' key: {data}"

        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
