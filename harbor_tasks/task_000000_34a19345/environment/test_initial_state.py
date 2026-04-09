# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
BEFORE the student performs the task of setting up a git submodule project.
"""

import os
import subprocess
import pytest


class TestSharedUtilsRepositoryExists:
    """Tests to verify the shared_utils repository exists and is properly set up."""

    def test_shared_utils_directory_exists(self):
        """The shared_utils directory must exist at /home/user/shared_utils."""
        path = "/home/user/shared_utils"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The shared_utils repository must be created before starting this task."
        )

    def test_shared_utils_is_git_repository(self):
        """The shared_utils directory must be a git repository."""
        git_dir = "/home/user/shared_utils/.git"
        assert os.path.exists(git_dir), (
            f"The directory /home/user/shared_utils is not a git repository. "
            f"Expected {git_dir} to exist. "
            "Please initialize git in /home/user/shared_utils before starting."
        )

    def test_shared_utils_has_csv_reader_file(self):
        """The shared_utils repository must contain csv_reader.py."""
        filepath = "/home/user/shared_utils/csv_reader.py"
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The shared_utils repository must contain csv_reader.py before starting this task."
        )

    def test_shared_utils_has_at_least_one_commit(self):
        """The shared_utils repository must have at least one commit."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/user/shared_utils",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "The shared_utils repository has no commits. "
            "Please make an initial commit in /home/user/shared_utils before starting this task. "
            f"Git error: {result.stderr}"
        )


class TestSalesAnalysisDoesNotExist:
    """Tests to verify the sales_analysis directory does not exist yet."""

    def test_sales_analysis_directory_does_not_exist(self):
        """The sales_analysis directory should NOT exist before the task."""
        path = "/home/user/sales_analysis"
        assert not os.path.exists(path), (
            f"Directory {path} already exists. "
            "The student needs to create this directory as part of the task. "
            "Please remove it before starting."
        )


class TestHomeDirectoryExists:
    """Tests to verify the home directory structure is correct."""

    def test_home_user_directory_exists(self):
        """The /home/user directory must exist."""
        path = "/home/user"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The home directory must exist before starting this task."
        )

    def test_home_user_is_writable(self):
        """The /home/user directory must be writable."""
        path = "/home/user"
        assert os.access(path, os.W_OK), (
            f"Directory {path} is not writable. "
            "The student needs write access to create the sales_analysis project."
        )


class TestGitIsAvailable:
    """Tests to verify git is installed and available."""

    def test_git_is_installed(self):
        """Git must be installed and available in PATH."""
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Git is not installed or not available in PATH. "
            "Please install git before starting this task."
        )
