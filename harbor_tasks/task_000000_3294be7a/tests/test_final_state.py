# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has completed the log analysis task.
"""

import pytest
import os
import csv


class TestReportsDirectoryExists:
    """Test that the reports directory was created."""

    def test_reports_directory_exists(self):
        """The /home/user/reports/ directory must exist after task completion."""
        reports_dir = "/home/user/reports"
        assert os.path.isdir(reports_dir), (
            f"Directory '{reports_dir}' does not exist. "
            "The agent should have created this directory for output files."
        )


class TestIpCountsFile:
    """Test the ip_counts.txt output file."""

    def test_ip_counts_file_exists(self):
        """The ip_counts.txt file must exist."""
        output_file = "/home/user/reports/ip_counts.txt"
        assert os.path.isfile(output_file), (
            f"File '{output_file}' does not exist. "
            "The agent should have created this file with IP address counts."
        )

    def test_ip_counts_content(self):
        """The ip_counts.txt file must have correct content."""
        output_file = "/home/user/reports/ip_counts.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        expected_lines = [
            "5 192.168.1.100",
            "4 10.0.0.55",
            "3 172.16.0.25",
            "3 203.0.113.50"
        ]

        assert len(lines) == 4, (
            f"File '{output_file}' has {len(lines)} lines, expected 4. "
            f"Found lines: {lines}"
        )

        # Check first two lines exactly (order matters for descending sort)
        assert lines[0] == "5 192.168.1.100", (
            f"First line should be '5 192.168.1.100', got '{lines[0]}'. "
            "IP with highest count should be first."
        )

        assert lines[1] == "4 10.0.0.55", (
            f"Second line should be '4 10.0.0.55', got '{lines[1]}'."
        )

        # Lines 3 and 4 both have count 3, so order between them may vary
        remaining_lines = set(lines[2:4])
        expected_remaining = {"3 172.16.0.25", "3 203.0.113.50"}

        assert remaining_lines == expected_remaining, (
            f"Lines 3-4 should be {expected_remaining}, got {remaining_lines}. "
            "Both IPs with count 3 should be present."
        )


class TestErrorsCsvFile:
    """Test the errors.csv output file."""

    def test_errors_csv_file_exists(self):
        """The errors.csv file must exist."""
        output_file = "/home/user/reports/errors.csv"
        assert os.path.isfile(output_file), (
            f"File '{output_file}' does not exist. "
            "The agent should have created this CSV file with error requests."
        )

    def test_errors_csv_has_header(self):
        """The errors.csv file must have the correct header row."""
        output_file = "/home/user/reports/errors.csv"

        with open(output_file, 'r') as f:
            first_line = f.readline().strip()

        assert first_line == "ip,status,path", (
            f"Header row should be 'ip,status,path', got '{first_line}'. "
            "The CSV must have a proper header row."
        )

    def test_errors_csv_content(self):
        """The errors.csv file must contain all error requests."""
        output_file = "/home/user/reports/errors.csv"

        with open(output_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 4, (
            f"File '{output_file}' has {len(rows)} data rows, expected 4. "
            "There should be 4 error requests (4xx and 5xx status codes)."
        )

        # Expected error entries (order may vary)
        expected_errors = {
            ("192.168.1.100", "403", "/admin/login"),
            ("10.0.0.55", "404", "/api/missing"),
            ("203.0.113.50", "500", "/broken"),
            ("192.168.1.100", "403", "/api/admin"),
        }

        found_errors = set()
        for row in rows:
            ip = row.get('ip', '').strip()
            status = row.get('status', '').strip()
            path = row.get('path', '').strip()
            found_errors.add((ip, status, path))

        assert found_errors == expected_errors, (
            f"Error entries don't match expected. "
            f"Expected: {expected_errors}, "
            f"Found: {found_errors}"
        )


class TestTotalBandwidthFile:
    """Test the total_bandwidth.txt output file."""

    def test_total_bandwidth_file_exists(self):
        """The total_bandwidth.txt file must exist."""
        output_file = "/home/user/reports/total_bandwidth.txt"
        assert os.path.isfile(output_file), (
            f"File '{output_file}' does not exist. "
            "The agent should have created this file with total bandwidth."
        )

    def test_total_bandwidth_content(self):
        """The total_bandwidth.txt file must contain the correct value."""
        output_file = "/home/user/reports/total_bandwidth.txt"

        with open(output_file, 'r') as f:
            content = f.read().strip()

        assert content == "21386", (
            f"Total bandwidth should be '21386', got '{content}'. "
            "The file should contain just the integer byte count with no formatting."
        )


class TestTopPathsFile:
    """Test the top_paths.txt output file."""

    def test_top_paths_file_exists(self):
        """The top_paths.txt file must exist."""
        output_file = "/home/user/reports/top_paths.txt"
        assert os.path.isfile(output_file), (
            f"File '{output_file}' does not exist. "
            "The agent should have created this file with top 5 paths."
        )

    def test_top_paths_has_five_lines(self):
        """The top_paths.txt file must have exactly 5 lines."""
        output_file = "/home/user/reports/top_paths.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        assert len(lines) == 5, (
            f"File '{output_file}' has {len(lines)} lines, expected 5. "
            "The file should contain exactly the top 5 most requested paths."
        )

    def test_top_paths_content(self):
        """The top_paths.txt file must have correct content."""
        output_file = "/home/user/reports/top_paths.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        # Parse the lines into (count, path) tuples
        parsed_lines = []
        for line in lines:
            parts = line.split(' ', 1)
            if len(parts) == 2:
                parsed_lines.append((int(parts[0]), parts[1]))

        # First two entries should have count 3 (index.html and products)
        top_two_counts = [p[0] for p in parsed_lines[:2]]
        assert all(c == 3 for c in top_two_counts), (
            f"Top 2 paths should have count 3, got counts {top_two_counts}."
        )

        top_two_paths = {p[1] for p in parsed_lines[:2]}
        expected_top_two = {"/index.html", "/products"}
        assert top_two_paths == expected_top_two, (
            f"Top 2 paths should be {expected_top_two}, got {top_two_paths}."
        )

        # Next two entries should have count 2 (api/users and style.css)
        next_two_counts = [p[0] for p in parsed_lines[2:4]]
        assert all(c == 2 for c in next_two_counts), (
            f"Paths 3-4 should have count 2, got counts {next_two_counts}."
        )

        next_two_paths = {p[1] for p in parsed_lines[2:4]}
        expected_next_two = {"/api/users", "/style.css"}
        assert next_two_paths == expected_next_two, (
            f"Paths 3-4 should be {expected_next_two}, got {next_two_paths}."
        )

        # Fifth entry should have count 1
        assert parsed_lines[4][0] == 1, (
            f"5th path should have count 1, got {parsed_lines[4][0]}."
        )

        # The 5th path could be any of the paths with count 1
        # Based on the expected output, it should be /admin/login
        # But other paths with count 1 exist, so we check it's a valid path
        valid_count_1_paths = {"/admin/login", "/api/missing", "/broken", "/api/admin"}
        assert parsed_lines[4][1] in valid_count_1_paths or parsed_lines[4][1] == "/admin/login", (
            f"5th path should be a path with count 1, got '{parsed_lines[4][1]}'."
        )


class TestSummaryFile:
    """Test the summary.txt output file."""

    def test_summary_file_exists(self):
        """The summary.txt file must exist."""
        output_file = "/home/user/reports/summary.txt"
        assert os.path.isfile(output_file), (
            f"File '{output_file}' does not exist. "
            "The agent should have created this summary file."
        )

    def test_summary_has_four_lines(self):
        """The summary.txt file must have exactly 4 lines."""
        output_file = "/home/user/reports/summary.txt"

        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f]

        # Remove trailing empty lines
        while lines and lines[-1] == '':
            lines.pop()

        assert len(lines) == 4, (
            f"File '{output_file}' has {len(lines)} lines, expected 4. "
            f"Lines found: {lines}"
        )

    def test_summary_unique_ips_line(self):
        """The summary.txt must have correct 'Unique IPs' line."""
        output_file = "/home/user/reports/summary.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f]

        assert lines[0] == "Unique IPs: 4", (
            f"Line 1 should be 'Unique IPs: 4', got '{lines[0]}'."
        )

    def test_summary_total_requests_line(self):
        """The summary.txt must have correct 'Total Requests' line."""
        output_file = "/home/user/reports/summary.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f]

        assert lines[1] == "Total Requests: 15", (
            f"Line 2 should be 'Total Requests: 15', got '{lines[1]}'."
        )

    def test_summary_error_requests_line(self):
        """The summary.txt must have correct 'Error Requests' line."""
        output_file = "/home/user/reports/summary.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f]

        assert lines[2] == "Error Requests: 4", (
            f"Line 3 should be 'Error Requests: 4', got '{lines[2]}'."
        )

    def test_summary_total_bandwidth_line(self):
        """The summary.txt must have correct 'Total Bandwidth' line."""
        output_file = "/home/user/reports/summary.txt"

        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f]

        assert lines[3] == "Total Bandwidth: 21386 bytes", (
            f"Line 4 should be 'Total Bandwidth: 21386 bytes', got '{lines[3]}'."
        )


class TestAllFilesCreated:
    """Test that all required output files exist."""

    def test_all_output_files_exist(self):
        """All 5 output files must exist in the reports directory."""
        required_files = [
            "/home/user/reports/ip_counts.txt",
            "/home/user/reports/errors.csv",
            "/home/user/reports/total_bandwidth.txt",
            "/home/user/reports/top_paths.txt",
            "/home/user/reports/summary.txt",
        ]

        missing_files = []
        for filepath in required_files:
            if not os.path.isfile(filepath):
                missing_files.append(filepath)

        assert not missing_files, (
            f"The following required output files are missing: {missing_files}"
        )
