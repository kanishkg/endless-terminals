# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the Apache log parsing task.
"""

import os
import pytest
import re


class TestInitialState:
    """Test suite to validate initial state before the task."""

    def test_logs_directory_exists(self):
        """Verify /home/user/logs/ directory exists."""
        logs_dir = "/home/user/logs"
        assert os.path.isdir(logs_dir), (
            f"Directory {logs_dir} does not exist. "
            "The logs directory must be present for this task."
        )

    def test_access_log_exists(self):
        """Verify /home/user/logs/access.log file exists."""
        access_log = "/home/user/logs/access.log"
        assert os.path.isfile(access_log), (
            f"File {access_log} does not exist. "
            "The Apache access log must be present for this task."
        )

    def test_access_log_is_readable(self):
        """Verify /home/user/logs/access.log is readable."""
        access_log = "/home/user/logs/access.log"
        assert os.access(access_log, os.R_OK), (
            f"File {access_log} is not readable. "
            "The access log must be readable to extract IP addresses and status codes."
        )

    def test_access_log_has_content(self):
        """Verify access.log has approximately 50 lines of content."""
        access_log = "/home/user/logs/access.log"
        with open(access_log, 'r') as f:
            lines = f.readlines()

        line_count = len(lines)
        assert line_count > 0, (
            f"File {access_log} is empty. "
            "The access log must contain log entries."
        )
        # Allow some flexibility around ~50 lines
        assert 10 <= line_count <= 200, (
            f"File {access_log} has {line_count} lines. "
            "Expected approximately 50 lines of log entries."
        )

    def test_access_log_has_combined_log_format(self):
        """Verify access.log contains entries in Combined Log Format."""
        access_log = "/home/user/logs/access.log"

        # Combined Log Format pattern:
        # IP - - [timestamp] "REQUEST" STATUS SIZE "REFERER" "USER_AGENT"
        combined_log_pattern = re.compile(
            r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+'  # IP address
            r'-\s+-\s+'  # Two dashes
            r'\[[^\]]+\]\s+'  # Timestamp in brackets
            r'"[^"]*"\s+'  # Request in quotes
            r'(\d{3})\s+'  # Status code (3 digits)
            r'\d+\s+'  # Response size
            r'"[^"]*"\s+'  # Referer in quotes
            r'"[^"]*"'  # User agent in quotes
        )

        with open(access_log, 'r') as f:
            lines = f.readlines()

        valid_lines = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if line:  # Skip empty lines
                match = combined_log_pattern.match(line)
                if match:
                    valid_lines += 1
                else:
                    # Allow some flexibility but at least check first few lines
                    if i < 5:
                        pytest.fail(
                            f"Line {i+1} does not match Combined Log Format:\n"
                            f"  {line}\n"
                            "Expected format like: "
                            '192.168.1.45 - - [15/Jan/2024:10:23:15 +0000] "GET /index.html HTTP/1.1" 200 1234 "-" "Mozilla/5.0"'
                        )

        assert valid_lines > 0, (
            f"No valid Combined Log Format entries found in {access_log}. "
            "The log file must contain properly formatted Apache log entries."
        )

    def test_logs_directory_is_writable(self):
        """Verify /home/user/logs/ directory is writable."""
        logs_dir = "/home/user/logs"
        assert os.access(logs_dir, os.W_OK), (
            f"Directory {logs_dir} is not writable. "
            "The logs directory must be writable to create ip_status.txt."
        )

    def test_ip_status_txt_does_not_exist(self):
        """Verify /home/user/logs/ip_status.txt does not exist initially."""
        ip_status = "/home/user/logs/ip_status.txt"
        assert not os.path.exists(ip_status), (
            f"File {ip_status} already exists. "
            "The output file should not exist before the task is performed."
        )

    def test_required_tools_available(self):
        """Verify required text processing tools are available."""
        import shutil

        required_tools = ['awk', 'sed', 'grep', 'cut']
        missing_tools = []

        for tool in required_tools:
            if shutil.which(tool) is None:
                missing_tools.append(tool)

        assert not missing_tools, (
            f"Required tools are missing: {', '.join(missing_tools)}. "
            "These tools must be available for text processing."
        )

    def test_access_log_contains_valid_ips(self):
        """Verify access.log contains valid IP addresses in field 1."""
        access_log = "/home/user/logs/access.log"
        ip_pattern = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

        with open(access_log, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if line:
                match = ip_pattern.match(line)
                assert match, (
                    f"Line {i+1} does not start with a valid IP address:\n"
                    f"  {line[:50]}..."
                )

    def test_access_log_contains_valid_status_codes(self):
        """Verify access.log contains valid HTTP status codes."""
        access_log = "/home/user/logs/access.log"

        # Pattern to find status code after the request
        status_pattern = re.compile(r'"\s+(\d{3})\s+')

        with open(access_log, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if line:
                match = status_pattern.search(line)
                assert match, (
                    f"Line {i+1} does not contain a valid HTTP status code:\n"
                    f"  {line}"
                )
                status_code = int(match.group(1))
                assert 100 <= status_code <= 599, (
                    f"Line {i+1} has invalid status code {status_code}. "
                    "Expected a valid HTTP status code (100-599)."
                )
