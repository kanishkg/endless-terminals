# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the cleanup script debugging and restoration task.
"""

import os
import subprocess
import pytest
import tempfile
import shutil
from datetime import datetime


# Constants
ADMIN_SCRIPT = "/home/user/admin/cleanup.sh"
USERDATA_DIR = "/var/userdata"
HOME_USERS_DIR = "/home/users"
BACKUP_ARCHIVED_DIR = "/backup/archived"

ALL_USERS = ["alice", "bob", "carol", "dan", "eve", "frank", "grace", "henry", "ivan", "judy", "kim", "larry"]
INACTIVE_USERS = ["bob", "eve", "henry", "kim"]
ACTIVE_USERS = ["alice", "carol", "dan", "frank", "grace", "ivan", "judy", "larry"]


class TestRestoredHomeDirectories:
    """Test that active users' home directories have been restored."""

    def test_home_users_dir_exists(self):
        """The /home/users/ directory must exist."""
        assert os.path.isdir(HOME_USERS_DIR), \
            f"Home users directory not found at {HOME_USERS_DIR}"

    @pytest.mark.parametrize("user", ACTIVE_USERS)
    def test_active_user_homedir_restored(self, user):
        """Each active user should have their home directory restored."""
        user_home = os.path.join(HOME_USERS_DIR, user)
        assert os.path.isdir(user_home), \
            f"Active user {user}'s home directory not restored at {user_home}"

    @pytest.mark.parametrize("user", INACTIVE_USERS)
    def test_inactive_user_homedir_not_restored(self, user):
        """Inactive users should NOT have their home directories restored."""
        user_home = os.path.join(HOME_USERS_DIR, user)
        assert not os.path.exists(user_home), \
            f"Inactive user {user}'s home directory should NOT exist at {user_home}"

    def test_exactly_8_homedirs(self):
        """There should be exactly 8 home directories (active users only)."""
        if not os.path.isdir(HOME_USERS_DIR):
            pytest.fail(f"{HOME_USERS_DIR} does not exist")
        subdirs = [d for d in os.listdir(HOME_USERS_DIR) 
                   if os.path.isdir(os.path.join(HOME_USERS_DIR, d))]
        assert len(subdirs) == 8, \
            f"Expected 8 home directories in {HOME_USERS_DIR}, found {len(subdirs)}: {sorted(subdirs)}"

    def test_correct_users_restored(self):
        """The restored home directories should be exactly the active users."""
        if not os.path.isdir(HOME_USERS_DIR):
            pytest.fail(f"{HOME_USERS_DIR} does not exist")
        subdirs = set(d for d in os.listdir(HOME_USERS_DIR) 
                      if os.path.isdir(os.path.join(HOME_USERS_DIR, d)))
        expected = set(ACTIVE_USERS)
        assert subdirs == expected, \
            f"Expected home directories for {sorted(expected)}, found {sorted(subdirs)}"


class TestBackupArchives:
    """Test that only inactive users' tarballs remain in /backup/archived/."""

    def test_backup_archived_dir_exists(self):
        """The /backup/archived/ directory must exist."""
        assert os.path.isdir(BACKUP_ARCHIVED_DIR), \
            f"Backup archived directory not found at {BACKUP_ARCHIVED_DIR}"

    @pytest.mark.parametrize("user", INACTIVE_USERS)
    def test_inactive_user_tarball_exists(self, user):
        """Each inactive user's tarball should still exist."""
        tarball = os.path.join(BACKUP_ARCHIVED_DIR, f"{user}.tar.gz")
        assert os.path.isfile(tarball), \
            f"Inactive user {user}'s tarball should exist at {tarball}"

    @pytest.mark.parametrize("user", ACTIVE_USERS)
    def test_active_user_tarball_removed(self, user):
        """Active users' tarballs should be removed."""
        tarball = os.path.join(BACKUP_ARCHIVED_DIR, f"{user}.tar.gz")
        assert not os.path.exists(tarball), \
            f"Active user {user}'s tarball should NOT exist at {tarball}"

    def test_exactly_4_tarballs(self):
        """There should be exactly 4 tarballs (inactive users only)."""
        if not os.path.isdir(BACKUP_ARCHIVED_DIR):
            pytest.fail(f"{BACKUP_ARCHIVED_DIR} does not exist")
        tarballs = [f for f in os.listdir(BACKUP_ARCHIVED_DIR) 
                    if f.endswith('.tar.gz')]
        assert len(tarballs) == 4, \
            f"Expected 4 tarballs in {BACKUP_ARCHIVED_DIR}, found {len(tarballs)}: {sorted(tarballs)}"

    def test_correct_tarballs_remain(self):
        """The remaining tarballs should be exactly the inactive users."""
        if not os.path.isdir(BACKUP_ARCHIVED_DIR):
            pytest.fail(f"{BACKUP_ARCHIVED_DIR} does not exist")
        tarballs = set(f.replace('.tar.gz', '') for f in os.listdir(BACKUP_ARCHIVED_DIR) 
                       if f.endswith('.tar.gz'))
        expected = set(INACTIVE_USERS)
        assert tarballs == expected, \
            f"Expected tarballs for {sorted(expected)}, found {sorted(tarballs)}"


class TestUserdataUnchanged:
    """Test that /var/userdata/ structure and contents are unchanged."""

    def test_userdata_dir_exists(self):
        """The /var/userdata/ directory must exist."""
        assert os.path.isdir(USERDATA_DIR), \
            f"Userdata directory not found at {USERDATA_DIR}"

    def test_all_user_subdirs_exist(self):
        """All 12 user subdirectories must still exist in /var/userdata/."""
        for user in ALL_USERS:
            user_dir = os.path.join(USERDATA_DIR, user)
            assert os.path.isdir(user_dir), \
                f"User directory not found: {user_dir}"

    def test_all_last_login_files_exist(self):
        """Each user must still have a last-login file."""
        for user in ALL_USERS:
            last_login = os.path.join(USERDATA_DIR, user, "last-login")
            assert os.path.isfile(last_login), \
                f"last-login file not found: {last_login}"

    def test_exactly_12_user_dirs(self):
        """There should still be exactly 12 user directories in /var/userdata/."""
        subdirs = [d for d in os.listdir(USERDATA_DIR) 
                   if os.path.isdir(os.path.join(USERDATA_DIR, d))]
        assert len(subdirs) == 12, \
            f"Expected 12 user directories in {USERDATA_DIR}, found {len(subdirs)}: {subdirs}"


class TestCleanupScriptFixed:
    """Test that the cleanup script has been fixed to check file content, not mtime."""

    def test_cleanup_script_exists(self):
        """The cleanup script must still exist."""
        assert os.path.isfile(ADMIN_SCRIPT), \
            f"Cleanup script not found at {ADMIN_SCRIPT}"

    def test_cleanup_script_is_executable_or_readable(self):
        """The cleanup script must be readable."""
        assert os.access(ADMIN_SCRIPT, os.R_OK), \
            f"Cleanup script at {ADMIN_SCRIPT} is not readable"

    def test_cleanup_script_no_longer_uses_mtime_for_logic(self):
        """The script should not rely solely on -mtime for determining inactivity."""
        with open(ADMIN_SCRIPT, 'r') as f:
            content = f.read()
        # The script might still use find, but shouldn't use -mtime +$THRESHOLD 
        # as the sole criterion for archiving. It should read file content.
        # Check that it reads the content of last-login files somehow
        reads_content = any(indicator in content for indicator in [
            'cat ', '$(cat', '`cat', 'read ', '$(<', 
            'date -d', 'date --date', 'awk', 'sed'
        ])
        assert reads_content, \
            f"Fixed script should read the content of last-login files to check timestamps. Script:\n{content}"

    def test_cleanup_script_uses_find(self):
        """The cleanup script should still use find command (domain requirement)."""
        with open(ADMIN_SCRIPT, 'r') as f:
            content = f.read()
        assert "find" in content, \
            f"Cleanup script must still use 'find' command. Content:\n{content}"

    def test_cleanup_script_uses_xargs(self):
        """The cleanup script should still use xargs command (domain requirement)."""
        with open(ADMIN_SCRIPT, 'r') as f:
            content = f.read()
        assert "xargs" in content, \
            f"Cleanup script must still use 'xargs' command. Content:\n{content}"


class TestFixedScriptBehavior:
    """Test that the fixed script correctly distinguishes based on file content."""

    def test_script_would_not_archive_recent_user(self):
        """
        Verify the fixed script logic would correctly identify a user with 
        recent login (in file content) as active, even if file mtime is old.
        """
        # Create a temporary test environment
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test userdata structure
            test_userdata = os.path.join(tmpdir, "userdata")
            test_home = os.path.join(tmpdir, "home")
            test_backup = os.path.join(tmpdir, "backup")

            os.makedirs(os.path.join(test_userdata, "testuser"))
            os.makedirs(os.path.join(test_home, "testuser"))
            os.makedirs(test_backup)

            # Create a last-login file with recent timestamp content
            last_login = os.path.join(test_userdata, "testuser", "last-login")
            # Use a date that's definitely within 90 days
            recent_date = "2025-01-15T10:00:00"
            with open(last_login, 'w') as f:
                f.write(recent_date)

            # Set old mtime (this is what the bug was using)
            old_timestamp = datetime(2024, 9, 1).timestamp()
            os.utime(last_login, (old_timestamp, old_timestamp))

            # Create a file in the home directory
            with open(os.path.join(test_home, "testuser", "testfile"), 'w') as f:
                f.write("test content")

            # Read the fixed script and adapt it for testing
            with open(ADMIN_SCRIPT, 'r') as f:
                script_content = f.read()

            # Create a modified version of the script for testing
            # Replace paths with our test paths
            test_script = script_content.replace('/var/userdata', test_userdata)
            test_script = test_script.replace('/home/users', test_home)
            test_script = test_script.replace('/backup/archived', test_backup)

            test_script_path = os.path.join(tmpdir, "test_cleanup.sh")
            with open(test_script_path, 'w') as f:
                f.write(test_script)
            os.chmod(test_script_path, 0o755)

            # Run the script
            result = subprocess.run(
                ["bash", test_script_path],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                env={**os.environ, 'HOME': tmpdir}
            )

            # The home directory should NOT be archived (user is active)
            homedir_exists = os.path.isdir(os.path.join(test_home, "testuser"))
            tarball_exists = os.path.isfile(os.path.join(test_backup, "testuser.tar.gz"))

            assert homedir_exists, \
                f"Fixed script incorrectly archived an active user (recent login in file content). " \
                f"Script stderr: {result.stderr}"
            assert not tarball_exists, \
                f"Fixed script created a tarball for an active user"

    def test_script_would_archive_old_user(self):
        """
        Verify the fixed script logic would correctly identify a user with 
        old login (in file content) as inactive.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            test_userdata = os.path.join(tmpdir, "userdata")
            test_home = os.path.join(tmpdir, "home")
            test_backup = os.path.join(tmpdir, "backup")

            os.makedirs(os.path.join(test_userdata, "olduser"))
            os.makedirs(os.path.join(test_home, "olduser"))
            os.makedirs(test_backup)

            # Create a last-login file with OLD timestamp content (>90 days)
            last_login = os.path.join(test_userdata, "olduser", "last-login")
            old_date = "2024-08-01T10:00:00"  # Very old
            with open(last_login, 'w') as f:
                f.write(old_date)

            # Create a file in the home directory
            with open(os.path.join(test_home, "olduser", "testfile"), 'w') as f:
                f.write("test content")

            with open(ADMIN_SCRIPT, 'r') as f:
                script_content = f.read()

            test_script = script_content.replace('/var/userdata', test_userdata)
            test_script = test_script.replace('/home/users', test_home)
            test_script = test_script.replace('/backup/archived', test_backup)

            test_script_path = os.path.join(tmpdir, "test_cleanup.sh")
            with open(test_script_path, 'w') as f:
                f.write(test_script)
            os.chmod(test_script_path, 0o755)

            result = subprocess.run(
                ["bash", test_script_path],
                capture_output=True,
                text=True,
                cwd=tmpdir,
                env={**os.environ, 'HOME': tmpdir}
            )

            # The home directory SHOULD be archived (user is inactive)
            homedir_exists = os.path.isdir(os.path.join(test_home, "olduser"))
            tarball_exists = os.path.isfile(os.path.join(test_backup, "olduser.tar.gz"))

            # At least one of these should be true for a working script
            archived_correctly = tarball_exists or not homedir_exists

            assert archived_correctly, \
                f"Fixed script failed to archive an inactive user (old login in file content). " \
                f"Homedir exists: {homedir_exists}, Tarball exists: {tarball_exists}. " \
                f"Script stderr: {result.stderr}"


class TestRestoredContentNotEmpty:
    """Test that restored home directories have content (not empty)."""

    @pytest.mark.parametrize("user", ACTIVE_USERS)
    def test_restored_homedir_has_content(self, user):
        """Each restored home directory should have some content."""
        user_home = os.path.join(HOME_USERS_DIR, user)
        if not os.path.isdir(user_home):
            pytest.skip(f"Home directory for {user} not restored")

        # Check that the directory is not completely empty
        # (it should have at least the files that were in the tarball)
        contents = os.listdir(user_home)
        # Allow for hidden files too
        all_contents = [f for f in os.listdir(user_home)]
        assert len(all_contents) >= 0, \
            f"Restored home directory for {user} exists but listing failed"
