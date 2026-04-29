# test_final_state.py
"""
Tests to validate the final state after the student has fixed the rsync backup issue.
The sync.sh script should now successfully mirror source to dest.
"""

import os
import subprocess
import pytest


HOME = "/home/user"
BACKUP_DIR = os.path.join(HOME, "backup")
SOURCE_DIR = os.path.join(BACKUP_DIR, "source")
DEST_DIR = os.path.join(BACKUP_DIR, "dest")
SYNC_SCRIPT = os.path.join(BACKUP_DIR, "sync.sh")
LOG_FILE = os.path.join(BACKUP_DIR, "sync.log")


class TestSyncScriptExecution:
    """Test that sync.sh runs successfully and syncs files."""

    def test_sync_script_exists(self):
        """Sync script must still exist."""
        assert os.path.isfile(SYNC_SCRIPT), f"Sync script {SYNC_SCRIPT} does not exist"

    def test_sync_script_is_executable(self):
        """Sync script must be executable."""
        assert os.access(SYNC_SCRIPT, os.X_OK), f"Sync script {SYNC_SCRIPT} is not executable"

    def test_sync_script_uses_rsync(self):
        """Sync script must still use rsync (not replaced with cp or other tool)."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert 'rsync' in content, (
            "Sync script must use rsync command. "
            "Replacing with cp or other tools is not acceptable."
        )

    def test_sync_script_logs_to_sync_log(self):
        """Sync script must still log to sync.log."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert 'sync.log' in content, (
            "Sync script must still log to sync.log"
        )

    def test_sync_script_exits_zero(self):
        """Running sync.sh must exit with code 0."""
        result = subprocess.run(
            [SYNC_SCRIPT],
            capture_output=True,
            text=True,
            cwd=BACKUP_DIR
        )
        assert result.returncode == 0, (
            f"Sync script exited with code {result.returncode}. "
            f"Stderr: {result.stderr}"
        )


class TestSourceDirectoryUnchanged:
    """Test that source directory is unchanged (invariant)."""

    def test_source_directory_exists(self):
        """Source directory must still exist."""
        assert os.path.isdir(SOURCE_DIR), f"Source directory {SOURCE_DIR} does not exist"

    def test_source_has_expected_file_count(self):
        """Source should still have ~217 files."""
        files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
        assert len(files) >= 200, (
            f"Source directory should have ~200+ files, found {len(files)}. "
            "Source should not have been modified."
        )
        assert len(files) <= 250, (
            f"Source directory should have ~200 files, found {len(files)}. "
            "Source should not have been modified."
        )


class TestDestDirectoryMirrorsSource:
    """Test that dest directory now mirrors source after running sync.sh."""

    def test_dest_directory_exists(self):
        """Dest directory must exist."""
        assert os.path.isdir(DEST_DIR), f"Destination directory {DEST_DIR} does not exist"

    def test_dest_has_same_file_count_as_source(self):
        """Dest must have the same number of files as source."""
        # First run the sync script to ensure it's been executed
        subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=BACKUP_DIR)

        source_files = sorted([
            f for f in os.listdir(SOURCE_DIR) 
            if os.path.isfile(os.path.join(SOURCE_DIR, f))
        ])
        dest_files = sorted([
            f for f in os.listdir(DEST_DIR) 
            if os.path.isfile(os.path.join(DEST_DIR, f))
        ])

        assert len(dest_files) == len(source_files), (
            f"Dest should have same file count as source. "
            f"Source: {len(source_files)}, Dest: {len(dest_files)}. "
            f"The sync is not working correctly."
        )

    def test_dest_has_same_files_as_source(self):
        """Dest must contain exactly the same files as source."""
        # Run the sync script
        subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=BACKUP_DIR)

        source_files = sorted([
            f for f in os.listdir(SOURCE_DIR) 
            if os.path.isfile(os.path.join(SOURCE_DIR, f))
        ])
        dest_files = sorted([
            f for f in os.listdir(DEST_DIR) 
            if os.path.isfile(os.path.join(DEST_DIR, f))
        ])

        # Check that the file lists match
        missing_in_dest = set(source_files) - set(dest_files)
        extra_in_dest = set(dest_files) - set(source_files)

        assert source_files == dest_files, (
            f"Dest must contain exactly the same files as source. "
            f"Missing in dest: {list(missing_in_dest)[:10]}{'...' if len(missing_in_dest) > 10 else ''} "
            f"({len(missing_in_dest)} total). "
            f"Extra in dest: {list(extra_in_dest)[:10]}{'...' if len(extra_in_dest) > 10 else ''} "
            f"({len(extra_in_dest)} total)."
        )

    def test_dest_has_more_than_ten_files(self):
        """Dest must have significantly more files than before (was nearly empty)."""
        # Run the sync script
        subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=BACKUP_DIR)

        dest_files = [
            f for f in os.listdir(DEST_DIR) 
            if os.path.isfile(os.path.join(DEST_DIR, f))
        ]

        assert len(dest_files) > 10, (
            f"Dest directory should have many files after sync, found only {len(dest_files)}. "
            "The sync is not transferring files."
        )


class TestLogFileShowsTransfer:
    """Test that the log file shows actual file transfers."""

    def test_log_file_exists(self):
        """Log file must exist."""
        assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist"

    def test_log_shows_nonzero_transfer(self):
        """After running sync.sh, log should show non-zero total size."""
        # Clear or note the current log size
        initial_size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0

        # Run the sync script
        subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=BACKUP_DIR)

        with open(LOG_FILE, 'r') as f:
            content = f.read()

        # The log should show rsync activity
        assert 'sent' in content.lower() or 'sending' in content.lower(), (
            "Log file should show rsync transfer activity"
        )


class TestSyncScriptFunctionality:
    """Integration test to verify the complete fix."""

    def test_full_sync_workflow(self):
        """
        Complete integration test:
        1. Run sync.sh
        2. Verify it exits 0
        3. Verify dest mirrors source
        """
        # Run the sync script
        result = subprocess.run(
            [SYNC_SCRIPT],
            capture_output=True,
            text=True,
            cwd=BACKUP_DIR
        )

        # Check exit code
        assert result.returncode == 0, (
            f"Sync script must exit with code 0, got {result.returncode}. "
            f"Stderr: {result.stderr}"
        )

        # Get file lists
        source_files = sorted([
            f for f in os.listdir(SOURCE_DIR) 
            if os.path.isfile(os.path.join(SOURCE_DIR, f))
        ])
        dest_files = sorted([
            f for f in os.listdir(DEST_DIR) 
            if os.path.isfile(os.path.join(DEST_DIR, f))
        ])

        # Verify counts match
        assert len(source_files) == len(dest_files), (
            f"After running sync.sh, dest should have same file count as source. "
            f"Source: {len(source_files)}, Dest: {len(dest_files)}"
        )

        # Verify file names match
        assert source_files == dest_files, (
            f"After running sync.sh, dest should contain exactly the same files as source."
        )

    def test_repeated_sync_is_idempotent(self):
        """Running sync.sh multiple times should work and be idempotent."""
        # Run twice
        result1 = subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=BACKUP_DIR)
        result2 = subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=BACKUP_DIR)

        assert result1.returncode == 0, "First sync run should exit 0"
        assert result2.returncode == 0, "Second sync run should exit 0"

        # Verify dest still matches source
        source_files = sorted([
            f for f in os.listdir(SOURCE_DIR) 
            if os.path.isfile(os.path.join(SOURCE_DIR, f))
        ])
        dest_files = sorted([
            f for f in os.listdir(DEST_DIR) 
            if os.path.isfile(os.path.join(DEST_DIR, f))
        ])

        assert source_files == dest_files, (
            "After multiple sync runs, dest should still mirror source"
        )
