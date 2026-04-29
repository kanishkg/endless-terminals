# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the Apache log parsing task.
"""

import os
import pytest
import re


class TestFinalState:
    """Test suite to validate final state after the task is completed."""

    def test_ip_status_file_exists(self):
        """Verify /home/user/logs/ip_status.txt exists."""
        ip_status = "/home/user/logs/ip_status.txt"
        assert os.path.isfile(ip_status), (
            f"File {ip_status} does not exist. "
            "The output file must be created with extracted IP addresses and status codes."
        )

    def test_ip_status_file_is_readable(self):
        """Verify /home/user/logs/ip_status.txt is readable."""
        ip_status = "/home/user/logs/ip_status.txt"
        assert os.access(ip_status, os.R_OK), (
            f"File {ip_status} is not readable."
        )

    def test_access_log_unchanged(self):
        """Verify /home/user/logs/access.log still exists and has content."""
        access_log = "/home/user/logs/access.log"
        assert os.path.isfile(access_log), (
            f"File {access_log} no longer exists. "
            "The original access log should not be deleted."
        )
        with open(access_log, 'r') as f:
            content = f.read()
        assert len(content) > 0, (
            f"File {access_log} is now empty. "
            "The original access log should not be modified."
        )

    def test_line_count_matches(self):
        """Verify ip_status.txt has the same number of lines as access.log."""
        access_log = "/home/user/logs/access.log"
        ip_status = "/home/user/logs/ip_status.txt"

        with open(access_log, 'r') as f:
            access_lines = [line for line in f.readlines() if line.strip()]

        with open(ip_status, 'r') as f:
            status_lines = [line for line in f.readlines() if line.strip()]

        assert len(status_lines) == len(access_lines), (
            f"Line count mismatch: ip_status.txt has {len(status_lines)} lines, "
            f"but access.log has {len(access_lines)} lines. "
            "Each log entry should produce exactly one output line."
        )

    def test_output_format_tab_separated(self):
        """Verify each line in ip_status.txt is tab-separated IP and status code."""
        ip_status = "/home/user/logs/ip_status.txt"

        with open(ip_status, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.rstrip('\n\r')
            if not line:
                continue

            # Check for tab separator
            assert '\t' in line, (
                f"Line {i+1} does not contain a tab separator:\n"
                f"  '{line}'\n"
                "Expected format: IP<tab>STATUS_CODE (e.g., '192.168.1.1\\t200')"
            )

            parts = line.split('\t')
            assert len(parts) == 2, (
                f"Line {i+1} does not have exactly 2 tab-separated fields:\n"
                f"  '{line}'\n"
                f"  Found {len(parts)} fields: {parts}\n"
                "Expected format: IP<tab>STATUS_CODE"
            )

    def test_valid_ip_addresses(self):
        """Verify all IPs in ip_status.txt are valid IPv4 addresses."""
        ip_status = "/home/user/logs/ip_status.txt"
        ip_pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')

        with open(ip_status, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.rstrip('\n\r')
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            ip = parts[0].strip()
            match = ip_pattern.match(ip)
            assert match, (
                f"Line {i+1} has invalid IP address: '{ip}'\n"
                "Expected a valid IPv4 address (e.g., 192.168.1.1)"
            )

            # Verify each octet is 0-255
            for j, octet in enumerate(match.groups()):
                octet_val = int(octet)
                assert 0 <= octet_val <= 255, (
                    f"Line {i+1} has invalid IP octet: {octet_val} in '{ip}'"
                )

    def test_valid_status_codes(self):
        """Verify all status codes in ip_status.txt are valid 3-digit HTTP codes."""
        ip_status = "/home/user/logs/ip_status.txt"

        with open(ip_status, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.rstrip('\n\r')
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 2:
                continue

            status = parts[1].strip()

            # Check it's a 3-digit number
            assert re.match(r'^\d{3}$', status), (
                f"Line {i+1} has invalid status code: '{status}'\n"
                "Expected a 3-digit HTTP status code (e.g., 200, 404, 500)"
            )

            status_int = int(status)
            assert 100 <= status_int <= 599, (
                f"Line {i+1} has out-of-range status code: {status_int}\n"
                "Expected HTTP status code between 100 and 599"
            )

    def test_ips_match_access_log(self):
        """Verify IPs in ip_status.txt match field 1 of corresponding access.log lines."""
        access_log = "/home/user/logs/access.log"
        ip_status = "/home/user/logs/ip_status.txt"

        with open(access_log, 'r') as f:
            access_lines = [line.strip() for line in f.readlines() if line.strip()]

        with open(ip_status, 'r') as f:
            status_lines = [line.rstrip('\n\r') for line in f.readlines() if line.strip()]

        ip_pattern = re.compile(r'^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

        for i, (access_line, status_line) in enumerate(zip(access_lines, status_lines)):
            # Extract IP from access log (first field)
            access_match = ip_pattern.match(access_line)
            assert access_match, f"Could not extract IP from access.log line {i+1}"
            expected_ip = access_match.group(1)

            # Extract IP from status file
            parts = status_line.split('\t')
            actual_ip = parts[0].strip() if parts else ""

            assert actual_ip == expected_ip, (
                f"Line {i+1}: IP mismatch\n"
                f"  Expected: {expected_ip}\n"
                f"  Got: {actual_ip}\n"
                f"  Access log line: {access_line[:80]}..."
            )

    def test_status_codes_match_access_log(self):
        """Verify status codes in ip_status.txt match the HTTP response codes from access.log."""
        access_log = "/home/user/logs/access.log"
        ip_status = "/home/user/logs/ip_status.txt"

        with open(access_log, 'r') as f:
            access_lines = [line.strip() for line in f.readlines() if line.strip()]

        with open(ip_status, 'r') as f:
            status_lines = [line.rstrip('\n\r') for line in f.readlines() if line.strip()]

        # Pattern to extract status code from Combined Log Format
        # Status code appears after the closing quote of the request string
        status_pattern = re.compile(r'"\s+(\d{3})\s+')

        for i, (access_line, status_line) in enumerate(zip(access_lines, status_lines)):
            # Extract status code from access log
            status_match = status_pattern.search(access_line)
            assert status_match, (
                f"Could not extract status code from access.log line {i+1}:\n"
                f"  {access_line}"
            )
            expected_status = status_match.group(1)

            # Extract status code from status file
            parts = status_line.split('\t')
            actual_status = parts[1].strip() if len(parts) > 1 else ""

            assert actual_status == expected_status, (
                f"Line {i+1}: Status code mismatch\n"
                f"  Expected: {expected_status}\n"
                f"  Got: {actual_status}\n"
                f"  Access log line: {access_line[:80]}..."
            )

    def test_no_extra_whitespace_in_output(self):
        """Verify output lines don't have leading/trailing whitespace issues."""
        ip_status = "/home/user/logs/ip_status.txt"

        with open(ip_status, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            # Remove only the newline, not other whitespace
            line_no_newline = line.rstrip('\n\r')
            if not line_no_newline:
                continue

            parts = line_no_newline.split('\t')
            if len(parts) == 2:
                ip_part = parts[0]
                status_part = parts[1]

                # IP should not have leading/trailing spaces
                assert ip_part == ip_part.strip(), (
                    f"Line {i+1}: IP has extra whitespace: '{ip_part}'"
                )

                # Status should not have leading/trailing spaces
                assert status_part == status_part.strip(), (
                    f"Line {i+1}: Status code has extra whitespace: '{status_part}'"
                )

    def test_output_file_not_empty(self):
        """Verify ip_status.txt is not empty."""
        ip_status = "/home/user/logs/ip_status.txt"

        with open(ip_status, 'r') as f:
            content = f.read()

        assert content.strip(), (
            f"File {ip_status} is empty. "
            "It should contain extracted IP addresses and status codes."
        )
