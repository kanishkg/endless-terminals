# test_initial_state.py
"""
Tests to validate the initial state of the system before the student fixes
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


class TestSSHDirectoryAndFiles:
    """Test that SSH directory and key files exist."""

    def test_ssh_directory_exists(self):
        """~/.ssh directory must exist."""
        assert os.path.isdir(SSH_DIR), f"SSH directory {SSH_DIR} does not exist"

    def test_private_key_exists(self):
        """Private key file must exist."""
        assert os.path.isfile(PRIVATE_KEY), f"Private key {PRIVATE_KEY} does not exist"

    def test_public_key_exists(self):
        """Public key file must exist."""
        assert os.path.isfile(PUBLIC_KEY), f"Public key {PUBLIC_KEY} does not exist"

    def test_ssh_config_exists(self):
        """SSH config file must exist."""
        assert os.path.isfile(SSH_CONFIG), f"SSH config {SSH_CONFIG} does not exist"

    def test_ssh_directory_is_writable(self):
        """~/.ssh directory must be writable."""
        assert os.access(SSH_DIR, os.W_OK), f"SSH directory {SSH_DIR} is not writable"


class TestPrivateKeyPermissions:
    """Test that private key has the problematic permissions (0644)."""

    def test_private_key_has_loose_permissions(self):
        """Private key must have 0644 permissions (the root cause of the issue)."""
        key_stat = os.stat(PRIVATE_KEY)
        mode = stat.S_IMODE(key_stat.st_mode)
        assert mode == 0o644, (
            f"Private key {PRIVATE_KEY} should have permissions 0644 (the bug), "
            f"but has {oct(mode)}"
        )

    def test_private_key_is_world_readable(self):
        """Private key must be readable by others (part of the bug)."""
        key_stat = os.stat(PRIVATE_KEY)
        mode = stat.S_IMODE(key_stat.st_mode)
        # Check if 'other' read bit is set
        assert mode & stat.S_IROTH, (
            f"Private key {PRIVATE_KEY} should be world-readable (the bug condition)"
        )


class TestSSHConfig:
    """Test SSH config content."""

    def test_ssh_config_contains_warehouse_host(self):
        """SSH config must contain warehouse host configuration."""
        with open(SSH_CONFIG, 'r') as f:
            content = f.read()
        assert "Host warehouse" in content, (
            f"SSH config {SSH_CONFIG} must contain 'Host warehouse' entry"
        )

    def test_ssh_config_references_correct_key(self):
        """SSH config must reference the etl_warehouse key."""
        with open(SSH_CONFIG, 'r') as f:
            content = f.read()
        assert "etl_warehouse" in content, (
            f"SSH config {SSH_CONFIG} must reference etl_warehouse key"
        )


class TestETLDirectory:
    """Test ETL directory and script setup."""

    def test_etl_directory_exists(self):
        """ETL directory must exist."""
        assert os.path.isdir(ETL_DIR), f"ETL directory {ETL_DIR} does not exist"

    def test_sync_script_exists(self):
        """Sync script must exist."""
        assert os.path.isfile(SYNC_SCRIPT), f"Sync script {SYNC_SCRIPT} does not exist"

    def test_sync_script_is_executable(self):
        """Sync script must be executable."""
        assert os.access(SYNC_SCRIPT, os.X_OK), (
            f"Sync script {SYNC_SCRIPT} must be executable"
        )

    def test_sync_script_contains_rsync(self):
        """Sync script must contain rsync command."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert "rsync" in content, (
            f"Sync script {SYNC_SCRIPT} must contain rsync command"
        )

    def test_sync_script_references_etl_warehouse_key(self):
        """Sync script must reference the etl_warehouse key."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        assert "etl_warehouse" in content, (
            f"Sync script {SYNC_SCRIPT} must reference etl_warehouse key"
        )


class TestStagingDirectory:
    """Test staging directory and sample files."""

    def test_staging_directory_exists(self):
        """Staging directory must exist."""
        assert os.path.isdir(STAGING_DIR), (
            f"Staging directory {STAGING_DIR} does not exist"
        )

    def test_staging_has_csv_files(self):
        """Staging directory must contain CSV files."""
        files = os.listdir(STAGING_DIR)
        csv_files = [f for f in files if f.endswith('.csv')]
        assert len(csv_files) > 0, (
            f"Staging directory {STAGING_DIR} must contain CSV files"
        )

    def test_expected_csv_files_exist(self):
        """Expected CSV files must exist in staging."""
        expected_files = [
            "orders_20240115.csv",
            "orders_20240116.csv",
            "orders_20240117.csv"
        ]
        for filename in expected_files:
            filepath = os.path.join(STAGING_DIR, filename)
            assert os.path.isfile(filepath), (
                f"Expected CSV file {filepath} does not exist"
            )


class TestMockSSHTools:
    """Test that mock SSH tools are set up correctly."""

    def test_ssh_permission_check_exists(self):
        """SSH permission check script must exist."""
        assert os.path.isfile(SSH_PERMISSION_CHECK), (
            f"SSH permission check script {SSH_PERMISSION_CHECK} does not exist"
        )

    def test_ssh_permission_check_is_executable(self):
        """SSH permission check script must be executable."""
        assert os.access(SSH_PERMISSION_CHECK, os.X_OK), (
            f"SSH permission check script {SSH_PERMISSION_CHECK} must be executable"
        )

    def test_test_ssh_script_exists(self):
        """Test SSH script must exist."""
        assert os.path.isfile(TEST_SSH_SCRIPT), (
            f"Test SSH script {TEST_SSH_SCRIPT} does not exist"
        )

    def test_test_ssh_script_is_executable(self):
        """Test SSH script must be executable."""
        assert os.access(TEST_SSH_SCRIPT, os.X_OK), (
            f"Test SSH script {TEST_SSH_SCRIPT} must be executable"
        )


class TestPermissionCheckFailsInitially:
    """Test that the permission check fails with current (buggy) state."""

    def test_ssh_permission_check_fails(self):
        """SSH permission check must fail due to loose key permissions."""
        result = subprocess.run(
            [SSH_PERMISSION_CHECK],
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": HOME}
        )
        assert result.returncode != 0, (
            "SSH permission check should FAIL with current loose permissions, "
            f"but it exited with code {result.returncode}. "
            "This indicates the key already has correct permissions."
        )

    def test_ssh_permission_check_mentions_too_open(self):
        """SSH permission check output should mention permissions are too open."""
        result = subprocess.run(
            [SSH_PERMISSION_CHECK],
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": HOME}
        )
        output = result.stdout + result.stderr
        assert "too open" in output.lower(), (
            f"SSH permission check should mention 'too open', got: {output}"
        )


class TestSystemTools:
    """Test that required system tools are available."""

    def test_stat_available(self):
        """stat command must be available."""
        result = subprocess.run(["which", "stat"], capture_output=True)
        assert result.returncode == 0, "stat command is not available"

    def test_chmod_available(self):
        """chmod command must be available."""
        result = subprocess.run(["which", "chmod"], capture_output=True)
        assert result.returncode == 0, "chmod command is not available"

    def test_ls_available(self):
        """ls command must be available."""
        result = subprocess.run(["which", "ls"], capture_output=True)
        assert result.returncode == 0, "ls command is not available"


class TestPrivateKeyContent:
    """Test that private key has actual content (not empty/corrupted)."""

    def test_private_key_not_empty(self):
        """Private key file must not be empty."""
        size = os.path.getsize(PRIVATE_KEY)
        assert size > 0, f"Private key {PRIVATE_KEY} is empty"

    def test_private_key_has_reasonable_size(self):
        """Private key file must have reasonable size for an SSH key."""
        size = os.path.getsize(PRIVATE_KEY)
        # SSH private keys are typically between 400 bytes and 10KB
        assert 100 < size < 20000, (
            f"Private key {PRIVATE_KEY} has unusual size {size} bytes"
        )
