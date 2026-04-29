# test_initial_state.py
"""
Pre-task validation tests to verify the initial state before the student
performs the disk space analysis task.
"""

import os
import subprocess
import pytest


class TestVarDataStructure:
    """Verify /var/data exists and has the expected structure."""

    def test_var_data_exists(self):
        """Check that /var/data directory exists."""
        assert os.path.exists("/var/data"), "/var/data directory does not exist"

    def test_var_data_is_directory(self):
        """Check that /var/data is a directory."""
        assert os.path.isdir("/var/data"), "/var/data is not a directory"

    def test_var_data_is_readable(self):
        """Check that /var/data is readable."""
        assert os.access("/var/data", os.R_OK), "/var/data is not readable"

    def test_var_data_logs_subdir_exists(self):
        """Check that /var/data/logs subdirectory exists."""
        assert os.path.isdir("/var/data/logs"), "/var/data/logs directory does not exist"

    def test_var_data_cache_subdir_exists(self):
        """Check that /var/data/cache subdirectory exists."""
        assert os.path.isdir("/var/data/cache"), "/var/data/cache directory does not exist"

    def test_var_data_uploads_subdir_exists(self):
        """Check that /var/data/uploads subdirectory exists."""
        assert os.path.isdir("/var/data/uploads"), "/var/data/uploads directory does not exist"

    def test_var_data_tmp_subdir_exists(self):
        """Check that /var/data/tmp subdirectory exists."""
        assert os.path.isdir("/var/data/tmp"), "/var/data/tmp directory does not exist"


class TestLargeFilesExist:
    """Verify all expected large files (>100MB) exist with correct sizes."""

    LARGE_FILES = {
        "/var/data/logs/app.log.2024-01-15": 247 * 1024 * 1024,  # 247MB
        "/var/data/logs/debug.log": 189 * 1024 * 1024,  # 189MB
        "/var/data/cache/thumbnails.db": 312 * 1024 * 1024,  # 312MB
        "/var/data/uploads/video_backup.tar": 524 * 1024 * 1024,  # 524MB
        "/var/data/tmp/core.1847": 156 * 1024 * 1024,  # 156MB
    }

    def test_app_log_exists(self):
        """Check that /var/data/logs/app.log.2024-01-15 exists."""
        filepath = "/var/data/logs/app.log.2024-01-15"
        assert os.path.isfile(filepath), f"{filepath} does not exist"

    def test_app_log_size(self):
        """Check that /var/data/logs/app.log.2024-01-15 is approximately 247MB."""
        filepath = "/var/data/logs/app.log.2024-01-15"
        size = os.path.getsize(filepath)
        expected_min = 240 * 1024 * 1024  # Allow some tolerance
        expected_max = 255 * 1024 * 1024
        assert expected_min <= size <= expected_max, \
            f"{filepath} size {size} bytes is not approximately 247MB"

    def test_debug_log_exists(self):
        """Check that /var/data/logs/debug.log exists."""
        filepath = "/var/data/logs/debug.log"
        assert os.path.isfile(filepath), f"{filepath} does not exist"

    def test_debug_log_size(self):
        """Check that /var/data/logs/debug.log is approximately 189MB."""
        filepath = "/var/data/logs/debug.log"
        size = os.path.getsize(filepath)
        expected_min = 180 * 1024 * 1024
        expected_max = 200 * 1024 * 1024
        assert expected_min <= size <= expected_max, \
            f"{filepath} size {size} bytes is not approximately 189MB"

    def test_thumbnails_db_exists(self):
        """Check that /var/data/cache/thumbnails.db exists."""
        filepath = "/var/data/cache/thumbnails.db"
        assert os.path.isfile(filepath), f"{filepath} does not exist"

    def test_thumbnails_db_size(self):
        """Check that /var/data/cache/thumbnails.db is approximately 312MB."""
        filepath = "/var/data/cache/thumbnails.db"
        size = os.path.getsize(filepath)
        expected_min = 305 * 1024 * 1024
        expected_max = 320 * 1024 * 1024
        assert expected_min <= size <= expected_max, \
            f"{filepath} size {size} bytes is not approximately 312MB"

    def test_video_backup_exists(self):
        """Check that /var/data/uploads/video_backup.tar exists."""
        filepath = "/var/data/uploads/video_backup.tar"
        assert os.path.isfile(filepath), f"{filepath} does not exist"

    def test_video_backup_size(self):
        """Check that /var/data/uploads/video_backup.tar is approximately 524MB."""
        filepath = "/var/data/uploads/video_backup.tar"
        size = os.path.getsize(filepath)
        expected_min = 515 * 1024 * 1024
        expected_max = 535 * 1024 * 1024
        assert expected_min <= size <= expected_max, \
            f"{filepath} size {size} bytes is not approximately 524MB"

    def test_core_dump_exists(self):
        """Check that /var/data/tmp/core.1847 exists."""
        filepath = "/var/data/tmp/core.1847"
        assert os.path.isfile(filepath), f"{filepath} does not exist"

    def test_core_dump_size(self):
        """Check that /var/data/tmp/core.1847 is approximately 156MB."""
        filepath = "/var/data/tmp/core.1847"
        size = os.path.getsize(filepath)
        expected_min = 150 * 1024 * 1024
        expected_max = 165 * 1024 * 1024
        assert expected_min <= size <= expected_max, \
            f"{filepath} size {size} bytes is not approximately 156MB"

    def test_exactly_five_large_files(self):
        """Verify there are exactly 5 files over 100MB in /var/data."""
        threshold = 100 * 1024 * 1024  # 100MB in bytes
        large_files = []
        for root, dirs, files in os.walk("/var/data"):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    if os.path.getsize(filepath) >= threshold:
                        large_files.append(filepath)
                except OSError:
                    pass
        assert len(large_files) == 5, \
            f"Expected 5 files over 100MB, found {len(large_files)}: {large_files}"


class TestHomeUserDirectory:
    """Verify /home/user exists and is writable."""

    def test_home_user_exists(self):
        """Check that /home/user directory exists."""
        assert os.path.exists("/home/user"), "/home/user directory does not exist"

    def test_home_user_is_directory(self):
        """Check that /home/user is a directory."""
        assert os.path.isdir("/home/user"), "/home/user is not a directory"

    def test_home_user_is_writable(self):
        """Check that /home/user is writable."""
        assert os.access("/home/user", os.W_OK), "/home/user is not writable"


class TestOutputFileNotExists:
    """Verify the output file does not exist yet."""

    def test_big_files_txt_not_exists(self):
        """Check that /home/user/big_files.txt does not exist yet."""
        assert not os.path.exists("/home/user/big_files.txt"), \
            "/home/user/big_files.txt already exists - should not exist before task"


class TestRequiredTools:
    """Verify standard coreutils are available."""

    @pytest.mark.parametrize("tool", ["find", "du", "sort", "awk", "head", "tail"])
    def test_tool_available(self, tool):
        """Check that required tool is available in PATH."""
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Required tool '{tool}' is not available in PATH"


class TestSmallerFilesExist:
    """Verify there are smaller files to create realistic noise."""

    def test_has_files_under_100mb(self):
        """Check that /var/data contains files under 100MB for realistic noise."""
        threshold = 100 * 1024 * 1024
        small_files = []
        for root, dirs, files in os.walk("/var/data"):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    if os.path.getsize(filepath) < threshold:
                        small_files.append(filepath)
                except OSError:
                    pass
        assert len(small_files) > 0, \
            "Expected some files under 100MB for realistic noise, found none"
