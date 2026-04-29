# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the rsync debugging task.
"""

import os
import subprocess
import pytest


HOME = "/home/user"
BACKUP_DIR = os.path.join(HOME, "backup")
SOURCE_DIR = os.path.join(BACKUP_DIR, "source")
DEST_DIR = os.path.join(BACKUP_DIR, "dest")
SYNC_SCRIPT = os.path.join(BACKUP_DIR, "sync.sh")
EXCLUDE_FILE = os.path.join(BACKUP_DIR, "exclude.lst")
LOG_FILE = os.path.join(BACKUP_DIR, "sync.log")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_backup_directory_exists(self):
        assert os.path.isdir(BACKUP_DIR), f"Backup directory {BACKUP_DIR} does not exist"

    def test_source_directory_exists(self):
        assert os.path.isdir(SOURCE_DIR), f"Source directory {SOURCE_DIR} does not exist"

    def test_dest_directory_exists(self):
        assert os.path.isdir(DEST_DIR), f"Destination directory {DEST_DIR} does not exist"


class TestSourceDirectory:
    """Test that source directory has the expected files."""

    def test_source_has_approximately_200_files(self):
        """Source should have ~217 files (around 200)."""
        files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
        assert len(files) >= 200, f"Source directory should have ~200+ files, found {len(files)}"
        assert len(files) <= 250, f"Source directory should have ~200 files, found {len(files)}"

    def test_source_has_various_file_types(self):
        """Source should have files with various extensions."""
        files = os.listdir(SOURCE_DIR)
        extensions = set()
        for f in files:
            if '.' in f:
                ext = os.path.splitext(f)[1]
                extensions.add(ext)
        # Should have at least some variety in extensions
        assert len(extensions) >= 2, f"Source should have various file types, found extensions: {extensions}"


class TestDestDirectory:
    """Test that dest directory is nearly empty (the bug symptom)."""

    def test_dest_has_very_few_files(self):
        """Dest should have only a few files (the bug symptom)."""
        files = [f for f in os.listdir(DEST_DIR) if os.path.isfile(os.path.join(DEST_DIR, f))]
        assert len(files) <= 10, f"Dest directory should be nearly empty (<=10 files), found {len(files)}"

    def test_dest_has_fewer_files_than_source(self):
        """Dest should have significantly fewer files than source."""
        source_files = len([f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))])
        dest_files = len([f for f in os.listdir(DEST_DIR) if os.path.isfile(os.path.join(DEST_DIR, f))])
        assert dest_files < source_files / 10, (
            f"Dest should have far fewer files than source. Source: {source_files}, Dest: {dest_files}"
        )


class TestSyncScript:
    """Test that sync.sh exists and has expected properties."""

    def test_sync_script_exists(self):
        assert os.path.isfile(SYNC_SCRIPT), f"Sync script {SYNC_SCRIPT} does not exist"

    def test_sync_script_is_executable(self):
        assert os.access(SYNC_SCRIPT, os.X_OK), f"Sync script {SYNC_SCRIPT} is not executable"

    def test_sync_script_contains_rsync(self):
        """Script should use rsync."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert 'rsync' in content, f"Sync script should contain rsync command"

    def test_sync_script_has_exclude_from_flag(self):
        """Script should reference exclude-from (the source of the bug)."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert '--exclude-from' in content, f"Sync script should have --exclude-from flag"

    def test_sync_script_references_exclude_list(self):
        """Script should reference the exclude.lst file."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert 'exclude.lst' in content, f"Sync script should reference exclude.lst"

    def test_sync_script_logs_to_sync_log(self):
        """Script should log to sync.log."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert 'sync.log' in content, f"Sync script should log to sync.log"

    def test_sync_script_has_shebang(self):
        """Script should have bash shebang."""
        with open(SYNC_SCRIPT, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('#!') and 'bash' in first_line, (
            f"Sync script should have bash shebang, found: {first_line}"
        )


class TestExcludeFile:
    """Test that exclude.lst exists and contains the buggy pattern."""

    def test_exclude_file_exists(self):
        assert os.path.isfile(EXCLUDE_FILE), f"Exclude file {EXCLUDE_FILE} does not exist"

    def test_exclude_file_contains_wildcard(self):
        """Exclude file should contain the buggy * pattern."""
        with open(EXCLUDE_FILE, 'r') as f:
            content = f.read()
        # Check for a line that is just * (the bug)
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        assert '*' in lines, f"Exclude file should contain wildcard '*' pattern (the bug). Found lines: {lines}"

    def test_exclude_file_has_comment_about_update(self):
        """Exclude file should have a comment indicating recent update."""
        with open(EXCLUDE_FILE, 'r') as f:
            content = f.read()
        # Should have some comment about being updated
        assert '#' in content, f"Exclude file should have comments"


class TestLogFile:
    """Test that sync.log exists and shows the symptom."""

    def test_log_file_exists(self):
        assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist"

    def test_log_file_shows_rsync_output(self):
        """Log should show rsync ran."""
        with open(LOG_FILE, 'r') as f:
            content = f.read()
        assert 'sending' in content.lower() or 'sent' in content.lower(), (
            f"Log file should show rsync output"
        )


class TestRequiredTools:
    """Test that required tools are available."""

    def test_rsync_available(self):
        result = subprocess.run(['which', 'rsync'], capture_output=True)
        assert result.returncode == 0, "rsync command not available"

    def test_bash_available(self):
        result = subprocess.run(['which', 'bash'], capture_output=True)
        assert result.returncode == 0, "bash command not available"

    def test_grep_available(self):
        result = subprocess.run(['which', 'grep'], capture_output=True)
        assert result.returncode == 0, "grep command not available"

    def test_cat_available(self):
        result = subprocess.run(['which', 'cat'], capture_output=True)
        assert result.returncode == 0, "cat command not available"

    def test_diff_available(self):
        result = subprocess.run(['which', 'diff'], capture_output=True)
        assert result.returncode == 0, "diff command not available"

    def test_wc_available(self):
        result = subprocess.run(['which', 'wc'], capture_output=True)
        assert result.returncode == 0, "wc command not available"

    def test_ls_available(self):
        result = subprocess.run(['which', 'ls'], capture_output=True)
        assert result.returncode == 0, "ls command not available"

    def test_find_available(self):
        result = subprocess.run(['which', 'find'], capture_output=True)
        assert result.returncode == 0, "find command not available"


class TestPermissions:
    """Test that backup directory and contents are writable."""

    def test_backup_dir_writable(self):
        assert os.access(BACKUP_DIR, os.W_OK), f"Backup directory {BACKUP_DIR} is not writable"

    def test_sync_script_writable(self):
        assert os.access(SYNC_SCRIPT, os.W_OK), f"Sync script {SYNC_SCRIPT} is not writable"

    def test_exclude_file_writable(self):
        assert os.access(EXCLUDE_FILE, os.W_OK), f"Exclude file {EXCLUDE_FILE} is not writable"

    def test_dest_dir_writable(self):
        assert os.access(DEST_DIR, os.W_OK), f"Dest directory {DEST_DIR} is not writable"
