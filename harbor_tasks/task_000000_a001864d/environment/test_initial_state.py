# test_initial_state.py
"""
Tests to validate the initial state of the system before the student
performs the task of commenting out the log rotation cron job.
"""

import os
import pytest


CRON_FILE_PATH = "/etc/cron.d/logrotate-daily"


class TestInitialState:
    """Tests to verify the system is in the expected initial state."""

    def test_cron_file_exists(self):
        """Verify that /etc/cron.d/logrotate-daily exists."""
        assert os.path.exists(CRON_FILE_PATH), (
            f"File {CRON_FILE_PATH} does not exist. "
            "The cron file must exist for the task to be performed."
        )

    def test_cron_file_is_regular_file(self):
        """Verify that /etc/cron.d/logrotate-daily is a regular file."""
        assert os.path.isfile(CRON_FILE_PATH), (
            f"{CRON_FILE_PATH} exists but is not a regular file. "
            "It must be a regular file for the task."
        )

    def test_cron_file_is_writable(self):
        """Verify that the cron file is writable by the current user."""
        assert os.access(CRON_FILE_PATH, os.W_OK), (
            f"{CRON_FILE_PATH} is not writable by the current user. "
            "The agent user must have write access to modify the file."
        )

    def test_cron_file_contains_daily_log_rotation_comment(self):
        """Verify the file contains the '# Daily log rotation' comment."""
        with open(CRON_FILE_PATH, 'r') as f:
            content = f.read()

        assert "# Daily log rotation" in content, (
            f"{CRON_FILE_PATH} does not contain the expected comment "
            "'# Daily log rotation'. The file may not be in the expected initial state."
        )

    def test_cron_file_contains_uncommented_logrotate_line(self):
        """Verify the file contains an uncommented logrotate cron line."""
        with open(CRON_FILE_PATH, 'r') as f:
            lines = f.readlines()

        # Look for a line that starts with "0 2" (the cron schedule)
        # and is not commented out
        uncommented_cron_lines = [
            line for line in lines 
            if line.strip().startswith("0 2") and "logrotate" in line
        ]

        assert len(uncommented_cron_lines) > 0, (
            f"{CRON_FILE_PATH} does not contain an uncommented cron line "
            "starting with '0 2' that includes 'logrotate'. "
            "The initial state should have the cron job active (not commented out)."
        )

    def test_cron_file_contains_logrotate_command(self):
        """Verify the file contains the logrotate command."""
        with open(CRON_FILE_PATH, 'r') as f:
            content = f.read()

        assert "logrotate" in content, (
            f"{CRON_FILE_PATH} does not contain 'logrotate'. "
            "The file should contain the logrotate command."
        )

    def test_cron_file_has_expected_content_structure(self):
        """Verify the file has the expected initial content structure."""
        with open(CRON_FILE_PATH, 'r') as f:
            content = f.read()

        # Check for the expected cron schedule pattern
        assert "0 2 * * *" in content, (
            f"{CRON_FILE_PATH} does not contain the expected cron schedule "
            "'0 2 * * *' (2am daily). The file may not be in the expected initial state."
        )

        assert "root" in content, (
            f"{CRON_FILE_PATH} does not contain 'root' as the user. "
            "The cron job should run as root."
        )

        assert "/usr/sbin/logrotate" in content or "logrotate" in content, (
            f"{CRON_FILE_PATH} does not contain the logrotate command path. "
            "The file should contain the logrotate command."
        )

    def test_cron_directory_exists(self):
        """Verify that /etc/cron.d/ directory exists."""
        cron_dir = "/etc/cron.d"
        assert os.path.isdir(cron_dir), (
            f"Directory {cron_dir} does not exist. "
            "The cron.d directory must exist for cron files."
        )
