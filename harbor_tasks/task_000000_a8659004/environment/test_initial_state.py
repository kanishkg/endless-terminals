# test_initial_state.py
"""
Tests to validate the initial state of the system before the student performs the task.
This verifies the broken log aggregation setup exists as described.
"""

import os
import stat
import subprocess
import pytest


class TestScriptExists:
    """Verify the aggregate_logs.sh script exists and has correct properties."""

    def test_script_file_exists(self):
        """The script file must exist at the specified path."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        assert os.path.exists(script_path), f"Script not found at {script_path}"

    def test_script_is_file(self):
        """The script must be a regular file."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        assert os.path.isfile(script_path), f"{script_path} is not a regular file"

    def test_script_is_executable(self):
        """The script must be executable."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        mode = os.stat(script_path).st_mode
        assert mode & stat.S_IXUSR, f"{script_path} is not executable by owner"

    def test_script_is_writable(self):
        """The script must be writable by the user."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        assert os.access(script_path, os.W_OK), f"{script_path} is not writable"

    def test_script_has_bash_shebang(self):
        """The script should start with a bash shebang."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash", f"Script shebang is '{first_line}', expected '#!/bin/bash'"

    def test_script_contains_expected_variables(self):
        """The script should contain the expected variable definitions."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        with open(script_path, 'r') as f:
            content = f.read()
        assert 'LOG_DIR="/var/log/nginx"' in content, "Script missing LOG_DIR variable"
        assert 'OUTPUT="/var/log/reports/top_paths.txt"' in content, "Script missing OUTPUT variable"

    def test_script_uses_wrong_filename_pattern(self):
        """The script should be using the wrong date-based filename pattern (the bug)."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        with open(script_path, 'r') as f:
            content = f.read()
        # The script expects access.YYYYMMDD.log format
        assert 'access.$YESTERDAY.log' in content or 'access.${YESTERDAY}.log' in content, \
            "Script should be looking for date-formatted log files (the bug)"


class TestNginxLogs:
    """Verify the nginx log directory and files exist with correct format."""

    def test_nginx_log_dir_exists(self):
        """The nginx log directory must exist."""
        log_dir = "/var/log/nginx"
        assert os.path.exists(log_dir), f"Log directory not found at {log_dir}"

    def test_nginx_log_dir_is_directory(self):
        """The nginx log path must be a directory."""
        log_dir = "/var/log/nginx"
        assert os.path.isdir(log_dir), f"{log_dir} is not a directory"

    def test_nginx_log_dir_is_readable(self):
        """The nginx log directory must be readable."""
        log_dir = "/var/log/nginx"
        assert os.access(log_dir, os.R_OK), f"{log_dir} is not readable"

    def test_access_log_exists(self):
        """Today's access.log must exist."""
        log_file = "/var/log/nginx/access.log"
        assert os.path.exists(log_file), f"Access log not found at {log_file}"

    def test_access_log_1_exists(self):
        """Yesterday's rotated log (access.log.1) must exist."""
        log_file = "/var/log/nginx/access.log.1"
        assert os.path.exists(log_file), f"Yesterday's log not found at {log_file}"

    def test_access_log_1_has_content(self):
        """Yesterday's log must have content (847 lines expected)."""
        log_file = "/var/log/nginx/access.log.1"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        assert len(lines) > 0, f"{log_file} is empty"
        assert len(lines) == 847, f"{log_file} has {len(lines)} lines, expected 847"

    def test_access_log_1_has_valid_format(self):
        """Yesterday's log entries should be in combined log format."""
        log_file = "/var/log/nginx/access.log.1"
        with open(log_file, 'r') as f:
            first_line = f.readline().strip()
        # Check for combined log format pattern
        parts = first_line.split()
        assert len(parts) >= 7, f"Log line doesn't have enough fields: {first_line}"
        # Field 7 (index 6) should be a path starting with /
        assert parts[6].startswith('/') or parts[6] == '-', \
            f"Field 7 should be a path, got: {parts[6]}"

    def test_date_formatted_logs_do_not_exist(self):
        """Logs with YYYYMMDD format should NOT exist (this is why the script fails)."""
        import datetime
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
        wrong_format_log = f"/var/log/nginx/access.{yesterday}.log"
        assert not os.path.exists(wrong_format_log), \
            f"Date-formatted log {wrong_format_log} should NOT exist (script bug depends on this)"


class TestReportsDirectory:
    """Verify the reports directory and output file state."""

    def test_reports_dir_exists(self):
        """The reports directory must exist."""
        reports_dir = "/var/log/reports"
        assert os.path.exists(reports_dir), f"Reports directory not found at {reports_dir}"

    def test_reports_dir_is_directory(self):
        """The reports path must be a directory."""
        reports_dir = "/var/log/reports"
        assert os.path.isdir(reports_dir), f"{reports_dir} is not a directory"

    def test_reports_dir_is_writable(self):
        """The reports directory must be writable."""
        reports_dir = "/var/log/reports"
        assert os.access(reports_dir, os.W_OK), f"{reports_dir} is not writable"

    def test_top_paths_file_exists(self):
        """The top_paths.txt file must exist."""
        output_file = "/var/log/reports/top_paths.txt"
        assert os.path.exists(output_file), f"Output file not found at {output_file}"

    def test_top_paths_file_is_empty(self):
        """The top_paths.txt file should be empty (the problem we're fixing)."""
        output_file = "/var/log/reports/top_paths.txt"
        size = os.path.getsize(output_file)
        assert size == 0, f"{output_file} has {size} bytes, expected 0 (empty)"


class TestCronJob:
    """Verify the cron job configuration exists."""

    def test_cron_file_exists(self):
        """The cron job file must exist."""
        cron_file = "/etc/cron.d/logstats"
        assert os.path.exists(cron_file), f"Cron file not found at {cron_file}"

    def test_cron_file_is_readable(self):
        """The cron file must be readable."""
        cron_file = "/etc/cron.d/logstats"
        assert os.access(cron_file, os.R_OK), f"{cron_file} is not readable"

    def test_cron_file_references_script(self):
        """The cron file should reference the aggregate_logs.sh script."""
        cron_file = "/etc/cron.d/logstats"
        with open(cron_file, 'r') as f:
            content = f.read()
        assert '/home/user/scripts/aggregate_logs.sh' in content, \
            "Cron file doesn't reference the expected script"


class TestRequiredTools:
    """Verify required tools are installed."""

    def test_bash_installed(self):
        """bash must be installed."""
        result = subprocess.run(['which', 'bash'], capture_output=True)
        assert result.returncode == 0, "bash is not installed"

    def test_sort_installed(self):
        """sort must be installed."""
        result = subprocess.run(['which', 'sort'], capture_output=True)
        assert result.returncode == 0, "sort is not installed"

    def test_uniq_installed(self):
        """uniq must be installed."""
        result = subprocess.run(['which', 'uniq'], capture_output=True)
        assert result.returncode == 0, "uniq is not installed"

    def test_head_installed(self):
        """head must be installed."""
        result = subprocess.run(['which', 'head'], capture_output=True)
        assert result.returncode == 0, "head is not installed"

    def test_cat_installed(self):
        """cat must be installed."""
        result = subprocess.run(['which', 'cat'], capture_output=True)
        assert result.returncode == 0, "cat is not installed"

    def test_date_installed(self):
        """date must be installed."""
        result = subprocess.run(['which', 'date'], capture_output=True)
        assert result.returncode == 0, "date is not installed"

    def test_awk_installed(self):
        """awk must be installed."""
        result = subprocess.run(['which', 'awk'], capture_output=True)
        assert result.returncode == 0, "awk is not installed"


class TestScriptCurrentlyFails:
    """Verify that the script currently fails (exits silently with no output)."""

    def test_script_exits_silently(self):
        """Running the script should exit without error but produce no useful output."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        # Run the script
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True
        )
        # The script exits silently (no error message to stderr typically)
        # But the output file remains empty
        output_file = "/var/log/reports/top_paths.txt"
        size = os.path.getsize(output_file)
        assert size == 0, f"After running script, {output_file} should still be empty (bug not fixed yet)"
