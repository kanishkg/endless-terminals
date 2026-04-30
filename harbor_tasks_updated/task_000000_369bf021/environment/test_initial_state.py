# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the cleanup script debugging and restoration task.
"""

import os
import subprocess
import pytest
from datetime import datetime, timedelta


# Constants
ADMIN_SCRIPT = "/home/user/admin/cleanup.sh"
USERDATA_DIR = "/var/userdata"
HOME_USERS_DIR = "/home/users"
BACKUP_ARCHIVED_DIR = "/backup/archived"

ALL_USERS = ["alice", "bob", "carol", "dan", "eve", "frank", "grace", "henry", "ivan", "judy", "kim", "larry"]
INACTIVE_USERS = ["bob", "eve", "henry", "kim"]
ACTIVE_USERS = ["alice", "carol", "dan", "frank", "grace", "ivan", "judy", "larry"]


class TestCleanupScriptExists:
    """Test that the cleanup script exists and has the expected buggy content."""

    def test_cleanup_script_exists(self):
        """The cleanup script must exist at /home/user/admin/cleanup.sh"""
        assert os.path.isfile(ADMIN_SCRIPT), \
            f"Cleanup script not found at {ADMIN_SCRIPT}"

    def test_cleanup_script_is_readable(self):
        """The cleanup script must be readable."""
        assert os.access(ADMIN_SCRIPT, os.R_OK), \
            f"Cleanup script at {ADMIN_SCRIPT} is not readable"

    def test_cleanup_script_contains_mtime_bug(self):
        """The cleanup script should use -mtime (the bug we need to fix)."""
        with open(ADMIN_SCRIPT, 'r') as f:
            content = f.read()
        assert "-mtime" in content, \
            f"Cleanup script should contain '-mtime' (the bug). Content:\n{content}"

    def test_cleanup_script_uses_find(self):
        """The cleanup script should use find command."""
        with open(ADMIN_SCRIPT, 'r') as f:
            content = f.read()
        assert "find" in content, \
            f"Cleanup script should use 'find' command. Content:\n{content}"

    def test_cleanup_script_uses_xargs(self):
        """The cleanup script should use xargs command."""
        with open(ADMIN_SCRIPT, 'r') as f:
            content = f.read()
        assert "xargs" in content, \
            f"Cleanup script should use 'xargs' command. Content:\n{content}"


class TestUserdataDirectory:
    """Test the /var/userdata/ directory structure."""

    def test_userdata_dir_exists(self):
        """The /var/userdata/ directory must exist."""
        assert os.path.isdir(USERDATA_DIR), \
            f"Userdata directory not found at {USERDATA_DIR}"

    def test_all_user_subdirs_exist(self):
        """All 12 user subdirectories must exist in /var/userdata/."""
        for user in ALL_USERS:
            user_dir = os.path.join(USERDATA_DIR, user)
            assert os.path.isdir(user_dir), \
                f"User directory not found: {user_dir}"

    def test_all_last_login_files_exist(self):
        """Each user must have a last-login file in their userdata directory."""
        for user in ALL_USERS:
            last_login = os.path.join(USERDATA_DIR, user, "last-login")
            assert os.path.isfile(last_login), \
                f"last-login file not found: {last_login}"

    def test_last_login_files_contain_timestamps(self):
        """Each last-login file should contain an ISO timestamp."""
        for user in ALL_USERS:
            last_login = os.path.join(USERDATA_DIR, user, "last-login")
            with open(last_login, 'r') as f:
                content = f.read().strip()
            # Check it looks like an ISO timestamp (YYYY-MM-DDTHH:MM:SS)
            assert len(content) >= 19, \
                f"last-login for {user} doesn't contain valid timestamp: '{content}'"
            assert "T" in content, \
                f"last-login for {user} doesn't look like ISO format: '{content}'"

    def test_exactly_12_user_dirs(self):
        """There should be exactly 12 user directories in /var/userdata/."""
        subdirs = [d for d in os.listdir(USERDATA_DIR) 
                   if os.path.isdir(os.path.join(USERDATA_DIR, d))]
        assert len(subdirs) == 12, \
            f"Expected 12 user directories in {USERDATA_DIR}, found {len(subdirs)}: {subdirs}"


class TestHomeUsersDirectory:
    """Test that /home/users/ is empty (all homedirs were archived)."""

    def test_home_users_dir_exists(self):
        """The /home/users/ directory must exist."""
        assert os.path.isdir(HOME_USERS_DIR), \
            f"Home users directory not found at {HOME_USERS_DIR}"

    def test_home_users_is_empty(self):
        """The /home/users/ directory should be empty (all users were archived)."""
        contents = os.listdir(HOME_USERS_DIR)
        assert len(contents) == 0, \
            f"Expected {HOME_USERS_DIR} to be empty, but found: {contents}"


class TestBackupArchivedDirectory:
    """Test the /backup/archived/ directory with all tarballs."""

    def test_backup_archived_dir_exists(self):
        """The /backup/archived/ directory must exist."""
        assert os.path.isdir(BACKUP_ARCHIVED_DIR), \
            f"Backup archived directory not found at {BACKUP_ARCHIVED_DIR}"

    def test_all_user_tarballs_exist(self):
        """All 12 user tarballs must exist in /backup/archived/."""
        for user in ALL_USERS:
            tarball = os.path.join(BACKUP_ARCHIVED_DIR, f"{user}.tar.gz")
            assert os.path.isfile(tarball), \
                f"Tarball not found: {tarball}"

    def test_exactly_12_tarballs(self):
        """There should be exactly 12 tarballs in /backup/archived/."""
        tarballs = [f for f in os.listdir(BACKUP_ARCHIVED_DIR) 
                    if f.endswith('.tar.gz')]
        assert len(tarballs) == 12, \
            f"Expected 12 tarballs in {BACKUP_ARCHIVED_DIR}, found {len(tarballs)}: {tarballs}"

    def test_tarballs_are_valid(self):
        """Each tarball should be a valid gzip archive."""
        for user in ALL_USERS:
            tarball = os.path.join(BACKUP_ARCHIVED_DIR, f"{user}.tar.gz")
            # Try to list contents to verify it's valid
            result = subprocess.run(
                ["tar", "-tzf", tarball],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"Tarball {tarball} is not a valid tar.gz archive: {result.stderr}"


class TestDirectoriesWritable:
    """Test that required directories are writable."""

    def test_admin_dir_writable(self):
        """The /home/user/admin/ directory should be writable."""
        admin_dir = "/home/user/admin"
        assert os.path.isdir(admin_dir), \
            f"Admin directory not found at {admin_dir}"
        assert os.access(admin_dir, os.W_OK), \
            f"Admin directory {admin_dir} is not writable"

    def test_home_users_writable(self):
        """The /home/users/ directory should be writable."""
        assert os.access(HOME_USERS_DIR, os.W_OK), \
            f"{HOME_USERS_DIR} is not writable"

    def test_backup_archived_writable(self):
        """The /backup/archived/ directory should be writable."""
        assert os.access(BACKUP_ARCHIVED_DIR, os.W_OK), \
            f"{BACKUP_ARCHIVED_DIR} is not writable"


class TestRequiredTools:
    """Test that required tools are available."""

    @pytest.mark.parametrize("tool", ["bash", "find", "xargs", "tar", "date", "awk", "sed", "grep", "stat", "touch"])
    def test_tool_available(self, tool):
        """Required tools must be available in PATH."""
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Required tool '{tool}' is not available in PATH"

    def test_gnu_date_available(self):
        """GNU date with -d option must be available."""
        result = subprocess.run(
            ["date", "-d", "2024-01-01", "+%Y-%m-%d"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"GNU date with -d option is not available: {result.stderr}"
        assert "2024-01-01" in result.stdout, \
            f"GNU date -d option not working as expected: {result.stdout}"
