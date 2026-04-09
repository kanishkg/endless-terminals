# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
BEFORE the student performs the disk monitoring script creation task.

This verifies that the necessary directories and files do NOT exist yet,
since the student is expected to create everything from scratch.
"""

import pytest
import os
import subprocess


class TestInitialStateBeforeTask:
    """Test that the initial state is clean - no pre-existing task artifacts."""

    def test_home_user_directory_exists(self):
        """Verify the base home directory exists for the user."""
        home_dir = "/home/user"
        assert os.path.isdir(home_dir), (
            f"Home directory {home_dir} does not exist. "
            "The user's home directory must exist before starting the task."
        )

    def test_scripts_directory_does_not_exist(self):
        """Verify /home/user/scripts directory does NOT exist yet (student should create it)."""
        scripts_dir = "/home/user/scripts"
        assert not os.path.exists(scripts_dir), (
            f"Directory {scripts_dir} already exists but should not. "
            "The student is expected to create this directory as part of the task."
        )

    def test_logs_directory_does_not_exist(self):
        """Verify /home/user/logs directory does NOT exist yet (student should create it)."""
        logs_dir = "/home/user/logs"
        assert not os.path.exists(logs_dir), (
            f"Directory {logs_dir} already exists but should not. "
            "The student is expected to create this directory as part of the task."
        )

    def test_disk_monitor_script_does_not_exist(self):
        """Verify the disk_monitor.sh script does NOT exist yet."""
        script_path = "/home/user/scripts/disk_monitor.sh"
        assert not os.path.exists(script_path), (
            f"Script {script_path} already exists but should not. "
            "The student is expected to create this script as part of the task."
        )

    def test_disk_status_log_does_not_exist(self):
        """Verify the disk_status.log file does NOT exist yet."""
        log_path = "/home/user/logs/disk_status.log"
        assert not os.path.exists(log_path), (
            f"Log file {log_path} already exists but should not. "
            "The student is expected to create this file by running the script."
        )

    def test_df_command_available(self):
        """Verify the df command is available (required for the task)."""
        result = subprocess.run(
            ["which", "df"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "The 'df' command is not available on this system. "
            "This command is required for the disk monitoring script."
        )

    def test_date_command_available(self):
        """Verify the date command is available (required for the task)."""
        result = subprocess.run(
            ["which", "date"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "The 'date' command is not available on this system. "
            "This command is required for the disk monitoring script."
        )

    def test_bash_available(self):
        """Verify bash is available for shell scripting."""
        result = subprocess.run(
            ["which", "bash"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Bash shell is not available on this system. "
            "Bash is required for creating the shell script."
        )

    def test_user_has_write_permission_in_home(self):
        """Verify the user can write to their home directory."""
        home_dir = "/home/user"
        assert os.access(home_dir, os.W_OK), (
            f"User does not have write permission in {home_dir}. "
            "Write permission is required to create scripts and logs directories."
        )

    def test_root_filesystem_mounted(self):
        """Verify the root filesystem (/) is mounted and accessible."""
        result = subprocess.run(
            ["df", "/"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Unable to get disk usage for root filesystem (/). "
            "The root filesystem must be accessible for the monitoring script."
        )
        # Verify we get meaningful output
        assert "/" in result.stdout, (
            "The df command did not return information about the root filesystem. "
            "The root filesystem (/) must be properly mounted."
        )
