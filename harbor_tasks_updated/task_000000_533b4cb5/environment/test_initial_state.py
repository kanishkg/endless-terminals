# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the backup permission fix task.
"""

import os
import pwd
import grp
import stat
import subprocess
import pytest


class TestUsersAndGroups:
    """Verify users and groups exist with correct initial configuration."""

    def test_backupd_user_exists(self):
        """Verify backupd user exists with uid 1001."""
        try:
            pw = pwd.getpwnam('backupd')
            assert pw.pw_uid == 1001, f"backupd uid should be 1001, got {pw.pw_uid}"
        except KeyError:
            pytest.fail("User 'backupd' does not exist")

    def test_backupd_group_exists(self):
        """Verify backupd group exists with gid 1001."""
        try:
            gr = grp.getgrnam('backupd')
            assert gr.gr_gid == 1001, f"backupd gid should be 1001, got {gr.gr_gid}"
        except KeyError:
            pytest.fail("Group 'backupd' does not exist")

    def test_backupd_primary_group(self):
        """Verify backupd user has backupd as primary group."""
        pw = pwd.getpwnam('backupd')
        gr = grp.getgrgid(pw.pw_gid)
        assert gr.gr_name == 'backupd', f"backupd primary group should be 'backupd', got '{gr.gr_name}'"

    def test_backup_group_exists(self):
        """Verify backup group exists."""
        try:
            grp.getgrnam('backup')
        except KeyError:
            pytest.fail("Group 'backup' does not exist")

    def test_user_exists(self):
        """Verify user 'user' exists with uid 1000."""
        try:
            pw = pwd.getpwnam('user')
            assert pw.pw_uid == 1000, f"user uid should be 1000, got {pw.pw_uid}"
        except KeyError:
            pytest.fail("User 'user' does not exist")

    def test_user_in_backup_group(self):
        """Verify user 'user' is a member of backup group."""
        gr = grp.getgrnam('backup')
        assert 'user' in gr.gr_mem, "User 'user' should be a member of 'backup' group"

    def test_user_in_backupd_group(self):
        """Verify user 'user' is a member of backupd group."""
        gr = grp.getgrnam('backupd')
        assert 'user' in gr.gr_mem, "User 'user' should be a member of 'backupd' group"

    def test_backupd_not_in_backup_group(self):
        """Verify backupd is NOT in backup group (this is the problem to fix)."""
        gr = grp.getgrnam('backup')
        assert 'backupd' not in gr.gr_mem, \
            "Initial state: backupd should NOT be in 'backup' group (this is the problem)"


class TestVerifyRestoreScript:
    """Verify the restore verification script exists with correct properties."""

    SCRIPT_PATH = '/home/user/backup/verify_restore.sh'

    def test_script_exists(self):
        """Verify verify_restore.sh exists."""
        assert os.path.isfile(self.SCRIPT_PATH), \
            f"Script {self.SCRIPT_PATH} does not exist"

    def test_script_owner(self):
        """Verify script is owned by user:backup."""
        st = os.stat(self.SCRIPT_PATH)
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'user', f"Script owner should be 'user', got '{owner}'"
        assert group == 'backup', f"Script group should be 'backup', got '{group}'"

    def test_script_permissions(self):
        """Verify script has mode 750."""
        st = os.stat(self.SCRIPT_PATH)
        mode = stat.S_IMODE(st.st_mode)
        assert mode == 0o750, f"Script mode should be 0750, got {oct(mode)}"

    def test_script_is_executable_by_owner(self):
        """Verify script is executable by owner."""
        st = os.stat(self.SCRIPT_PATH)
        assert st.st_mode & stat.S_IXUSR, "Script should be executable by owner"

    def test_script_is_executable_by_group(self):
        """Verify script is executable by group."""
        st = os.stat(self.SCRIPT_PATH)
        assert st.st_mode & stat.S_IXGRP, "Script should be executable by group"

    def test_script_not_world_executable(self):
        """Verify script is not world executable."""
        st = os.stat(self.SCRIPT_PATH)
        assert not (st.st_mode & stat.S_IXOTH), "Script should NOT be world executable"

    def test_script_contains_expected_content(self):
        """Verify script has expected shebang and key content."""
        with open(self.SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert content.startswith('#!/bin/bash'), "Script should start with bash shebang"
        assert 'STAGING=/srv/backup-staging' in content, "Script should reference /srv/backup-staging"
        assert 'RESTORE_DIR=/tmp/restore-verify' in content, "Script should reference /tmp/restore-verify"
        assert 'LOGFILE=/var/log/backup/verify.log' in content, "Script should reference verify.log"

    def test_backup_directory_exists(self):
        """Verify /home/user/backup directory exists."""
        assert os.path.isdir('/home/user/backup'), "/home/user/backup directory does not exist"


class TestBackupStagingDirectory:
    """Verify /srv/backup-staging exists with correct properties."""

    STAGING_PATH = '/srv/backup-staging'

    def test_staging_exists(self):
        """Verify /srv/backup-staging exists."""
        assert os.path.isdir(self.STAGING_PATH), \
            f"{self.STAGING_PATH} directory does not exist"

    def test_staging_owner(self):
        """Verify staging is owned by root:backup."""
        st = os.stat(self.STAGING_PATH)
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'root', f"Staging owner should be 'root', got '{owner}'"
        assert group == 'backup', f"Staging group should be 'backup', got '{group}'"

    def test_staging_permissions(self):
        """Verify staging has mode 2750 (setgid)."""
        st = os.stat(self.STAGING_PATH)
        mode = stat.S_IMODE(st.st_mode)
        assert mode == 0o2750, f"Staging mode should be 2750, got {oct(mode)}"

    def test_staging_has_setgid(self):
        """Verify staging has setgid bit set."""
        st = os.stat(self.STAGING_PATH)
        assert st.st_mode & stat.S_ISGID, "Staging should have setgid bit set"

    def test_daily_tarball_exists(self):
        """Verify daily tarball exists."""
        tarball = os.path.join(self.STAGING_PATH, 'daily-2024-01-15.tar.gz')
        assert os.path.isfile(tarball), f"Daily tarball {tarball} does not exist"

    def test_weekly_tarball_exists(self):
        """Verify weekly tarball exists."""
        tarball = os.path.join(self.STAGING_PATH, 'weekly-2024-01-14.tar.gz')
        assert os.path.isfile(tarball), f"Weekly tarball {tarball} does not exist"


class TestLogDirectory:
    """Verify /var/log/backup exists with correct properties."""

    LOG_DIR = '/var/log/backup'
    LOG_FILE = '/var/log/backup/verify.log'

    def test_log_dir_exists(self):
        """Verify /var/log/backup exists."""
        assert os.path.isdir(self.LOG_DIR), \
            f"{self.LOG_DIR} directory does not exist"

    def test_log_dir_owner(self):
        """Verify log dir is owned by root:backup."""
        st = os.stat(self.LOG_DIR)
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'root', f"Log dir owner should be 'root', got '{owner}'"
        assert group == 'backup', f"Log dir group should be 'backup', got '{group}'"

    def test_log_dir_permissions(self):
        """Verify log dir has mode 2770."""
        st = os.stat(self.LOG_DIR)
        mode = stat.S_IMODE(st.st_mode)
        assert mode == 0o2770, f"Log dir mode should be 2770, got {oct(mode)}"

    def test_log_file_exists(self):
        """Verify verify.log exists."""
        assert os.path.isfile(self.LOG_FILE), \
            f"{self.LOG_FILE} does not exist"

    def test_log_file_owner(self):
        """Verify log file is owned by user:backup."""
        st = os.stat(self.LOG_FILE)
        owner = pwd.getpwuid(st.st_uid).pw_name
        group = grp.getgrgid(st.st_gid).gr_name
        assert owner == 'user', f"Log file owner should be 'user', got '{owner}'"
        assert group == 'backup', f"Log file group should be 'backup', got '{group}'"

    def test_log_file_permissions(self):
        """Verify log file has mode 660."""
        st = os.stat(self.LOG_FILE)
        mode = stat.S_IMODE(st.st_mode)
        assert mode == 0o660, f"Log file mode should be 660, got {oct(mode)}"


class TestRestoreVerifyDirectory:
    """Verify /tmp/restore-verify does not exist initially."""

    def test_restore_verify_does_not_exist(self):
        """Verify /tmp/restore-verify does not exist initially."""
        assert not os.path.exists('/tmp/restore-verify'), \
            "/tmp/restore-verify should not exist initially"


class TestSudoersConfiguration:
    """Verify sudo configuration for user."""

    def test_sudoers_file_exists(self):
        """Verify sudoers.d/backup-admin exists."""
        sudoers_file = '/etc/sudoers.d/backup-admin'
        assert os.path.isfile(sudoers_file), \
            f"{sudoers_file} does not exist"

    def test_sudo_usermod_available(self):
        """Verify user can sudo usermod (check by running --help)."""
        result = subprocess.run(
            ['sudo', '-n', '/usr/sbin/usermod', '--help'],
            capture_output=True
        )
        # usermod --help returns 0 on success
        assert result.returncode == 0, \
            "User should be able to sudo usermod without password"

    def test_sudo_groupmod_available(self):
        """Verify user can sudo groupmod (check by running --help)."""
        result = subprocess.run(
            ['sudo', '-n', '/usr/sbin/groupmod', '--help'],
            capture_output=True
        )
        # groupmod --help returns 0 on success
        assert result.returncode == 0, \
            "User should be able to sudo groupmod without password"


class TestRequiredCommands:
    """Verify required commands are available."""

    @pytest.mark.parametrize("cmd", [
        'usermod', 'groupmod', 'gpasswd', 'chmod', 'chown', 'chgrp',
        'ls', 'stat', 'id', 'groups', 'getent', 'su', 'sudo', 'tar', 'sha256sum'
    ])
    def test_command_exists(self, cmd):
        """Verify required command exists."""
        result = subprocess.run(['which', cmd], capture_output=True)
        assert result.returncode == 0, f"Command '{cmd}' not found in PATH"
