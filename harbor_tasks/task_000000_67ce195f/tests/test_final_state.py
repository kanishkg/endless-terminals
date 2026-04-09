# test_final_state.py
"""
Tests to validate the final state of the operating system after the student
has completed the PostgreSQL backup task.
"""

import gzip
import hashlib
import os
import re
import tarfile
import pytest


class TestBackupArchiveExists:
    """Tests for the backup archive file existence and basic properties."""

    def test_backup_archive_exists(self):
        """The backup archive file must exist at the specified location."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        assert os.path.exists(path), (
            f"Backup archive '{path}' does not exist. "
            "You need to create a gzipped tar archive of the postgres_config directory."
        )

    def test_backup_archive_is_file(self):
        """The backup archive must be a regular file."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        assert os.path.isfile(path), (
            f"'{path}' exists but is not a regular file. "
            "It should be a gzipped tar archive file."
        )

    def test_backup_archive_not_empty(self):
        """The backup archive must not be empty."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        if os.path.exists(path):
            size = os.path.getsize(path)
            assert size > 0, (
                f"Backup archive '{path}' is empty (0 bytes). "
                "The archive should contain the PostgreSQL configuration files."
            )


class TestBackupArchiveValidity:
    """Tests to verify the backup archive is a valid gzipped tar archive."""

    def test_backup_is_valid_gzip(self):
        """The backup archive must be a valid gzip file."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        if not os.path.exists(path):
            pytest.skip("Backup archive does not exist")

        try:
            with gzip.open(path, 'rb') as f:
                # Try to read a small portion to verify it's valid gzip
                f.read(1)
        except gzip.BadGzipFile:
            pytest.fail(
                f"'{path}' is not a valid gzip file. "
                "Make sure you created the archive with gzip compression (tar -czf)."
            )
        except Exception as e:
            pytest.fail(
                f"Error reading '{path}' as gzip: {e}. "
                "The file should be a valid gzipped tar archive."
            )

    def test_backup_is_valid_tar(self):
        """The backup archive must be a valid tar archive."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        if not os.path.exists(path):
            pytest.skip("Backup archive does not exist")

        try:
            with tarfile.open(path, 'r:gz') as tar:
                # Get the list of members to verify it's a valid tar
                members = tar.getnames()
                assert len(members) > 0, (
                    "The tar archive is empty. "
                    "It should contain the PostgreSQL configuration files."
                )
        except tarfile.TarError as e:
            pytest.fail(
                f"'{path}' is not a valid tar archive: {e}. "
                "Make sure you created a proper tar.gz archive."
            )


class TestBackupArchiveContents:
    """Tests to verify the backup archive contains the expected files."""

    def test_archive_contains_postgresql_conf(self):
        """The archive must contain postgresql.conf."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        if not os.path.exists(path):
            pytest.skip("Backup archive does not exist")

        try:
            with tarfile.open(path, 'r:gz') as tar:
                members = tar.getnames()
                found = any('postgresql.conf' in m for m in members)
                assert found, (
                    f"Archive does not contain 'postgresql.conf'. "
                    f"Archive contents: {members}. "
                    "Make sure you archived the postgres_config directory."
                )
        except tarfile.TarError:
            pytest.skip("Archive is not a valid tar file")

    def test_archive_contains_pg_hba_conf(self):
        """The archive must contain pg_hba.conf."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        if not os.path.exists(path):
            pytest.skip("Backup archive does not exist")

        try:
            with tarfile.open(path, 'r:gz') as tar:
                members = tar.getnames()
                found = any('pg_hba.conf' in m for m in members)
                assert found, (
                    f"Archive does not contain 'pg_hba.conf'. "
                    f"Archive contents: {members}. "
                    "Make sure you archived the postgres_config directory."
                )
        except tarfile.TarError:
            pytest.skip("Archive is not a valid tar file")

    def test_archive_contains_recovery_conf(self):
        """The archive must contain recovery.conf."""
        path = "/home/user/backups/pg_config_backup.tar.gz"
        if not os.path.exists(path):
            pytest.skip("Backup archive does not exist")

        try:
            with tarfile.open(path, 'r:gz') as tar:
                members = tar.getnames()
                found = any('recovery.conf' in m for m in members)
                assert found, (
                    f"Archive does not contain 'recovery.conf'. "
                    f"Archive contents: {members}. "
                    "Make sure you archived the postgres_config directory."
                )
        except tarfile.TarError:
            pytest.skip("Archive is not a valid tar file")


class TestVerificationLogExists:
    """Tests for the verification log file existence."""

    def test_verification_log_exists(self):
        """The verification log file must exist at the specified location."""
        path = "/home/user/backups/backup_verification.log"
        assert os.path.exists(path), (
            f"Verification log '{path}' does not exist. "
            "You need to create a verification log with the backup details."
        )

    def test_verification_log_is_file(self):
        """The verification log must be a regular file."""
        path = "/home/user/backups/backup_verification.log"
        assert os.path.isfile(path), (
            f"'{path}' exists but is not a regular file. "
            "It should be a text log file."
        )

    def test_verification_log_not_empty(self):
        """The verification log must not be empty."""
        path = "/home/user/backups/backup_verification.log"
        if os.path.exists(path):
            size = os.path.getsize(path)
            assert size > 0, (
                f"Verification log '{path}' is empty. "
                "It should contain the backup verification report."
            )


class TestVerificationLogFormat:
    """Tests to verify the verification log has the correct format."""

    def test_log_has_at_least_three_lines(self):
        """The verification log must have at least 3 lines."""
        path = "/home/user/backups/backup_verification.log"
        if not os.path.exists(path):
            pytest.skip("Verification log does not exist")

        with open(path, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 3, (
            f"Verification log has only {len(lines)} line(s), expected at least 3. "
            "The log should contain: header, MD5 checksum, and file count."
        )

    def test_first_line_is_header(self):
        """The first line must be exactly 'BACKUP VERIFICATION REPORT'."""
        path = "/home/user/backups/backup_verification.log"
        if not os.path.exists(path):
            pytest.skip("Verification log does not exist")

        with open(path, 'r') as f:
            first_line = f.readline().strip()

        expected = "BACKUP VERIFICATION REPORT"
        assert first_line == expected, (
            f"First line is '{first_line}', expected '{expected}'. "
            "The first line must be exactly 'BACKUP VERIFICATION REPORT'."
        )

    def test_second_line_starts_with_md5(self):
        """The second line must start with 'MD5: '."""
        path = "/home/user/backups/backup_verification.log"
        if not os.path.exists(path):
            pytest.skip("Verification log does not exist")

        with open(path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 2:
            pytest.skip("Log has fewer than 2 lines")

        second_line = lines[1].strip()
        assert second_line.startswith("MD5: "), (
            f"Second line is '{second_line}', expected it to start with 'MD5: '. "
            "The format should be 'MD5: <checksum_value>'."
        )

    def test_second_line_has_valid_md5_format(self):
        """The second line must contain a valid 32-character hex MD5 checksum."""
        path = "/home/user/backups/backup_verification.log"
        if not os.path.exists(path):
            pytest.skip("Verification log does not exist")

        with open(path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 2:
            pytest.skip("Log has fewer than 2 lines")

        second_line = lines[1].strip()
        # Extract the checksum part after "MD5: "
        if second_line.startswith("MD5: "):
            checksum = second_line[5:].strip()
            # MD5 checksums are 32 hexadecimal characters
            md5_pattern = re.compile(r'^[a-fA-F0-9]{32}$')
            assert md5_pattern.match(checksum), (
                f"MD5 checksum '{checksum}' is not a valid 32-character hex string. "
                "MD5 checksums should be exactly 32 hexadecimal characters."
            )
        else:
            pytest.fail("Second line does not start with 'MD5: '")

    def test_third_line_has_file_count_format(self):
        """The third line must match the format 'FILE_COUNT: <number>'."""
        path = "/home/user/backups/backup_verification.log"
        if not os.path.exists(path):
            pytest.skip("Verification log does not exist")

        with open(path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 3:
            pytest.skip("Log has fewer than 3 lines")

        third_line = lines[2].strip()
        file_count_pattern = re.compile(r'^FILE_COUNT: \d+$')
        assert file_count_pattern.match(third_line), (
            f"Third line is '{third_line}', expected format 'FILE_COUNT: <number>'. "
            "The file count should be a positive integer."
        )


class TestVerificationLogAccuracy:
    """Tests to verify the verification log contains accurate information."""

    def test_md5_checksum_matches_archive(self):
        """The MD5 checksum in the log must match the actual archive checksum."""
        log_path = "/home/user/backups/backup_verification.log"
        archive_path = "/home/user/backups/pg_config_backup.tar.gz"

        if not os.path.exists(log_path):
            pytest.skip("Verification log does not exist")
        if not os.path.exists(archive_path):
            pytest.skip("Backup archive does not exist")

        # Read the checksum from the log
        with open(log_path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 2:
            pytest.skip("Log has fewer than 2 lines")

        second_line = lines[1].strip()
        if not second_line.startswith("MD5: "):
            pytest.skip("Second line does not have MD5 format")

        logged_checksum = second_line[5:].strip().lower()

        # Calculate the actual MD5 checksum of the archive
        md5_hash = hashlib.md5()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5_hash.update(chunk)
        actual_checksum = md5_hash.hexdigest().lower()

        assert logged_checksum == actual_checksum, (
            f"MD5 checksum in log '{logged_checksum}' does not match "
            f"actual archive checksum '{actual_checksum}'. "
            "The checksum in the log must be calculated from the archive file."
        )

    def test_file_count_is_reasonable(self):
        """The file count should match the number of entries in the archive."""
        log_path = "/home/user/backups/backup_verification.log"
        archive_path = "/home/user/backups/pg_config_backup.tar.gz"

        if not os.path.exists(log_path):
            pytest.skip("Verification log does not exist")
        if not os.path.exists(archive_path):
            pytest.skip("Backup archive does not exist")

        # Read the file count from the log
        with open(log_path, 'r') as f:
            lines = f.readlines()

        if len(lines) < 3:
            pytest.skip("Log has fewer than 3 lines")

        third_line = lines[2].strip()
        match = re.match(r'^FILE_COUNT: (\d+)$', third_line)
        if not match:
            pytest.skip("Third line does not have FILE_COUNT format")

        logged_count = int(match.group(1))

        # Count entries in the archive
        try:
            with tarfile.open(archive_path, 'r:gz') as tar:
                actual_count = len(tar.getnames())
        except tarfile.TarError:
            pytest.skip("Archive is not a valid tar file")

        assert logged_count == actual_count, (
            f"FILE_COUNT in log is {logged_count}, but archive contains {actual_count} entries. "
            "The file count should match the number of files/directories in the archive."
        )


class TestBackupsDirectoryState:
    """Tests for the final state of the backups directory."""

    def test_backups_directory_still_exists(self):
        """The backups directory must still exist after task completion."""
        path = "/home/user/backups"
        assert os.path.exists(path), (
            f"Backups directory '{path}' does not exist. "
            "The directory should exist and contain the backup files."
        )

    def test_backups_directory_contains_required_files(self):
        """The backups directory must contain both required files."""
        backups_dir = "/home/user/backups"
        if not os.path.exists(backups_dir):
            pytest.skip("Backups directory does not exist")

        required_files = ['pg_config_backup.tar.gz', 'backup_verification.log']
        existing_files = os.listdir(backups_dir)

        for required_file in required_files:
            assert required_file in existing_files, (
                f"Required file '{required_file}' not found in '{backups_dir}'. "
                f"Directory contains: {existing_files}"
            )
