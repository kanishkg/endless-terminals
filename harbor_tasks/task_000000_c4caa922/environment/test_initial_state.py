# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the CSV to JSON conversion task.
"""

import os
import subprocess
import pytest


class TestInitialState:
    """Test the initial state before the task is performed."""

    def test_backups_directory_exists(self):
        """Verify /home/user/backups/ directory exists."""
        backups_dir = "/home/user/backups"
        assert os.path.isdir(backups_dir), (
            f"Directory {backups_dir} does not exist. "
            "The backups directory must exist before performing the task."
        )

    def test_csv_file_exists(self):
        """Verify the source CSV file exists."""
        csv_path = "/home/user/backups/users_20240115.csv"
        assert os.path.isfile(csv_path), (
            f"CSV file {csv_path} does not exist. "
            "The source CSV file must exist before performing the task."
        )

    def test_csv_file_is_readable(self):
        """Verify the CSV file is readable."""
        csv_path = "/home/user/backups/users_20240115.csv"
        assert os.access(csv_path, os.R_OK), (
            f"CSV file {csv_path} is not readable. "
            "The source CSV file must be readable."
        )

    def test_csv_file_has_correct_headers(self):
        """Verify the CSV file has the expected headers."""
        csv_path = "/home/user/backups/users_20240115.csv"
        with open(csv_path, 'r') as f:
            header_line = f.readline().strip()

        expected_headers = "id,name,email,created_at"
        assert header_line == expected_headers, (
            f"CSV file has unexpected headers. "
            f"Expected: '{expected_headers}', Got: '{header_line}'"
        )

    def test_csv_file_has_three_data_rows(self):
        """Verify the CSV file has exactly 3 data rows (plus header)."""
        csv_path = "/home/user/backups/users_20240115.csv"
        with open(csv_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        # Should have 1 header + 3 data rows = 4 lines
        assert len(lines) == 4, (
            f"CSV file should have 4 lines (1 header + 3 data rows), "
            f"but has {len(lines)} lines."
        )

    def test_csv_file_content_matches_expected(self):
        """Verify the CSV file content matches expected data."""
        csv_path = "/home/user/backups/users_20240115.csv"
        with open(csv_path, 'r') as f:
            content = f.read()

        expected_content = """id,name,email,created_at
1,Alice Chen,alice@example.com,2023-06-12
2,Bob Martinez,bob@example.com,2023-08-24
3,Carol Smith,carol@example.com,2024-01-03"""

        # Normalize line endings and whitespace
        content_normalized = content.strip()
        expected_normalized = expected_content.strip()

        assert content_normalized == expected_normalized, (
            f"CSV file content does not match expected. "
            f"Expected:\n{expected_normalized}\n\nGot:\n{content_normalized}"
        )

    def test_restore_directory_exists(self):
        """Verify /home/user/restore/ directory exists."""
        restore_dir = "/home/user/restore"
        assert os.path.isdir(restore_dir), (
            f"Directory {restore_dir} does not exist. "
            "The restore directory must exist before performing the task."
        )

    def test_restore_directory_is_writable(self):
        """Verify the restore directory is writable."""
        restore_dir = "/home/user/restore"
        assert os.access(restore_dir, os.W_OK), (
            f"Directory {restore_dir} is not writable. "
            "The restore directory must be writable."
        )

    def test_restore_directory_is_empty(self):
        """Verify the restore directory is empty."""
        restore_dir = "/home/user/restore"
        contents = os.listdir(restore_dir)
        assert len(contents) == 0, (
            f"Directory {restore_dir} should be empty but contains: {contents}"
        )

    def test_python3_available(self):
        """Verify Python 3 is available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python 3 is not available. "
            f"Error: {result.stderr}"
        )

    def test_python3_json_module_available(self):
        """Verify Python 3 json module is available."""
        result = subprocess.run(
            ["python3", "-c", "import json; print('ok')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python 3 json module is not available. "
            f"Error: {result.stderr}"
        )

    def test_python3_csv_module_available(self):
        """Verify Python 3 csv module is available."""
        result = subprocess.run(
            ["python3", "-c", "import csv; print('ok')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python 3 csv module is not available. "
            f"Error: {result.stderr}"
        )

    def test_jq_installed(self):
        """Verify jq is installed."""
        result = subprocess.run(
            ["which", "jq"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq is not installed. "
            "jq should be available for this task."
        )

    def test_csvkit_not_installed(self):
        """Verify csvkit is NOT installed (as per task specification)."""
        result = subprocess.run(
            ["which", "csvjson"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, (
            "csvkit appears to be installed (csvjson found). "
            "According to task specification, csvkit should NOT be installed."
        )
