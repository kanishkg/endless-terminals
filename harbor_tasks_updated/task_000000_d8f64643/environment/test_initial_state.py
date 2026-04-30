# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the debugging task for the mobile CI pipeline signing service issue.
"""

import json
import os
import subprocess
import pytest


class TestPipelineFilesExist:
    """Verify the pipeline files and directories exist."""

    def test_submit_script_exists(self):
        """The submit.py script must exist."""
        path = "/home/user/pipeline/submit.py"
        assert os.path.isfile(path), f"Submit script not found at {path}"

    def test_submit_script_is_readable(self):
        """The submit.py script must be readable."""
        path = "/home/user/pipeline/submit.py"
        assert os.access(path, os.R_OK), f"Submit script at {path} is not readable"

    def test_submit_script_is_writable(self):
        """The submit.py script must be writable (agent needs to fix it)."""
        path = "/home/user/pipeline/submit.py"
        assert os.access(path, os.W_OK), f"Submit script at {path} is not writable"

    def test_config_directory_exists(self):
        """The config directory must exist."""
        path = "/home/user/pipeline/config"
        assert os.path.isdir(path), f"Config directory not found at {path}"

    def test_auth_json_exists(self):
        """The auth.json config file must exist."""
        path = "/home/user/pipeline/config/auth.json"
        assert os.path.isfile(path), f"Auth config not found at {path}"

    def test_pipeline_directory_is_writable(self):
        """The pipeline directory must be writable."""
        path = "/home/user/pipeline"
        assert os.access(path, os.W_OK), f"Pipeline directory at {path} is not writable"


class TestAuthJsonContent:
    """Verify the auth.json has the expected content."""

    def test_auth_json_is_valid_json(self):
        """auth.json must be valid JSON."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            content = f.read()
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(f"auth.json is not valid JSON: {e}")

    def test_auth_json_has_api_key(self):
        """auth.json must contain an api_key field."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            data = json.load(f)
        assert "api_key" in data, "auth.json missing 'api_key' field"

    def test_auth_json_has_api_version(self):
        """auth.json must contain an api_version field."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            data = json.load(f)
        assert "api_version" in data, "auth.json missing 'api_version' field"

    def test_auth_json_api_key_value(self):
        """auth.json api_key must have the expected value."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            data = json.load(f)
        expected_key = "sk-mobile-2024-abc123"
        assert data.get("api_key") == expected_key, \
            f"auth.json api_key expected '{expected_key}', got '{data.get('api_key')}'"

    def test_auth_json_api_version_value(self):
        """auth.json api_version must be 'v2'."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            data = json.load(f)
        assert data.get("api_version") == "v2", \
            f"auth.json api_version expected 'v2', got '{data.get('api_version')}'"


class TestSigningServiceFiles:
    """Verify the signing service files exist."""

    def test_service_source_exists(self):
        """The signing service source must exist."""
        path = "/opt/signing-service/server.py"
        assert os.path.isfile(path), f"Signing service source not found at {path}"

    def test_valid_keys_file_exists(self):
        """The valid_keys.txt file must exist."""
        path = "/opt/signing-service/keys/valid_keys.txt"
        assert os.path.isfile(path), f"Valid keys file not found at {path}"


class TestLogFiles:
    """Verify the log files exist and have expected content."""

    def test_signing_log_directory_exists(self):
        """The signing log directory must exist."""
        path = "/var/log/signing"
        assert os.path.isdir(path), f"Signing log directory not found at {path}"

    def test_access_log_exists(self):
        """The access.log file must exist."""
        path = "/var/log/signing/access.log"
        assert os.path.isfile(path), f"Access log not found at {path}"

    def test_changelog_exists(self):
        """The changelog.txt file must exist."""
        path = "/var/log/signing/changelog.txt"
        assert os.path.isfile(path), f"Changelog not found at {path}"

    def test_access_log_shows_auth_failures(self):
        """Access log should show auth failures with key format mismatch."""
        path = "/var/log/signing/access.log"
        with open(path, 'r') as f:
            content = f.read()
        assert "Auth failed" in content or "key format mismatch" in content or "401" in content, \
            "Access log should contain evidence of authentication failures"

    def test_changelog_mentions_version_prefix(self):
        """Changelog should mention the version prefix requirement."""
        path = "/var/log/signing/changelog.txt"
        with open(path, 'r') as f:
            content = f.read()
        assert "prefix" in content.lower() or "v2:" in content, \
            "Changelog should mention the version prefix requirement"


class TestSigningServiceRunning:
    """Verify the signing service is running and accessible."""

    def test_service_listening_on_8443(self):
        """The signing service must be listening on port 8443."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert "8443" in result.stdout, \
            "No service listening on port 8443. The signing service must be running."

    def test_health_endpoint_responds(self):
        """The /health endpoint should respond (doesn't need auth)."""
        result = subprocess.run(
            ["curl", "-sk", "https://localhost:8443/health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should get some response (not a connection error)
        assert result.returncode == 0, \
            f"Failed to connect to health endpoint: {result.stderr}"

    def test_sign_endpoint_exists(self):
        """The /api/v2/sign endpoint should exist (will return 401 without proper auth)."""
        result = subprocess.run(
            ["curl", "-sk", "-X", "POST", "https://localhost:8443/api/v2/sign"],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should connect successfully (even if we get 401)
        assert result.returncode == 0, \
            f"Failed to connect to sign endpoint: {result.stderr}"


class TestSubmitScriptContent:
    """Verify submit.py has expected structure."""

    def test_submit_script_is_python(self):
        """submit.py should be a Python script."""
        path = "/home/user/pipeline/submit.py"
        with open(path, 'r') as f:
            content = f.read()
        # Should contain Python-like content
        assert "import" in content or "def " in content or "print" in content, \
            "submit.py doesn't appear to be a Python script"

    def test_submit_script_reads_auth_json(self):
        """submit.py should reference the auth.json config."""
        path = "/home/user/pipeline/submit.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "auth.json" in content or "config" in content, \
            "submit.py should reference auth.json or config"

    def test_submit_script_uses_localhost_8443(self):
        """submit.py should connect to localhost:8443."""
        path = "/home/user/pipeline/submit.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "8443" in content or "localhost" in content, \
            "submit.py should reference localhost:8443"

    def test_submit_script_mentions_sign_endpoint(self):
        """submit.py should use the /api/v2/sign endpoint."""
        path = "/home/user/pipeline/submit.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "sign" in content.lower() or "api" in content, \
            "submit.py should reference the sign endpoint"


class TestInitialBrokenState:
    """Verify the script is currently broken (returns non-zero)."""

    def test_submit_script_currently_fails(self):
        """submit.py should currently fail (exit non-zero) due to the auth issue."""
        result = subprocess.run(
            ["python3", "/home/user/pipeline/submit.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode != 0, \
            "submit.py should currently be failing (the bug hasn't been fixed yet)"
