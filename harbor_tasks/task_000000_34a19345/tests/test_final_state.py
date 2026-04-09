# test_final_state.py
"""
Tests to validate the FINAL state of the operating system/filesystem
AFTER the student has completed the task of setting up a git submodule project.
"""

import os
import subprocess
import re
import pytest


class TestSalesAnalysisRepository:
    """Tests to verify the sales_analysis repository is properly set up."""

    def test_sales_analysis_directory_exists(self):
        """The sales_analysis directory must exist at /home/user/sales_analysis."""
        path = "/home/user/sales_analysis"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The student must create the sales_analysis directory."
        )

    def test_sales_analysis_is_git_repository(self):
        """The sales_analysis directory must be a git repository."""
        git_dir = "/home/user/sales_analysis/.git"
        assert os.path.exists(git_dir), (
            f"The directory /home/user/sales_analysis is not a git repository. "
            f"Expected {git_dir} to exist. "
            "The student must initialize git in /home/user/sales_analysis."
        )


class TestSubmoduleSetup:
    """Tests to verify the submodule is properly configured."""

    def test_utils_directory_exists(self):
        """The utils submodule directory must exist."""
        path = "/home/user/sales_analysis/utils"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The student must add the submodule into a 'utils' directory."
        )

    def test_utils_contains_csv_reader(self):
        """The utils submodule must contain csv_reader.py from shared_utils."""
        filepath = "/home/user/sales_analysis/utils/csv_reader.py"
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The submodule content should include csv_reader.py from shared_utils."
        )

    def test_gitmodules_file_exists(self):
        """The .gitmodules file must exist in the project root."""
        filepath = "/home/user/sales_analysis/.gitmodules"
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "Adding a submodule should create a .gitmodules file."
        )

    def test_gitmodules_contains_utils_section(self):
        """The .gitmodules file must contain a section for utils submodule."""
        filepath = "/home/user/sales_analysis/.gitmodules"
        with open(filepath, 'r') as f:
            content = f.read()
        assert '[submodule "utils"]' in content or "[submodule 'utils']" in content, (
            f"The .gitmodules file does not contain a [submodule \"utils\"] section. "
            f"Content: {content}"
        )

    def test_gitmodules_contains_correct_path(self):
        """The .gitmodules file must specify path = utils."""
        filepath = "/home/user/sales_analysis/.gitmodules"
        with open(filepath, 'r') as f:
            content = f.read()
        # Check for path = utils with flexible whitespace
        assert re.search(r'path\s*=\s*utils', content), (
            f"The .gitmodules file does not contain 'path = utils'. "
            f"Content: {content}"
        )

    def test_gitmodules_contains_correct_url(self):
        """The .gitmodules file must specify url = /home/user/shared_utils."""
        filepath = "/home/user/sales_analysis/.gitmodules"
        with open(filepath, 'r') as f:
            content = f.read()
        # Check for url = /home/user/shared_utils with flexible whitespace
        assert re.search(r'url\s*=\s*/home/user/shared_utils', content), (
            f"The .gitmodules file does not contain 'url = /home/user/shared_utils'. "
            f"Content: {content}"
        )


class TestGitCommit:
    """Tests to verify the commit was made correctly."""

    def test_commit_exists_with_correct_message(self):
        """A commit with message 'Add shared utilities submodule' must exist."""
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd="/home/user/sales_analysis",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get git log. Error: {result.stderr}"
        )
        assert "Add shared utilities submodule" in result.stdout, (
            f"No commit found with message 'Add shared utilities submodule'. "
            f"Git log output: {result.stdout}"
        )

    def test_submodule_is_committed(self):
        """The submodule must be committed (not just added)."""
        # Check that there are no uncommitted changes to .gitmodules
        result = subprocess.run(
            ["git", "status", "--porcelain", ".gitmodules"],
            cwd="/home/user/sales_analysis",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to check git status. Error: {result.stderr}"
        )
        # If .gitmodules shows up in status, it's not committed
        gitmodules_uncommitted = ".gitmodules" in result.stdout and result.stdout.strip()
        assert not gitmodules_uncommitted, (
            f"The .gitmodules file has uncommitted changes. "
            f"Git status: {result.stdout}"
        )


class TestSetupLogFile:
    """Tests to verify the setup_log.txt file is correctly created."""

    def test_setup_log_exists(self):
        """The setup_log.txt file must exist."""
        filepath = "/home/user/sales_analysis/setup_log.txt"
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The student must create setup_log.txt with the required content."
        )

    def test_setup_log_has_three_lines(self):
        """The setup_log.txt file must have exactly 3 lines."""
        filepath = "/home/user/sales_analysis/setup_log.txt"
        with open(filepath, 'r') as f:
            lines = f.readlines()
        # Filter out empty lines at the end
        non_empty_lines = [l for l in lines if l.strip()]
        assert len(non_empty_lines) == 3, (
            f"The setup_log.txt file should have exactly 3 non-empty lines, "
            f"but has {len(non_empty_lines)}. "
            f"Lines: {lines}"
        )

    def test_setup_log_line1_submodule_status(self):
        """Line 1 must contain git submodule status output (commit hash and 'utils')."""
        filepath = "/home/user/sales_analysis/setup_log.txt"
        with open(filepath, 'r') as f:
            lines = f.readlines()

        line1 = lines[0].strip() if lines else ""

        # The submodule status line should contain a commit hash (40 hex chars, possibly with leading space or -)
        # and the word "utils"
        has_hash = re.search(r'[0-9a-f]{40}', line1) is not None
        has_utils = 'utils' in line1

        assert has_hash and has_utils, (
            f"Line 1 should contain git submodule status output with a commit hash and 'utils'. "
            f"Got: '{line1}'"
        )

    def test_setup_log_line2_submodule_path(self):
        """Line 2 must be 'SUBMODULE_PATH: utils'."""
        filepath = "/home/user/sales_analysis/setup_log.txt"
        with open(filepath, 'r') as f:
            lines = f.readlines()

        line2 = lines[1].strip() if len(lines) > 1 else ""

        assert line2 == "SUBMODULE_PATH: utils", (
            f"Line 2 should be 'SUBMODULE_PATH: utils'. "
            f"Got: '{line2}'"
        )

    def test_setup_log_line3_submodule_url(self):
        """Line 3 must be 'SUBMODULE_URL: /home/user/shared_utils'."""
        filepath = "/home/user/sales_analysis/setup_log.txt"
        with open(filepath, 'r') as f:
            lines = f.readlines()

        line3 = lines[2].strip() if len(lines) > 2 else ""

        assert line3 == "SUBMODULE_URL: /home/user/shared_utils", (
            f"Line 3 should be 'SUBMODULE_URL: /home/user/shared_utils'. "
            f"Got: '{line3}'"
        )


class TestSubmoduleIntegrity:
    """Tests to verify the submodule is properly initialized and functional."""

    def test_submodule_status_shows_utils(self):
        """Git submodule status should show the utils submodule."""
        result = subprocess.run(
            ["git", "submodule", "status"],
            cwd="/home/user/sales_analysis",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get submodule status. Error: {result.stderr}"
        )
        assert "utils" in result.stdout, (
            f"Submodule 'utils' not found in submodule status. "
            f"Output: {result.stdout}"
        )

    def test_utils_is_git_submodule(self):
        """The utils directory should be a proper git submodule (has .git reference)."""
        # A submodule has either a .git file (pointing to parent's .git/modules) 
        # or a .git directory
        utils_git = "/home/user/sales_analysis/utils/.git"
        assert os.path.exists(utils_git), (
            f"The utils directory does not appear to be a proper git submodule. "
            f"Expected {utils_git} to exist (as file or directory)."
        )
