# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the SHA256 verification task.
"""

import os
import subprocess
import pytest


class TestInitialState:
    """Test suite to verify the initial state for the SHA256 verification task."""

    def test_data_directory_exists(self):
        """Verify that /home/user/data/ directory exists."""
        data_dir = "/home/user/data"
        assert os.path.isdir(data_dir), f"Directory {data_dir} does not exist"

    def test_data_directory_readable(self):
        """Verify that /home/user/data/ is readable."""
        data_dir = "/home/user/data"
        assert os.access(data_dir, os.R_OK), f"Directory {data_dir} is not readable"

    def test_data_directory_writable(self):
        """Verify that /home/user/data/ is writable."""
        data_dir = "/home/user/data"
        assert os.access(data_dir, os.W_OK), f"Directory {data_dir} is not writable"

    def test_tarball_exists(self):
        """Verify that the tarball file exists."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        assert os.path.isfile(tarball_path), f"Tarball {tarball_path} does not exist"

    def test_tarball_is_reasonable_size(self):
        """Verify that the tarball is approximately 50MB (reasonable size check)."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        file_size = os.path.getsize(tarball_path)
        # Check that file is between 10MB and 100MB (allowing some flexibility)
        min_size = 10 * 1024 * 1024  # 10MB
        max_size = 100 * 1024 * 1024  # 100MB
        assert min_size <= file_size <= max_size, (
            f"Tarball size {file_size} bytes is outside expected range "
            f"({min_size} - {max_size} bytes)"
        )

    def test_tarball_is_readable(self):
        """Verify that the tarball is readable."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        assert os.access(tarball_path, os.R_OK), f"Tarball {tarball_path} is not readable"

    def test_sha256_file_exists(self):
        """Verify that the SHA256 checksum file exists."""
        sha256_path = "/home/user/data/imagenet_subset.sha256"
        assert os.path.isfile(sha256_path), f"SHA256 file {sha256_path} does not exist"

    def test_sha256_file_is_readable(self):
        """Verify that the SHA256 file is readable."""
        sha256_path = "/home/user/data/imagenet_subset.sha256"
        assert os.access(sha256_path, os.R_OK), f"SHA256 file {sha256_path} is not readable"

    def test_sha256_file_format(self):
        """Verify that the SHA256 file has the correct format."""
        sha256_path = "/home/user/data/imagenet_subset.sha256"
        with open(sha256_path, 'r') as f:
            content = f.read().strip()

        # Should be a single line
        lines = content.split('\n')
        assert len(lines) == 1, f"SHA256 file should contain exactly one line, found {len(lines)}"

        # Should be in format: <hash>  <filename> (two spaces between hash and filename)
        # or <hash> <filename> (one space)
        parts = content.split()
        assert len(parts) == 2, (
            f"SHA256 file should contain hash and filename separated by space(s), "
            f"found: {content}"
        )

        hash_value, filename = parts
        # SHA256 hash is 64 hex characters
        assert len(hash_value) == 64, (
            f"SHA256 hash should be 64 characters, found {len(hash_value)}"
        )
        assert all(c in '0123456789abcdefABCDEF' for c in hash_value), (
            f"SHA256 hash should contain only hexadecimal characters"
        )
        assert filename == "imagenet_subset.tar.gz", (
            f"SHA256 file should reference 'imagenet_subset.tar.gz', found '{filename}'"
        )

    def test_sha256sum_utility_available(self):
        """Verify that sha256sum utility is available."""
        result = subprocess.run(
            ["which", "sha256sum"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "sha256sum utility is not available in PATH"

    def test_sha256sum_utility_works(self):
        """Verify that sha256sum utility is functional."""
        result = subprocess.run(
            ["sha256sum", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "sha256sum utility is not working properly"

    def test_tarball_is_valid_gzip(self):
        """Verify that the tarball is a valid gzip file."""
        tarball_path = "/home/user/data/imagenet_subset.tar.gz"
        # Check gzip magic number
        with open(tarball_path, 'rb') as f:
            magic = f.read(2)
        assert magic == b'\x1f\x8b', f"File {tarball_path} does not appear to be a valid gzip file"

    def test_hash_matches_tarball(self):
        """Verify that the hash in the .sha256 file matches the actual tarball hash."""
        sha256_path = "/home/user/data/imagenet_subset.sha256"
        data_dir = "/home/user/data"

        # Run sha256sum -c to verify
        result = subprocess.run(
            ["sha256sum", "-c", "imagenet_subset.sha256"],
            cwd=data_dir,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"SHA256 verification failed. The hash in {sha256_path} does not match "
            f"the actual hash of the tarball. Output: {result.stdout} {result.stderr}"
        )
