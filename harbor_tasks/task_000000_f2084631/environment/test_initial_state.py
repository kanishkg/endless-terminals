# test_initial_state.py
"""
Tests to validate the initial state of the system before the student fixes the correlate.py script.
"""

import os
import json
import subprocess
import pytest


class TestSuricataLogExists:
    """Verify Suricata eve.json log file exists and has expected content."""

    def test_eve_json_exists(self):
        """Check that /var/log/suricata/eve.json exists."""
        path = "/var/log/suricata/eve.json"
        assert os.path.isfile(path), f"Suricata log file not found at {path}"

    def test_eve_json_readable(self):
        """Check that eve.json is readable."""
        path = "/var/log/suricata/eve.json"
        assert os.access(path, os.R_OK), f"Cannot read {path}"

    def test_eve_json_has_content(self):
        """Check that eve.json has substantial content (~50,000 lines expected)."""
        path = "/var/log/suricata/eve.json"
        line_count = 0
        with open(path, 'r') as f:
            for _ in f:
                line_count += 1
                if line_count >= 1000:  # At least 1000 lines for meaningful data
                    break
        assert line_count >= 1000, f"eve.json has only {line_count} lines, expected at least 1000"

    def test_eve_json_valid_json_lines(self):
        """Check that eve.json contains valid JSON lines."""
        path = "/var/log/suricata/eve.json"
        valid_count = 0
        with open(path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 100:  # Check first 100 lines
                    break
                try:
                    json.loads(line)
                    valid_count += 1
                except json.JSONDecodeError:
                    pass
        assert valid_count >= 90, f"Only {valid_count}/100 lines are valid JSON"

    def test_eve_json_has_flow_events(self):
        """Check that eve.json contains flow event types."""
        path = "/var/log/suricata/eve.json"
        flow_count = 0
        with open(path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "flow":
                        flow_count += 1
                        if flow_count >= 100:
                            break
                except json.JSONDecodeError:
                    continue
        assert flow_count >= 100, f"Only found {flow_count} flow events, expected at least 100"

    def test_eve_json_has_internal_traffic(self):
        """Check that eve.json contains internal-to-internal traffic (10.x.x.x)."""
        path = "/var/log/suricata/eve.json"
        internal_flow_count = 0
        with open(path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "flow":
                        src = event.get("src_ip", "")
                        dst = event.get("dest_ip", "")
                        if src.startswith("10.") and dst.startswith("10."):
                            internal_flow_count += 1
                            if internal_flow_count >= 50:
                                break
                except json.JSONDecodeError:
                    continue
        assert internal_flow_count >= 50, f"Only found {internal_flow_count} internal-to-internal flows"

    def test_eve_json_has_scanner_activity(self):
        """Check that eve.json contains scanning activity from 10.1.5.23."""
        path = "/var/log/suricata/eve.json"
        scanner_destinations = set()
        with open(path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "flow":
                        src = event.get("src_ip", "")
                        dst = event.get("dest_ip", "")
                        if src == "10.1.5.23" and dst.startswith("10.") and dst != src:
                            scanner_destinations.add(dst)
                except json.JSONDecodeError:
                    continue
        assert len(scanner_destinations) >= 10, \
            f"Scanner 10.1.5.23 only contacted {len(scanner_destinations)} distinct internal hosts, expected significant scanning activity"

    def test_eve_json_has_multiple_event_types(self):
        """Check that eve.json has various event types (alert, flow, dns, etc.)."""
        path = "/var/log/suricata/eve.json"
        event_types = set()
        with open(path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 5000:  # Check first 5000 lines
                    break
                try:
                    event = json.loads(line)
                    et = event.get("event_type")
                    if et:
                        event_types.add(et)
                except json.JSONDecodeError:
                    continue
        assert "flow" in event_types, "No 'flow' event_type found in eve.json"
        assert len(event_types) >= 2, f"Only found event types: {event_types}, expected variety"


class TestCorrelateScriptExists:
    """Verify the correlate.py script exists with expected bugs."""

    def test_correlate_script_exists(self):
        """Check that /home/user/correlate.py exists."""
        path = "/home/user/correlate.py"
        assert os.path.isfile(path), f"Correlation script not found at {path}"

    def test_correlate_script_readable(self):
        """Check that correlate.py is readable."""
        path = "/home/user/correlate.py"
        assert os.access(path, os.R_OK), f"Cannot read {path}"

    def test_correlate_script_is_python(self):
        """Check that correlate.py appears to be a Python script."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "import json" in content or "import" in content, "Script doesn't appear to be Python"
        assert "def " in content or "class " in content, "Script doesn't contain function or class definitions"

    def test_correlate_script_has_netflow_bug(self):
        """Check that correlate.py has the 'netflow' bug (checks for wrong event_type)."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()
        # The bug is checking for "netflow" instead of "flow"
        assert '"netflow"' in content or "'netflow'" in content, \
            "Script should contain the 'netflow' bug (checking for wrong event_type)"

    def test_correlate_script_has_threshold_3(self):
        """Check that correlate.py uses threshold of 3."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "THRESHOLD = 3" in content or "THRESHOLD=3" in content, \
            "Script should have THRESHOLD = 3"

    def test_correlate_script_has_window_5(self):
        """Check that correlate.py uses 5-minute window."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "WINDOW_MINUTES = 5" in content or "WINDOW_MINUTES=5" in content, \
            "Script should have WINDOW_MINUTES = 5"

    def test_correlate_script_has_internal_prefix(self):
        """Check that correlate.py uses '10.' as internal prefix."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()
        assert 'INTERNAL_PREFIX = "10."' in content or "INTERNAL_PREFIX = '10.'" in content, \
            "Script should have INTERNAL_PREFIX = '10.'"

    def test_correlate_script_has_output_format(self):
        """Check that correlate.py has the expected output format."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()
        assert "LATERAL_MOVEMENT_CANDIDATE" in content, \
            "Script should contain 'LATERAL_MOVEMENT_CANDIDATE' output format"


class TestCorrelateScriptCurrentlyFails:
    """Verify that the correlate.py script currently fails to detect the scanner."""

    def test_correlate_script_produces_no_output(self):
        """Check that running correlate.py currently produces no lateral movement candidates."""
        result = subprocess.run(
            ["python3", "/home/user/correlate.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        # The script should run but produce no output due to the netflow bug
        output = result.stdout.strip()
        assert "LATERAL_MOVEMENT_CANDIDATE: 10.1.5.23" not in output, \
            "Script should NOT currently detect 10.1.5.23 (bug not yet fixed)"


class TestDirectoryPermissions:
    """Verify directory permissions are correct."""

    def test_home_user_exists(self):
        """Check that /home/user directory exists."""
        path = "/home/user"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_home_user_writable(self):
        """Check that /home/user is writable."""
        path = "/home/user"
        assert os.access(path, os.W_OK), f"Directory {path} is not writable"

    def test_suricata_log_dir_exists(self):
        """Check that /var/log/suricata directory exists."""
        path = "/var/log/suricata"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_suricata_log_dir_readable(self):
        """Check that /var/log/suricata is readable."""
        path = "/var/log/suricata"
        assert os.access(path, os.R_OK), f"Directory {path} is not readable"


class TestPythonEnvironment:
    """Verify Python environment is suitable."""

    def test_python3_available(self):
        """Check that Python 3 is available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python 3 is not available"
        assert "Python 3" in result.stdout, f"Unexpected Python version: {result.stdout}"

    def test_python_version_sufficient(self):
        """Check that Python version is 3.8+ for good datetime handling."""
        result = subprocess.run(
            ["python3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        assert major >= 3 and minor >= 8, f"Python version {version} may be too old, need 3.8+"


class TestToolsAvailable:
    """Verify required tools are available."""

    def test_jq_installed(self):
        """Check that jq is installed."""
        result = subprocess.run(
            ["which", "jq"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "jq is not installed"
