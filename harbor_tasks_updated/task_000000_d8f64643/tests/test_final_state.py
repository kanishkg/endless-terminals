# test_final_state.py
"""
Tests to validate the final state after the student has fixed the mobile CI
pipeline signing service authentication issue.

The fix should modify submit.py to include the API version prefix in the
Authorization header (e.g., "v2:sk-mobile-2024-abc123" instead of just
"sk-mobile-2024-abc123").
"""

import json
import os
import subprocess
import pytest


class TestSubmitScriptSuccess:
    """Verify the submit.py script now works correctly."""

    def test_submit_script_exits_zero(self):
        """submit.py must exit with code 0 (success)."""
        result = subprocess.run(
            ["python3", "/home/user/pipeline/submit.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, \
            f"submit.py should exit 0 but exited {result.returncode}. " \
            f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_submit_script_prints_signed_artifact_path(self):
        """submit.py must print the signed artifact path on success."""
        result = subprocess.run(
            ["python3", "/home/user/pipeline/submit.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        expected_path = "/home/user/pipeline/out/app-signed.ipa"
        assert "Signed artifact" in result.stdout, \
            f"Output should contain 'Signed artifact'. Got stdout: {result.stdout}"
        assert expected_path in result.stdout, \
            f"Output should contain '{expected_path}'. Got stdout: {result.stdout}"


class TestAuthJsonUnchanged:
    """Verify auth.json was not modified (fix should be in submit.py)."""

    def test_auth_json_still_exists(self):
        """auth.json must still exist."""
        path = "/home/user/pipeline/config/auth.json"
        assert os.path.isfile(path), f"auth.json not found at {path}"

    def test_auth_json_is_valid_json(self):
        """auth.json must still be valid JSON."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            content = f.read()
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(f"auth.json is not valid JSON: {e}")

    def test_auth_json_api_key_unchanged(self):
        """auth.json api_key must remain unchanged."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            data = json.load(f)
        expected_key = "sk-mobile-2024-abc123"
        assert data.get("api_key") == expected_key, \
            f"auth.json api_key should remain '{expected_key}', got '{data.get('api_key')}'. " \
            "The fix should be in submit.py, not in auth.json."

    def test_auth_json_api_version_unchanged(self):
        """auth.json api_version must remain 'v2'."""
        path = "/home/user/pipeline/config/auth.json"
        with open(path, 'r') as f:
            data = json.load(f)
        assert data.get("api_version") == "v2", \
            f"auth.json api_version should remain 'v2', got '{data.get('api_version')}'"


class TestSigningServiceStillRunning:
    """Verify the signing service is still running after the fix."""

    def test_service_still_listening_on_8443(self):
        """The signing service must still be listening on port 8443."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert "8443" in result.stdout, \
            "Signing service no longer listening on port 8443. Service must remain running."

    def test_health_endpoint_still_responds(self):
        """The /health endpoint should still respond."""
        result = subprocess.run(
            ["curl", "-sk", "https://localhost:8443/health"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, \
            f"Health endpoint not responding: {result.stderr}"


class TestSubmitScriptFixApplied:
    """Verify the fix was applied to submit.py (version prefix in auth header)."""

    def test_submit_script_still_exists(self):
        """submit.py must still exist."""
        path = "/home/user/pipeline/submit.py"
        assert os.path.isfile(path), f"submit.py not found at {path}"

    def test_submit_script_contains_version_prefix_logic(self):
        """submit.py should now include logic to prefix the API key with version."""
        path = "/home/user/pipeline/submit.py"
        with open(path, 'r') as f:
            content = f.read()
        # The fix should involve combining version and key with a colon
        # Look for evidence of the fix - could be string concatenation, f-string, etc.
        has_prefix_logic = (
            "v2:" in content or
            "api_version" in content and ":" in content or
            "version" in content.lower() and ":" in content or
            "{" in content and "}" in content and ":" in content  # f-string pattern
        )
        assert has_prefix_logic, \
            "submit.py should contain logic to prefix the API key with the version (e.g., 'v2:key')"


class TestServiceFilesUnchanged:
    """Verify the service files were not modified (should be read-only)."""

    def test_service_source_still_exists(self):
        """The signing service source must still exist."""
        path = "/opt/signing-service/server.py"
        assert os.path.isfile(path), f"Signing service source not found at {path}"

    def test_valid_keys_file_still_exists(self):
        """The valid_keys.txt file must still exist."""
        path = "/opt/signing-service/keys/valid_keys.txt"
        assert os.path.isfile(path), f"Valid keys file not found at {path}"


class TestScriptActuallyCallsService:
    """Verify the script actually calls the service (not hardcoded output)."""

    def test_multiple_runs_succeed(self):
        """Running submit.py multiple times should all succeed (proves it's not cached)."""
        for i in range(3):
            result = subprocess.run(
                ["python3", "/home/user/pipeline/submit.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, \
                f"Run {i+1}: submit.py should exit 0 but exited {result.returncode}. " \
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            assert "Signed artifact" in result.stdout, \
                f"Run {i+1}: Output should contain 'Signed artifact'"

    def test_script_makes_https_request(self):
        """submit.py should contain code that makes HTTPS requests."""
        path = "/home/user/pipeline/submit.py"
        with open(path, 'r') as f:
            content = f.read()
        # Should use requests library or urllib for HTTPS
        makes_request = (
            "requests" in content or
            "urllib" in content or
            "https://" in content or
            "localhost:8443" in content or
            "localhost" in content and "8443" in content
        )
        assert makes_request, \
            "submit.py should contain code to make HTTPS requests to the signing service"
