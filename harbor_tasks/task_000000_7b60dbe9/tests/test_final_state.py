# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the health-check dashboard bug in check_all.py.
"""

import json
import os
import subprocess
import signal
import time
import urllib.request
import urllib.error
import pytest


class TestServicesStillRunning:
    """Tests to verify the three Flask services are still running after the fix."""

    def test_inventory_service_listening_on_8081(self):
        """Verify inventory service is still listening on port 8081."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert ":8081" in result.stdout, (
            "No service is listening on port 8081. "
            "The inventory service should still be running on 127.0.0.1:8081 after the fix."
        )

    def test_pricing_service_listening_on_8082(self):
        """Verify pricing service is still listening on port 8082."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert ":8082" in result.stdout, (
            "No service is listening on port 8082. "
            "The pricing service should still be running on 127.0.0.1:8082 after the fix."
        )

    def test_fulfillment_service_listening_on_8083(self):
        """Verify fulfillment service is still listening on port 8083."""
        result = subprocess.run(
            ["ss", "-tlnp"],
            capture_output=True,
            text=True
        )
        assert ":8083" in result.stdout, (
            "No service is listening on port 8083. "
            "The fulfillment service should still be running on 127.0.0.1:8083 after the fix."
        )

    def test_inventory_health_still_returns_status_ok(self):
        """Verify inventory service /health still returns {"status":"ok"}."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8081/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, (
                    f"Inventory service returned status {response.status}, expected 200."
                )
                body = json.loads(response.read().decode())
                assert body.get("status") == "ok", (
                    f"Inventory service returned {body}, expected {{'status': 'ok'}}."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to inventory service on 8081: {e}")

    def test_pricing_health_still_returns_status_ok(self):
        """Verify pricing service /health still returns {"status":"ok"}."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8082/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, (
                    f"Pricing service returned status {response.status}, expected 200."
                )
                body = json.loads(response.read().decode())
                assert body.get("status") == "ok", (
                    f"Pricing service returned {body}, expected {{'status': 'ok'}}."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to pricing service on 8082: {e}")

    def test_fulfillment_health_still_returns_status_ok(self):
        """Verify fulfillment service /health still returns {"status":"ok"}."""
        try:
            req = urllib.request.Request("http://127.0.0.1:8083/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                assert response.status == 200, (
                    f"Fulfillment service returned status {response.status}, expected 200."
                )
                body = json.loads(response.read().decode())
                assert body.get("status") == "ok", (
                    f"Fulfillment service returned {body}, expected {{'status': 'ok'}}."
                )
        except urllib.error.URLError as e:
            pytest.fail(f"Failed to connect to fulfillment service on 8083: {e}")


class TestScriptExecution:
    """Tests to verify check_all.py runs correctly."""

    def test_check_all_script_exists(self):
        """Verify check_all.py still exists."""
        script_path = "/home/user/monitor/check_all.py"
        assert os.path.isfile(script_path), (
            f"File {script_path} does not exist. "
            "The check_all.py script should still be present."
        )

    def test_check_all_script_exits_zero(self):
        """Verify running check_all.py exits with code 0."""
        result = subprocess.run(
            ["python3", "/home/user/monitor/check_all.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"check_all.py exited with code {result.returncode}, expected 0. "
            f"stderr: {result.stderr}"
        )

    def test_check_all_writes_to_correct_path(self):
        """Verify check_all.py writes to /home/user/monitor/status.json."""
        # Run the script first
        subprocess.run(
            ["python3", "/home/user/monitor/check_all.py"],
            capture_output=True,
            timeout=30
        )
        status_path = "/home/user/monitor/status.json"
        assert os.path.isfile(status_path), (
            f"File {status_path} does not exist after running check_all.py. "
            "The script should write to /home/user/monitor/status.json."
        )


class TestStatusJsonContent:
    """Tests to verify status.json has correct content after fix."""

    @pytest.fixture(autouse=True)
    def run_check_all_first(self):
        """Run check_all.py before each test in this class."""
        subprocess.run(
            ["python3", "/home/user/monitor/check_all.py"],
            capture_output=True,
            timeout=30
        )

    def test_status_json_is_valid_json(self):
        """Verify status.json contains valid JSON."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            content = f.read()
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(f"status.json is not valid JSON: {e}")

    def test_status_json_has_services_object(self):
        """Verify status.json has a 'services' object."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        assert "services" in data, (
            "status.json is missing 'services' key. "
            f"Found keys: {list(data.keys())}"
        )
        assert isinstance(data["services"], dict), (
            f"'services' should be an object/dict, got {type(data['services']).__name__}"
        )

    def test_status_json_has_all_three_services(self):
        """Verify status.json has inventory, pricing, and fulfillment services."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        services = data.get("services", {})
        required_services = ["inventory", "pricing", "fulfillment"]
        for svc in required_services:
            assert svc in services, (
                f"status.json is missing '{svc}' service. "
                f"Found services: {list(services.keys())}"
            )

    def test_inventory_service_shows_healthy(self):
        """Verify inventory service shows healthy status."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        inventory = data.get("services", {}).get("inventory", {})
        status = inventory.get("status", "").lower() if isinstance(inventory, dict) else str(inventory).lower()
        # Accept "healthy", "ok", "up", or similar positive indicators
        positive_indicators = ["healthy", "ok", "up", "running", "good", "active"]
        is_healthy = any(ind in status for ind in positive_indicators)
        assert is_healthy, (
            f"Inventory service should show healthy status, but got: {inventory}. "
            "The bug should be fixed so services show healthy when they respond with status:ok."
        )

    def test_pricing_service_shows_healthy(self):
        """Verify pricing service shows healthy status."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        pricing = data.get("services", {}).get("pricing", {})
        status = pricing.get("status", "").lower() if isinstance(pricing, dict) else str(pricing).lower()
        positive_indicators = ["healthy", "ok", "up", "running", "good", "active"]
        is_healthy = any(ind in status for ind in positive_indicators)
        assert is_healthy, (
            f"Pricing service should show healthy status, but got: {pricing}. "
            "The bug should be fixed so services show healthy when they respond with status:ok."
        )

    def test_fulfillment_service_shows_healthy(self):
        """Verify fulfillment service shows healthy status."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        fulfillment = data.get("services", {}).get("fulfillment", {})
        status = fulfillment.get("status", "").lower() if isinstance(fulfillment, dict) else str(fulfillment).lower()
        positive_indicators = ["healthy", "ok", "up", "running", "good", "active"]
        is_healthy = any(ind in status for ind in positive_indicators)
        assert is_healthy, (
            f"Fulfillment service should show healthy status, but got: {fulfillment}. "
            "The bug should be fixed so services show healthy when they respond with status:ok."
        )

    def test_overall_healthy_is_true(self):
        """Verify overall 'healthy' field is boolean true."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        assert "healthy" in data, (
            f"status.json is missing 'healthy' key. Found keys: {list(data.keys())}"
        )
        assert data["healthy"] is True, (
            f"Overall 'healthy' should be true (boolean), but got: {data['healthy']} "
            f"(type: {type(data['healthy']).__name__}). "
            "When all services are healthy, the overall healthy should be true."
        )

    def test_timestamp_field_present(self):
        """Verify status.json has a timestamp field."""
        status_path = "/home/user/monitor/status.json"
        with open(status_path, "r") as f:
            data = json.load(f)
        assert "timestamp" in data, (
            f"status.json is missing 'timestamp' key. Found keys: {list(data.keys())}"
        )
        # Timestamp should be non-empty
        assert data["timestamp"], (
            "Timestamp field is present but empty."
        )


class TestAntiShortcutGuards:
    """Tests to ensure the fix is legitimate and not hardcoded."""

    def test_script_does_not_hardcode_healthy_true(self):
        """Verify check_all.py does not hardcode 'healthy': true."""
        script_path = "/home/user/monitor/check_all.py"
        with open(script_path, "r") as f:
            content = f.read()

        # Check for obvious hardcoding patterns
        import re
        # Pattern to match "healthy": true or 'healthy': true or "healthy":true
        hardcode_pattern = re.compile(r'["\']healthy["\']\s*:\s*[Tt]rue', re.IGNORECASE)
        match = hardcode_pattern.search(content)
        assert match is None, (
            "check_all.py appears to hardcode 'healthy': true. "
            "The healthy boolean must be derived from actual service responses, not hardcoded."
        )

    def test_script_still_polls_services(self):
        """Verify check_all.py still contains code to poll services."""
        script_path = "/home/user/monitor/check_all.py"
        with open(script_path, "r") as f:
            content = f.read()

        # Should contain references to the service ports or URLs
        assert "8081" in content or "inventory" in content.lower(), (
            "check_all.py should poll the inventory service (port 8081)."
        )
        assert "8082" in content or "pricing" in content.lower(), (
            "check_all.py should poll the pricing service (port 8082)."
        )
        assert "8083" in content or "fulfillment" in content.lower(), (
            "check_all.py should poll the fulfillment service (port 8083)."
        )

    def test_script_uses_requests_or_urllib(self):
        """Verify check_all.py uses requests or urllib to make HTTP calls."""
        script_path = "/home/user/monitor/check_all.py"
        with open(script_path, "r") as f:
            content = f.read()

        uses_http_lib = "requests" in content or "urllib" in content or "http.client" in content
        assert uses_http_lib, (
            "check_all.py should use requests, urllib, or http.client to poll services."
        )

    def test_bug_is_fixed_state_key_removed(self):
        """Verify the bug (checking 'state' instead of 'status') is fixed."""
        script_path = "/home/user/monitor/check_all.py"
        with open(script_path, "r") as f:
            content = f.read()

        # The fix should change "state" to "status" in the response parsing
        # We check that the script now uses "status" for checking the response
        import re
        # Look for patterns like .get("state") or ["state"] that would indicate the bug
        # But allow "state" in comments or strings that aren't the bug

        # This is a heuristic - check if "status" is used in a get() call
        uses_status_key = re.search(r'\.get\s*\(\s*["\']status["\']\s*\)', content)
        uses_state_key = re.search(r'\.get\s*\(\s*["\']state["\']\s*\)', content)

        # Either the bug is fixed (uses status) or state is removed
        # The key check is that the output is now correct (tested elsewhere)
        # This test just verifies the code structure changed appropriately
        if uses_state_key and not uses_status_key:
            pytest.fail(
                "check_all.py still uses .get('state') instead of .get('status'). "
                "The bug was that the script checks for 'state' key but services return 'status' key."
            )


class TestScriptActuallyChecksServices:
    """
    Tests to verify the script actually checks services rather than hardcoding results.
    This is done by checking that the script's behavior changes when services are down.
    """

    def test_script_detects_degraded_service_when_stopped(self):
        """
        Verify that stopping a service causes check_all.py to report it as degraded.
        This proves the script actually polls services rather than hardcoding success.
        """
        # Find the PID of the fulfillment service (port 8083)
        result = subprocess.run(
            ["lsof", "-ti", ":8083"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0 or not result.stdout.strip():
            # Try alternative method with ss
            result = subprocess.run(
                ["ss", "-tlnp", "sport", "=", ":8083"],
                capture_output=True,
                text=True
            )
            # Extract PID from ss output if possible
            import re
            pid_match = re.search(r'pid=(\d+)', result.stdout)
            if pid_match:
                pid = int(pid_match.group(1))
            else:
                pytest.skip("Could not find PID of fulfillment service to test degraded detection")
        else:
            pid = int(result.stdout.strip().split('\n')[0])

        try:
            # Stop the service temporarily
            os.kill(pid, signal.SIGSTOP)
            time.sleep(0.5)

            # Run check_all.py with a short timeout (service is stopped so it should fail/timeout)
            run_result = subprocess.run(
                ["python3", "/home/user/monitor/check_all.py"],
                capture_output=True,
                text=True,
                timeout=60
            )

            # Read the status.json
            status_path = "/home/user/monitor/status.json"
            with open(status_path, "r") as f:
                data = json.load(f)

            # The fulfillment service should now show degraded or unhealthy
            fulfillment = data.get("services", {}).get("fulfillment", {})
            fulfillment_status = fulfillment.get("status", "").lower() if isinstance(fulfillment, dict) else str(fulfillment).lower()

            # Overall healthy should be false when one service is down
            overall_healthy = data.get("healthy")

            # Check that the script detected the stopped service
            positive_indicators = ["healthy", "ok", "up", "running", "good", "active"]
            service_shows_healthy = any(ind in fulfillment_status for ind in positive_indicators)

            # At least one of these should indicate the service is not healthy
            detected_problem = (not service_shows_healthy) or (overall_healthy is False)

            assert detected_problem, (
                "When fulfillment service was stopped, check_all.py still reported it as healthy. "
                f"fulfillment status: {fulfillment}, overall healthy: {overall_healthy}. "
                "This suggests the script hardcodes results instead of actually checking services."
            )

        finally:
            # Resume the service
            try:
                os.kill(pid, signal.SIGCONT)
                time.sleep(0.5)
            except ProcessLookupError:
                pass  # Process may have been killed

            # Re-run check_all.py to restore correct state for other tests
            subprocess.run(
                ["python3", "/home/user/monitor/check_all.py"],
                capture_output=True,
                timeout=30
            )
