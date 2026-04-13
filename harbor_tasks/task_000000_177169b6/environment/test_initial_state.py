# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
performs the vulnerability filtering task.
"""

import os
import pytest


class TestInitialState:
    """Test the initial state of the filesystem before task execution."""

    def test_pentest_directory_exists(self):
        """Verify that the /home/user/pentest directory exists."""
        pentest_dir = "/home/user/pentest"
        assert os.path.isdir(pentest_dir), (
            f"Directory '{pentest_dir}' does not exist. "
            "The pentest directory must be created before starting the task."
        )

    def test_pentest_directory_is_writable(self):
        """Verify that the /home/user/pentest directory is writable."""
        pentest_dir = "/home/user/pentest"
        assert os.access(pentest_dir, os.W_OK), (
            f"Directory '{pentest_dir}' is not writable. "
            "The user must have write permissions to the pentest directory."
        )

    def test_scan_results_log_exists(self):
        """Verify that the scan_results.log file exists."""
        log_file = "/home/user/pentest/scan_results.log"
        assert os.path.isfile(log_file), (
            f"File '{log_file}' does not exist. "
            "The scan results log file must be present before starting the task."
        )

    def test_scan_results_log_is_readable(self):
        """Verify that the scan_results.log file is readable."""
        log_file = "/home/user/pentest/scan_results.log"
        assert os.access(log_file, os.R_OK), (
            f"File '{log_file}' is not readable. "
            "The user must have read permissions on the scan results log file."
        )

    def test_scan_results_log_has_content(self):
        """Verify that the scan_results.log file is not empty."""
        log_file = "/home/user/pentest/scan_results.log"
        assert os.path.getsize(log_file) > 0, (
            f"File '{log_file}' is empty. "
            "The scan results log file must contain log entries."
        )

    def test_scan_results_log_has_expected_line_count(self):
        """Verify that the scan_results.log file has the expected number of lines."""
        log_file = "/home/user/pentest/scan_results.log"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 13, (
            f"File '{log_file}' has {len(lines)} lines, expected 13 lines. "
            "The scan results log file must contain exactly 13 log entries."
        )

    def test_scan_results_log_contains_critical_entries(self):
        """Verify that the scan_results.log file contains CRITICAL severity entries."""
        log_file = "/home/user/pentest/scan_results.log"
        with open(log_file, 'r') as f:
            content = f.read()
        critical_count = content.count('[CRITICAL]')
        assert critical_count == 3, (
            f"File '{log_file}' contains {critical_count} CRITICAL entries, expected 3. "
            "The scan results log file must contain exactly 3 CRITICAL severity entries."
        )

    def test_scan_results_log_contains_high_entries(self):
        """Verify that the scan_results.log file contains HIGH severity entries."""
        log_file = "/home/user/pentest/scan_results.log"
        with open(log_file, 'r') as f:
            content = f.read()
        high_count = content.count('[HIGH]')
        assert high_count == 3, (
            f"File '{log_file}' contains {high_count} HIGH entries, expected 3. "
            "The scan results log file must contain exactly 3 HIGH severity entries."
        )

    def test_scan_results_log_contains_expected_severities(self):
        """Verify that the scan_results.log file contains all expected severity levels."""
        log_file = "/home/user/pentest/scan_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        expected_severities = ['[INFO]', '[LOW]', '[MEDIUM]', '[HIGH]', '[CRITICAL]']
        for severity in expected_severities:
            assert severity in content, (
                f"File '{log_file}' does not contain {severity} entries. "
                f"The scan results log file must contain entries with {severity} severity."
            )

    def test_scan_results_log_format(self):
        """Verify that the scan_results.log file entries follow the expected format."""
        log_file = "/home/user/pentest/scan_results.log"
        import re

        # Expected format: [TIMESTAMP] [SEVERITY] [TARGET_IP] [VULN_ID] - Description
        pattern = r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[(INFO|LOW|MEDIUM|HIGH|CRITICAL)\] \[\d+\.\d+\.\d+\.\d+\] \[[A-Z0-9-]+\] - .+$'

        with open(log_file, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            line = line.rstrip('\n')
            assert re.match(pattern, line), (
                f"Line {i} in '{log_file}' does not match expected format: '{line}'. "
                "Each line should follow: [TIMESTAMP] [SEVERITY] [TARGET_IP] [VULN_ID] - Description"
            )

    def test_output_file_does_not_exist(self):
        """Verify that the output file critical_high_vulns.txt does not exist yet."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        # This is a soft check - the file shouldn't exist before the task
        # but we don't fail if it does, as the task might be re-run
        if os.path.exists(output_file):
            pytest.skip(
                f"Output file '{output_file}' already exists. "
                "This may indicate the task has already been attempted."
            )

    def test_summary_file_does_not_exist(self):
        """Verify that the summary file vuln_summary.txt does not exist yet."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        # This is a soft check - the file shouldn't exist before the task
        # but we don't fail if it does, as the task might be re-run
        if os.path.exists(summary_file):
            pytest.skip(
                f"Summary file '{summary_file}' already exists. "
                "This may indicate the task has already been attempted."
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
