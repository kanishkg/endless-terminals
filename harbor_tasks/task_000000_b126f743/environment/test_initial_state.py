# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the archive/restore scripts.
"""

import os
import stat
import subprocess
import pytest


HOME = "/home/user"
SCRIPTS_DIR = os.path.join(HOME, "scripts")
TEST_PAYLOAD_DIR = os.path.join(HOME, "test_payload")
ARTIFACTS_DIR = os.path.join(HOME, "artifacts")
ARCHIVE_SCRIPT = os.path.join(SCRIPTS_DIR, "archive.sh")
RESTORE_SCRIPT = os.path.join(SCRIPTS_DIR, "restore.sh")
BASHRC = os.path.join(HOME, ".bashrc")
COLLATE_SETTING = os.path.join(HOME, ".collate_setting")


class TestDirectoriesExist:
    """Test that required directories exist."""

    def test_home_directory_exists(self):
        assert os.path.isdir(HOME), f"Home directory {HOME} does not exist"

    def test_scripts_directory_exists(self):
        assert os.path.isdir(SCRIPTS_DIR), f"Scripts directory {SCRIPTS_DIR} does not exist"

    def test_test_payload_directory_exists(self):
        assert os.path.isdir(TEST_PAYLOAD_DIR), f"Test payload directory {TEST_PAYLOAD_DIR} does not exist"

    def test_scripts_directory_writable(self):
        assert os.access(SCRIPTS_DIR, os.W_OK), f"Scripts directory {SCRIPTS_DIR} is not writable"


class TestScriptsExist:
    """Test that the archive and restore scripts exist and are executable."""

    def test_archive_script_exists(self):
        assert os.path.isfile(ARCHIVE_SCRIPT), f"Archive script {ARCHIVE_SCRIPT} does not exist"

    def test_restore_script_exists(self):
        assert os.path.isfile(RESTORE_SCRIPT), f"Restore script {RESTORE_SCRIPT} does not exist"

    def test_archive_script_executable(self):
        assert os.access(ARCHIVE_SCRIPT, os.X_OK), f"Archive script {ARCHIVE_SCRIPT} is not executable"

    def test_restore_script_executable(self):
        assert os.access(RESTORE_SCRIPT, os.X_OK), f"Restore script {RESTORE_SCRIPT} is not executable"


class TestArchiveScriptContent:
    """Test that archive.sh has the expected buggy content."""

    def test_archive_script_uses_tar(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'tar' in content, "Archive script should use tar command"

    def test_archive_script_uses_gzip(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'gzip' in content, "Archive script should use gzip command"

    def test_archive_script_uses_split(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'split' in content, "Archive script should use split command"

    def test_archive_script_uses_50m_chunks(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert '50M' in content or '50m' in content.lower(), "Archive script should use 50M chunk size"


class TestRestoreScriptContent:
    """Test that restore.sh has the expected buggy content."""

    def test_restore_script_uses_cat(self):
        with open(RESTORE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'cat' in content, "Restore script should use cat command"

    def test_restore_script_uses_gunzip(self):
        with open(RESTORE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'gunzip' in content, "Restore script should use gunzip command"

    def test_restore_script_uses_tar(self):
        with open(RESTORE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'tar' in content, "Restore script should use tar command"

    def test_restore_script_uses_chunk_glob(self):
        with open(RESTORE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'chunk_*' in content or 'chunk_' in content, "Restore script should reference chunk files"


class TestTestPayload:
    """Test that test_payload has appropriate content (~180MB)."""

    def test_test_payload_not_empty(self):
        contents = os.listdir(TEST_PAYLOAD_DIR)
        assert len(contents) > 0, f"Test payload directory {TEST_PAYLOAD_DIR} is empty"

    def test_test_payload_has_files(self):
        """Check that test_payload contains actual files (not just directories)."""
        has_files = False
        for root, dirs, files in os.walk(TEST_PAYLOAD_DIR):
            if files:
                has_files = True
                break
        assert has_files, f"Test payload directory {TEST_PAYLOAD_DIR} contains no files"

    def test_test_payload_size_approximately_180mb(self):
        """Check that test_payload is approximately 180MB (enough to create 4+ chunks)."""
        total_size = 0
        for root, dirs, files in os.walk(TEST_PAYLOAD_DIR):
            for f in files:
                filepath = os.path.join(root, f)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)

        # Should be at least 150MB to ensure 4 chunks (50MB each)
        min_size = 150 * 1024 * 1024  # 150MB
        max_size = 250 * 1024 * 1024  # 250MB

        assert total_size >= min_size, (
            f"Test payload is too small ({total_size / (1024*1024):.1f}MB). "
            f"Expected at least 150MB to produce 4+ chunks for testing the bug."
        )
        assert total_size <= max_size, (
            f"Test payload is too large ({total_size / (1024*1024):.1f}MB). "
            f"Expected around 180MB."
        )


class TestLocaleRotationMechanism:
    """Test that the locale rotation mechanism exists in .bashrc."""

    def test_bashrc_exists(self):
        assert os.path.isfile(BASHRC), f"Bashrc file {BASHRC} does not exist"

    def test_collate_setting_file_exists(self):
        assert os.path.isfile(COLLATE_SETTING), (
            f"Collate setting file {COLLATE_SETTING} does not exist. "
            "This file is needed for the locale rotation mechanism."
        )

    def test_bashrc_references_collate(self):
        """Check that .bashrc has some locale/collate configuration."""
        with open(BASHRC, 'r') as f:
            content = f.read()

        has_locale_ref = any(term in content for term in ['LC_COLLATE', 'LC_ALL', 'collate', 'COLLATE'])
        assert has_locale_ref, (
            ".bashrc should contain locale/collate configuration for the rotation mechanism"
        )


class TestRequiredTools:
    """Test that required tools are available."""

    def test_bash_available(self):
        result = subprocess.run(['which', 'bash'], capture_output=True)
        assert result.returncode == 0, "bash is not available"

    def test_tar_available(self):
        result = subprocess.run(['which', 'tar'], capture_output=True)
        assert result.returncode == 0, "tar is not available"

    def test_gzip_available(self):
        result = subprocess.run(['which', 'gzip'], capture_output=True)
        assert result.returncode == 0, "gzip is not available"

    def test_split_available(self):
        result = subprocess.run(['which', 'split'], capture_output=True)
        assert result.returncode == 0, "split is not available"

    def test_cat_available(self):
        result = subprocess.run(['which', 'cat'], capture_output=True)
        assert result.returncode == 0, "cat is not available"

    def test_sort_available(self):
        result = subprocess.run(['which', 'sort'], capture_output=True)
        assert result.returncode == 0, "sort is not available"

    def test_diff_available(self):
        result = subprocess.run(['which', 'diff'], capture_output=True)
        assert result.returncode == 0, "diff is not available"

    def test_locale_available(self):
        result = subprocess.run(['which', 'locale'], capture_output=True)
        assert result.returncode == 0, "locale command is not available"


class TestLocalesInstalled:
    """Test that required locales are available for the bug to manifest."""

    def test_c_locale_available(self):
        """C locale should always be available."""
        result = subprocess.run(['locale', '-a'], capture_output=True, text=True)
        assert 'C' in result.stdout or 'POSIX' in result.stdout, "C locale is not available"

    def test_utf8_locale_available(self):
        """en_US.UTF-8 or similar UTF-8 locale should be available."""
        result = subprocess.run(['locale', '-a'], capture_output=True, text=True)
        locales = result.stdout.lower()
        has_utf8 = 'en_us.utf-8' in locales or 'en_us.utf8' in locales or 'utf-8' in locales or 'utf8' in locales
        assert has_utf8, "No UTF-8 locale is available (needed for the bug to manifest)"
