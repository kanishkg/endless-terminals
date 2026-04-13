# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student performs
the log analysis task.
"""

import os
import pytest


class TestServerLogsDirectory:
    """Tests for the /home/user/server_logs directory and its contents."""

    def test_server_logs_directory_exists(self):
        """The server_logs directory must exist."""
        path = "/home/user/server_logs"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The server_logs directory must be present for the task."
        )

    def test_access_log_2024_01_15_exists(self):
        """The access_2024_01_15.log file must exist."""
        path = "/home/user/server_logs/access_2024_01_15.log"
        assert os.path.isfile(path), (
            f"File {path} does not exist. "
            "This log file is required for the task."
        )

    def test_access_log_2024_01_15_content(self):
        """The access_2024_01_15.log file must have correct content."""
        path = "/home/user/server_logs/access_2024_01_15.log"
        with open(path, 'r') as f:
            content = f.read()

        # Check for expected log entries
        assert '192.168.1.100' in content, (
            f"File {path} is missing expected log entry with IP 192.168.1.100"
        )
        assert '192.168.1.101' in content, (
            f"File {path} is missing expected log entry with IP 192.168.1.101"
        )
        assert 'missing-page.html' in content, (
            f"File {path} is missing expected 404 entry for missing-page.html"
        )
        assert 'old-link.html' in content, (
            f"File {path} is missing expected 404 entry for old-link.html"
        )

    def test_access_log_2024_01_16_exists(self):
        """The access_2024_01_16.log file must exist."""
        path = "/home/user/server_logs/access_2024_01_16.log"
        assert os.path.isfile(path), (
            f"File {path} does not exist. "
            "This log file is required for the task."
        )

    def test_access_log_2024_01_16_content(self):
        """The access_2024_01_16.log file must have correct content."""
        path = "/home/user/server_logs/access_2024_01_16.log"
        with open(path, 'r') as f:
            content = f.read()

        # Check for expected log entries
        assert '10.0.0.50' in content, (
            f"File {path} is missing expected log entry with IP 10.0.0.50"
        )
        assert '10.0.0.51' in content, (
            f"File {path} is missing expected log entry with IP 10.0.0.51"
        )
        assert '/nonexistent' in content, (
            f"File {path} is missing expected 404 entry for /nonexistent"
        )
        assert ' 500 ' in content, (
            f"File {path} is missing expected 500 error entry"
        )

    def test_access_log_2024_01_17_exists(self):
        """The access_2024_01_17.log file must exist."""
        path = "/home/user/server_logs/access_2024_01_17.log"
        assert os.path.isfile(path), (
            f"File {path} does not exist. "
            "This log file is required for the task."
        )

    def test_access_log_2024_01_17_content(self):
        """The access_2024_01_17.log file must have correct content."""
        path = "/home/user/server_logs/access_2024_01_17.log"
        with open(path, 'r') as f:
            content = f.read()

        # Check for expected log entries
        assert '172.16.0.25' in content, (
            f"File {path} is missing expected log entry with IP 172.16.0.25"
        )
        assert '172.16.0.26' in content, (
            f"File {path} is missing expected log entry with IP 172.16.0.26"
        )
        assert '/deleted-resource' in content, (
            f"File {path} is missing expected 404 entry for /deleted-resource"
        )

    def test_notes_txt_exists(self):
        """The notes.txt file must exist (to test that non-.log files are ignored)."""
        path = "/home/user/server_logs/notes.txt"
        assert os.path.isfile(path), (
            f"File {path} does not exist. "
            "This file is needed to verify that non-.log files are not searched."
        )

    def test_notes_txt_content(self):
        """The notes.txt file must contain the expected content."""
        path = "/home/user/server_logs/notes.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert '404' in content, (
            f"File {path} should contain '404' text to test filtering of non-.log files"
        )

    def test_log_files_count(self):
        """There should be exactly 3 .log files in the server_logs directory."""
        path = "/home/user/server_logs"
        log_files = [f for f in os.listdir(path) if f.endswith('.log')]
        assert len(log_files) == 3, (
            f"Expected 3 .log files in {path}, but found {len(log_files)}: {log_files}"
        )


class TestExpected404Entries:
    """Tests to verify the log files contain the expected 404 entries."""

    def test_total_404_entries_in_logs(self):
        """There should be exactly 4 lines containing ' 404 ' across all .log files."""
        log_dir = "/home/user/server_logs"
        total_404_count = 0

        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(log_dir, filename)
                with open(filepath, 'r') as f:
                    for line in f:
                        if ' 404 ' in line:
                            total_404_count += 1

        assert total_404_count == 4, (
            f"Expected exactly 4 lines with ' 404 ' pattern across all .log files, "
            f"but found {total_404_count}"
        )

    def test_404_in_access_2024_01_15(self):
        """The access_2024_01_15.log should have exactly 2 lines with 404."""
        path = "/home/user/server_logs/access_2024_01_15.log"
        with open(path, 'r') as f:
            count = sum(1 for line in f if ' 404 ' in line)

        assert count == 2, (
            f"Expected 2 lines with ' 404 ' in {path}, but found {count}"
        )

    def test_404_in_access_2024_01_16(self):
        """The access_2024_01_16.log should have exactly 1 line with 404."""
        path = "/home/user/server_logs/access_2024_01_16.log"
        with open(path, 'r') as f:
            count = sum(1 for line in f if ' 404 ' in line)

        assert count == 1, (
            f"Expected 1 line with ' 404 ' in {path}, but found {count}"
        )

    def test_404_in_access_2024_01_17(self):
        """The access_2024_01_17.log should have exactly 1 line with 404."""
        path = "/home/user/server_logs/access_2024_01_17.log"
        with open(path, 'r') as f:
            count = sum(1 for line in f if ' 404 ' in line)

        assert count == 1, (
            f"Expected 1 line with ' 404 ' in {path}, but found {count}"
        )


class TestHomeDirectory:
    """Tests for the home directory structure."""

    def test_home_user_exists(self):
        """The /home/user directory must exist."""
        path = "/home/user"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The home directory must be present."
        )
