# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the CI/CD pipeline backup task.
"""

import os
import pytest


class TestSourceDirectoryExists:
    """Test that the source ci-pipelines directory exists with required files."""

    def test_ci_pipelines_directory_exists(self):
        """The /home/user/ci-pipelines directory must exist."""
        path = "/home/user/ci-pipelines"
        assert os.path.isdir(path), (
            f"Source directory '{path}' does not exist. "
            "This directory should contain the CI/CD pipeline configuration files to be backed up."
        )

    def test_jenkinsfile_exists(self):
        """The Jenkinsfile must exist in the ci-pipelines directory."""
        path = "/home/user/ci-pipelines/Jenkinsfile"
        assert os.path.isfile(path), (
            f"File '{path}' does not exist. "
            "The Jenkinsfile is required as part of the CI/CD configuration files."
        )

    def test_jenkinsfile_has_content(self):
        """The Jenkinsfile must have expected content."""
        path = "/home/user/ci-pipelines/Jenkinsfile"
        with open(path, "r") as f:
            content = f.read()
        assert "pipeline" in content, (
            f"File '{path}' does not contain expected Jenkins pipeline content. "
            "The file should contain a valid Jenkins pipeline definition."
        )

    def test_gitlab_ci_yml_exists(self):
        """The .gitlab-ci.yml file must exist in the ci-pipelines directory."""
        path = "/home/user/ci-pipelines/.gitlab-ci.yml"
        assert os.path.isfile(path), (
            f"File '{path}' does not exist. "
            "The .gitlab-ci.yml is required as part of the CI/CD configuration files."
        )

    def test_gitlab_ci_yml_has_content(self):
        """The .gitlab-ci.yml must have expected content."""
        path = "/home/user/ci-pipelines/.gitlab-ci.yml"
        with open(path, "r") as f:
            content = f.read()
        assert "stages" in content, (
            f"File '{path}' does not contain expected GitLab CI content. "
            "The file should contain a valid GitLab CI configuration."
        )

    def test_azure_pipelines_yml_exists(self):
        """The azure-pipelines.yml file must exist in the ci-pipelines directory."""
        path = "/home/user/ci-pipelines/azure-pipelines.yml"
        assert os.path.isfile(path), (
            f"File '{path}' does not exist. "
            "The azure-pipelines.yml is required as part of the CI/CD configuration files."
        )

    def test_azure_pipelines_yml_has_content(self):
        """The azure-pipelines.yml must have expected content."""
        path = "/home/user/ci-pipelines/azure-pipelines.yml"
        with open(path, "r") as f:
            content = f.read()
        assert "trigger" in content or "pool" in content, (
            f"File '{path}' does not contain expected Azure Pipelines content. "
            "The file should contain a valid Azure Pipelines configuration."
        )


class TestBackupsDirectoryDoesNotExist:
    """Test that the backups directory does NOT exist initially."""

    def test_backups_directory_does_not_exist(self):
        """The /home/user/backups directory must NOT exist initially."""
        path = "/home/user/backups"
        assert not os.path.exists(path), (
            f"Directory '{path}' already exists but should NOT exist initially. "
            "The student/agent must create this directory as part of the task."
        )


class TestHomeDirectoryExists:
    """Test that the home directory exists and is accessible."""

    def test_home_user_directory_exists(self):
        """The /home/user directory must exist."""
        path = "/home/user"
        assert os.path.isdir(path), (
            f"Home directory '{path}' does not exist. "
            "The user's home directory must exist for the task to be performed."
        )

    def test_home_user_directory_is_writable(self):
        """The /home/user directory must be writable."""
        path = "/home/user"
        assert os.access(path, os.W_OK), (
            f"Home directory '{path}' is not writable. "
            "The user must have write permissions to create the backups directory."
        )
