# test_final_state.py
"""
Tests to validate the final state of the system after the student fixes
the SSH private key permission issue.
"""

import os
import stat
import subprocess
import pytest

HOME = "/home/user"
SSH_DIR = os.path.join(HOME, ".ssh")
ETL_DIR = os.path.join(HOME, "etl")
PRIVATE_KEY = os.path.join(SSH_DIR, "etl_warehouse")
PUBLIC_KEY = os.path.join(SSH_DIR, "etl_warehouse.pub")
SSH_CONFIG = os.path.join(SSH_DIR, "config")
SYNC_SCRIPT = os.path.join(ETL_DIR, "sync_to_warehouse.sh")
STAGING_DIR = os.path.join(ETL_DIR, "staging")
SSH_PERMISSION_CHECK = "/usr/local/bin/ssh-permission-check"
TEST_SSH_SCRIPT = os.path.join(ETL_DIR, "test_ssh.sh")


class TestPrivateKeyPermissionsFix:
    """Test that the private key now has correct permissions."""

    def test_private_key_exists(self):
        """Private key file must still exist after fix."""
        assert os.path.isfile(PRIVATE_KEY), (
            f"Private key {PRIVATE_KEY} does not exist. "
            "The fix should chmod the key, not delete it."
        )

    def test_private_key_has_secure_permissions(self):
        """Private key must have permissions 0600 or 0400."""
        key_stat = os.stat(PRIVATE_KEY)
        mode = stat.S_IMODE(key_stat.st_mode)
        assert mode in (0o600, 0o400), (
            f"Private key {PRIVATE_KEY} must have permissions 0600 or 0400, "
            f"but has {oct(mode)}. SSH requires private keys to not be accessible by others."
        )

    def test_private_key_not_world_readable(self):
        """Private key must not be readable by others."""
        key_stat = os.stat(PRIVATE_KEY)
        mode = stat.S_IMODE(key_stat.st_mode)
        assert not (mode & stat.S_IROTH), (
            f"Private key {PRIVATE_KEY} must not be world-readable. "
            f"Current permissions: {oct(mode)}"
        )

    def test_private_key_not_group_readable(self):
        """Private key must not be readable by group."""
        key_stat = os.stat(PRIVATE_KEY)
        mode = stat.S_IMODE(key_stat.st_mode)
        assert not (mode & stat.S_IRGRP), (
            f"Private key {PRIVATE_KEY} must not be group-readable. "
            f"Current permissions: {oct(mode)}"
        )

    def test_stat_command_shows_correct_permissions(self):
        """stat command must show 600 or 400 for the private key."""
        result = subprocess.run(
            ["stat", "-c", "%a", PRIVATE_KEY],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"stat command failed: {result.stderr}"
        perms = result.stdout.strip()
        assert perms in ("600", "400"), (
            f"stat -c %a {PRIVATE_KEY} must return 600 or 400, "
            f"but returned '{perms}'"
        )


class TestSSHPermissionCheckPasses:
    """Test that the SSH permission check now passes."""

    def test_ssh_permission_check_succeeds(self):
        """SSH permission check must now succeed."""
        result = subprocess.run(
            [SSH_PERMISSION_CHECK],
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": HOME}
        )
        assert result.returncode == 0, (
            f"SSH permission check should PASS after fixing key permissions, "
            f"but it exited with code {result.returncode}. "
            f"stdout: {result.stdout}, stderr: {result.stderr}"
        )

    def test_ssh_permission_check_outputs_ok(self):
        """SSH permission check should output 'Key permissions OK'."""
        result = subprocess.run(
            [SSH_PERMISSION_CHECK],
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": HOME}
        )
        output = result.stdout + result.stderr
        assert "Key permissions OK" in output, (
            f"SSH permission check should output 'Key permissions OK', "
            f"got: {output}"
        )


class TestPrivateKeyIntegrity:
    """Test that the private key content was not corrupted."""

    def test_private_key_not_empty(self):
        """Private key file must not be empty."""
        size = os.path.getsize(PRIVATE_KEY)
        assert size > 0, (
            f"Private key {PRIVATE_KEY} is empty. "
            "The fix should only change permissions, not truncate the file."
        )

    def test_private_key_has_reasonable_size(self):
        """Private key file must have reasonable size for an SSH key."""
        size = os.path.getsize(PRIVATE_KEY)
        # SSH private keys are typically between 400 bytes and 10KB
        assert 100 < size < 20000, (
            f"Private key {PRIVATE_KEY} has unusual size {size} bytes. "
            "The key content may have been corrupted."
        )

    def test_private_key_is_readable_by_owner(self):
        """Private key must still be readable by owner."""
        key_stat = os.stat(PRIVATE_KEY)
        mode = stat.S_IMODE(key_stat.st_mode)
        assert mode & stat.S_IRUSR, (
            f"Private key {PRIVATE_KEY} must be readable by owner. "
            f"Current permissions: {oct(mode)}"
        )


class TestInvariantsPreserved:
    """Test that invariant files were not modified."""

    def test_public_key_exists(self):
        """Public key file must still exist."""
        assert os.path.isfile(PUBLIC_KEY), (
            f"Public key {PUBLIC_KEY} must still exist"
        )

    def test_ssh_config_exists(self):
        """SSH config file must still exist."""
        assert os.path.isfile(SSH_CONFIG), (
            f"SSH config {SSH_CONFIG} must still exist"
        )

    def test_ssh_config_contains_warehouse_host(self):
        """SSH config must still contain warehouse host configuration."""
        with open(SSH_CONFIG, 'r') as f:
            content = f.read()
        assert "Host warehouse" in content, (
            f"SSH config {SSH_CONFIG} must still contain 'Host warehouse' entry"
        )

    def test_ssh_config_references_etl_warehouse_key(self):
        """SSH config must still reference the etl_warehouse key."""
        with open(SSH_CONFIG, 'r') as f:
            content = f.read()
        assert "etl_warehouse" in content, (
            f"SSH config {SSH_CONFIG} must still reference etl_warehouse key"
        )

    def test_sync_script_exists(self):
        """Sync script must still exist."""
        assert os.path.isfile(SYNC_SCRIPT), (
            f"Sync script {SYNC_SCRIPT} must still exist"
        )

    def test_sync_script_contains_rsync(self):
        """Sync script must still contain rsync command."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert "rsync" in content, (
            f"Sync script {SYNC_SCRIPT} must still contain rsync command"
        )

    def test_sync_script_references_etl_warehouse_key(self):
        """Sync script must still reference the etl_warehouse key."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert "etl_warehouse" in content, (
            f"Sync script {SYNC_SCRIPT} must still reference etl_warehouse key"
        )

    def test_staging_directory_exists(self):
        """Staging directory must still exist."""
        assert os.path.isdir(STAGING_DIR), (
            f"Staging directory {STAGING_DIR} must still exist"
        )

    def test_staging_csv_files_exist(self):
        """Expected CSV files must still exist in staging."""
        expected_files = [
            "orders_20240115.csv",
            "orders_20240116.csv",
            "orders_20240117.csv"
        ]
        for filename in expected_files:
            filepath = os.path.join(STAGING_DIR, filename)
            assert os.path.isfile(filepath), (
                f"Expected CSV file {filepath} must still exist"
            )


class TestAntiShortcutGuards:
    """Test that the fix was done correctly, not via shortcuts."""

    def test_private_key_path_unchanged(self):
        """The fix must use the same key path, not a different key."""
        # Check that the original key location is what's being used
        assert os.path.isfile(PRIVATE_KEY), (
            f"The original private key at {PRIVATE_KEY} must still exist. "
            "The fix should chmod this key, not use a different key."
        )

    def test_sync_script_not_modified_to_use_different_key(self):
        """Sync script must not be modified to use a different key path."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        # The script should still reference ~/.ssh/etl_warehouse
        assert "~/.ssh/etl_warehouse" in content or "$HOME/.ssh/etl_warehouse" in content, (
            f"Sync script must still reference the original key path ~/.ssh/etl_warehouse. "
            "The fix should be chmod of the key, not changing the script to use a different key."
        )

    def test_permissions_are_exactly_600_or_400(self):
        """Permissions must be exactly 600 or 400, not some other restrictive value."""
        result = subprocess.run(
            ["stat", "-c", "%a", PRIVATE_KEY],
            capture_output=True,
            text=True
        )
        perms = result.stdout.strip()
        # Only 600 and 400 are acceptable for SSH private keys
        assert perms in ("600", "400"), (
            f"Private key permissions must be exactly 600 or 400, not {perms}. "
            "These are the standard secure permissions for SSH private keys."
        )
