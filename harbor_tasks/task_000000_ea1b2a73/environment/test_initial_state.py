# test_initial_state.py
"""
Tests to validate the initial state of the system before the student
sets up a Python virtual environment for backup-tools.
"""

import os
import subprocess
import pytest


class TestBackupToolsDirectoryExists:
    """Test that the backup-tools directory exists and is writable."""

    def test_backup_tools_directory_exists(self):
        """Verify /home/user/backup-tools/ directory exists."""
        path = "/home/user/backup-tools"
        assert os.path.exists(path), f"Directory {path} does not exist"
        assert os.path.isdir(path), f"{path} exists but is not a directory"

    def test_backup_tools_directory_is_writable(self):
        """Verify /home/user/backup-tools/ directory is writable."""
        path = "/home/user/backup-tools"
        assert os.access(path, os.W_OK), f"Directory {path} is not writable"


class TestRequirementsFile:
    """Test that requirements.txt exists with correct content."""

    def test_requirements_file_exists(self):
        """Verify requirements.txt exists in backup-tools directory."""
        path = "/home/user/backup-tools/requirements.txt"
        assert os.path.exists(path), f"File {path} does not exist"
        assert os.path.isfile(path), f"{path} exists but is not a file"

    def test_requirements_contains_boto3(self):
        """Verify requirements.txt contains boto3==1.34.0."""
        path = "/home/user/backup-tools/requirements.txt"
        with open(path, "r") as f:
            content = f.read()
        assert "boto3==1.34.0" in content, (
            f"requirements.txt does not contain 'boto3==1.34.0'. Content: {content}"
        )

    def test_requirements_contains_pyyaml(self):
        """Verify requirements.txt contains PyYAML==6.0.1."""
        path = "/home/user/backup-tools/requirements.txt"
        with open(path, "r") as f:
            content = f.read()
        assert "PyYAML==6.0.1" in content, (
            f"requirements.txt does not contain 'PyYAML==6.0.1'. Content: {content}"
        )


class TestSyncBackupsScript:
    """Test that sync_backups.py exists."""

    def test_sync_backups_script_exists(self):
        """Verify sync_backups.py exists in backup-tools directory."""
        path = "/home/user/backup-tools/sync_backups.py"
        assert os.path.exists(path), f"File {path} does not exist"
        assert os.path.isfile(path), f"{path} exists but is not a file"


class TestPythonAvailability:
    """Test that Python 3 and pip are available."""

    def test_python3_available(self):
        """Verify python3 is available and is version 3.10+."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"python3 is not available. Error: {result.stderr}"
        )
        # Parse version from output like "Python 3.10.12"
        version_output = result.stdout.strip()
        assert "Python 3" in version_output, (
            f"Expected Python 3, got: {version_output}"
        )
        # Extract version numbers
        version_parts = version_output.split()[1].split(".")
        major = int(version_parts[0])
        minor = int(version_parts[1])
        assert major == 3 and minor >= 10, (
            f"Python version must be 3.10+, got: {version_output}"
        )

    def test_pip_available(self):
        """Verify pip is available."""
        result = subprocess.run(
            ["python3", "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"pip is not available. Error: {result.stderr}"
        )

    def test_venv_module_available(self):
        """Verify venv module is available."""
        result = subprocess.run(
            ["python3", "-c", "import venv"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"venv module is not available. Error: {result.stderr}"
        )


class TestNoExistingVenv:
    """Test that no venv directory exists yet."""

    def test_venv_directory_does_not_exist(self):
        """Verify venv directory does not exist in backup-tools."""
        path = "/home/user/backup-tools/venv"
        assert not os.path.exists(path), (
            f"Directory {path} already exists - it should not exist in the initial state"
        )
