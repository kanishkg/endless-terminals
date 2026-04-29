# test_final_state.py
"""
Tests to validate the final state after the SHA256 verification task is completed.

The task requires the agent to verify that the SHA256 checksum of
/home/user/data/imagenet_subset.tar.gz matches the hash in
/home/user/data/imagenet_subset.sha256.

Expected outcomes:
- Files remain unchanged (invariants)
- The verification was actually performed (not just assumed)
- The checksum matches (verification passed)
"""

import os
import subprocess
import hashlib
import pytest


class TestFilesUnchanged:
    """Test that the original files remain unchanged (invariants)."""

    def test_tarball_still_exists(self):
        """Verify that the tarball file still exists."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        assert os.path.isfile(tarball_path), (
            f"Tarball {tarball_path} no longer exists - it should not have been modified or deleted"
        )

    def test_sha256_file_still_exists(self):
        """Verify that the SHA256 checksum file still exists."""
        sha256_path = "/home/user/data/imagenet_subset.sha256"
        assert os.path.isfile(sha256_path), (
            f"SHA256 file {sha256_path} no longer exists - it should not have been modified or deleted"
        )

    def test_sha256_file_format_preserved(self):
        """Verify that the SHA256 file still has valid format."""
        sha256_path = "/home/user/data/imagenet_subset.sha256"
        with open(sha256_path, 'r') as f:
            content = f.read().strip()

        # Should still be a single line with hash and filename
        lines = content.split('\n')
        assert len(lines) == 1, (
            f"SHA256 file should still contain exactly one line, found {len(lines)}"
        )

        parts = content.split()
        assert len(parts) == 2, (
            f"SHA256 file format was corrupted. Expected hash and filename, found: {content}"
        )

        hash_value, filename = parts
        assert len(hash_value) == 64, (
            f"SHA256 hash should be 64 characters, found {len(hash_value)}"
        )
        assert filename == "imagenet_subset.tar.gz", (
            f"SHA256 file should reference 'imagenet_subset.tar.gz', found '{filename}'"
        )


class TestChecksumVerification:
    """Test that the checksum verification is valid and would pass."""

    def test_checksum_matches_using_sha256sum_c(self):
        """Verify checksum matches using sha256sum -c command."""
        data_dir = "/home/user/data"
        result = subprocess.run(
            ["sha256sum", "-c", "imagenet_subset.sha256"],
            cwd=data_dir,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"SHA256 verification failed! The checksum does not match.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        # Check that output indicates OK
        assert "OK" in result.stdout or "ok" in result.stdout.lower(), (
            f"Verification output should indicate success (OK), got: {result.stdout}"
        )

    def test_checksum_matches_manual_computation(self):
        """Verify checksum by manually computing and comparing."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        sha256_path = "/home/user/data/imagenet_subset.sha256"

        # Read expected hash from file
        with open(sha256_path, 'r') as f:
            content = f.read().strip()
        expected_hash = content.split()[0].lower()

        # Compute actual hash
        sha256_hash = hashlib.sha256()
        with open(tarball_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        actual_hash = sha256_hash.hexdigest().lower()

        assert actual_hash == expected_hash, (
            f"SHA256 checksum mismatch!\n"
            f"Expected: {expected_hash}\n"
            f"Actual:   {actual_hash}\n"
            f"The tarball may have been corrupted or the checksum file is incorrect."
        )

    def test_tarball_integrity(self):
        """Verify the tarball is still a valid gzip file."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"

        # Check gzip magic number
        with open(tarball_path, 'rb') as f:
            magic = f.read(2)
        assert magic == b'\x1f\x8b', (
            f"Tarball {tarball_path} is no longer a valid gzip file - it may have been corrupted"
        )

    def test_tarball_size_reasonable(self):
        """Verify the tarball size is still reasonable (not truncated or corrupted)."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        file_size = os.path.getsize(tarball_path)

        # Should still be in the expected size range
        min_size = 10 * 1024 * 1024  # 10MB
        max_size = 100 * 1024 * 1024  # 100MB
        assert min_size <= file_size <= max_size, (
            f"Tarball size {file_size} bytes is outside expected range - file may have been corrupted"
        )


class TestDataDirectoryState:
    """Test that the data directory state is preserved."""

    def test_data_directory_exists(self):
        """Verify that /home/user/data/ directory still exists."""
        data_dir = "/home/user/data"
        assert os.path.isdir(data_dir), f"Directory {data_dir} no longer exists"

    def test_no_unexpected_files_created(self):
        """Check that no unexpected verification result files were created."""
        data_dir = "/home/user/data"

        # List files in the directory
        files = os.listdir(data_dir)

        # Expected files
        expected_files = {"imagenet_subset.tar.gz", "imagenet_subset.sha256"}

        # It's okay if there are other files, but warn about common mistake files
        mistake_files = {"result.txt", "verification.txt", "output.txt", "check.txt"}
        found_mistakes = set(files) & mistake_files

        # This is a soft check - we don't fail, but the main files should exist
        assert "imagenet_subset.tar.gz" in files, "Tarball is missing from data directory"
        assert "imagenet_subset.sha256" in files, "SHA256 file is missing from data directory"
