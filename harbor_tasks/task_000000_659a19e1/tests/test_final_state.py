# test_final_state.py
"""
Tests to validate the FINAL state of the operating system/filesystem
AFTER the student has completed the disk monitoring script creation task.

This verifies that all required directories, scripts, and log files exist
with the correct format and permissions.
"""

import pytest
import os
import re
import stat
import subprocess


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_scripts_directory_exists(self):
        """Verify /home/user/scripts directory exists."""
        scripts_dir = "/home/user/scripts"
        assert os.path.isdir(scripts_dir), (
            f"Directory {scripts_dir} does not exist. "
            "The student must create this directory to store the disk_monitor.sh script."
        )

    def test_logs_directory_exists(self):
        """Verify /home/user/logs directory exists."""
        logs_dir = "/home/user/logs"
        assert os.path.isdir(logs_dir), (
            f"Directory {logs_dir} does not exist. "
            "The student must create this directory to store the disk_status.log file."
        )


class TestScriptFile:
    """Test that the disk_monitor.sh script exists and is properly configured."""

    def test_script_exists(self):
        """Verify the disk_monitor.sh script exists at the correct path."""
        script_path = "/home/user/scripts/disk_monitor.sh"
        assert os.path.isfile(script_path), (
            f"Script {script_path} does not exist. "
            "The student must create the disk monitoring script at this exact path."
        )

    def test_script_is_executable(self):
        """Verify the script has executable permissions."""
        script_path = "/home/user/scripts/disk_monitor.sh"
        assert os.path.isfile(script_path), (
            f"Script {script_path} does not exist. Cannot check permissions."
        )
        assert os.access(script_path, os.X_OK), (
            f"Script {script_path} is not executable. "
            "The student must make the script executable using 'chmod +x'."
        )

    def test_script_has_shebang(self):
        """Verify the script has a valid shebang line."""
        script_path = "/home/user/scripts/disk_monitor.sh"
        assert os.path.isfile(script_path), (
            f"Script {script_path} does not exist. Cannot check shebang."
        )
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()

        valid_shebangs = ['#!/bin/bash', '#!/bin/sh', '#!/usr/bin/env bash', '#!/usr/bin/env sh']
        assert any(first_line.startswith(shebang) for shebang in valid_shebangs), (
            f"Script {script_path} does not have a valid shebang. "
            f"Found: '{first_line}'. "
            "Expected one of: #!/bin/bash, #!/bin/sh, #!/usr/bin/env bash, #!/usr/bin/env sh"
        )

    def test_script_is_not_empty(self):
        """Verify the script has content beyond just the shebang."""
        script_path = "/home/user/scripts/disk_monitor.sh"
        assert os.path.isfile(script_path), (
            f"Script {script_path} does not exist. Cannot check content."
        )
        with open(script_path, 'r') as f:
            content = f.read()

        # Remove comments and empty lines to check for actual code
        lines = [line.strip() for line in content.split('\n') 
                 if line.strip() and not line.strip().startswith('#')]

        # Should have at least the shebang line removed, so check if there's actual code
        assert len(lines) > 0 or len(content) > 20, (
            f"Script {script_path} appears to be empty or contains only comments. "
            "The script must contain actual shell commands to monitor disk usage."
        )


class TestLogFile:
    """Test that the log file exists and has the correct format."""

    def test_log_file_exists(self):
        """Verify the disk_status.log file exists."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist. "
            "The student must run the script at least once to generate the log file."
        )

    def test_log_file_not_empty(self):
        """Verify the log file is not empty."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        assert os.path.getsize(log_path) > 0, (
            f"Log file {log_path} is empty. "
            "The script must write a status line to the log file."
        )

    def test_log_file_has_content(self):
        """Verify the log file contains at least one line."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, (
            f"Log file {log_path} does not contain any non-empty lines. "
            "The script must write at least one status line to the log."
        )

    def test_log_line_format_overall(self):
        """Verify the log line matches the expected pipe-delimited format."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, f"Log file {log_path} has no content."

        # Check the last line (most recent entry)
        last_line = lines[-1]

        # Expected format: TIMESTAMP|FILESYSTEM|USAGE_PERCENT|STATUS
        # Pattern: YYYY-MM-DD HH:MM:SS|/|NUMBER|OK or WARNING
        pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\|/\|\d+\|(OK|WARNING)$'

        assert re.match(pattern, last_line), (
            f"Log line does not match expected format.\n"
            f"Found: '{last_line}'\n"
            f"Expected format: 'YYYY-MM-DD HH:MM:SS|/|USAGE_PERCENT|STATUS'\n"
            f"Example: '2024-01-15 14:30:22|/|45|OK'"
        )

    def test_log_timestamp_format(self):
        """Verify the timestamp field is in correct format."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, f"Log file {log_path} has no content."

        last_line = lines[-1]
        fields = last_line.split('|')

        assert len(fields) >= 1, (
            f"Log line has no fields. Found: '{last_line}'"
        )

        timestamp = fields[0]
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'

        assert re.match(timestamp_pattern, timestamp), (
            f"Timestamp field is not in correct format.\n"
            f"Found: '{timestamp}'\n"
            f"Expected format: 'YYYY-MM-DD HH:MM:SS' (e.g., '2024-01-15 14:30:22')"
        )

    def test_log_filesystem_field(self):
        """Verify the filesystem field is exactly '/'."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, f"Log file {log_path} has no content."

        last_line = lines[-1]
        fields = last_line.split('|')

        assert len(fields) >= 2, (
            f"Log line does not have enough fields. Found: '{last_line}'\n"
            f"Expected 4 pipe-delimited fields."
        )

        filesystem = fields[1]
        assert filesystem == "/", (
            f"Filesystem field is not '/'.\n"
            f"Found: '{filesystem}'\n"
            f"Expected: '/'"
        )

    def test_log_usage_percent_field(self):
        """Verify the usage percent field is a valid integer."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, f"Log file {log_path} has no content."

        last_line = lines[-1]
        fields = last_line.split('|')

        assert len(fields) >= 3, (
            f"Log line does not have enough fields. Found: '{last_line}'\n"
            f"Expected 4 pipe-delimited fields."
        )

        usage_percent = fields[2]

        assert usage_percent.isdigit(), (
            f"Usage percent field is not a valid integer.\n"
            f"Found: '{usage_percent}'\n"
            f"Expected: a number without % sign (e.g., '45')"
        )

        usage_int = int(usage_percent)
        assert 0 <= usage_int <= 100, (
            f"Usage percent is out of expected range (0-100).\n"
            f"Found: {usage_int}\n"
            f"This should represent disk usage percentage."
        )

    def test_log_status_field(self):
        """Verify the status field is either 'OK' or 'WARNING'."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, f"Log file {log_path} has no content."

        last_line = lines[-1]
        fields = last_line.split('|')

        assert len(fields) >= 4, (
            f"Log line does not have enough fields. Found: '{last_line}'\n"
            f"Expected 4 pipe-delimited fields: TIMESTAMP|FILESYSTEM|USAGE_PERCENT|STATUS"
        )

        status = fields[3]
        assert status in ["OK", "WARNING"], (
            f"Status field is not valid.\n"
            f"Found: '{status}'\n"
            f"Expected: 'OK' (if usage < 80%) or 'WARNING' (if usage >= 80%)"
        )

    def test_log_status_matches_usage(self):
        """Verify the status correctly reflects the usage percentage."""
        log_path = "/home/user/logs/disk_status.log"
        assert os.path.isfile(log_path), (
            f"Log file {log_path} does not exist."
        )
        with open(log_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) >= 1, f"Log file {log_path} has no content."

        last_line = lines[-1]
        fields = last_line.split('|')

        assert len(fields) >= 4, (
            f"Log line does not have enough fields."
        )

        usage_percent = fields[2]
        status = fields[3]

        if usage_percent.isdigit():
            usage_int = int(usage_percent)
            if usage_int >= 80:
                assert status == "WARNING", (
                    f"Status should be 'WARNING' when usage is {usage_int}% (>= 80%).\n"
                    f"Found status: '{status}'"
                )
            else:
                assert status == "OK", (
                    f"Status should be 'OK' when usage is {usage_int}% (< 80%).\n"
                    f"Found status: '{status}'"
                )


class TestScriptExecution:
    """Test that the script can be executed successfully."""

    def test_script_runs_without_error(self):
        """Verify the script can be executed without errors."""
        script_path = "/home/user/scripts/disk_monitor.sh"

        if not os.path.isfile(script_path):
            pytest.skip(f"Script {script_path} does not exist.")

        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Script execution failed with return code {result.returncode}.\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    def test_script_updates_log_file(self):
        """Verify running the script adds/updates the log file."""
        script_path = "/home/user/scripts/disk_monitor.sh"
        log_path = "/home/user/logs/disk_status.log"

        if not os.path.isfile(script_path):
            pytest.skip(f"Script {script_path} does not exist.")

        # Get initial state
        initial_exists = os.path.isfile(log_path)
        initial_size = os.path.getsize(log_path) if initial_exists else 0

        # Run the script
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Script execution failed."
        )

        # Verify log file exists after execution
        assert os.path.isfile(log_path), (
            f"Log file {log_path} was not created after running the script."
        )

        # Verify log file has content
        assert os.path.getsize(log_path) > 0, (
            f"Log file {log_path} is empty after running the script."
        )
