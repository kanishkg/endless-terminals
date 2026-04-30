# test_initial_state.py
"""
Tests to validate the initial state of the system before the student performs the task.
Task: Fix permissions on /var/log/syscheck.log so that syscheck.sh can write to it.
"""

import os
import stat
import subprocess
import pytest


class TestScriptExists:
    """Verify the syscheck.sh script exists and is properly configured."""

    def test_script_file_exists(self):
        """The script file must exist at the expected location."""
        script_path = "/home/user/scripts/syscheck.sh"
        assert os.path.exists(script_path), f"Script not found at {script_path}"

    def test_script_is_file(self):
        """The script must be a regular file."""
        script_path = "/home/user/scripts/syscheck.sh"
        assert os.path.isfile(script_path), f"{script_path} is not a regular file"

    def test_script_is_executable(self):
        """The script must be executable."""
        script_path = "/home/user/scripts/syscheck.sh"
        mode = os.stat(script_path).st_mode
        assert mode & stat.S_IXUSR, f"{script_path} is not executable by owner"

    def test_script_permissions_755(self):
        """The script should have permissions 755."""
        script_path = "/home/user/scripts/syscheck.sh"
        mode = os.stat(script_path).st_mode & 0o777
        assert mode == 0o755, f"Script permissions are {oct(mode)}, expected 0o755"

    def test_script_content_correct(self):
        """The script must contain the expected content."""
        script_path = "/home/user/scripts/syscheck.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for shebang
        assert content.startswith("#!/bin/bash"), "Script must start with #!/bin/bash"

        # Check for key commands
        assert "/var/log/syscheck.log" in content, "Script must write to /var/log/syscheck.log"
        assert "df -h" in content, "Script must contain df -h command"
        assert "free -m" in content, "Script must contain free -m command"
        assert "uptime" in content, "Script must contain uptime command"
        assert "System Check" in content, "Script must contain 'System Check' header"
        assert "Disk Usage:" in content, "Script must contain 'Disk Usage:' label"
        assert "Memory:" in content, "Script must contain 'Memory:' label"
        assert "Load Average:" in content, "Script must contain 'Load Average:' label"


class TestScriptsDirectory:
    """Verify the scripts directory is properly configured."""

    def test_scripts_directory_exists(self):
        """The scripts directory must exist."""
        scripts_dir = "/home/user/scripts"
        assert os.path.exists(scripts_dir), f"Scripts directory not found at {scripts_dir}"

    def test_scripts_directory_is_directory(self):
        """The scripts path must be a directory."""
        scripts_dir = "/home/user/scripts"
        assert os.path.isdir(scripts_dir), f"{scripts_dir} is not a directory"

    def test_scripts_directory_writable(self):
        """The scripts directory must be writable by the agent."""
        scripts_dir = "/home/user/scripts"
        assert os.access(scripts_dir, os.W_OK), f"{scripts_dir} is not writable"


class TestLogFile:
    """Verify the log file exists with the expected initial state."""

    def test_log_file_exists(self):
        """The log file must exist."""
        log_path = "/var/log/syscheck.log"
        assert os.path.exists(log_path), f"Log file not found at {log_path}"

    def test_log_file_is_file(self):
        """The log path must be a regular file."""
        log_path = "/var/log/syscheck.log"
        assert os.path.isfile(log_path), f"{log_path} is not a regular file"

    def test_log_file_is_empty(self):
        """The log file must be empty (0 bytes)."""
        log_path = "/var/log/syscheck.log"
        size = os.path.getsize(log_path)
        assert size == 0, f"Log file should be empty but has {size} bytes"

    def test_log_file_owned_by_user(self):
        """The log file must be owned by user:user."""
        log_path = "/var/log/syscheck.log"
        stat_info = os.stat(log_path)

        # Get current user's uid and gid
        current_uid = os.getuid()
        current_gid = os.getgid()

        assert stat_info.st_uid == current_uid, \
            f"Log file owner uid is {stat_info.st_uid}, expected {current_uid} (current user)"
        assert stat_info.st_gid == current_gid, \
            f"Log file group gid is {stat_info.st_gid}, expected {current_gid} (current user's group)"

    def test_log_file_permissions_read_only(self):
        """The log file must have read-only permissions (444)."""
        log_path = "/var/log/syscheck.log"
        mode = os.stat(log_path).st_mode & 0o777
        assert mode == 0o444, f"Log file permissions are {oct(mode)}, expected 0o444 (read-only)"

    def test_log_file_not_writable(self):
        """The log file must NOT be writable in its initial state."""
        log_path = "/var/log/syscheck.log"
        assert not os.access(log_path, os.W_OK), \
            f"{log_path} should not be writable in initial state (this is the problem to fix)"


class TestRequiredTools:
    """Verify that required system tools are available."""

    def test_chmod_available(self):
        """chmod command must be available."""
        result = subprocess.run(["which", "chmod"], capture_output=True)
        assert result.returncode == 0, "chmod command not found"

    def test_df_available(self):
        """df command must be available."""
        result = subprocess.run(["which", "df"], capture_output=True)
        assert result.returncode == 0, "df command not found"

    def test_free_available(self):
        """free command must be available."""
        result = subprocess.run(["which", "free"], capture_output=True)
        assert result.returncode == 0, "free command not found"

    def test_uptime_available(self):
        """uptime command must be available."""
        result = subprocess.run(["which", "uptime"], capture_output=True)
        assert result.returncode == 0, "uptime command not found"

    def test_date_available(self):
        """date command must be available."""
        result = subprocess.run(["which", "date"], capture_output=True)
        assert result.returncode == 0, "date command not found"

    def test_cat_available(self):
        """cat command must be available."""
        result = subprocess.run(["which", "cat"], capture_output=True)
        assert result.returncode == 0, "cat command not found"

    def test_bash_available(self):
        """bash must be available for the script."""
        result = subprocess.run(["which", "bash"], capture_output=True)
        assert result.returncode == 0, "bash not found"


class TestScriptFailsInitially:
    """Verify that the script fails to write in the initial state."""

    def test_script_cannot_write_to_log(self):
        """Running the script should fail to write due to permissions."""
        script_path = "/home/user/scripts/syscheck.sh"
        log_path = "/var/log/syscheck.log"

        # Run the script and capture output
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True
        )

        # The script should fail (non-zero exit) or produce errors
        # because it can't write to the log file
        # Check that the log file is still empty
        size = os.path.getsize(log_path)
        assert size == 0, \
            f"Log file should still be empty after running script in initial state, but has {size} bytes"
