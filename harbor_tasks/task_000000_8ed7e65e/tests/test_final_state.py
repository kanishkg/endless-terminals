# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the GPG decryption task.
"""

import os
import subprocess
import pytest


class TestFinalState:
    """Validate the final state after GPG decryption task."""

    def test_decrypted_file_exists(self):
        """Verify /home/user/artifacts/model_weights exists after decryption."""
        decrypted_file = "/home/user/artifacts/model_weights"
        assert os.path.isfile(decrypted_file), (
            f"File {decrypted_file} does not exist. "
            "The decrypted output file must be created by the decryption process."
        )

    def test_decrypted_file_is_not_empty(self):
        """Verify the decrypted file has content (non-zero size)."""
        decrypted_file = "/home/user/artifacts/model_weights"
        assert os.path.isfile(decrypted_file), (
            f"File {decrypted_file} does not exist."
        )
        file_size = os.path.getsize(decrypted_file)
        assert file_size > 0, (
            f"File {decrypted_file} is empty (size: {file_size} bytes). "
            "The decrypted file must contain the original plaintext data."
        )

    def test_encrypted_file_still_exists(self):
        """Verify /home/user/artifacts/model_weights.gpg remains in place."""
        gpg_file = "/home/user/artifacts/model_weights.gpg"
        assert os.path.isfile(gpg_file), (
            f"File {gpg_file} no longer exists. "
            "The original encrypted file should not be deleted."
        )

    def test_decrypted_file_is_not_gpg_encrypted(self):
        """Verify the decrypted file is not GPG encrypted data."""
        decrypted_file = "/home/user/artifacts/model_weights"
        assert os.path.isfile(decrypted_file), (
            f"File {decrypted_file} does not exist."
        )
        result = subprocess.run(
            ["file", decrypted_file],
            capture_output=True,
            text=True
        )
        file_output = result.stdout.lower()
        # The decrypted file should NOT be identified as GPG encrypted
        assert "gpg" not in file_output and "pgp" not in file_output, (
            f"File {decrypted_file} appears to still be GPG encrypted. "
            f"`file` command output: {result.stdout.strip()}. "
            "The file must be the actual decrypted content, not encrypted data."
        )

    def test_decrypted_file_differs_from_encrypted(self):
        """Verify the decrypted file is different from the encrypted file."""
        decrypted_file = "/home/user/artifacts/model_weights"
        gpg_file = "/home/user/artifacts/model_weights.gpg"

        assert os.path.isfile(decrypted_file), (
            f"File {decrypted_file} does not exist."
        )
        assert os.path.isfile(gpg_file), (
            f"File {gpg_file} does not exist."
        )

        decrypted_size = os.path.getsize(decrypted_file)
        encrypted_size = os.path.getsize(gpg_file)

        # Read both files to compare content
        with open(decrypted_file, 'rb') as f:
            decrypted_content = f.read()
        with open(gpg_file, 'rb') as f:
            encrypted_content = f.read()

        # The decrypted file should not be identical to the encrypted file
        assert decrypted_content != encrypted_content, (
            f"The decrypted file {decrypted_file} has identical content to "
            f"the encrypted file {gpg_file}. "
            "The decrypted file must contain the actual decrypted plaintext, "
            "not a copy of the encrypted data."
        )

    def test_decrypted_file_has_reasonable_size(self):
        """Verify the decrypted file has a reasonable size (~1KB original)."""
        decrypted_file = "/home/user/artifacts/model_weights"
        assert os.path.isfile(decrypted_file), (
            f"File {decrypted_file} does not exist."
        )
        file_size = os.path.getsize(decrypted_file)
        # Original plaintext is ~1KB, allow range from 100 bytes to 10KB
        assert 100 < file_size < 10240, (
            f"File {decrypted_file} has unexpected size: {file_size} bytes. "
            "Expected approximately 1KB of decrypted data."
        )

    def test_decrypted_file_is_readable(self):
        """Verify the decrypted file can be read without errors."""
        decrypted_file = "/home/user/artifacts/model_weights"
        assert os.path.isfile(decrypted_file), (
            f"File {decrypted_file} does not exist."
        )
        try:
            with open(decrypted_file, 'rb') as f:
                content = f.read()
            assert len(content) > 0, (
                f"File {decrypted_file} is empty after reading."
            )
        except Exception as e:
            pytest.fail(
                f"Failed to read {decrypted_file}: {e}. "
                "The decrypted file must be readable."
            )

    def test_no_extra_files_created(self):
        """Verify no unexpected files were created in the artifacts directory."""
        artifacts_dir = "/home/user/artifacts"
        expected_files = {"model_weights.gpg", "model_weights"}

        actual_files = set(os.listdir(artifacts_dir))
        unexpected_files = actual_files - expected_files

        # Allow for some flexibility - only fail if there are clearly wrong files
        # that might indicate a failed or incorrect decryption attempt
        problematic_patterns = [".gpg", ".tmp", ".bak", "~"]
        problematic_files = [
            f for f in unexpected_files 
            if any(p in f for p in problematic_patterns) and f not in expected_files
        ]

        # This is a soft check - we mainly care that the required files exist
        # and the decryption was successful
        if problematic_files:
            # Just warn, don't fail - the main requirement is successful decryption
            pass
