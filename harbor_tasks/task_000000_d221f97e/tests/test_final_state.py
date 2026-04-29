# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the filter_logs.py script to correctly filter slow requests.
"""

import os
import re
import subprocess
import pytest


class TestInvariants:
    """Test that invariant files remain unchanged."""

    def test_access_log_unchanged_exists(self):
        """The access.log file must still exist."""
        assert os.path.isfile("/var/log/gateway/access.log"), \
            "Log file /var/log/gateway/access.log no longer exists"

    def test_access_log_unchanged_line_count(self):
        """The access.log should still have approximately 5000 lines."""
        with open("/var/log/gateway/access.log", "r") as f:
            line_count = sum(1 for _ in f)

        assert 4500 <= line_count <= 5500, \
            f"Access log has {line_count} lines, expected ~5000 (file may have been modified)"

    def test_test_access_log_unchanged_exists(self):
        """The test_access.log file must still exist."""
        assert os.path.isfile("/home/user/perf/test_access.log"), \
            "Test log file /home/user/perf/test_access.log no longer exists"

    def test_test_access_log_unchanged_line_count(self):
        """The test_access.log should still have exactly 10 lines."""
        with open("/home/user/perf/test_access.log", "r") as f:
            line_count = sum(1 for _ in f)

        assert line_count == 10, \
            f"Test access log has {line_count} lines, expected exactly 10 (file may have been modified)"


class TestScriptIOPaths:
    """Test that the script still uses the correct I/O paths."""

    def test_script_still_reads_access_log(self):
        """The script must still read from /var/log/gateway/access.log."""
        with open("/home/user/perf/filter_logs.py", "r") as f:
            content = f.read()

        assert "/var/log/gateway/access.log" in content, \
            "Script no longer references /var/log/gateway/access.log as input"

    def test_script_still_writes_slow_txt(self):
        """The script must still write to /home/user/perf/slow.txt."""
        with open("/home/user/perf/filter_logs.py", "r") as f:
            content = f.read()

        assert "/home/user/perf/slow.txt" in content or "slow.txt" in content, \
            "Script no longer references slow.txt as output"


class TestScriptExecution:
    """Test that the script runs successfully."""

    def test_script_runs_without_error(self):
        """The script must execute without errors."""
        result = subprocess.run(
            ["python3", "/home/user/perf/filter_logs.py"],
            capture_output=True,
            text=True,
            cwd="/home/user/perf"
        )

        assert result.returncode == 0, \
            f"Script failed with return code {result.returncode}. Stderr: {result.stderr}"

    def test_slow_txt_created(self):
        """The script must create /home/user/perf/slow.txt."""
        # First run the script to ensure output is generated
        subprocess.run(
            ["python3", "/home/user/perf/filter_logs.py"],
            capture_output=True,
            text=True,
            cwd="/home/user/perf"
        )

        assert os.path.isfile("/home/user/perf/slow.txt"), \
            "Output file /home/user/perf/slow.txt was not created"


class TestOutputCorrectness:
    """Test that the output file contains exactly the correct slow requests."""

    @pytest.fixture(autouse=True)
    def run_script(self):
        """Run the script before each test in this class."""
        subprocess.run(
            ["python3", "/home/user/perf/filter_logs.py"],
            capture_output=True,
            text=True,
            cwd="/home/user/perf"
        )

    def test_output_has_exactly_187_lines(self):
        """The output must contain exactly 187 lines."""
        with open("/home/user/perf/slow.txt", "r") as f:
            lines = [line for line in f if line.strip()]  # Non-empty lines

        assert len(lines) == 187, \
            f"Output has {len(lines)} lines, expected exactly 187 slow requests"

    def test_all_output_lines_have_slow_response_time(self):
        """Every line in output must have actual response time > 500ms."""
        # Pattern for legacy format: response_time=XXXms (but NOT upstream_response_time)
        legacy_pattern = re.compile(r'(?<![a-z_])response_time=(\d+)ms')
        # Pattern for new format: response_time_ms=XXX
        new_pattern = re.compile(r'response_time_ms=(\d+)')

        with open("/home/user/perf/slow.txt", "r") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                response_time = None

                # Check legacy format
                legacy_match = legacy_pattern.search(line)
                if legacy_match:
                    response_time = int(legacy_match.group(1))

                # Check new format
                new_match = new_pattern.search(line)
                if new_match:
                    response_time = int(new_match.group(1))

                assert response_time is not None, \
                    f"Line {line_num} has no valid response_time field: {line[:100]}..."

                assert response_time > 500, \
                    f"Line {line_num} has response_time={response_time}ms which is not > 500ms: {line[:100]}..."

    def test_output_lines_are_from_access_log(self):
        """Every line in output must be a complete line from access.log."""
        with open("/var/log/gateway/access.log", "r") as f:
            access_log_lines = set(line.strip() for line in f)

        with open("/home/user/perf/slow.txt", "r") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped:
                    continue

                assert stripped in access_log_lines, \
                    f"Line {line_num} in slow.txt is not from access.log: {stripped[:100]}..."


class TestNoFalsePositivesFromUpstream:
    """Test that upstream_response_time is not causing false positives."""

    @pytest.fixture(autouse=True)
    def run_script(self):
        """Run the script before each test in this class."""
        subprocess.run(
            ["python3", "/home/user/perf/filter_logs.py"],
            capture_output=True,
            text=True,
            cwd="/home/user/perf"
        )

    def test_no_lines_solely_from_upstream_response_time(self):
        """
        No line should appear in slow.txt solely because upstream_response_time > 500ms
        while actual response_time <= 500ms.
        """
        # Pattern for legacy format: response_time=XXXms (but NOT upstream_response_time)
        legacy_pattern = re.compile(r'(?<![a-z_])response_time=(\d+)ms')
        # Pattern for new format: response_time_ms=XXX
        new_pattern = re.compile(r'response_time_ms=(\d+)')

        false_positives = []

        with open("/home/user/perf/slow.txt", "r") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue

                # Get actual response time
                actual_response_time = None

                legacy_match = legacy_pattern.search(line)
                if legacy_match:
                    actual_response_time = int(legacy_match.group(1))

                new_match = new_pattern.search(line)
                if new_match:
                    actual_response_time = int(new_match.group(1))

                # If actual response time is <= 500, this is a false positive
                if actual_response_time is not None and actual_response_time <= 500:
                    false_positives.append((line_num, actual_response_time, line[:100]))

        assert len(false_positives) == 0, \
            f"Found {len(false_positives)} false positives (lines with actual response_time <= 500ms): {false_positives[:5]}"


class TestBothFormatsHandled:
    """Test that both log formats are correctly handled."""

    @pytest.fixture(autouse=True)
    def run_script(self):
        """Run the script before each test in this class."""
        subprocess.run(
            ["python3", "/home/user/perf/filter_logs.py"],
            capture_output=True,
            text=True,
            cwd="/home/user/perf"
        )

    def test_output_contains_v1_api_entries(self):
        """Output should contain slow requests from /api/v1/ (legacy format)."""
        with open("/home/user/perf/slow.txt", "r") as f:
            content = f.read()

        v1_count = len(re.findall(r'/api/v1/', content))

        assert v1_count > 0, \
            "Output contains no /api/v1/ entries - legacy format may not be handled"

    def test_output_contains_v2_api_entries(self):
        """Output should contain slow requests from /api/v2/ (new format)."""
        with open("/home/user/perf/slow.txt", "r") as f:
            content = f.read()

        v2_count = len(re.findall(r'/api/v2/', content))

        assert v2_count > 0, \
            "Output contains no /api/v2/ entries - new format (response_time_ms=) may not be handled"


class TestAntiShortcutGuards:
    """Tests to ensure the fix is genuine and not a shortcut."""

    @pytest.fixture(autouse=True)
    def run_script(self):
        """Run the script before each test in this class."""
        subprocess.run(
            ["python3", "/home/user/perf/filter_logs.py"],
            capture_output=True,
            text=True,
            cwd="/home/user/perf"
        )

    def test_not_hardcoded_line_count(self):
        """
        Verify the script actually processes the log file, not just outputs
        a hardcoded number of lines.
        """
        with open("/home/user/perf/filter_logs.py", "r") as f:
            script_content = f.read()

        # Check that script doesn't just print "187" or similar hardcoded values
        assert "187" not in script_content or "open" in script_content, \
            "Script may have hardcoded the expected line count"

    def test_not_simple_grep_for_500(self):
        """
        Verify the output isn't just all lines containing "500" somewhere.
        """
        with open("/home/user/perf/slow.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        # Count lines that have response_time values that are NOT > 500
        # but might contain "500" somewhere else
        lines_with_500_in_text = sum(1 for line in lines if "500" in line)

        # If every single line contains "500", it might be a naive grep
        # But this is actually okay if they're legitimately slow requests
        # The real test is that we have exactly 187 lines with proper filtering
        assert len(lines) == 187, \
            f"Output has {len(lines)} lines, not the expected 187"

    def test_script_uses_regex_or_parsing(self):
        """Verify the script uses some form of pattern matching or parsing."""
        with open("/home/user/perf/filter_logs.py", "r") as f:
            script_content = f.read()

        # Should use re module or string parsing
        uses_regex = "import re" in script_content or "re." in script_content
        uses_string_ops = "split" in script_content or "find" in script_content

        assert uses_regex or uses_string_ops, \
            "Script doesn't appear to use regex or string parsing for filtering"
