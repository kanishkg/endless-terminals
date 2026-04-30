# test_final_state.py
"""
Tests to validate the final state after the student has fixed the backup
permission issue by adding backupd to the backup group.
"""

import os
import pwd
import grp
import stat
import subprocess
import hashlib
import pytest


class TestBackupdGroupMembership:
    """Verify backupd user is now a member of the backup group."""

    def test_backupd_in_backup_group(self):
        """Verify backupd is a member of the backup group."""
        gr = grp.getgrnam('backup')
        # Check supplementary groups
        if 'backupd' not in gr.gr_mem:
            # Also check if backup is the primary group (unlikely but possible)
            pw = pwd.getpwnam('backupd')
            primary_gid = pw.pw_gid
            backup_gid = gr.gr_gid
            if primary_gid != backup_gid:
                pytest.fail(
                    f"User 'backupd' must be a member of 'backup' group. "
                    f"Current backup group members: {gr.gr_mem}"
                )

    def test_groups_command_shows_backup(self):
        """Verify 'id backupd' shows backup group membership."""
        result = subprocess.run(
            ['id', 'backupd'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"'id backupd' failed: {result.stderr}"
        # Check that 'backup' appears in the groups
        assert 'backup' in result.stdout, \
            f"'id backupd' output should contain 'backup' group: {result.stdout}"


class TestScriptExecutionAsBackupd:
    """Verify the script runs successfully as backupd user."""

    SCRIPT_PATH = '/home/user/backup/verify_restore.sh'
    LOG_FILE = '/var/log/backup/verify.log'

    def test_script_runs_successfully_as_backupd(self):
        """Verify verify_restore.sh runs without errors as backupd."""
        # Use sudo -u backupd with a new login shell to pick up group changes
        # The sg command or newgrp could also work, but sudo -u is cleaner
        result = subprocess.run(
            ['sudo', '-u', 'backupd', self.SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, \
            f"Script failed with exit code {result.returncode}.\n" \
            f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_log_file_contains_verification_entries(self):
        """Verify log file contains successful verification entries."""
        assert os.path.isfile(self.LOG_FILE), \
            f"Log file {self.LOG_FILE} does not exist"

        with open(self.LOG_FILE, 'r') as f:
            content = f.read()

        # Check for verification of both archives
        assert 'daily-2024-01-15' in content, \
            "Log should contain verification entry for daily-2024-01-15"
        assert 'weekly-2024-01-14' in content, \
            "Log should contain verification entry for weekly-2024-01-14"

        # Check for completion message
        assert 'Restore verification complete' in content, \
            "Log should contain 'Restore verification complete' message"

    def test_log_file_contains_start_message(self):
        """Verify log file contains start message."""
        with open(self.LOG_FILE, 'r') as f:
            content = f.read()

        assert 'Starting restore verification' in content, \
            "Log should contain 'Starting restore verification' message"


class TestPermissionsUnchanged:
    """Verify permissions remain properly locked down (anti-shortcut guards)."""

    def test_staging_permissions_secure(self):
        """Verify /srv/backup-staging is not world-readable."""
        st = os.stat('/srv/backup-staging')
        mode = stat.S_IMODE(st.st_mode)
        # Must be 2750 or 750 (not 755, 775, or 777)
        assert mode in (0o2750, 0o750), \
            f"/srv/backup-staging mode should be 2750 or 750, got {oct(mode)}"
        # Explicitly check no world read/execute
        assert not (mode & stat.S_IROTH), \
            "/srv/backup-staging should not be world-readable"
        assert not (mode & stat.S_IXOTH), \
            "/srv/backup-staging should not be world-executable"

    def test_log_dir_permissions_secure(self):
        """Verify /var/log/backup is not world-writable."""
        st = os.stat('/var/log/backup')
        mode = stat.S_IMODE(st.st_mode)
        # Must be 2770 or 770 (not 775 or 777)
        assert mode in (0o2770, 0o770), \
            f"/var/log/backup mode should be 2770 or 770, got {oct(mode)}"
        # Explicitly check no world write
        assert not (mode & stat.S_IWOTH), \
            "/var/log/backup should not be world-writable"

    def test_script_permissions_secure(self):
        """Verify script is not world-executable."""
        st = os.stat('/home/user/backup/verify_restore.sh')
        mode = stat.S_IMODE(st.st_mode)
        # Must be 750 (not 755 or 777)
        assert mode == 0o750, \
            f"Script mode should be 750, got {oct(mode)}"
        # Explicitly check no world execute
        assert not (mode & stat.S_IXOTH), \
            "Script should not be world-executable"


class TestScriptUnmodified:
    """Verify the script content was not modified to bypass permission checks."""

    SCRIPT_PATH = '/home/user/backup/verify_restore.sh'

    # Expected script content (normalized)
    EXPECTED_CONTENT = '''#!/bin/bash
set -e
STAGING=/srv/backup-staging
RESTORE_DIR=/tmp/restore-verify
LOGFILE=/var/log/backup/verify.log

echo "[$(date)] Starting restore verification" >> "$LOGFILE"

mkdir -p "$RESTORE_DIR"

for archive in "$STAGING"/*.tar.gz; do
    [ -e "$archive" ] || continue
    name=$(basename "$archive" .tar.gz)
    echo "[$(date)] Verifying $name" >> "$LOGFILE"
    tar -tzf "$archive" > /dev/null
    tar -xzf "$archive" -C "$RESTORE_DIR"
    # Simulated integrity check
    if [ -f "$RESTORE_DIR/$name/manifest.sha256" ]; then
        cd "$RESTORE_DIR/$name"
        sha256sum -c manifest.sha256 >> "$LOGFILE" 2>&1
        cd - > /dev/null
    fi
done

rm -rf "$RESTORE_DIR"
echo "[$(date)] Restore verification complete" >> "$LOGFILE"
'''

    def test_script_content_unchanged(self):
        """Verify script content matches expected (byte-identical)."""
        with open(self.SCRIPT_PATH, 'r') as f:
            actual_content = f.read()

        # Normalize line endings for comparison
        expected_normalized = self.EXPECTED_CONTENT.strip()
        actual_normalized = actual_content.strip()

        assert actual_normalized == expected_normalized, \
            "Script content has been modified. The fix should only involve " \
            "group membership changes, not script modifications."

    def test_script_has_correct_shebang(self):
        """Verify script starts with correct shebang."""
        with open(self.SCRIPT_PATH, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == '#!/bin/bash', \
            f"Script shebang should be '#!/bin/bash', got '{first_line}'"

    def test_script_references_correct_paths(self):
        """Verify script references the correct paths."""
        with open(self.SCRIPT_PATH, 'r') as f:
            content = f.read()

        assert 'STAGING=/srv/backup-staging' in content, \
            "Script should reference /srv/backup-staging"
        assert 'RESTORE_DIR=/tmp/restore-verify' in content, \
            "Script should reference /tmp/restore-verify"
        assert 'LOGFILE=/var/log/backup/verify.log' in content, \
            "Script should reference /var/log/backup/verify.log"


class TestNoNewUsers:
    """Verify no new users were created as a workaround."""

    def test_backupd_uid_unchanged(self):
        """Verify backupd user still has uid 1001."""
        pw = pwd.getpwnam('backupd')
        assert pw.pw_uid == 1001, \
            f"backupd uid should still be 1001, got {pw.pw_uid}"

    def test_backupd_primary_group_unchanged(self):
        """Verify backupd primary group is still backupd."""
        pw = pwd.getpwnam('backupd')
        gr = grp.getgrgid(pw.pw_gid)
        assert gr.gr_name == 'backupd', \
            f"backupd primary group should still be 'backupd', got '{gr.gr_name}'"


class TestOwnershipUnchanged:
    """Verify file/directory ownership was not changed as a workaround."""

    def test_staging_ownership(self):
        """Verify /srv/backup-staging is still owned by root:backup."""
        st = os.stat('/srv/backup-staging')
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'root', \
            f"/srv/backup-staging owner should be 'root', got '{owner}'"
        assert group == 'backup', \
            f"/srv/backup-staging group should be 'backup', got '{group}'"

    def test_log_dir_ownership(self):
        """Verify /var/log/backup is still owned by root:backup."""
        st = os.stat('/var/log/backup')
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'root', \
            f"/var/log/backup owner should be 'root', got '{owner}'"
        assert group == 'backup', \
            f"/var/log/backup group should be 'backup', got '{group}'"

    def test_script_ownership(self):
        """Verify script is still owned by user:backup."""
        st = os.stat('/home/user/backup/verify_restore.sh')
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'user', \
            f"Script owner should be 'user', got '{owner}'"
        assert group == 'backup', \
            f"Script group should be 'backup', got '{group}'"


class TestCleanup:
    """Verify the script cleaned up after itself."""

    def test_restore_verify_cleaned_up(self):
        """Verify /tmp/restore-verify was cleaned up after script run."""
        # The script should remove this directory at the end
        assert not os.path.exists('/tmp/restore-verify'), \
            "/tmp/restore-verify should be cleaned up after script execution"
