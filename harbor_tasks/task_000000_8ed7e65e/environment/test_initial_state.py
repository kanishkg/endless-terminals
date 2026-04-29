# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the GPG decryption task.
"""

import os
import subprocess
import pytest


class TestInitialState:
    """Validate the initial state before GPG decryption task."""

    def test_artifacts_directory_exists(self):
        """Verify /home/user/artifacts/ directory exists."""
        artifacts_dir = "/home/user/artifacts"
        assert os.path.isdir(artifacts_dir), (
            f"Directory {artifacts_dir} does not exist. "
            "The artifacts directory must be present for the task."
        )

    def test_artifacts_directory_is_writable(self):
        """Verify /home/user/artifacts/ is writable by the current user."""
        artifacts_dir = "/home/user/artifacts"
        assert os.access(artifacts_dir, os.W_OK), (
            f"Directory {artifacts_dir} is not writable. "
            "The agent user must have write permissions to create the decrypted file."
        )

    def test_encrypted_file_exists(self):
        """Verify /home/user/artifacts/model_weights.gpg exists."""
        gpg_file = "/home/user/artifacts/model_weights.gpg"
        assert os.path.isfile(gpg_file), (
            f"File {gpg_file} does not exist. "
            "The encrypted GPG file must be present for decryption."
        )

    def test_encrypted_file_is_not_empty(self):
        """Verify the encrypted file has content."""
        gpg_file = "/home/user/artifacts/model_weights.gpg"
        file_size = os.path.getsize(gpg_file)
        assert file_size > 0, (
            f"File {gpg_file} is empty (size: {file_size} bytes). "
            "The encrypted file must contain data."
        )

    def test_encrypted_file_is_gpg_encrypted(self):
        """Verify the file is actually GPG encrypted data."""
        gpg_file = "/home/user/artifacts/model_weights.gpg"
        result = subprocess.run(
            ["file", gpg_file],
            capture_output=True,
            text=True
        )
        file_output = result.stdout.lower()
        # GPG encrypted files are typically identified as "GPG symmetrically encrypted data"
        # or similar by the `file` command
        assert "gpg" in file_output or "pgp" in file_output or "encrypted" in file_output, (
            f"File {gpg_file} does not appear to be GPG encrypted. "
            f"`file` command output: {result.stdout.strip()}. "
            "The file must be a valid GPG-encrypted file."
        )

    def test_decrypted_file_does_not_exist(self):
        """Verify /home/user/artifacts/model_weights does NOT exist initially."""
        decrypted_file = "/home/user/artifacts/model_weights"
        assert not os.path.exists(decrypted_file), (
            f"File {decrypted_file} already exists. "
            "The decrypted output file should not exist before the task is performed."
        )

    def test_gpg_is_installed(self):
        """Verify gpg (GnuPG) is installed and available."""
        result = subprocess.run(
            ["which", "gpg"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "gpg command not found in PATH. "
            "GnuPG must be installed for the decryption task."
        )

    def test_gpg_version_is_2x(self):
        """Verify gpg version is 2.x."""
        result = subprocess.run(
            ["gpg", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Failed to get gpg version. "
            f"Error: {result.stderr}"
        )
        version_line = result.stdout.split('\n')[0]
        # Version line typically looks like: "gpg (GnuPG) 2.2.27"
        assert "2." in version_line, (
            f"gpg version does not appear to be 2.x. "
            f"Version output: {version_line}. "
            "GnuPG 2.x is required for this task."
        )

    def test_encrypted_file_has_reasonable_size(self):
        """Verify the encrypted file is approximately 1KB as specified."""
        gpg_file = "/home/user/artifacts/model_weights.gpg"
        file_size = os.path.getsize(gpg_file)
        # Allow some flexibility - GPG adds overhead, so check it's in a reasonable range
        # Original is ~1KB, with GPG overhead it should be between 100 bytes and 10KB
        assert 100 < file_size < 10240, (
            f"File {gpg_file} has unexpected size: {file_size} bytes. "
            "Expected approximately 1KB of encrypted data."
        )
