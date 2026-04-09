# test_final_state.py
"""
Tests to validate the FINAL state of the operating system/filesystem
AFTER the student has completed the git repository setup task.
"""

import os
import re
import subprocess
import pytest


class TestFinalState:
    """Test that the final state is correct after the task is performed."""

    # Expected paths
    CONFIG_DIR = "/home/user/config-tracking"
    GIT_DIR = "/home/user/config-tracking/.git"
    APP_CONF = "/home/user/config-tracking/app.conf"
    SETUP_LOG = "/home/user/config-tracking/setup.log"

    # Expected content
    EXPECTED_APP_CONF_CONTENT = """[database]
host=localhost
port=5432
name=production_db

[logging]
level=INFO
path=/var/log/app.log
"""
    EXPECTED_COMMIT_MESSAGE = "Initial configuration setup"

    def test_config_tracking_directory_exists(self):
        """Verify the config-tracking directory exists."""
        assert os.path.isdir(self.CONFIG_DIR), (
            f"Directory {self.CONFIG_DIR} does not exist. "
            "The student should have created this directory."
        )

    def test_git_repository_initialized(self):
        """Verify the .git directory exists (confirming git init was run)."""
        assert os.path.isdir(self.GIT_DIR), (
            f"Git directory {self.GIT_DIR} does not exist. "
            "The student should have initialized a git repository with 'git init'."
        )

    def test_app_conf_exists(self):
        """Verify the app.conf file exists."""
        assert os.path.isfile(self.APP_CONF), (
            f"Configuration file {self.APP_CONF} does not exist. "
            "The student should have created this file."
        )

    def test_app_conf_content_is_correct(self):
        """Verify the app.conf file has the exact expected content."""
        assert os.path.isfile(self.APP_CONF), f"Configuration file {self.APP_CONF} does not exist."

        with open(self.APP_CONF, 'r') as f:
            actual_content = f.read()

        assert actual_content == self.EXPECTED_APP_CONF_CONTENT, (
            f"Configuration file content does not match expected.\n"
            f"Expected:\n{repr(self.EXPECTED_APP_CONF_CONTENT)}\n"
            f"Actual:\n{repr(actual_content)}"
        )

    def test_setup_log_exists(self):
        """Verify the setup.log file exists."""
        assert os.path.isfile(self.SETUP_LOG), (
            f"Log file {self.SETUP_LOG} does not exist. "
            "The student should have created this file."
        )

    def test_setup_log_has_four_lines(self):
        """Verify the setup.log file has exactly 4 lines."""
        assert os.path.isfile(self.SETUP_LOG), f"Log file {self.SETUP_LOG} does not exist."

        with open(self.SETUP_LOG, 'r') as f:
            lines = f.read().splitlines()

        assert len(lines) == 4, (
            f"Log file should have exactly 4 lines, but has {len(lines)} lines.\n"
            f"Content: {lines}"
        )

    def test_setup_log_line1_repository_path(self):
        """Verify line 1 of setup.log contains the correct repository path."""
        assert os.path.isfile(self.SETUP_LOG), f"Log file {self.SETUP_LOG} does not exist."

        with open(self.SETUP_LOG, 'r') as f:
            lines = f.read().splitlines()

        assert len(lines) >= 1, "Log file has no lines."
        assert lines[0] == self.CONFIG_DIR, (
            f"Line 1 of setup.log should be '{self.CONFIG_DIR}', "
            f"but got '{lines[0]}'"
        )

    def test_setup_log_line2_config_filename(self):
        """Verify line 2 of setup.log contains 'app.conf'."""
        assert os.path.isfile(self.SETUP_LOG), f"Log file {self.SETUP_LOG} does not exist."

        with open(self.SETUP_LOG, 'r') as f:
            lines = f.read().splitlines()

        assert len(lines) >= 2, "Log file has fewer than 2 lines."
        assert lines[1] == "app.conf", (
            f"Line 2 of setup.log should be 'app.conf', "
            f"but got '{lines[1]}'"
        )

    def test_setup_log_line3_is_valid_commit_hash(self):
        """Verify line 3 of setup.log is a valid 40-character hex string (git commit hash)."""
        assert os.path.isfile(self.SETUP_LOG), f"Log file {self.SETUP_LOG} does not exist."

        with open(self.SETUP_LOG, 'r') as f:
            lines = f.read().splitlines()

        assert len(lines) >= 3, "Log file has fewer than 3 lines."

        commit_hash = lines[2]
        # Check it's exactly 40 characters and all hex
        hex_pattern = re.compile(r'^[0-9a-f]{40}$')
        assert hex_pattern.match(commit_hash), (
            f"Line 3 of setup.log should be a 40-character hex commit hash, "
            f"but got '{commit_hash}'"
        )

    def test_setup_log_line4_commit_message(self):
        """Verify line 4 of setup.log contains the correct commit message."""
        assert os.path.isfile(self.SETUP_LOG), f"Log file {self.SETUP_LOG} does not exist."

        with open(self.SETUP_LOG, 'r') as f:
            lines = f.read().splitlines()

        assert len(lines) >= 4, "Log file has fewer than 4 lines."
        assert lines[3] == self.EXPECTED_COMMIT_MESSAGE, (
            f"Line 4 of setup.log should be '{self.EXPECTED_COMMIT_MESSAGE}', "
            f"but got '{lines[3]}'"
        )

    def test_git_repository_has_exactly_one_commit(self):
        """Verify the git repository has exactly one commit."""
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=self.CONFIG_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"Failed to count git commits. Error: {result.stderr}"
        )

        commit_count = int(result.stdout.strip())
        assert commit_count == 1, (
            f"Repository should have exactly 1 commit, but has {commit_count} commits."
        )

    def test_commit_hash_in_log_matches_repository(self):
        """Verify the commit hash in setup.log matches the actual commit in the repository."""
        assert os.path.isfile(self.SETUP_LOG), f"Log file {self.SETUP_LOG} does not exist."

        with open(self.SETUP_LOG, 'r') as f:
            lines = f.read().splitlines()

        assert len(lines) >= 3, "Log file has fewer than 3 lines."
        logged_hash = lines[2]

        # Get actual commit hash from repository
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.CONFIG_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"Failed to get commit hash from repository. Error: {result.stderr}"
        )

        actual_hash = result.stdout.strip()
        assert logged_hash == actual_hash, (
            f"Commit hash in setup.log ({logged_hash}) does not match "
            f"actual repository commit hash ({actual_hash})."
        )

    def test_app_conf_is_tracked_by_git(self):
        """Verify app.conf is tracked by git (shown in git ls-files)."""
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=self.CONFIG_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"Failed to list tracked files. Error: {result.stderr}"
        )

        tracked_files = result.stdout.strip().split('\n')
        assert "app.conf" in tracked_files, (
            f"app.conf is not tracked by git. Tracked files: {tracked_files}"
        )

    def test_commit_message_matches_expected(self):
        """Verify the actual commit message in the repository matches the expected message."""
        result = subprocess.run(
            ["git", "log", "--format=%s", "-1"],
            cwd=self.CONFIG_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"Failed to get commit message. Error: {result.stderr}"
        )

        actual_message = result.stdout.strip()
        assert actual_message == self.EXPECTED_COMMIT_MESSAGE, (
            f"Commit message should be '{self.EXPECTED_COMMIT_MESSAGE}', "
            f"but got '{actual_message}'"
        )

    def test_app_conf_is_committed(self):
        """Verify app.conf has been committed (not just staged)."""
        # Check that app.conf appears in the commit tree
        result = subprocess.run(
            ["git", "ls-tree", "HEAD", "--name-only"],
            cwd=self.CONFIG_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"Failed to list files in commit. Error: {result.stderr}"
        )

        committed_files = result.stdout.strip().split('\n')
        assert "app.conf" in committed_files, (
            f"app.conf is not in the commit. Files in commit: {committed_files}"
        )
