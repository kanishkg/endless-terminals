# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has fixed the capacity report script.
"""

import os
import json
import pytest
import subprocess
import hashlib


class TestScriptExecution:
    """Verify the script runs successfully."""

    def test_script_runs_without_error(self):
        """The capacity_report.py script must execute with exit code 0."""
        result = subprocess.run(
            ["python3", "/home/user/tools/capacity_report.py"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Script exited with code {result.returncode}. Stderr: {result.stderr}"


class TestOutputFileExists:
    """Verify the output file is created properly."""

    def test_windows_json_exists(self):
        """The windows.json output file must exist after script execution."""
        # Run the script first to ensure output is generated
        subprocess.run(
            ["python3", "/home/user/tools/capacity_report.py"],
            capture_output=True
        )
        output_path = "/home/user/reports/windows.json"
        assert os.path.isfile(output_path), \
            f"Output file {output_path} does not exist after script execution"

    def test_windows_json_is_valid_json(self):
        """The windows.json file must contain valid JSON."""
        subprocess.run(
            ["python3", "/home/user/tools/capacity_report.py"],
            capture_output=True
        )
        output_path = "/home/user/reports/windows.json"
        with open(output_path, 'r') as f:
            content = f.read()
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(f"windows.json is not valid JSON: {e}")


class TestOutputContent:
    """Verify the output file contains correct data."""

    @pytest.fixture(autouse=True)
    def run_script_and_load_output(self):
        """Run the script and load the output for each test."""
        subprocess.run(
            ["python3", "/home/user/tools/capacity_report.py"],
            capture_output=True
        )
        output_path = "/home/user/reports/windows.json"
        with open(output_path, 'r') as f:
            self.output_data = json.load(f)

    def test_output_has_overlapping_hours_key(self):
        """Output JSON must have 'overlapping_hours' key."""
        assert "overlapping_hours" in self.output_data, \
            "Output JSON missing 'overlapping_hours' key"

    def test_output_has_idle_hours_key(self):
        """Output JSON must have 'idle_hours' key."""
        assert "idle_hours" in self.output_data, \
            "Output JSON missing 'idle_hours' key"

    def test_overlapping_hours_is_list(self):
        """overlapping_hours must be a list."""
        assert isinstance(self.output_data["overlapping_hours"], list), \
            "overlapping_hours must be a list"

    def test_idle_hours_is_list(self):
        """idle_hours must be a list."""
        assert isinstance(self.output_data["idle_hours"], list), \
            "idle_hours must be a list"

    def test_overlapping_hours_contains_hour_2(self):
        """overlapping_hours must contain hour 2 (ETL overlaps with backup and cleanup)."""
        overlapping = self.output_data["overlapping_hours"]
        assert 2 in overlapping, \
            f"Hour 2 should be in overlapping_hours (ETL ends 02:47, backup starts 02:00, cleanup starts 02:30). Got: {overlapping}"

    def test_overlapping_hours_contains_hour_3(self):
        """overlapping_hours must contain hour 3 (backup overlaps with db_vacuum)."""
        overlapping = self.output_data["overlapping_hours"]
        assert 3 in overlapping, \
            f"Hour 3 should be in overlapping_hours (backup ends 03:12, db_vacuum starts 03:00). Got: {overlapping}"

    def test_overlapping_hours_exact_count(self):
        """overlapping_hours must contain exactly 2 elements."""
        overlapping = self.output_data["overlapping_hours"]
        assert len(overlapping) == 2, \
            f"overlapping_hours should have exactly 2 elements [2, 3], got {len(overlapping)}: {overlapping}"

    def test_overlapping_hours_exact_values(self):
        """overlapping_hours must be exactly [2, 3] (in any order)."""
        overlapping = set(self.output_data["overlapping_hours"])
        expected = {2, 3}
        assert overlapping == expected, \
            f"overlapping_hours should be [2, 3], got {sorted(overlapping)}"

    def test_idle_hours_contains_hour_0(self):
        """idle_hours must contain hour 0 (no jobs running)."""
        idle = self.output_data["idle_hours"]
        assert 0 in idle, \
            f"Hour 0 should be idle (no jobs running). Got idle_hours: {idle}"

    def test_idle_hours_contains_hour_5(self):
        """idle_hours must contain hour 5 (no jobs running)."""
        idle = self.output_data["idle_hours"]
        assert 5 in idle, \
            f"Hour 5 should be idle (no jobs running). Got idle_hours: {idle}"

    def test_idle_hours_does_not_contain_hour_1(self):
        """idle_hours must NOT contain hour 1 (ETL running)."""
        idle = self.output_data["idle_hours"]
        assert 1 not in idle, \
            f"Hour 1 should NOT be idle (ETL running 01:00-02:47). Got idle_hours: {idle}"

    def test_idle_hours_does_not_contain_hour_2(self):
        """idle_hours must NOT contain hour 2 (multiple jobs running)."""
        idle = self.output_data["idle_hours"]
        assert 2 not in idle, \
            f"Hour 2 should NOT be idle (ETL, backup, cleanup running). Got idle_hours: {idle}"

    def test_idle_hours_does_not_contain_hour_3(self):
        """idle_hours must NOT contain hour 3 (backup and db_vacuum running)."""
        idle = self.output_data["idle_hours"]
        assert 3 not in idle, \
            f"Hour 3 should NOT be idle (backup ends 03:12, db_vacuum 03:00-03:45). Got idle_hours: {idle}"

    def test_idle_hours_does_not_contain_hour_4(self):
        """idle_hours must NOT contain hour 4 (reports running)."""
        idle = self.output_data["idle_hours"]
        assert 4 not in idle, \
            f"Hour 4 should NOT be idle (reports running 04:00-04:22). Got idle_hours: {idle}"

    def test_idle_hours_does_not_contain_hour_6(self):
        """idle_hours must NOT contain hour 6 (health_check running)."""
        idle = self.output_data["idle_hours"]
        assert 6 not in idle, \
            f"Hour 6 should NOT be idle (health_check running 06:00-06:03). Got idle_hours: {idle}"

    def test_idle_hours_exact_values(self):
        """idle_hours must be exactly [0, 5, 7-23]."""
        idle = set(self.output_data["idle_hours"])
        expected = {0, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23}
        assert idle == expected, \
            f"idle_hours should be {sorted(expected)}, got {sorted(idle)}"

    def test_idle_hours_exact_count(self):
        """idle_hours must contain exactly 19 elements."""
        idle = self.output_data["idle_hours"]
        assert len(idle) == 19, \
            f"idle_hours should have 19 elements, got {len(idle)}: {sorted(idle)}"


class TestInvariants:
    """Verify that required files were not modified."""

    def test_crontab_file_unchanged(self):
        """The crontab file must not be modified."""
        crontab_path = "/var/spool/cron/crontabs/user"
        assert os.path.isfile(crontab_path), \
            "Crontab file must still exist"
        with open(crontab_path, 'r') as f:
            content = f.read()
        # Check key entries are still present
        assert "0 1 * * * /opt/batch/etl_main.sh" in content, \
            "Crontab ETL entry should not be modified"
        assert "0 2 * * * /opt/batch/backup.sh" in content, \
            "Crontab backup entry should not be modified"
        assert "30 2 * * * /opt/batch/cleanup.sh" in content, \
            "Crontab cleanup entry should not be modified"
        assert "0 3 * * * /opt/batch/db_vacuum.sh" in content, \
            "Crontab db_vacuum entry should not be modified"

    def test_log_files_exist(self):
        """All batch log files must still exist."""
        log_files = [
            "etl_main.log", "backup.log", "cleanup.log",
            "db_vacuum.log", "reports.log", "health_check.log"
        ]
        for log_file in log_files:
            log_path = f"/var/log/batch/{log_file}"
            assert os.path.isfile(log_path), \
                f"Log file {log_path} must still exist"

    def test_etl_log_timestamps_unchanged(self):
        """ETL log timestamps must not be modified."""
        log_path = "/var/log/batch/etl_main.log"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "START 2024-01-15 01:00:03" in content, \
            "ETL log START timestamp should not be modified"
        assert "END 2024-01-15 02:47:19" in content, \
            "ETL log END timestamp should not be modified"

    def test_backup_log_timestamps_unchanged(self):
        """Backup log timestamps must not be modified."""
        log_path = "/var/log/batch/backup.log"
        with open(log_path, 'r') as f:
            content = f.read()
        assert "START 2024-01-15 02:00:01" in content, \
            "Backup log START timestamp should not be modified"
        assert "END 2024-01-15 03:12:44" in content, \
            "Backup log END timestamp should not be modified"


class TestAntiShortcutGuards:
    """Verify the solution is not hardcoded."""

    def test_no_hardcoded_overlapping_hours(self):
        """The script must not have hardcoded overlapping_hours values."""
        script_path = "/home/user/tools/capacity_report.py"
        # Use grep to check for hardcoded values
        result = subprocess.run(
            ["grep", "-E", r'^\s*"overlapping_hours"\s*:\s*\[2,\s*3\]|^\s*\[2,\s*3\]', script_path],
            capture_output=True,
            text=True
        )
        # grep returns 0 if match found, 1 if no match
        assert result.returncode != 0, \
            "Script appears to have hardcoded overlapping_hours values [2, 3]"

    def test_script_reads_log_files(self):
        """The script must reference log file reading logic."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        # Check for file reading patterns
        reads_files = (
            "open(" in content or
            "read" in content.lower() or
            "glob" in content.lower() or
            "os.listdir" in content or
            "pathlib" in content.lower()
        )
        assert reads_files, \
            "Script must contain file reading logic to parse log files"

    def test_script_parses_timestamps(self):
        """The script must contain timestamp parsing logic."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        # Check for datetime/time parsing patterns
        parses_time = (
            "datetime" in content or
            "strptime" in content or
            "time" in content.lower() or
            "START" in content or
            "END" in content
        )
        assert parses_time, \
            "Script must contain timestamp parsing logic"

    def test_script_reads_crontab(self):
        """The script must read from the crontab file."""
        script_path = "/home/user/tools/capacity_report.py"
        with open(script_path, 'r') as f:
            content = f.read()
        reads_crontab = (
            "/var/spool/cron/crontabs" in content or
            "crontab" in content.lower()
        )
        assert reads_crontab, \
            "Script must read from crontab file"


class TestScriptIntegrity:
    """Additional tests to verify script behavior."""

    def test_script_produces_consistent_output(self):
        """Running the script multiple times should produce consistent output."""
        # Run twice
        subprocess.run(["python3", "/home/user/tools/capacity_report.py"], capture_output=True)
        with open("/home/user/reports/windows.json", 'r') as f:
            first_output = json.load(f)

        subprocess.run(["python3", "/home/user/tools/capacity_report.py"], capture_output=True)
        with open("/home/user/reports/windows.json", 'r') as f:
            second_output = json.load(f)

        assert set(first_output["overlapping_hours"]) == set(second_output["overlapping_hours"]), \
            "Script output should be consistent across runs"
        assert set(first_output["idle_hours"]) == set(second_output["idle_hours"]), \
            "Script output should be consistent across runs"

    def test_all_hours_accounted_for(self):
        """Every hour 0-23 should be in either overlapping, idle, or busy (but not overlapping)."""
        subprocess.run(["python3", "/home/user/tools/capacity_report.py"], capture_output=True)
        with open("/home/user/reports/windows.json", 'r') as f:
            data = json.load(f)

        overlapping = set(data["overlapping_hours"])
        idle = set(data["idle_hours"])

        # Overlapping and idle should not intersect
        assert overlapping.isdisjoint(idle), \
            f"Overlapping hours {overlapping} and idle hours {idle} should not overlap"

        # All 24 hours should be categorized
        all_hours = set(range(24))
        categorized = overlapping | idle
        busy_not_overlapping = {1, 3, 4, 6}  # Hours with single job running

        # Actually, let's check the expected categorization
        # Overlapping: 2, 3
        # Idle: 0, 5, 7-23
        # Busy but not overlapping: 1, 4, 6
        expected_busy_single = {1, 4, 6}
        actual_busy_single = all_hours - overlapping - idle

        # Hour 3 is overlapping (backup + db_vacuum), so it shouldn't be in busy_single
        assert 3 not in actual_busy_single, \
            "Hour 3 should be in overlapping_hours, not busy single job hours"
