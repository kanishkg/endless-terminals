# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the capacity report script fix task.
"""

import os
import pytest
import subprocess
import stat


class TestDirectoriesExist:
    """Verify required directories exist."""

    def test_tools_directory_exists(self):
        """The /home/user/tools directory must exist."""
        assert os.path.isdir("/home/user/tools"), \
            "Directory /home/user/tools does not exist"

    def test_reports_directory_exists(self):
        """The /home/user/reports directory must exist."""
        assert os.path.isdir("/home/user/reports"), \
            "Directory /home/user/reports does not exist"

    def test_batch_log_directory_exists(self):
        """The /var/log/batch directory must exist."""
        assert os.path.isdir("/var/log/batch"), \
            "Directory /var/log/batch does not exist"

    def test_crontabs_directory_exists(self):
        """The /var/spool/cron/crontabs directory must exist."""
        assert os.path.isdir("/var/spool/cron/crontabs"), \
            "Directory /var/spool/cron/crontabs does not exist"


class TestCapacityReportScript:
    """Verify the capacity_report.py script exists and is accessible."""

    def test_capacity_report_script_exists(self):
        """The capacity_report.py script must exist."""
        script_path = "/home/user/tools/capacity_report.py"
        assert os.path.isfile(script_path), \
            f"Script {script_path} does not exist"

    def test_capacity_report_script_is_readable(self):
        """The capacity_report.py script must be readable."""
        script_path = "/home/user/tools/capacity_report.py"
        assert os.access(script_path, os.R_OK), \
            f"Script {script_path} is not readable"

    def test_capacity_report_script_is_writable(self):
        """The capacity_report.py script must be writable (for fixing)."""
        script_path = "/home/user/tools/capacity_report.py"
        assert os.access(script_path, os.W_OK), \
            f"Script {script_path} is not writable"

    def test_capacity_report_is_python_file(self):
        """The script should be a valid Python file (at least parseable header)."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        # Basic check that it looks like Python
        assert len(content) > 0, "Script is empty"


class TestCrontabFile:
    """Verify the crontab file exists with expected entries."""

    def test_crontab_file_exists(self):
        """The user crontab file must exist."""
        crontab_path = "/var/spool/cron/crontabs/user"
        assert os.path.isfile(crontab_path), \
            f"Crontab file {crontab_path} does not exist"

    def test_crontab_file_is_readable(self):
        """The user crontab file must be readable."""
        crontab_path = "/var/spool/cron/crontabs/user"
        assert os.access(crontab_path, os.R_OK), \
            f"Crontab file {crontab_path} is not readable"

    def test_crontab_contains_etl_entry(self):
        """Crontab must contain the ETL job entry."""
        crontab_path = "/var/spool/cron/crontabs/user"
        with open(crontab_path, 'r') as f:
            content = f.read()
        assert "etl_main.sh" in content, \
            "Crontab missing etl_main.sh entry"

    def test_crontab_contains_backup_entry(self):
        """Crontab must contain the backup job entry."""
        crontab_path = "/var/spool/cron/crontabs/user"
        with open(crontab_path, 'r') as f:
            content = f.read()
        assert "backup.sh" in content, \
            "Crontab missing backup.sh entry"

    def test_crontab_contains_cleanup_entry(self):
        """Crontab must contain the cleanup job entry."""
        crontab_path = "/var/spool/cron/crontabs/user"
        with open(crontab_path, 'r') as f:
            content = f.read()
        assert "cleanup.sh" in content, \
            "Crontab missing cleanup.sh entry"

    def test_crontab_contains_db_vacuum_entry(self):
        """Crontab must contain the db_vacuum job entry."""
        crontab_path = "/var/spool/cron/crontabs/user"
        with open(crontab_path, 'r') as f:
            content = f.read()
        assert "db_vacuum.sh" in content, \
            "Crontab missing db_vacuum.sh entry"

    def test_crontab_contains_reports_entry(self):
        """Crontab must contain the reports job entry."""
        crontab_path = "/var/spool/cron/crontabs/user"
        with open(crontab_path, 'r') as f:
            content = f.read()
        assert "reports.sh" in content, \
            "Crontab missing reports.sh entry"

    def test_crontab_contains_health_check_entry(self):
        """Crontab must contain the health_check job entry."""
        crontab_path = "/var/spool/cron/crontabs/user"
        with open(crontab_path, 'r') as f:
            content = f.read()
        assert "health_check.sh" in content, \
            "Crontab missing health_check.sh entry"


class TestBatchLogFiles:
    """Verify all required batch log files exist with proper content."""

    LOG_FILES = [
        "etl_main.log",
        "backup.log",
        "cleanup.log",
        "db_vacuum.log",
        "reports.log",
        "health_check.log"
    ]

    @pytest.mark.parametrize("log_file", LOG_FILES)
    def test_log_file_exists(self, log_file):
        """Each batch log file must exist."""
        log_path = f"/var/log/batch/{log_file}"
        assert os.path.isfile(log_path), \
            f"Log file {log_path} does not exist"

    @pytest.mark.parametrize("log_file", LOG_FILES)
    def test_log_file_is_readable(self, log_file):
        """Each batch log file must be readable."""
        log_path = f"/var/log/batch/{log_file}"
        assert os.access(log_path, os.R_OK), \
            f"Log file {log_path} is not readable"

    @pytest.mark.parametrize("log_file", LOG_FILES)
    def test_log_file_has_start_timestamp(self, log_file):
        """Each log file must contain a START timestamp."""
        log_path = f"/var/log/batch/{log_file}"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "START" in content, \
            f"Log file {log_path} missing START timestamp"

    @pytest.mark.parametrize("log_file", LOG_FILES)
    def test_log_file_has_end_timestamp(self, log_file):
        """Each log file must contain an END timestamp."""
        log_path = f"/var/log/batch/{log_file}"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "END" in content, \
            f"Log file {log_path} missing END timestamp"


class TestSpecificLogTimestamps:
    """Verify specific log files have the expected timestamps for the scenario."""

    def test_etl_main_log_timestamps(self):
        """ETL main log should have correct start/end times."""
        log_path = "/var/log/batch/etl_main.log"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "01:00" in content, \
            "etl_main.log should have start time around 01:00"
        assert "02:47" in content, \
            "etl_main.log should have end time around 02:47"

    def test_backup_log_timestamps(self):
        """Backup log should have correct start/end times."""
        log_path = "/var/log/batch/backup.log"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "02:00" in content, \
            "backup.log should have start time around 02:00"
        assert "03:12" in content, \
            "backup.log should have end time around 03:12"

    def test_cleanup_log_timestamps(self):
        """Cleanup log should have correct start/end times."""
        log_path = "/var/log/batch/cleanup.log"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "02:30" in content, \
            "cleanup.log should have start time around 02:30"
        assert "02:58" in content, \
            "cleanup.log should have end time around 02:58"

    def test_db_vacuum_log_timestamps(self):
        """DB vacuum log should have correct start/end times."""
        log_path = "/var/log/batch/db_vacuum.log"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "03:00" in content, \
            "db_vacuum.log should have start time around 03:00"
        assert "03:45" in content, \
            "db_vacuum.log should have end time around 03:45"


class TestReportsDirectory:
    """Verify reports directory state."""

    def test_reports_directory_is_writable(self):
        """The /home/user/reports directory must be writable."""
        reports_dir = "/home/user/reports"
        assert os.access(reports_dir, os.W_OK), \
            f"Directory {reports_dir} is not writable"

    def test_windows_json_does_not_exist(self):
        """The windows.json output file should not exist initially."""
        output_path = "/home/user/reports/windows.json"
        assert not os.path.exists(output_path), \
            f"Output file {output_path} should not exist initially"


class TestPythonEnvironment:
    """Verify Python environment is suitable."""

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "python3 is not available"

    def test_python3_version_adequate(self):
        """Python version should be 3.10+."""
        result = subprocess.run(
            ["python3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Failed to get Python version"
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        assert major >= 3 and (major > 3 or minor >= 10), \
            f"Python version {version} is below required 3.10+"


class TestScriptHasBugs:
    """Verify the script exists and appears to have the described bugs."""

    def test_script_is_non_trivial(self):
        """The script should have substantial content (not empty stub)."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        # Should have reasonable amount of code
        assert len(content) > 100, \
            "Script appears to be too short - should have actual implementation"

    def test_script_references_crontab_path(self):
        """Script should reference the crontab path."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        assert "crontab" in content.lower() or "/var/spool/cron" in content, \
            "Script should reference crontab files"

    def test_script_references_log_path(self):
        """Script should reference the batch log path."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        assert "/var/log/batch" in content or "batch" in content.lower(), \
            "Script should reference batch log files"

    def test_script_references_output_path(self):
        """Script should reference the output path."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        assert "windows.json" in content or "/home/user/reports" in content, \
            "Script should reference output file windows.json"
