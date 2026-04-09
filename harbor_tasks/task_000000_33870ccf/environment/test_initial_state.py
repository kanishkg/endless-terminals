# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
performs the disk usage analysis task.
"""

import os
import pytest
from pathlib import Path
import time


HOME_DIR = "/home/user"
APP_DATA_DIR = "/home/user/app_data"


class TestDirectoryStructure:
    """Test that all required directories exist."""

    def test_home_directory_exists(self):
        """Verify /home/user exists."""
        assert os.path.isdir(HOME_DIR), f"Home directory {HOME_DIR} does not exist"

    def test_app_data_directory_exists(self):
        """Verify /home/user/app_data exists."""
        assert os.path.isdir(APP_DATA_DIR), f"App data directory {APP_DATA_DIR} does not exist"

    @pytest.mark.parametrize("subdir", [
        "logs",
        "uploads",
        "uploads/images",
        "uploads/videos",
        "uploads/documents",
        "cache",
        "backups",
        "config",
    ])
    def test_subdirectories_exist(self, subdir):
        """Verify all required subdirectories exist."""
        full_path = os.path.join(APP_DATA_DIR, subdir)
        assert os.path.isdir(full_path), f"Directory {full_path} does not exist"


class TestLogFiles:
    """Test that log files exist with correct properties."""

    @pytest.mark.parametrize("filename,expected_size_mb", [
        ("app.log", 15),
        ("error.log", 8),
        ("access.log", 25),
        ("debug.log", 3),
    ])
    def test_log_files_exist_with_correct_size(self, filename, expected_size_mb):
        """Verify log files exist with approximately correct sizes."""
        filepath = os.path.join(APP_DATA_DIR, "logs", filename)
        assert os.path.isfile(filepath), f"Log file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = expected_size_mb * 1024 * 1024
        # Allow 5% tolerance for size
        tolerance = expected_size * 0.05
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"

    @pytest.mark.parametrize("filename,days_old", [
        ("app.log", 10),
        ("error.log", 15),
        ("debug.log", 20),
    ])
    def test_old_log_files_have_correct_mtime(self, filename, days_old):
        """Verify old log files have modification time older than 7 days."""
        filepath = os.path.join(APP_DATA_DIR, "logs", filename)
        assert os.path.isfile(filepath), f"Log file {filepath} does not exist"

        mtime = os.path.getmtime(filepath)
        current_time = time.time()
        age_days = (current_time - mtime) / (24 * 3600)

        # Check that file is at least 7 days old (the threshold for "old" logs)
        assert age_days > 7, \
            f"File {filepath} should be older than 7 days, but is only {age_days:.1f} days old"

    def test_access_log_is_recent(self):
        """Verify access.log is recent (modified within 7 days)."""
        filepath = os.path.join(APP_DATA_DIR, "logs", "access.log")
        assert os.path.isfile(filepath), f"Log file {filepath} does not exist"

        mtime = os.path.getmtime(filepath)
        current_time = time.time()
        age_days = (current_time - mtime) / (24 * 3600)

        assert age_days <= 7, \
            f"File {filepath} should be recent (<=7 days old), but is {age_days:.1f} days old"


class TestUploadFiles:
    """Test that upload files exist with correct properties."""

    @pytest.mark.parametrize("subpath,expected_size_mb", [
        ("images/photo1.jpg", 2),
        ("images/photo2.jpg", 3),
        ("images/banner.png", 55),
        ("videos/demo.mp4", 120),
        ("videos/tutorial.mp4", 85),
        ("documents/report.pdf", 5),
        ("documents/data.csv", 10),
    ])
    def test_upload_files_exist_with_correct_size(self, subpath, expected_size_mb):
        """Verify upload files exist with approximately correct sizes."""
        filepath = os.path.join(APP_DATA_DIR, "uploads", subpath)
        assert os.path.isfile(filepath), f"Upload file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = expected_size_mb * 1024 * 1024
        # Allow 5% tolerance for size
        tolerance = expected_size * 0.05
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"


class TestCacheFiles:
    """Test that cache files exist with correct properties."""

    @pytest.mark.parametrize("filename,expected_size_mb", [
        ("session_cache.dat", 45),
        ("query_cache.dat", 75),
        ("temp.tmp", 1),
    ])
    def test_cache_files_exist_with_correct_size(self, filename, expected_size_mb):
        """Verify cache files exist with approximately correct sizes."""
        filepath = os.path.join(APP_DATA_DIR, "cache", filename)
        assert os.path.isfile(filepath), f"Cache file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = expected_size_mb * 1024 * 1024
        # Allow 5% tolerance for size
        tolerance = expected_size * 0.05
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"


class TestBackupFiles:
    """Test that backup files exist with correct properties."""

    def test_db_backup_old_exists_with_correct_size(self):
        """Verify db_backup_old.sql exists with correct size."""
        filepath = os.path.join(APP_DATA_DIR, "backups", "db_backup_old.sql")
        assert os.path.isfile(filepath), f"Backup file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = 200 * 1024 * 1024
        tolerance = expected_size * 0.05
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"

    def test_db_backup_old_is_old(self):
        """Verify db_backup_old.sql is modified more than 7 days ago."""
        filepath = os.path.join(APP_DATA_DIR, "backups", "db_backup_old.sql")
        assert os.path.isfile(filepath), f"Backup file {filepath} does not exist"

        mtime = os.path.getmtime(filepath)
        current_time = time.time()
        age_days = (current_time - mtime) / (24 * 3600)

        assert age_days > 7, \
            f"File {filepath} should be older than 7 days, but is only {age_days:.1f} days old"

    def test_db_backup_recent_exists_with_correct_size(self):
        """Verify db_backup_recent.sql exists with correct size."""
        filepath = os.path.join(APP_DATA_DIR, "backups", "db_backup_recent.sql")
        assert os.path.isfile(filepath), f"Backup file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = 180 * 1024 * 1024
        tolerance = expected_size * 0.05
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"

    def test_config_backup_exists_with_correct_size(self):
        """Verify config_backup.tar.gz exists with correct size."""
        filepath = os.path.join(APP_DATA_DIR, "backups", "config_backup.tar.gz")
        assert os.path.isfile(filepath), f"Backup file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = 500 * 1024  # 500KB
        tolerance = expected_size * 0.05
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"


class TestConfigFiles:
    """Test that config files exist with correct properties."""

    @pytest.mark.parametrize("filename,expected_size_kb", [
        ("app.conf", 2),
        ("database.yml", 1),
        ("settings.json", 3),
    ])
    def test_config_files_exist_with_correct_size(self, filename, expected_size_kb):
        """Verify config files exist with approximately correct sizes."""
        filepath = os.path.join(APP_DATA_DIR, "config", filename)
        assert os.path.isfile(filepath), f"Config file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        expected_size = expected_size_kb * 1024
        # Allow larger tolerance for small files
        tolerance = max(expected_size * 0.1, 512)  # At least 512 bytes tolerance
        assert abs(actual_size - expected_size) <= tolerance, \
            f"File {filepath} has size {actual_size} bytes, expected approximately {expected_size} bytes"


class TestLargeFilesExist:
    """Test that files larger than 50MB exist (for the report verification)."""

    @pytest.mark.parametrize("filepath", [
        "/home/user/app_data/uploads/images/banner.png",
        "/home/user/app_data/uploads/videos/demo.mp4",
        "/home/user/app_data/uploads/videos/tutorial.mp4",
        "/home/user/app_data/cache/query_cache.dat",
        "/home/user/app_data/backups/db_backup_old.sql",
        "/home/user/app_data/backups/db_backup_recent.sql",
    ])
    def test_large_file_exists_and_is_over_50mb(self, filepath):
        """Verify files that should be >50MB exist and are actually >50MB."""
        assert os.path.isfile(filepath), f"Large file {filepath} does not exist"

        actual_size = os.path.getsize(filepath)
        min_size = 50 * 1024 * 1024  # 50MB
        assert actual_size > min_size, \
            f"File {filepath} should be larger than 50MB, but is only {actual_size / (1024*1024):.1f}MB"


class TestOutputFileDoesNotExist:
    """Verify the output file does not exist yet (student needs to create it)."""

    def test_incident_report_does_not_exist(self):
        """Verify the incident report does not exist before the task."""
        filepath = "/home/user/incident_report.txt"
        assert not os.path.exists(filepath), \
            f"Output file {filepath} should not exist before the task is performed"
