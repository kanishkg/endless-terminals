# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has completed the CI/CD pipeline backup task.
"""

import os
import tarfile
import hashlib
import gzip
from datetime import date
import pytest


class TestBackupsDirectoryExists:
    """Test that the backups directory exists."""

    def test_backups_directory_exists(self):
        """The /home/user/backups directory must exist."""
        path = "/home/user/backups"
        assert os.path.isdir(path), (
            f"Directory '{path}' does not exist. "
            "The backups directory must be created as part of the task."
        )


class TestArchiveFile:
    """Test that the tar.gz archive exists and is valid."""

    def test_archive_file_exists(self):
        """The pipelines_backup.tar.gz file must exist."""
        path = "/home/user/backups/pipelines_backup.tar.gz"
        assert os.path.isfile(path), (
            f"Archive file '{path}' does not exist. "
            "A compressed tar archive of the ci-pipelines directory must be created."
        )

    def test_archive_is_valid_gzip(self):
        """The archive must be a valid gzip file."""
        path = "/home/user/backups/pipelines_backup.tar.gz"
        try:
            with gzip.open(path, 'rb') as f:
                # Try to read a small amount to verify it's valid gzip
                f.read(1)
        except (gzip.BadGzipFile, OSError) as e:
            pytest.fail(
                f"File '{path}' is not a valid gzip file: {e}. "
                "The archive must be gzip-compressed."
            )

    def test_archive_is_valid_tar(self):
        """The archive must be a valid tar archive."""
        path = "/home/user/backups/pipelines_backup.tar.gz"
        assert tarfile.is_tarfile(path), (
            f"File '{path}' is not a valid tar archive. "
            "The file must be a valid tar.gz archive."
        )

    def test_archive_contains_jenkinsfile(self):
        """The archive must contain the Jenkinsfile."""
        path = "/home/user/backups/pipelines_backup.tar.gz"
        with tarfile.open(path, 'r:gz') as tar:
            names = tar.getnames()
            # Check for Jenkinsfile in any path within the archive
            jenkinsfile_found = any('Jenkinsfile' in name for name in names)
            assert jenkinsfile_found, (
                f"Archive does not contain 'Jenkinsfile'. "
                f"Archive contents: {names}. "
                "The Jenkinsfile must be included in the backup."
            )

    def test_archive_contains_gitlab_ci_yml(self):
        """The archive must contain the .gitlab-ci.yml file."""
        path = "/home/user/backups/pipelines_backup.tar.gz"
        with tarfile.open(path, 'r:gz') as tar:
            names = tar.getnames()
            # Check for .gitlab-ci.yml in any path within the archive
            gitlab_ci_found = any('.gitlab-ci.yml' in name for name in names)
            assert gitlab_ci_found, (
                f"Archive does not contain '.gitlab-ci.yml'. "
                f"Archive contents: {names}. "
                "The .gitlab-ci.yml must be included in the backup."
            )

    def test_archive_contains_azure_pipelines_yml(self):
        """The archive must contain the azure-pipelines.yml file."""
        path = "/home/user/backups/pipelines_backup.tar.gz"
        with tarfile.open(path, 'r:gz') as tar:
            names = tar.getnames()
            # Check for azure-pipelines.yml in any path within the archive
            azure_found = any('azure-pipelines.yml' in name for name in names)
            assert azure_found, (
                f"Archive does not contain 'azure-pipelines.yml'. "
                f"Archive contents: {names}. "
                "The azure-pipelines.yml must be included in the backup."
            )


class TestChecksumFile:
    """Test that the SHA256 checksum file exists and is valid."""

    def test_checksum_file_exists(self):
        """The pipelines_backup.sha256 file must exist."""
        path = "/home/user/backups/pipelines_backup.sha256"
        assert os.path.isfile(path), (
            f"Checksum file '{path}' does not exist. "
            "A SHA256 checksum file must be created for the backup archive."
        )

    def test_checksum_file_format(self):
        """The checksum file must have the correct format."""
        path = "/home/user/backups/pipelines_backup.sha256"
        with open(path, 'r') as f:
            content = f.read().strip()

        # Expected format: <hash>  pipelines_backup.tar.gz (two spaces between)
        assert "pipelines_backup.tar.gz" in content, (
            f"Checksum file does not contain the filename 'pipelines_backup.tar.gz'. "
            f"Content: '{content}'. "
            "The checksum file should contain the hash followed by two spaces and the filename."
        )

        # Check for two spaces before filename
        assert "  pipelines_backup.tar.gz" in content, (
            f"Checksum file format is incorrect. Expected two spaces before filename. "
            f"Content: '{content}'. "
            "The format should be: <hash>  pipelines_backup.tar.gz"
        )

    def test_checksum_value_is_valid_sha256(self):
        """The checksum value must be a valid 64-character hex string."""
        path = "/home/user/backups/pipelines_backup.sha256"
        with open(path, 'r') as f:
            content = f.read().strip()

        # Extract the hash (everything before the two spaces)
        parts = content.split("  ")
        assert len(parts) >= 1, (
            f"Could not parse checksum file. Content: '{content}'"
        )

        hash_value = parts[0].strip()
        assert len(hash_value) == 64, (
            f"SHA256 hash should be 64 characters, got {len(hash_value)}. "
            f"Hash value: '{hash_value}'"
        )

        # Verify it's a valid hex string
        try:
            int(hash_value, 16)
        except ValueError:
            pytest.fail(
                f"Hash value '{hash_value}' is not a valid hexadecimal string."
            )

    def test_checksum_matches_archive(self):
        """The checksum must match the actual SHA256 hash of the archive."""
        checksum_path = "/home/user/backups/pipelines_backup.sha256"
        archive_path = "/home/user/backups/pipelines_backup.tar.gz"

        # Read the stored checksum
        with open(checksum_path, 'r') as f:
            content = f.read().strip()
        stored_hash = content.split("  ")[0].strip().lower()

        # Calculate the actual checksum
        sha256_hash = hashlib.sha256()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256_hash.update(chunk)
        actual_hash = sha256_hash.hexdigest().lower()

        assert stored_hash == actual_hash, (
            f"Checksum mismatch! "
            f"Stored hash: '{stored_hash}', "
            f"Actual hash: '{actual_hash}'. "
            "The checksum file must contain the correct SHA256 hash of the archive."
        )


class TestBackupLogFile:
    """Test that the backup log file exists and has correct content."""

    def test_backup_log_exists(self):
        """The backup.log file must exist."""
        path = "/home/user/backups/backup.log"
        assert os.path.isfile(path), (
            f"Backup log file '{path}' does not exist. "
            "A backup log file must be created with the backup details."
        )

    def test_backup_log_has_three_lines(self):
        """The backup log must have exactly three lines."""
        path = "/home/user/backups/backup.log"
        with open(path, 'r') as f:
            lines = f.read().strip().split('\n')

        assert len(lines) == 3, (
            f"Backup log should have exactly 3 lines, got {len(lines)}. "
            f"Lines: {lines}"
        )

    def test_backup_log_line1_date_format(self):
        """Line 1 must contain BACKUP_DATE with today's date in YYYY-MM-DD format."""
        path = "/home/user/backups/backup.log"
        with open(path, 'r') as f:
            lines = f.read().strip().split('\n')

        line1 = lines[0] if lines else ""
        assert line1.startswith("BACKUP_DATE="), (
            f"Line 1 should start with 'BACKUP_DATE='. "
            f"Got: '{line1}'"
        )

        # Extract the date value
        date_value = line1.replace("BACKUP_DATE=", "")
        today = date.today().strftime("%Y-%m-%d")

        assert date_value == today, (
            f"BACKUP_DATE should be today's date ({today}). "
            f"Got: '{date_value}'"
        )

    def test_backup_log_line2_archive_file(self):
        """Line 2 must contain ARCHIVE_FILE=pipelines_backup.tar.gz."""
        path = "/home/user/backups/backup.log"
        with open(path, 'r') as f:
            lines = f.read().strip().split('\n')

        line2 = lines[1] if len(lines) > 1 else ""
        expected = "ARCHIVE_FILE=pipelines_backup.tar.gz"

        assert line2 == expected, (
            f"Line 2 should be '{expected}'. "
            f"Got: '{line2}'"
        )

    def test_backup_log_line3_status(self):
        """Line 3 must contain STATUS=SUCCESS."""
        path = "/home/user/backups/backup.log"
        with open(path, 'r') as f:
            lines = f.read().strip().split('\n')

        line3 = lines[2] if len(lines) > 2 else ""
        expected = "STATUS=SUCCESS"

        assert line3 == expected, (
            f"Line 3 should be '{expected}'. "
            f"Got: '{line3}'"
        )


class TestSourceDirectoryPreserved:
    """Test that the source directory is still intact after backup."""

    def test_source_directory_still_exists(self):
        """The source ci-pipelines directory should still exist after backup."""
        path = "/home/user/ci-pipelines"
        assert os.path.isdir(path), (
            f"Source directory '{path}' no longer exists. "
            "The backup operation should not remove the source files."
        )

    def test_source_files_still_exist(self):
        """All source files should still exist after backup."""
        files = [
            "/home/user/ci-pipelines/Jenkinsfile",
            "/home/user/ci-pipelines/.gitlab-ci.yml",
            "/home/user/ci-pipelines/azure-pipelines.yml"
        ]
        for filepath in files:
            assert os.path.isfile(filepath), (
                f"Source file '{filepath}' no longer exists. "
                "The backup operation should not remove the source files."
            )
