# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student
has completed the vulnerability filtering task.
"""

import os
import pytest


class TestFinalState:
    """Test the final state of the filesystem after task execution."""

    # Expected content for critical_high_vulns.txt
    EXPECTED_FILTERED_LINES = [
        "[2024-01-15 09:23:52] [CRITICAL] [192.168.1.10] [CVE-2024-0012] - Remote code execution in web application",
        "[2024-01-15 09:24:15] [HIGH] [192.168.1.10] [CVE-2024-1086] - SQL injection vulnerability in login form",
        "[2024-01-15 09:24:45] [CRITICAL] [192.168.1.15] [CVE-2024-21887] - Authentication bypass in admin panel",
        "[2024-01-15 09:25:18] [HIGH] [192.168.1.15] [CVE-2024-20931] - Privilege escalation via misconfigured sudo",
        "[2024-01-15 09:25:50] [HIGH] [192.168.1.20] [CVE-2024-23897] - Arbitrary file read vulnerability",
        "[2024-01-15 09:26:22] [CRITICAL] [192.168.1.20] [CVE-2024-3400] - Command injection in firewall management",
    ]

    # Expected content for vuln_summary.txt
    EXPECTED_SUMMARY_LINES = [
        "CRITICAL: 3",
        "HIGH: 3",
    ]

    def test_pentest_directory_still_exists(self):
        """Verify that the /home/user/pentest directory still exists."""
        pentest_dir = "/home/user/pentest"
        assert os.path.isdir(pentest_dir), (
            f"Directory '{pentest_dir}' does not exist. "
            "The pentest directory should still be present after task completion."
        )

    def test_scan_results_log_still_exists(self):
        """Verify that the original scan_results.log file still exists."""
        log_file = "/home/user/pentest/scan_results.log"
        assert os.path.isfile(log_file), (
            f"File '{log_file}' does not exist. "
            "The original scan results log file should not be deleted."
        )

    def test_critical_high_vulns_file_exists(self):
        """Verify that the critical_high_vulns.txt file was created."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        assert os.path.isfile(output_file), (
            f"File '{output_file}' does not exist. "
            "The filtered vulnerabilities file must be created at this exact path."
        )

    def test_critical_high_vulns_file_is_readable(self):
        """Verify that the critical_high_vulns.txt file is readable."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        assert os.access(output_file, os.R_OK), (
            f"File '{output_file}' is not readable. "
            "The filtered vulnerabilities file must be readable."
        )

    def test_critical_high_vulns_has_exactly_six_lines(self):
        """Verify that the critical_high_vulns.txt file has exactly 6 lines."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines()]

        # Filter out empty lines for counting actual content
        non_empty_lines = [line for line in lines if line.strip()]

        assert len(non_empty_lines) == 6, (
            f"File '{output_file}' has {len(non_empty_lines)} non-empty lines, expected exactly 6 lines. "
            "The filtered file should contain exactly 6 vulnerability entries (3 CRITICAL + 3 HIGH)."
        )

    def test_critical_high_vulns_contains_only_critical_and_high(self):
        """Verify that the critical_high_vulns.txt file contains only CRITICAL and HIGH entries."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            assert '[CRITICAL]' in line or '[HIGH]' in line, (
                f"Line {i} in '{output_file}' does not contain [CRITICAL] or [HIGH]: '{line}'. "
                "Only CRITICAL and HIGH severity entries should be in the filtered file."
            )

        # Also verify no other severities are present
        for line in lines:
            assert '[INFO]' not in line, (
                f"File '{output_file}' contains INFO severity entry which should be filtered out."
            )
            assert '[LOW]' not in line, (
                f"File '{output_file}' contains LOW severity entry which should be filtered out."
            )
            assert '[MEDIUM]' not in line, (
                f"File '{output_file}' contains MEDIUM severity entry which should be filtered out."
            )

    def test_critical_high_vulns_exact_content(self):
        """Verify that the critical_high_vulns.txt file has the exact expected content."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        assert len(lines) == len(self.EXPECTED_FILTERED_LINES), (
            f"File '{output_file}' has {len(lines)} lines, expected {len(self.EXPECTED_FILTERED_LINES)}."
        )

        for i, (actual, expected) in enumerate(zip(lines, self.EXPECTED_FILTERED_LINES), 1):
            assert actual == expected, (
                f"Line {i} in '{output_file}' does not match expected content.\n"
                f"Expected: '{expected}'\n"
                f"Actual:   '{actual}'"
            )

    def test_critical_high_vulns_preserves_order(self):
        """Verify that the critical_high_vulns.txt file preserves the original log ordering."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        # Extract timestamps and verify they are in ascending order
        import re
        timestamps = []
        for line in lines:
            match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
            if match:
                timestamps.append(match.group(1))

        assert timestamps == sorted(timestamps), (
            f"Lines in '{output_file}' are not in chronological order. "
            "The filtered output must preserve the original log file ordering."
        )

    def test_vuln_summary_file_exists(self):
        """Verify that the vuln_summary.txt file was created."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        assert os.path.isfile(summary_file), (
            f"File '{summary_file}' does not exist. "
            "The vulnerability summary file must be created at this exact path."
        )

    def test_vuln_summary_file_is_readable(self):
        """Verify that the vuln_summary.txt file is readable."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        assert os.access(summary_file, os.R_OK), (
            f"File '{summary_file}' is not readable. "
            "The vulnerability summary file must be readable."
        )

    def test_vuln_summary_has_exactly_two_lines(self):
        """Verify that the vuln_summary.txt file has exactly 2 lines."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        with open(summary_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        assert len(lines) == 2, (
            f"File '{summary_file}' has {len(lines)} non-empty lines, expected exactly 2 lines. "
            "The summary file should contain exactly two lines: 'CRITICAL: X' and 'HIGH: Y'."
        )

    def test_vuln_summary_first_line_critical_count(self):
        """Verify that the first line of vuln_summary.txt shows CRITICAL: 3."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        with open(summary_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, (
            f"File '{summary_file}' is empty or has no content."
        )

        assert lines[0] == "CRITICAL: 3", (
            f"First line of '{summary_file}' is '{lines[0]}', expected 'CRITICAL: 3'. "
            "The first line must show the count of CRITICAL severity entries."
        )

    def test_vuln_summary_second_line_high_count(self):
        """Verify that the second line of vuln_summary.txt shows HIGH: 3."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        with open(summary_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        assert len(lines) >= 2, (
            f"File '{summary_file}' has fewer than 2 lines."
        )

        assert lines[1] == "HIGH: 3", (
            f"Second line of '{summary_file}' is '{lines[1]}', expected 'HIGH: 3'. "
            "The second line must show the count of HIGH severity entries."
        )

    def test_vuln_summary_exact_content(self):
        """Verify that the vuln_summary.txt file has the exact expected content."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        with open(summary_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        assert lines == self.EXPECTED_SUMMARY_LINES, (
            f"Content of '{summary_file}' does not match expected.\n"
            f"Expected: {self.EXPECTED_SUMMARY_LINES}\n"
            f"Actual:   {lines}"
        )

    def test_vuln_summary_no_extra_whitespace(self):
        """Verify that the vuln_summary.txt file has no extra blank lines."""
        summary_file = "/home/user/pentest/vuln_summary.txt"
        with open(summary_file, 'r') as f:
            content = f.read()

        # Check that the file contains exactly what we expect with minimal formatting
        # Allow for optional trailing newline
        expected_content_options = [
            "CRITICAL: 3\nHIGH: 3",
            "CRITICAL: 3\nHIGH: 3\n",
        ]

        assert content in expected_content_options, (
            f"File '{summary_file}' has unexpected formatting or extra whitespace.\n"
            f"Expected content: 'CRITICAL: 3\\nHIGH: 3' (with optional trailing newline)\n"
            f"Actual content (repr): {repr(content)}"
        )

    def test_critical_count_is_correct(self):
        """Verify that there are exactly 3 CRITICAL entries in the filtered file."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            content = f.read()

        critical_count = content.count('[CRITICAL]')
        assert critical_count == 3, (
            f"File '{output_file}' contains {critical_count} CRITICAL entries, expected 3."
        )

    def test_high_count_is_correct(self):
        """Verify that there are exactly 3 HIGH entries in the filtered file."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            content = f.read()

        high_count = content.count('[HIGH]')
        assert high_count == 3, (
            f"File '{output_file}' contains {high_count} HIGH entries, expected 3."
        )

    def test_filtered_file_contains_expected_cves(self):
        """Verify that the filtered file contains all expected CVE identifiers."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            content = f.read()

        expected_cves = [
            'CVE-2024-0012',
            'CVE-2024-1086',
            'CVE-2024-21887',
            'CVE-2024-20931',
            'CVE-2024-23897',
            'CVE-2024-3400',
        ]

        for cve in expected_cves:
            assert cve in content, (
                f"File '{output_file}' does not contain expected CVE '{cve}'. "
                "All CRITICAL and HIGH severity CVEs must be present in the filtered output."
            )

    def test_filtered_file_does_not_contain_excluded_cves(self):
        """Verify that the filtered file does not contain LOW/MEDIUM/INFO entries."""
        output_file = "/home/user/pentest/critical_high_vulns.txt"
        with open(output_file, 'r') as f:
            content = f.read()

        excluded_identifiers = [
            'SCAN-001',  # INFO
            'CVE-2023-1234',  # LOW
            'CVE-2023-5678',  # MEDIUM
            'SCAN-002',  # INFO
            'CVE-2022-9999',  # LOW
            'CVE-2023-4567',  # MEDIUM
            'SCAN-003',  # INFO
        ]

        for identifier in excluded_identifiers:
            assert identifier not in content, (
                f"File '{output_file}' contains '{identifier}' which should have been filtered out. "
                "Only CRITICAL and HIGH severity entries should be in the filtered file."
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
