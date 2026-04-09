# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has completed the git submodule addition task.
"""

import os
import re
import subprocess
import pytest


class TestFinalState:
    """Test suite to validate the environment after task completion."""

    def test_gitmodules_file_exists(self):
        """Verify that .gitmodules file exists in the repository root."""
        gitmodules_path = "/home/user/monitoring-project/.gitmodules"
        assert os.path.isfile(gitmodules_path), (
            f"File '{gitmodules_path}' does not exist. "
            "The .gitmodules file should be created when adding a submodule."
        )

    def test_gitmodules_contains_alertmanager_section(self):
        """Verify that .gitmodules contains a section for alertmanager submodule."""
        gitmodules_path = "/home/user/monitoring-project/.gitmodules"
        assert os.path.isfile(gitmodules_path), (
            f"File '{gitmodules_path}' does not exist."
        )

        with open(gitmodules_path, "r") as f:
            content = f.read()

        assert '[submodule' in content and 'alertmanager' in content.lower(), (
            "The .gitmodules file does not contain an alertmanager submodule section. "
            f"Current content:\n{content}"
        )

    def test_gitmodules_contains_correct_path(self):
        """Verify that .gitmodules contains path = external/alertmanager."""
        gitmodules_path = "/home/user/monitoring-project/.gitmodules"
        assert os.path.isfile(gitmodules_path), (
            f"File '{gitmodules_path}' does not exist."
        )

        with open(gitmodules_path, "r") as f:
            content = f.read()

        # Check for path configuration (allowing for whitespace variations)
        path_pattern = r'path\s*=\s*external/alertmanager'
        assert re.search(path_pattern, content), (
            "The .gitmodules file does not contain 'path = external/alertmanager'. "
            f"Current content:\n{content}"
        )

    def test_gitmodules_contains_correct_url(self):
        """Verify that .gitmodules contains url = https://github.com/prometheus/alertmanager.git."""
        gitmodules_path = "/home/user/monitoring-project/.gitmodules"
        assert os.path.isfile(gitmodules_path), (
            f"File '{gitmodules_path}' does not exist."
        )

        with open(gitmodules_path, "r") as f:
            content = f.read()

        # Check for url configuration (allowing for whitespace variations)
        url_pattern = r'url\s*=\s*https://github\.com/prometheus/alertmanager\.git'
        assert re.search(url_pattern, content), (
            "The .gitmodules file does not contain 'url = https://github.com/prometheus/alertmanager.git'. "
            f"Current content:\n{content}"
        )

    def test_external_alertmanager_directory_exists(self):
        """Verify that external/alertmanager directory exists."""
        submodule_path = "/home/user/monitoring-project/external/alertmanager"
        assert os.path.isdir(submodule_path), (
            f"Directory '{submodule_path}' does not exist. "
            "The submodule directory should be created when adding the submodule."
        )

    def test_submodule_is_git_repository(self):
        """Verify that external/alertmanager is a git repository (has .git file or directory)."""
        submodule_path = "/home/user/monitoring-project/external/alertmanager"
        git_path = os.path.join(submodule_path, ".git")

        # Submodules can have either a .git directory or a .git file pointing to gitdir
        assert os.path.exists(git_path), (
            f"'{submodule_path}' does not appear to be a git repository. "
            "The .git file or directory is missing. "
            "Make sure the submodule is properly initialized."
        )

    def test_submodule_setup_log_exists(self):
        """Verify that submodule-setup.log file exists."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert os.path.isfile(log_path), (
            f"File '{log_path}' does not exist. "
            "The submodule-setup.log file should be created after adding the submodule."
        )

    def test_log_contains_submodule_path_line(self):
        """Verify that log contains correct SUBMODULE_PATH line."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert os.path.isfile(log_path), f"File '{log_path}' does not exist."

        with open(log_path, "r") as f:
            content = f.read()

        lines = content.strip().split('\n')
        path_line = None
        for line in lines:
            if line.startswith('SUBMODULE_PATH:'):
                path_line = line
                break

        assert path_line is not None, (
            "Log file does not contain a line starting with 'SUBMODULE_PATH:'. "
            f"Current content:\n{content}"
        )

        # Extract value after the label
        value = path_line.split(':', 1)[1].strip()
        assert value == "external/alertmanager", (
            f"SUBMODULE_PATH value is '{value}', expected 'external/alertmanager'. "
            f"Line found: '{path_line}'"
        )

    def test_log_contains_submodule_url_line(self):
        """Verify that log contains correct SUBMODULE_URL line."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert os.path.isfile(log_path), f"File '{log_path}' does not exist."

        with open(log_path, "r") as f:
            content = f.read()

        lines = content.strip().split('\n')
        url_line = None
        for line in lines:
            if line.startswith('SUBMODULE_URL:'):
                url_line = line
                break

        assert url_line is not None, (
            "Log file does not contain a line starting with 'SUBMODULE_URL:'. "
            f"Current content:\n{content}"
        )

        # Extract value after the label
        value = url_line.split(':', 1)[1].strip()
        # The URL contains colons, so we need to handle that
        # SUBMODULE_URL: https://github.com/prometheus/alertmanager.git
        expected_url = "https://github.com/prometheus/alertmanager.git"
        assert value == expected_url, (
            f"SUBMODULE_URL value is '{value}', expected '{expected_url}'. "
            f"Line found: '{url_line}'"
        )

    def test_log_contains_submodule_status_line_with_commit_hash(self):
        """Verify that log contains SUBMODULE_STATUS line with a valid commit hash."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert os.path.isfile(log_path), f"File '{log_path}' does not exist."

        with open(log_path, "r") as f:
            content = f.read()

        lines = content.strip().split('\n')
        status_line = None
        for line in lines:
            if line.startswith('SUBMODULE_STATUS:'):
                status_line = line
                break

        assert status_line is not None, (
            "Log file does not contain a line starting with 'SUBMODULE_STATUS:'. "
            f"Current content:\n{content}"
        )

        # Extract value after the label
        value = status_line.split(':', 1)[1].strip()

        # Check for a 40-character hex commit hash in the status
        # The status format is typically: [-+ ]<40-char-hash> <path> [(<description>)]
        hex_pattern = r'[0-9a-fA-F]{40}'
        assert re.search(hex_pattern, value), (
            f"SUBMODULE_STATUS does not contain a valid 40-character commit hash. "
            f"Value found: '{value}'"
        )

    def test_log_contains_setup_complete_line(self):
        """Verify that log contains SETUP_COMPLETE: true line."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert os.path.isfile(log_path), f"File '{log_path}' does not exist."

        with open(log_path, "r") as f:
            content = f.read()

        lines = content.strip().split('\n')
        complete_line = None
        for line in lines:
            if line.startswith('SETUP_COMPLETE:'):
                complete_line = line
                break

        assert complete_line is not None, (
            "Log file does not contain a line starting with 'SETUP_COMPLETE:'. "
            f"Current content:\n{content}"
        )

        # Extract value after the label
        value = complete_line.split(':', 1)[1].strip()
        assert value == "true", (
            f"SETUP_COMPLETE value is '{value}', expected 'true'. "
            f"Line found: '{complete_line}'"
        )

    def test_log_has_all_four_required_lines(self):
        """Verify that log contains all 4 required lines."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert os.path.isfile(log_path), f"File '{log_path}' does not exist."

        with open(log_path, "r") as f:
            content = f.read()

        required_labels = [
            'SUBMODULE_PATH:',
            'SUBMODULE_URL:',
            'SUBMODULE_STATUS:',
            'SETUP_COMPLETE:'
        ]

        missing_labels = []
        for label in required_labels:
            if label not in content:
                missing_labels.append(label)

        assert not missing_labels, (
            f"Log file is missing the following required labels: {missing_labels}. "
            f"Current content:\n{content}"
        )

    def test_git_submodule_status_shows_alertmanager(self):
        """Verify that git submodule status command shows the alertmanager submodule."""
        project_path = "/home/user/monitoring-project"

        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"'git submodule status' command failed with return code {result.returncode}. "
            f"stderr: {result.stderr}"
        )

        output = result.stdout
        assert "external/alertmanager" in output, (
            "The 'git submodule status' command does not show 'external/alertmanager'. "
            f"Output:\n{output}"
        )

    def test_submodule_contains_files(self):
        """Verify that the submodule directory contains cloned repository files."""
        submodule_path = "/home/user/monitoring-project/external/alertmanager"

        # Check that the directory is not empty and contains typical repo files
        contents = os.listdir(submodule_path)

        # Filter out hidden files for the check
        visible_contents = [f for f in contents if not f.startswith('.')]

        assert len(visible_contents) > 0, (
            f"The submodule directory '{submodule_path}' appears to be empty or only contains hidden files. "
            "The submodule should be properly cloned with repository contents."
        )

    def test_submodule_config_in_git_config(self):
        """Verify that the submodule is registered in the git config."""
        project_path = "/home/user/monitoring-project"

        result = subprocess.run(
            ["git", "config", "--file", ".gitmodules", "--get", "submodule.external/alertmanager.url"],
            cwd=project_path,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            "Failed to get submodule URL from .gitmodules. "
            "The submodule may not be properly configured. "
            f"stderr: {result.stderr}"
        )

        url = result.stdout.strip()
        assert url == "https://github.com/prometheus/alertmanager.git", (
            f"Submodule URL in .gitmodules is '{url}', "
            "expected 'https://github.com/prometheus/alertmanager.git'."
        )
