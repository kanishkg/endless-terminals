# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the log analysis task.
"""

import pytest
import os


class TestInitialDirectoryStructure:
    """Test that required directories exist before the task."""

    def test_logs_directory_exists(self):
        """The /home/user/logs/ directory must exist."""
        logs_dir = "/home/user/logs"
        assert os.path.isdir(logs_dir), (
            f"Directory '{logs_dir}' does not exist. "
            "The logs directory must be present before starting the task."
        )

    def test_reports_directory_does_not_exist(self):
        """The /home/user/reports/ directory should NOT exist initially (agent should create it)."""
        reports_dir = "/home/user/reports"
        # This is optional - the task says the agent should create it
        # We just verify it's not required to exist beforehand
        # If it exists, that's also fine - we just don't require it
        pass  # No assertion needed - agent will create if missing


class TestAccessLogFile:
    """Test that the access log file exists and has expected content."""

    def test_access_log_file_exists(self):
        """The access.log file must exist at /home/user/logs/access.log."""
        log_file = "/home/user/logs/access.log"
        assert os.path.isfile(log_file), (
            f"File '{log_file}' does not exist. "
            "The access log file must be present before starting the task."
        )

    def test_access_log_is_readable(self):
        """The access.log file must be readable."""
        log_file = "/home/user/logs/access.log"
        assert os.access(log_file, os.R_OK), (
            f"File '{log_file}' is not readable. "
            "The access log file must be readable to perform the analysis."
        )

    def test_access_log_is_not_empty(self):
        """The access.log file must not be empty."""
        log_file = "/home/user/logs/access.log"
        file_size = os.path.getsize(log_file)
        assert file_size > 0, (
            f"File '{log_file}' is empty (size: {file_size} bytes). "
            "The access log file must contain log entries."
        )

    def test_access_log_has_expected_line_count(self):
        """The access.log file should have exactly 15 log entries."""
        log_file = "/home/user/logs/access.log"
        with open(log_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        assert len(lines) == 15, (
            f"File '{log_file}' has {len(lines)} non-empty lines, expected 15. "
            "The access log file must contain exactly 15 log entries."
        )

    def test_access_log_contains_expected_ips(self):
        """The access.log file should contain the expected IP addresses."""
        log_file = "/home/user/logs/access.log"
        expected_ips = {"192.168.1.100", "10.0.0.55", "172.16.0.25", "203.0.113.50"}

        with open(log_file, 'r') as f:
            content = f.read()

        found_ips = set()
        for ip in expected_ips:
            if ip in content:
                found_ips.add(ip)

        missing_ips = expected_ips - found_ips
        assert not missing_ips, (
            f"File '{log_file}' is missing expected IP addresses: {missing_ips}. "
            "The access log file must contain all expected IP addresses."
        )

    def test_access_log_has_apache_format(self):
        """The access.log file should be in Apache Combined Log Format."""
        log_file = "/home/user/logs/access.log"

        with open(log_file, 'r') as f:
            first_line = f.readline().strip()

        # Check for typical Apache log format elements
        assert '"GET' in first_line or '"POST' in first_line or '"DELETE' in first_line, (
            f"First line of '{log_file}' does not appear to be in Apache log format. "
            "Expected HTTP method (GET/POST/DELETE) in quotes."
        )

        assert 'HTTP/1.1"' in first_line, (
            f"First line of '{log_file}' does not appear to be in Apache log format. "
            "Expected 'HTTP/1.1' protocol indicator."
        )

    def test_access_log_contains_error_codes(self):
        """The access.log file should contain some 4xx and 5xx error codes."""
        log_file = "/home/user/logs/access.log"

        with open(log_file, 'r') as f:
            content = f.read()

        has_403 = '" 403 ' in content
        has_404 = '" 404 ' in content
        has_500 = '" 500 ' in content

        assert has_403, (
            f"File '{log_file}' does not contain any 403 status codes. "
            "The access log should contain 403 Forbidden errors."
        )

        assert has_404, (
            f"File '{log_file}' does not contain any 404 status codes. "
            "The access log should contain 404 Not Found errors."
        )

        assert has_500, (
            f"File '{log_file}' does not contain any 500 status codes. "
            "The access log should contain 500 Internal Server Error."
        )


class TestOutputFilesDoNotExist:
    """Test that output files do not exist yet (agent should create them)."""

    def test_ip_counts_does_not_exist(self):
        """The ip_counts.txt output file should not exist initially."""
        output_file = "/home/user/reports/ip_counts.txt"
        # If reports dir doesn't exist, file definitely doesn't exist
        if os.path.isdir("/home/user/reports"):
            assert not os.path.exists(output_file), (
                f"Output file '{output_file}' already exists. "
                "This file should be created by the agent during the task."
            )

    def test_errors_csv_does_not_exist(self):
        """The errors.csv output file should not exist initially."""
        output_file = "/home/user/reports/errors.csv"
        if os.path.isdir("/home/user/reports"):
            assert not os.path.exists(output_file), (
                f"Output file '{output_file}' already exists. "
                "This file should be created by the agent during the task."
            )

    def test_total_bandwidth_does_not_exist(self):
        """The total_bandwidth.txt output file should not exist initially."""
        output_file = "/home/user/reports/total_bandwidth.txt"
        if os.path.isdir("/home/user/reports"):
            assert not os.path.exists(output_file), (
                f"Output file '{output_file}' already exists. "
                "This file should be created by the agent during the task."
            )

    def test_top_paths_does_not_exist(self):
        """The top_paths.txt output file should not exist initially."""
        output_file = "/home/user/reports/top_paths.txt"
        if os.path.isdir("/home/user/reports"):
            assert not os.path.exists(output_file), (
                f"Output file '{output_file}' already exists. "
                "This file should be created by the agent during the task."
            )

    def test_summary_does_not_exist(self):
        """The summary.txt output file should not exist initially."""
        output_file = "/home/user/reports/summary.txt"
        if os.path.isdir("/home/user/reports"):
            assert not os.path.exists(output_file), (
                f"Output file '{output_file}' already exists. "
                "This file should be created by the agent during the task."
            )
