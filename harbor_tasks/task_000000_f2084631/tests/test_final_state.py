# test_final_state.py
"""
Tests to validate the final state after the student fixes the correlate.py script.
The script should correctly detect lateral movement candidates from Suricata eve.json.
"""

import os
import json
import subprocess
import pytest
import re
import hashlib


class TestEveJsonUnchanged:
    """Verify that /var/log/suricata/eve.json was not modified."""

    def test_eve_json_exists(self):
        """Check that eve.json still exists."""
        path = "/var/log/suricata/eve.json"
        assert os.path.isfile(path), f"Suricata log file not found at {path}"

    def test_eve_json_has_flow_events(self):
        """Check that eve.json still contains flow events (wasn't corrupted)."""
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
        assert flow_count >= 100, f"eve.json should still have flow events, found {flow_count}"


class TestCorrelateScriptFixed:
    """Verify that correlate.py has been fixed correctly."""

    def test_correlate_script_exists(self):
        """Check that /home/user/correlate.py still exists."""
        path = "/home/user/correlate.py"
        assert os.path.isfile(path), f"Correlation script not found at {path}"

    def test_correlate_script_no_hardcoded_scanner_ip(self):
        """Check that correlate.py doesn't hardcode the scanner IP in output."""
        path = "/home/user/correlate.py"
        result = subprocess.run(
            ["grep", "-E", r'print.*10\.1\.5\.23', path],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, \
            "Script appears to hardcode 10.1.5.23 in print statement - this is not allowed"

    def test_correlate_script_checks_flow_event_type(self):
        """Check that correlate.py checks for 'flow' event_type, not 'netflow'."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        # Should check for "flow" event type
        has_flow_check = (
            '"flow"' in content or 
            "'flow'" in content
        )
        assert has_flow_check, "Script should check for event_type 'flow'"

        # Should NOT still have the netflow bug as the primary check
        # (it's okay if netflow appears in comments)
        lines = content.split('\n')
        for line in lines:
            # Skip comments
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            # Check for active netflow check that would filter events
            if 'event_type' in line and 'netflow' in line and '!=' in line:
                # This pattern: if event.get("event_type") != "netflow" would skip all flow events
                pytest.fail("Script still has the 'netflow' bug - checking for wrong event_type")

    def test_correlate_script_preserves_threshold(self):
        """Check that correlate.py still uses THRESHOLD = 3."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        # Look for THRESHOLD = 3 (with possible whitespace variations)
        threshold_match = re.search(r'THRESHOLD\s*=\s*3\b', content)
        assert threshold_match, "Script must preserve THRESHOLD = 3"

    def test_correlate_script_preserves_window(self):
        """Check that correlate.py still uses WINDOW_MINUTES = 5."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        # Look for WINDOW_MINUTES = 5 (with possible whitespace variations)
        window_match = re.search(r'WINDOW_MINUTES\s*=\s*5\b', content)
        assert window_match, "Script must preserve WINDOW_MINUTES = 5"

    def test_correlate_script_preserves_internal_prefix(self):
        """Check that correlate.py still uses INTERNAL_PREFIX = '10.'."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        # Look for INTERNAL_PREFIX = "10." or '10.'
        prefix_match = re.search(r'INTERNAL_PREFIX\s*=\s*["\']10\.["\']', content)
        assert prefix_match, "Script must preserve INTERNAL_PREFIX = '10.'"

    def test_correlate_script_preserves_output_format(self):
        """Check that correlate.py still uses LATERAL_MOVEMENT_CANDIDATE output format."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        assert "LATERAL_MOVEMENT_CANDIDATE" in content, \
            "Script must preserve 'LATERAL_MOVEMENT_CANDIDATE' output format"


class TestCorrelateScriptExecution:
    """Verify that correlate.py runs correctly and detects the scanner."""

    def test_correlate_script_exits_zero(self):
        """Check that running correlate.py exits with code 0."""
        result = subprocess.run(
            ["python3", "/home/user/correlate.py"],
            capture_output=True,
            text=True,
            timeout=300  # Allow up to 5 minutes for processing
        )
        assert result.returncode == 0, \
            f"Script exited with code {result.returncode}. stderr: {result.stderr}"

    def test_correlate_script_detects_scanner(self):
        """Check that correlate.py detects 10.1.5.23 as a lateral movement candidate."""
        result = subprocess.run(
            ["python3", "/home/user/correlate.py"],
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stdout

        # Check for the specific scanner IP in output
        assert "LATERAL_MOVEMENT_CANDIDATE: 10.1.5.23" in output, \
            f"Script should detect 10.1.5.23 as lateral movement candidate. Output was:\n{output}\nStderr: {result.stderr}"

    def test_correlate_script_output_format_correct(self):
        """Check that output follows the expected format."""
        result = subprocess.run(
            ["python3", "/home/user/correlate.py"],
            capture_output=True,
            text=True,
            timeout=300
        )

        output = result.stdout.strip()
        if output:
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if line:
                    # Each non-empty line should match the format
                    assert line.startswith("LATERAL_MOVEMENT_CANDIDATE: "), \
                        f"Output line doesn't match expected format: {line}"
                    # Extract IP and validate it's a valid IP format
                    ip_part = line.replace("LATERAL_MOVEMENT_CANDIDATE: ", "")
                    ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
                    assert ip_pattern.match(ip_part), \
                        f"IP address format invalid in output: {ip_part}"


class TestCorrelateScriptProcessesRealData:
    """Verify that the script actually processes the eve.json data correctly."""

    def test_script_processes_flow_events(self):
        """Verify script logic by checking it can parse flow events from eve.json."""
        # Run a quick check that the script's flow parsing would work
        path = "/var/log/suricata/eve.json"
        flow_count = 0
        internal_flow_count = 0

        with open(path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "flow":
                        flow_count += 1
                        src = event.get("src_ip", "")
                        dst = event.get("dest_ip", "")
                        if src.startswith("10.") and dst.startswith("10.") and src != dst:
                            internal_flow_count += 1
                except (json.JSONDecodeError, KeyError):
                    continue
                if flow_count >= 10000:
                    break

        assert flow_count >= 1000, \
            f"Expected at least 1000 flow events in eve.json, found {flow_count}"
        assert internal_flow_count >= 100, \
            f"Expected at least 100 internal-to-internal flows, found {internal_flow_count}"

    def test_scanner_activity_exists_in_logs(self):
        """Verify that 10.1.5.23 scanning activity exists in the logs."""
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
                except (json.JSONDecodeError, KeyError):
                    continue

        assert len(scanner_destinations) >= 10, \
            f"Scanner 10.1.5.23 should have contacted many internal hosts, found {len(scanner_destinations)}"


class TestAntiShortcutGuards:
    """Additional tests to prevent shortcut solutions."""

    def test_script_not_trivially_hardcoded(self):
        """Check that the script doesn't just print a hardcoded result."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        # Check that the script still opens and reads the eve.json file
        assert 'eve.json' in content or 'suricata' in content, \
            "Script should reference the eve.json log file"

        # Check that it still has JSON parsing logic
        assert 'json' in content.lower(), \
            "Script should use JSON parsing"

        # Check it still has the windowing logic
        assert 'window' in content.lower() or 'timedelta' in content.lower(), \
            "Script should have time window logic"

    def test_script_uses_actual_flow_data(self):
        """Verify script reads actual flow records, not just outputs hardcoded IPs."""
        path = "/home/user/correlate.py"
        with open(path, 'r') as f:
            content = f.read()

        # Should have logic to iterate through events
        has_iteration = (
            'for ' in content and 
            ('line' in content or 'event' in content)
        )
        assert has_iteration, "Script should iterate through log events"

        # Should check event_type
        assert 'event_type' in content, "Script should check event_type field"

    def test_modified_threshold_produces_different_output(self):
        """Test that changing threshold to 50 produces no output (scanner's max burst is ~12)."""
        # Create a temporary modified version of the script
        with open("/home/user/correlate.py", 'r') as f:
            original_content = f.read()

        # Modify threshold to 50
        modified_content = re.sub(
            r'THRESHOLD\s*=\s*3\b',
            'THRESHOLD = 50',
            original_content
        )

        # Write to a temp file
        temp_script = "/tmp/correlate_test_threshold.py"
        with open(temp_script, 'w') as f:
            f.write(modified_content)

        # Run the modified script
        result = subprocess.run(
            ["python3", temp_script],
            capture_output=True,
            text=True,
            timeout=300
        )

        # With threshold 50, should not detect 10.1.5.23 (max burst is ~12)
        output = result.stdout.strip()
        assert "10.1.5.23" not in output, \
            f"With THRESHOLD=50, script should NOT detect 10.1.5.23 (max burst ~12). Output: {output}"

        # Clean up
        os.remove(temp_script)


class TestTimestampParsing:
    """Verify that timestamp parsing works correctly for Suricata format."""

    def test_script_handles_suricata_timestamps(self):
        """Check that the script can handle Suricata timestamp format."""
        # Suricata timestamps look like: 2024-01-15T14:23:45.123456+0000
        # The script must parse these correctly

        # Get a sample timestamp from eve.json
        path = "/var/log/suricata/eve.json"
        sample_ts = None
        with open(path, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    if event.get("event_type") == "flow":
                        sample_ts = event.get("timestamp")
                        if sample_ts:
                            break
                except (json.JSONDecodeError, KeyError):
                    continue

        assert sample_ts is not None, "Could not find a flow event with timestamp"

        # The script should run without timestamp parsing errors
        result = subprocess.run(
            ["python3", "/home/user/correlate.py"],
            capture_output=True,
            text=True,
            timeout=300
        )

        # Check for common timestamp parsing errors
        stderr = result.stderr.lower()
        assert "strptime" not in stderr or "error" not in stderr, \
            f"Script has timestamp parsing issues: {result.stderr}"
        assert "valueerror" not in stderr, \
            f"Script has value errors (possibly timestamp): {result.stderr}"
        assert result.returncode == 0, \
            f"Script failed, possibly due to timestamp parsing: {result.stderr}"
