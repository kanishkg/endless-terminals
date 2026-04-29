# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the top_ips.sh script.
"""

import os
import stat
import subprocess
import pytest
from datetime import datetime, timedelta


class TestScriptExists:
    """Tests for the monitoring script existence and properties."""

    def test_script_file_exists(self):
        """Verify /home/user/scripts/top_ips.sh exists."""
        script_path = "/home/user/scripts/top_ips.sh"
        assert os.path.isfile(script_path), \
            f"Script file {script_path} does not exist"

    def test_script_is_executable(self):
        """Verify the script is executable."""
        script_path = "/home/user/scripts/top_ips.sh"
        assert os.access(script_path, os.X_OK), \
            f"Script {script_path} is not executable"

    def test_script_is_bash_script(self):
        """Verify the script starts with bash shebang."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash", \
            f"Script should start with '#!/bin/bash', got: {first_line}"

    def test_script_contains_expected_content(self):
        """Verify the script contains the buggy cut command."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for key elements of the original buggy script
        assert 'LOGDIR="/var/log/httpd"' in content, \
            "Script should define LOGDIR as /var/log/httpd"
        assert "date" in content and "yesterday" in content, \
            "Script should use date command to get yesterday's date"
        assert "cut -d' ' -f1" in content, \
            "Script should contain the buggy 'cut -d' ' -f1' command"
        assert "uniq -c" in content, \
            "Script should use uniq -c for counting"
        assert "head -10" in content, \
            "Script should use head -10 to get top 10"


class TestScriptsDirectory:
    """Tests for the scripts directory."""

    def test_scripts_directory_exists(self):
        """Verify /home/user/scripts/ directory exists."""
        scripts_dir = "/home/user/scripts"
        assert os.path.isdir(scripts_dir), \
            f"Scripts directory {scripts_dir} does not exist"

    def test_scripts_directory_is_writable(self):
        """Verify /home/user/scripts/ is writable."""
        scripts_dir = "/home/user/scripts"
        assert os.access(scripts_dir, os.W_OK), \
            f"Scripts directory {scripts_dir} is not writable"


class TestLogDirectory:
    """Tests for the log directory and files."""

    def test_log_directory_exists(self):
        """Verify /var/log/httpd/ directory exists."""
        log_dir = "/var/log/httpd"
        assert os.path.isdir(log_dir), \
            f"Log directory {log_dir} does not exist"

    def test_log_files_exist(self):
        """Verify daily log files exist from 20250120 to 20250125."""
        log_dir = "/var/log/httpd"
        expected_dates = ["20250120", "20250121", "20250122", "20250123", "20250124", "20250125"]

        for date in expected_dates:
            log_file = os.path.join(log_dir, f"access_{date}.log")
            assert os.path.isfile(log_file), \
                f"Log file {log_file} does not exist"

    def test_log_files_are_readable(self):
        """Verify log files are readable by current user."""
        log_dir = "/var/log/httpd"
        expected_dates = ["20250120", "20250121", "20250122", "20250123", "20250124", "20250125"]

        for date in expected_dates:
            log_file = os.path.join(log_dir, f"access_{date}.log")
            assert os.access(log_file, os.R_OK), \
                f"Log file {log_file} is not readable"

    def test_log_file_20250125_has_expected_line_count(self):
        """Verify access_20250125.log has approximately 8847 lines."""
        log_file = "/var/log/httpd/access_20250125.log"
        result = subprocess.run(['wc', '-l', log_file], capture_output=True, text=True)
        line_count = int(result.stdout.split()[0])
        assert 8800 <= line_count <= 8900, \
            f"Expected ~8847 lines in {log_file}, got {line_count}"


class TestLogFormat:
    """Tests for the log file format and the X-Forwarded-For issue."""

    def test_newer_logs_contain_x_forwarded_for(self):
        """Verify logs from 20250122 onwards contain X-Forwarded-For lines."""
        log_file = "/var/log/httpd/access_20250125.log"
        result = subprocess.run(
            ['grep', '-c', 'X-Forwarded-For:', log_file],
            capture_output=True, text=True
        )
        xff_count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert xff_count > 0, \
            f"Expected X-Forwarded-For lines in {log_file}, found none"

    def test_mixed_log_format_exists(self):
        """Verify both old and new format lines exist in recent logs."""
        log_file = "/var/log/httpd/access_20250125.log"

        # Count X-Forwarded-For lines
        result_xff = subprocess.run(
            ['grep', '-c', 'X-Forwarded-For:', log_file],
            capture_output=True, text=True
        )
        xff_count = int(result_xff.stdout.strip()) if result_xff.returncode == 0 else 0

        # Count total lines
        result_total = subprocess.run(['wc', '-l', log_file], capture_output=True, text=True)
        total_count = int(result_total.stdout.split()[0])

        # Non-XFF lines (old format)
        old_format_count = total_count - xff_count

        # About 2/3 should be new format, 1/3 old format
        assert xff_count > total_count * 0.5, \
            f"Expected ~2/3 of lines to have X-Forwarded-For, got {xff_count}/{total_count}"
        assert old_format_count > total_count * 0.2, \
            f"Expected ~1/3 of lines to be old format, got {old_format_count}/{total_count}"

    def test_older_logs_do_not_have_x_forwarded_for(self):
        """Verify logs before 20250122 don't have X-Forwarded-For."""
        log_file = "/var/log/httpd/access_20250121.log"
        result = subprocess.run(
            ['grep', '-c', 'X-Forwarded-For:', log_file],
            capture_output=True, text=True
        )
        xff_count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert xff_count == 0, \
            f"Expected no X-Forwarded-For lines in {log_file} (pre-load-balancer), found {xff_count}"


class TestCurrentScriptBehavior:
    """Tests verifying the current buggy behavior of the script."""

    def test_current_script_produces_x_forwarded_for_in_output(self):
        """Verify running the current script shows X-Forwarded-For as a top 'IP'."""
        # Run the script against the 20250125 log directly using the same logic
        result = subprocess.run(
            ['bash', '-c', 
             'cat /var/log/httpd/access_20250125.log | cut -d\' \' -f1 | sort | uniq -c | sort -rn | head -10'],
            capture_output=True, text=True
        )
        output = result.stdout
        assert "X-Forwarded-For:" in output, \
            "Current buggy script should produce 'X-Forwarded-For:' as a top entry, but it doesn't appear in output"

    def test_current_script_undercounts_real_ips(self):
        """Verify the current script significantly undercounts the expected top IP."""
        # The expected top IP is 192.168.44.12 with count 847
        # With the bug, it should show much less
        result = subprocess.run(
            ['bash', '-c',
             'cat /var/log/httpd/access_20250125.log | cut -d\' \' -f1 | sort | uniq -c | sort -rn'],
            capture_output=True, text=True
        )
        output_lines = result.stdout.strip().split('\n')

        # Find the count for 192.168.44.12
        ip_count = 0
        for line in output_lines:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[1] == "192.168.44.12":
                ip_count = int(parts[0])
                break

        # With the bug, we should see significantly less than 847
        # (only counting the ~1/3 old-format lines)
        assert ip_count < 500, \
            f"Expected current buggy script to undercount 192.168.44.12 (should be <500), got {ip_count}"


class TestRequiredTools:
    """Tests for availability of required tools."""

    def test_python3_available(self):
        """Verify python3 is available."""
        result = subprocess.run(['which', 'python3'], capture_output=True, text=True)
        assert result.returncode == 0, "python3 is not available"

    def test_awk_available(self):
        """Verify awk is available."""
        result = subprocess.run(['which', 'awk'], capture_output=True, text=True)
        assert result.returncode == 0, "awk is not available"

    def test_sed_available(self):
        """Verify sed is available."""
        result = subprocess.run(['which', 'sed'], capture_output=True, text=True)
        assert result.returncode == 0, "sed is not available"

    def test_grep_available(self):
        """Verify grep is available."""
        result = subprocess.run(['which', 'grep'], capture_output=True, text=True)
        assert result.returncode == 0, "grep is not available"

    def test_perl_available(self):
        """Verify perl is available."""
        result = subprocess.run(['which', 'perl'], capture_output=True, text=True)
        assert result.returncode == 0, "perl is not available"
