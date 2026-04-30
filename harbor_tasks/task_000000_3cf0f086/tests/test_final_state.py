# test_final_state.py
"""
Tests to validate the final state of the system after the student has completed the task.
Task: Fix permissions on /var/log/syscheck.log so that syscheck.sh can write to it.
"""

import os
import stat
import subprocess
import hashlib
import pytest


class TestLogFilePermissions:
    """Verify the log file has correct permissions after the fix."""

    def test_log_file_exists(self):
        """The log file must still exist."""
        log_path = "/var/log/syscheck.log"
        assert os.path.exists(log_path), f"Log file not found at {log_path}"

    def test_log_file_is_writable(self):
        """The log file must be writable by the owner."""
        log_path = "/var/log/syscheck.log"
        mode = os.stat(log_path).st_mode
        assert mode & stat.S_IWUSR, \
            f"Log file at {log_path} is not writable by owner. Current mode: {oct(mode & 0o777)}"

    def test_log_file_writable_access(self):
        """The log file must be writable by the current user."""
        log_path = "/var/log/syscheck.log"
        assert os.access(log_path, os.W_OK), \
            f"{log_path} is not writable by the current user"


class TestScriptUnmodified:
    """Verify the script has not been modified."""

    def test_script_exists(self):
        """The script must still exist."""
        script_path = "/home/user/scripts/syscheck.sh"
        assert os.path.exists(script_path), f"Script not found at {script_path}"

    def test_script_content_unchanged(self):
        """The script content must remain unchanged."""
        script_path = "/home/user/scripts/syscheck.sh"

        expected_content = '''#!/bin/bash
echo "=== System Check $(date) ===" >> /var/log/syscheck.log
echo "Disk Usage:" >> /var/log/syscheck.log
df -h >> /var/log/syscheck.log
echo "Memory:" >> /var/log/syscheck.log
free -m >> /var/log/syscheck.log
echo "Load Average:" >> /var/log/syscheck.log
uptime >> /var/log/syscheck.log
echo "" >> /var/log/syscheck.log
'''

        with open(script_path, 'r') as f:
            actual_content = f.read()

        # Normalize line endings for comparison
        expected_normalized = expected_content.strip()
        actual_normalized = actual_content.strip()

        assert actual_normalized == expected_normalized, \
            "The script /home/user/scripts/syscheck.sh has been modified. It must remain unchanged."

    def test_script_still_writes_to_correct_log(self):
        """The script must still write to /var/log/syscheck.log."""
        script_path = "/home/user/scripts/syscheck.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert "/var/log/syscheck.log" in content, \
            "Script must still write to /var/log/syscheck.log"


class TestScriptExecution:
    """Verify the script runs successfully and produces correct output."""

    def test_script_runs_successfully(self):
        """The script must exit with code 0."""
        script_path = "/home/user/scripts/syscheck.sh"
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Script failed with exit code {result.returncode}. Stderr: {result.stderr}"

    def test_log_file_has_content_after_script(self):
        """After running the script, the log file must have content."""
        log_path = "/var/log/syscheck.log"
        script_path = "/home/user/scripts/syscheck.sh"

        # Run the script
        subprocess.run([script_path], capture_output=True)

        size = os.path.getsize(log_path)
        assert size > 0, \
            f"Log file at {log_path} is still empty after running the script"


class TestLogFileContent:
    """Verify the log file contains the expected content from the script."""

    @pytest.fixture(autouse=True)
    def run_script_and_read_log(self):
        """Run the script and read the log content for all tests in this class."""
        script_path = "/home/user/scripts/syscheck.sh"
        log_path = "/var/log/syscheck.log"

        # Run the script
        subprocess.run([script_path], capture_output=True)

        # Read the log content
        with open(log_path, 'r') as f:
            self.log_content = f.read()

    def test_log_contains_system_check_header(self):
        """Log must contain the System Check header."""
        assert "=== System Check" in self.log_content, \
            "Log file does not contain '=== System Check' header"

    def test_log_contains_disk_usage_label(self):
        """Log must contain the Disk Usage label."""
        assert "Disk Usage:" in self.log_content, \
            "Log file does not contain 'Disk Usage:' label"

    def test_log_contains_df_output(self):
        """Log must contain actual df -h output (filesystem data)."""
        # df -h output typically contains "Filesystem" header or "Use%" column
        # or actual mount points like /dev, tmpfs, etc.
        has_filesystem_header = "Filesystem" in self.log_content
        has_use_percent = "Use%" in self.log_content or "%" in self.log_content
        has_dev_or_tmpfs = "/dev" in self.log_content or "tmpfs" in self.log_content or "overlay" in self.log_content

        assert has_filesystem_header or has_dev_or_tmpfs, \
            "Log file does not contain actual df -h output. " \
            "Expected to find 'Filesystem' header or actual filesystem entries like '/dev' or 'tmpfs'. " \
            "This suggests the content was manually created rather than by running the script."

    def test_log_contains_memory_label(self):
        """Log must contain the Memory label."""
        assert "Memory:" in self.log_content, \
            "Log file does not contain 'Memory:' label"

    def test_log_contains_free_output(self):
        """Log must contain actual free -m output."""
        # free -m output contains "Mem:" and/or "total" headers
        has_mem = "Mem:" in self.log_content
        has_total = "total" in self.log_content.lower()
        has_free_or_used = "free" in self.log_content.lower() or "used" in self.log_content.lower()

        assert has_mem or (has_total and has_free_or_used), \
            "Log file does not contain actual free -m output. " \
            "Expected to find 'Mem:' or memory statistics."

    def test_log_contains_load_average_label(self):
        """Log must contain the Load Average label."""
        assert "Load Average:" in self.log_content, \
            "Log file does not contain 'Load Average:' label"

    def test_log_contains_uptime_output(self):
        """Log must contain actual uptime output."""
        # uptime output typically contains "load average" or "up" and time information
        has_load_avg = "load average" in self.log_content.lower()
        has_up = " up " in self.log_content.lower()

        assert has_load_avg or has_up, \
            "Log file does not contain actual uptime output. " \
            "Expected to find 'load average' or 'up' time information."


class TestAntiShortcut:
    """Tests to ensure the task was completed properly, not by shortcuts."""

    def test_log_contains_real_filesystem_data(self):
        """Verify the log contains real filesystem data from df, not fake content."""
        log_path = "/var/log/syscheck.log"
        script_path = "/home/user/scripts/syscheck.sh"

        # Run the script to ensure fresh output
        subprocess.run([script_path], capture_output=True)

        with open(log_path, 'r') as f:
            log_content = f.read()

        # Get actual df output to compare
        df_result = subprocess.run(["df", "-h"], capture_output=True, text=True)
        df_lines = df_result.stdout.strip().split('\n')

        # At least one line from df output (other than header) should appear in log
        # Skip the header line and check for at least one filesystem entry
        found_real_df_data = False
        for line in df_lines[1:]:  # Skip header
            if line.strip():
                # Check if the first column (filesystem name) appears in the log
                fs_name = line.split()[0]
                if fs_name in log_content:
                    found_real_df_data = True
                    break

        assert found_real_df_data, \
            "Log file does not contain real filesystem data from df -h. " \
            "The log must be generated by actually running the script, not by manually creating content."

    def test_script_can_append_multiple_times(self):
        """Verify the script can be run multiple times and appends each time."""
        log_path = "/var/log/syscheck.log"
        script_path = "/home/user/scripts/syscheck.sh"

        # Get initial size
        initial_size = os.path.getsize(log_path)

        # Run the script
        result = subprocess.run([script_path], capture_output=True)
        assert result.returncode == 0, "Script should run successfully"

        # Check size increased
        new_size = os.path.getsize(log_path)
        assert new_size > initial_size, \
            "Script should append to log file, but file size did not increase"
