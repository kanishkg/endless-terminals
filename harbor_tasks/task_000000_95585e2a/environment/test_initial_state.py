# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the git submodule addition task.
"""

import os
import subprocess
import pytest


class TestInitialState:
    """Test suite to validate the environment before task execution."""

    def test_monitoring_project_directory_exists(self):
        """Verify that /home/user/monitoring-project directory exists."""
        project_path = "/home/user/monitoring-project"
        assert os.path.isdir(project_path), (
            f"Directory '{project_path}' does not exist. "
            "The monitoring-project directory must be created before starting the task."
        )

    def test_monitoring_project_is_git_repository(self):
        """Verify that /home/user/monitoring-project is initialized as a git repository."""
        project_path = "/home/user/monitoring-project"
        git_dir = os.path.join(project_path, ".git")
        assert os.path.isdir(git_dir), (
            f"'{project_path}' is not a git repository. "
            "The directory must be initialized with 'git init' before starting the task."
        )

    def test_git_is_installed(self):
        """Verify that git is installed and accessible."""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            assert result.returncode == 0
        except FileNotFoundError:
            pytest.fail("Git is not installed. Please install git before proceeding.")
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Git command failed: {e.stderr}")

    def test_git_repository_has_initial_commit(self):
        """Verify that the git repository has at least one commit."""
        project_path = "/home/user/monitoring-project"
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, (
                "The git repository has no commits. "
                "At least one initial commit is required before adding submodules."
            )
        except Exception as e:
            pytest.fail(f"Failed to check git commits: {e}")

    def test_git_user_configured(self):
        """Verify that git user.email and user.name are configured."""
        project_path = "/home/user/monitoring-project"

        # Check user.email
        result_email = subprocess.run(
            ["git", "config", "user.email"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        assert result_email.returncode == 0 and result_email.stdout.strip(), (
            "Git user.email is not configured. "
            "Please run 'git config user.email \"your@email.com\"' in the repository."
        )

        # Check user.name
        result_name = subprocess.run(
            ["git", "config", "user.name"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        assert result_name.returncode == 0 and result_name.stdout.strip(), (
            "Git user.name is not configured. "
            "Please run 'git config user.name \"Your Name\"' in the repository."
        )

    def test_directory_is_writable(self):
        """Verify that the user has write permissions to the project directory."""
        project_path = "/home/user/monitoring-project"
        assert os.access(project_path, os.W_OK), (
            f"No write permission for '{project_path}'. "
            "The user must have write permissions to add submodules."
        )

    def test_external_alertmanager_does_not_exist(self):
        """Verify that the external/alertmanager directory does not already exist."""
        submodule_path = "/home/user/monitoring-project/external/alertmanager"
        assert not os.path.exists(submodule_path), (
            f"Directory '{submodule_path}' already exists. "
            "The submodule directory should not exist before the task is performed."
        )

    def test_gitmodules_does_not_contain_alertmanager(self):
        """Verify that .gitmodules does not already contain alertmanager submodule."""
        gitmodules_path = "/home/user/monitoring-project/.gitmodules"
        if os.path.exists(gitmodules_path):
            with open(gitmodules_path, "r") as f:
                content = f.read()
            assert "alertmanager" not in content.lower(), (
                "The .gitmodules file already contains an alertmanager entry. "
                "The submodule should not be configured before the task is performed."
            )

    def test_submodule_setup_log_does_not_exist(self):
        """Verify that the submodule-setup.log file does not already exist."""
        log_path = "/home/user/monitoring-project/submodule-setup.log"
        assert not os.path.exists(log_path), (
            f"File '{log_path}' already exists. "
            "The setup log should not exist before the task is performed."
        )

    def test_readme_exists(self):
        """Verify that README.md exists (from initial commit)."""
        readme_path = "/home/user/monitoring-project/README.md"
        assert os.path.exists(readme_path), (
            f"File '{readme_path}' does not exist. "
            "The initial commit should have created a README.md file."
        )
