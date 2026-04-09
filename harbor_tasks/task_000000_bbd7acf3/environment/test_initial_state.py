# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
BEFORE the student performs the git repository setup task.
"""

import os
import pytest


class TestInitialState:
    """Test that the initial state is correct before the task is performed."""

    def test_home_directory_exists(self):
        """Verify the home directory exists."""
        home_dir = "/home/user"
        assert os.path.isdir(home_dir), f"Home directory {home_dir} does not exist"

    def test_config_tracking_directory_does_not_exist(self):
        """Verify the config-tracking directory does NOT exist yet (student needs to create it)."""
        config_dir = "/home/user/config-tracking"
        assert not os.path.exists(config_dir), (
            f"Directory {config_dir} already exists but should not. "
            "The student is expected to create this directory as part of the task."
        )

    def test_git_directory_does_not_exist(self):
        """Verify the .git directory does NOT exist yet (student needs to initialize it)."""
        git_dir = "/home/user/config-tracking/.git"
        assert not os.path.exists(git_dir), (
            f"Git directory {git_dir} already exists but should not. "
            "The student is expected to initialize the git repository as part of the task."
        )

    def test_app_conf_does_not_exist(self):
        """Verify the app.conf file does NOT exist yet (student needs to create it)."""
        app_conf = "/home/user/config-tracking/app.conf"
        assert not os.path.exists(app_conf), (
            f"Configuration file {app_conf} already exists but should not. "
            "The student is expected to create this file as part of the task."
        )

    def test_setup_log_does_not_exist(self):
        """Verify the setup.log file does NOT exist yet (student needs to create it)."""
        setup_log = "/home/user/config-tracking/setup.log"
        assert not os.path.exists(setup_log), (
            f"Log file {setup_log} already exists but should not. "
            "The student is expected to create this file as part of the task."
        )

    def test_git_command_available(self):
        """Verify that git is installed and available."""
        # Check if git executable exists in common locations or is in PATH
        git_in_path = os.system("which git > /dev/null 2>&1") == 0
        assert git_in_path, (
            "Git command is not available in PATH. "
            "Git must be installed for the student to complete this task."
        )

    def test_home_directory_is_writable(self):
        """Verify the home directory is writable so student can create subdirectories."""
        home_dir = "/home/user"
        assert os.access(home_dir, os.W_OK), (
            f"Home directory {home_dir} is not writable. "
            "The student needs write access to create the config-tracking directory."
        )
