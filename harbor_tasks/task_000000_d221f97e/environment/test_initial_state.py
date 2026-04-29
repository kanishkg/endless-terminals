# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the filter_logs.py script.
"""

import os
import re
import subprocess
import pytest


class TestInitialFileSystem:
    """Test that required files and directories exist."""

    def test_perf_directory_exists(self):
        """The /home/user/perf/ directory must exist."""
        assert os.path.isdir("/home/user/perf"), \
            "Directory /home/user/perf/ does not exist"

    def test_perf_directory_writable(self):
        """The /home/user/perf/ directory must be writable."""
        assert os.access("/home/user/perf", os.W_OK), \
            "Directory /home/user/perf/ is not writable"

    def test_filter_logs_script_exists(self):
        """The filter_logs.py script must exist."""
        assert os.path.isfile("/home/user/perf/filter_logs.py"), \
            "Script /home/user/perf/filter_logs.py does not exist"

    def test_filter_logs_script_writable(self):
        """The filter_logs.py script must be writable (for fixing)."""
        assert os.access("/home/user/perf/filter_logs.py", os.W_OK), \
            "Script /home/user/perf/filter_logs.py is not writable"

    def test_access_log_exists(self):
        """The access.log file must exist."""
        assert os.path.isfile("/var/log/gateway/access.log"), \
            "Log file /var/log/gateway/access.log does not exist"

    def test_access_log_readable(self):
        """The access.log file must be readable."""
        assert os.access("/var/log/gateway/access.log", os.R_OK), \
            "Log file /var/log/gateway/access.log is not readable"

    def test_gateway_log_directory_exists(self):
        """The /var/log/gateway/ directory must exist."""
        assert os.path.isdir("/var/log/gateway"), \
            "Directory /var/log/gateway/ does not exist"

    def test_test_access_log_exists(self):
        """The test_access.log file must exist."""
        assert os.path.isfile("/home/user/perf/test_access.log"), \
            "Test log file /home/user/perf/test_access.log does not exist"


class TestFilterLogsScriptContent:
    """Test that the filter_logs.py script has the expected buggy implementation."""

    def test_script_contains_buggy_regex(self):
        """The script must contain the buggy regex pattern."""
        with open("/home/user/perf/filter_logs.py", "r") as f:
            content = f.read()

        # Check for the specific buggy regex pattern
        assert r"response_time=(\d+)ms" in content or r'response_time=(\d+)ms' in content, \
            "Script does not contain the expected buggy regex pattern 'response_time=(\\d+)ms'"

    def test_script_reads_correct_input_file(self):
        """The script must reference the correct input log file."""
        with open("/home/user/perf/filter_logs.py", "r") as f:
            content = f.read()

        assert "/var/log/gateway/access.log" in content, \
            "Script does not reference /var/log/gateway/access.log as input"

    def test_script_writes_correct_output_file(self):
        """The script must reference the correct output file."""
        with open("/home/user/perf/filter_logs.py", "r") as f:
            content = f.read()

        assert "/home/user/perf/slow.txt" in content or "slow.txt" in content, \
            "Script does not reference slow.txt as output"


class TestAccessLogContent:
    """Test that the access.log has the expected format and content."""

    def test_access_log_has_approximately_5000_lines(self):
        """The access.log should have approximately 5000 lines."""
        with open("/var/log/gateway/access.log", "r") as f:
            line_count = sum(1 for _ in f)

        assert 4500 <= line_count <= 5500, \
            f"Access log has {line_count} lines, expected ~5000"

    def test_access_log_has_legacy_format_entries(self):
        """The access.log must contain legacy format entries (response_time=XXXms)."""
        with open("/var/log/gateway/access.log", "r") as f:
            content = f.read()

        # Check for legacy format with /api/v1/ paths
        legacy_pattern = r'/api/v1/.*response_time=\d+ms'
        matches = re.findall(legacy_pattern, content)

        assert len(matches) > 0, \
            "Access log does not contain legacy format entries (/api/v1/ with response_time=XXXms)"

    def test_access_log_has_new_format_entries(self):
        """The access.log must contain new format entries (response_time_ms=XXX)."""
        with open("/var/log/gateway/access.log", "r") as f:
            content = f.read()

        # Check for new format with /api/v2/ paths
        new_pattern = r'/api/v2/.*response_time_ms=\d+'
        matches = re.findall(new_pattern, content)

        assert len(matches) > 0, \
            "Access log does not contain new format entries (/api/v2/ with response_time_ms=XXX)"

    def test_access_log_has_upstream_response_time_fields(self):
        """The access.log must contain upstream_response_time fields."""
        with open("/var/log/gateway/access.log", "r") as f:
            content = f.read()

        upstream_pattern = r'upstream_response_time=\d+ms'
        matches = re.findall(upstream_pattern, content)

        assert len(matches) > 0, \
            "Access log does not contain upstream_response_time fields"

    def test_many_upstream_response_times_exceed_500ms(self):
        """Many upstream_response_time values should exceed 500ms (causing the bug)."""
        with open("/var/log/gateway/access.log", "r") as f:
            content = f.read()

        # Find all upstream_response_time values
        upstream_pattern = r'upstream_response_time=(\d+)ms'
        matches = re.findall(upstream_pattern, content)

        slow_upstream_count = sum(1 for m in matches if int(m) > 500)

        assert slow_upstream_count > 1000, \
            f"Only {slow_upstream_count} upstream_response_time values exceed 500ms, expected many more to explain the bug"


class TestTestAccessLogContent:
    """Test that the test_access.log has the expected simple format."""

    def test_test_log_has_10_lines(self):
        """The test_access.log should have exactly 10 lines."""
        with open("/home/user/perf/test_access.log", "r") as f:
            line_count = sum(1 for _ in f)

        assert line_count == 10, \
            f"Test access log has {line_count} lines, expected exactly 10"

    def test_test_log_uses_only_legacy_format(self):
        """The test_access.log should only use legacy format (response_time=XXXms)."""
        with open("/home/user/perf/test_access.log", "r") as f:
            content = f.read()

        # Should have legacy format
        legacy_pattern = r'response_time=\d+ms'
        legacy_matches = re.findall(legacy_pattern, content)
        assert len(legacy_matches) > 0, \
            "Test log does not contain legacy format entries"

    def test_test_log_has_no_upstream_response_time(self):
        """The test_access.log should not contain upstream_response_time fields."""
        with open("/home/user/perf/test_access.log", "r") as f:
            content = f.read()

        assert "upstream_response_time" not in content, \
            "Test log contains upstream_response_time fields, but should not (explains why script 'works' on test data)"


class TestPythonEnvironment:
    """Test that Python 3.11 is available."""

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "Python 3 is not available"

    def test_python3_version_is_3_11_or_higher(self):
        """Python 3.11 or higher should be available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        version_output = result.stdout.strip()
        # Parse version like "Python 3.11.x"
        match = re.search(r'Python (\d+)\.(\d+)', version_output)
        assert match, f"Could not parse Python version from: {version_output}"

        major, minor = int(match.group(1)), int(match.group(2))
        assert (major, minor) >= (3, 11), \
            f"Python version is {major}.{minor}, expected 3.11 or higher"


class TestExpectedSlowRequestCount:
    """Test that the actual number of slow requests matches the expected count."""

    def test_actual_slow_requests_count_is_187(self):
        """
        Verify that exactly 187 lines in access.log have actual response time > 500ms.
        This counts both formats: response_time=XXXms and response_time_ms=XXX
        but NOT upstream_response_time.
        """
        slow_count = 0

        # Pattern for legacy format: response_time=XXXms (but NOT upstream_response_time)
        # We need to ensure we're matching response_time= at word boundary or start
        legacy_pattern = re.compile(r'(?<![a-z_])response_time=(\d+)ms')

        # Pattern for new format: response_time_ms=XXX
        new_pattern = re.compile(r'response_time_ms=(\d+)')

        with open("/var/log/gateway/access.log", "r") as f:
            for line in f:
                # Check legacy format
                legacy_match = legacy_pattern.search(line)
                if legacy_match:
                    response_time = int(legacy_match.group(1))
                    if response_time > 500:
                        slow_count += 1
                        continue

                # Check new format
                new_match = new_pattern.search(line)
                if new_match:
                    response_time = int(new_match.group(1))
                    if response_time > 500:
                        slow_count += 1

        assert slow_count == 187, \
            f"Found {slow_count} slow requests (>500ms), expected exactly 187"
