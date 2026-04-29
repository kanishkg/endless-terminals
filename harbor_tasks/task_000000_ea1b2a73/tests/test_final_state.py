# test_final_state.py
"""
Tests to validate the final state of the system after the student
has set up a Python virtual environment for backup-tools with required packages.
"""

import os
import subprocess
import pytest


class TestVenvDirectoryExists:
    """Test that the venv directory exists and is a valid virtual environment."""

    def test_venv_directory_exists(self):
        """Verify /home/user/backup-tools/venv/ directory exists."""
        path = "/home/user/backup-tools/venv"
        assert os.path.exists(path), (
            f"Directory {path} does not exist. "
            "Did you run 'python3 -m venv venv' in /home/user/backup-tools/?"
        )
        assert os.path.isdir(path), f"{path} exists but is not a directory"

    def test_venv_bin_directory_exists(self):
        """Verify venv/bin directory exists."""
        path = "/home/user/backup-tools/venv/bin"
        assert os.path.exists(path), (
            f"Directory {path} does not exist. "
            "The venv may not have been created correctly."
        )
        assert os.path.isdir(path), f"{path} exists but is not a directory"

    def test_venv_python_exists_and_executable(self):
        """Verify venv/bin/python exists and is executable."""
        path = "/home/user/backup-tools/venv/bin/python"
        assert os.path.exists(path), (
            f"File {path} does not exist. "
            "The virtual environment may not have been created correctly."
        )
        assert os.access(path, os.X_OK), (
            f"File {path} exists but is not executable."
        )

    def test_venv_pip_exists_and_executable(self):
        """Verify venv/bin/pip exists and is executable."""
        path = "/home/user/backup-tools/venv/bin/pip"
        assert os.path.exists(path), (
            f"File {path} does not exist. "
            "The virtual environment may not have been created correctly."
        )
        assert os.access(path, os.X_OK), (
            f"File {path} exists but is not executable."
        )


class TestPackagesInstalled:
    """Test that required packages are installed in the venv."""

    def test_boto3_installed_in_venv(self):
        """Verify boto3 is installed in the virtual environment."""
        result = subprocess.run(
            ["/home/user/backup-tools/venv/bin/pip", "list"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to run pip list. Error: {result.stderr}"
        )
        # Check for boto3 in the output (case-insensitive)
        pip_output = result.stdout.lower()
        assert "boto3" in pip_output, (
            f"boto3 is not installed in the venv. "
            f"Did you run 'pip install -r requirements.txt' with the venv activated? "
            f"Installed packages: {result.stdout}"
        )

    def test_pyyaml_installed_in_venv(self):
        """Verify PyYAML is installed in the virtual environment."""
        result = subprocess.run(
            ["/home/user/backup-tools/venv/bin/pip", "list"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to run pip list. Error: {result.stderr}"
        )
        # Check for PyYAML in the output (case-insensitive)
        pip_output = result.stdout.lower()
        assert "pyyaml" in pip_output, (
            f"PyYAML is not installed in the venv. "
            f"Did you run 'pip install -r requirements.txt' with the venv activated? "
            f"Installed packages: {result.stdout}"
        )

    def test_can_import_boto3(self):
        """Verify boto3 can be imported using the venv Python."""
        result = subprocess.run(
            ["/home/user/backup-tools/venv/bin/python", "-c", "import boto3"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to import boto3 in the venv. "
            f"Error: {result.stderr}"
        )

    def test_can_import_yaml(self):
        """Verify yaml (PyYAML) can be imported using the venv Python."""
        result = subprocess.run(
            ["/home/user/backup-tools/venv/bin/python", "-c", "import yaml"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to import yaml in the venv. "
            f"Error: {result.stderr}"
        )

    def test_can_import_both_packages(self):
        """Verify both boto3 and yaml can be imported together."""
        result = subprocess.run(
            ["/home/user/backup-tools/venv/bin/python", "-c", "import boto3; import yaml"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to import boto3 and yaml together in the venv. "
            f"Error: {result.stderr}"
        )


class TestInvariants:
    """Test that original files remain unchanged."""

    def test_requirements_file_unchanged(self):
        """Verify requirements.txt still exists with expected content."""
        path = "/home/user/backup-tools/requirements.txt"
        assert os.path.exists(path), (
            f"File {path} no longer exists - it should not have been deleted"
        )
        with open(path, "r") as f:
            content = f.read()
        assert "boto3==1.34.0" in content, (
            f"requirements.txt was modified - boto3==1.34.0 is missing"
        )
        assert "PyYAML==6.0.1" in content, (
            f"requirements.txt was modified - PyYAML==6.0.1 is missing"
        )

    def test_sync_backups_script_unchanged(self):
        """Verify sync_backups.py still exists."""
        path = "/home/user/backup-tools/sync_backups.py"
        assert os.path.exists(path), (
            f"File {path} no longer exists - it should not have been deleted"
        )
        assert os.path.isfile(path), f"{path} exists but is not a file"


class TestAntiShortcutGuards:
    """Test that packages are installed in venv, not system-wide."""

    def test_boto3_in_venv_pip_list(self):
        """Verify boto3 appears in venv pip list output (anti-shortcut guard)."""
        result = subprocess.run(
            ["/home/user/backup-tools/venv/bin/pip", "list"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to run venv pip list. Error: {result.stderr}"
        )
        # Use grep-like check on the output
        lines = result.stdout.lower().split('\n')
        boto3_found = any('boto3' in line for line in lines)
        assert boto3_found, (
            f"boto3 not found in venv pip list. "
            f"Packages must be installed inside the venv, not system-wide. "
            f"Output: {result.stdout}"
        )

    def test_venv_python_is_different_from_system(self):
        """Verify venv python is a separate installation."""
        venv_python = "/home/user/backup-tools/venv/bin/python"

        # Get the venv python's sys.prefix
        result = subprocess.run(
            [venv_python, "-c", "import sys; print(sys.prefix)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get venv python prefix. Error: {result.stderr}"
        )
        venv_prefix = result.stdout.strip()

        # The prefix should be within the venv directory
        assert "/home/user/backup-tools/venv" in venv_prefix, (
            f"The venv python's sys.prefix ({venv_prefix}) does not point to the venv directory. "
            f"This suggests the venv was not created correctly."
        )
