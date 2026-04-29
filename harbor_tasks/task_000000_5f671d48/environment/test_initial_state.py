# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student performs the task.
This verifies the monitoring pipeline setup with the known bug conditions.
"""

import os
import json
import subprocess
import pytest
from pathlib import Path


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_ingest_log_directory_exists(self):
        """Verify /var/log/ingest/ directory exists."""
        assert os.path.isdir("/var/log/ingest"), \
            "Directory /var/log/ingest/ does not exist"

    def test_monitoring_directory_exists(self):
        """Verify /home/user/monitoring/ directory exists."""
        assert os.path.isdir("/home/user/monitoring"), \
            "Directory /home/user/monitoring/ does not exist"

    def test_summaries_directory_exists(self):
        """Verify /home/user/monitoring/summaries/ directory exists."""
        assert os.path.isdir("/home/user/monitoring/summaries"), \
            "Directory /home/user/monitoring/summaries/ does not exist"


class TestIngestLogFiles:
    """Test the ingest log files in /var/log/ingest/."""

    def test_ingest_log_files_exist(self):
        """Verify that ingest log files exist (should be 72 hourly files)."""
        ingest_dir = Path("/var/log/ingest")
        log_files = list(ingest_dir.glob("ingest_*.log"))
        assert len(log_files) == 72, \
            f"Expected 72 ingest log files, found {len(log_files)}"

    def test_ingest_log_file_naming_convention(self):
        """Verify log files follow ingest_YYYYMMDD_HH.log naming."""
        ingest_dir = Path("/var/log/ingest")
        log_files = list(ingest_dir.glob("ingest_*.log"))
        import re
        pattern = re.compile(r"ingest_\d{8}_\d{2}\.log")
        for log_file in log_files:
            assert pattern.match(log_file.name), \
                f"Log file {log_file.name} doesn't match expected pattern ingest_YYYYMMDD_HH.log"

    def test_ingest_log_contains_json_lines(self):
        """Verify at least one ingest log file contains valid JSON lines."""
        ingest_dir = Path("/var/log/ingest")
        log_files = list(ingest_dir.glob("ingest_*.log"))
        assert len(log_files) > 0, "No ingest log files found"

        # Check first log file
        log_file = sorted(log_files)[0]
        with open(log_file, 'r') as f:
            first_line = f.readline().strip()
            if first_line:
                data = json.loads(first_line)
                assert "ts" in data, f"Log entry missing 'ts' field in {log_file}"
                assert "status" in data, f"Log entry missing 'status' field in {log_file}"
                assert data["status"] in ("ok", "error"), \
                    f"Log entry status should be 'ok' or 'error', got {data['status']}"

    def test_high_error_rate_log_exists_20250610_14(self):
        """Verify the log file with ~12% error rate exists."""
        log_path = Path("/var/log/ingest/ingest_20250610_14.log")
        assert log_path.exists(), \
            f"Expected high error rate log file {log_path} does not exist"

    def test_high_error_rate_log_exists_20250611_09(self):
        """Verify the log file with ~8% error rate exists."""
        log_path = Path("/var/log/ingest/ingest_20250611_09.log")
        assert log_path.exists(), \
            f"Expected high error rate log file {log_path} does not exist"

    def test_ingest_directory_not_writable(self):
        """Verify /var/log/ingest/ is not writable by current user."""
        # Try to create a temp file - should fail
        test_file = Path("/var/log/ingest/.write_test")
        try:
            test_file.touch()
            test_file.unlink()  # Clean up if somehow succeeded
            pytest.fail("/var/log/ingest/ should not be writable but write succeeded")
        except PermissionError:
            pass  # Expected behavior


class TestMonitoringScripts:
    """Test the monitoring scripts exist."""

    def test_parse_logs_script_exists(self):
        """Verify parse_logs.py exists."""
        script_path = Path("/home/user/monitoring/parse_logs.py")
        assert script_path.exists(), \
            f"Parser script {script_path} does not exist"

    def test_alerter_script_exists(self):
        """Verify alerter.py exists."""
        script_path = Path("/home/user/monitoring/alerter.py")
        assert script_path.exists(), \
            f"Alerter script {script_path} does not exist"

    def test_config_yaml_exists(self):
        """Verify config.yaml exists."""
        config_path = Path("/home/user/monitoring/config.yaml")
        assert config_path.exists(), \
            f"Config file {config_path} does not exist"


class TestConfigFile:
    """Test the configuration file contents."""

    def test_config_has_threshold(self):
        """Verify config.yaml contains threshold: 0.05."""
        config_path = Path("/home/user/monitoring/config.yaml")
        content = config_path.read_text()
        assert "threshold" in content, \
            "config.yaml does not contain 'threshold' key"

    def test_config_threshold_value(self):
        """Verify threshold is set to 0.05 in config."""
        result = subprocess.run(
            ["grep", "threshold", "/home/user/monitoring/config.yaml"],
            capture_output=True, text=True
        )
        assert "0.05" in result.stdout, \
            f"config.yaml threshold should be 0.05, got: {result.stdout.strip()}"

    def test_config_has_summary_dir(self):
        """Verify config.yaml contains summary_dir setting."""
        config_path = Path("/home/user/monitoring/config.yaml")
        content = config_path.read_text()
        assert "summary_dir" in content, \
            "config.yaml does not contain 'summary_dir' key"

    def test_config_has_alert_log(self):
        """Verify config.yaml contains alert_log setting."""
        config_path = Path("/home/user/monitoring/config.yaml")
        content = config_path.read_text()
        assert "alert_log" in content, \
            "config.yaml does not contain 'alert_log' key"


class TestSummaryFiles:
    """Test the summary files in /home/user/monitoring/summaries/."""

    def test_summary_files_exist(self):
        """Verify that 72 summary files exist."""
        summaries_dir = Path("/home/user/monitoring/summaries")
        summary_files = list(summaries_dir.glob("summary_*.json"))
        assert len(summary_files) == 72, \
            f"Expected 72 summary files, found {len(summary_files)}"

    def test_summary_file_naming_convention(self):
        """Verify summary files follow summary_YYYYMMDD_HH.json naming."""
        summaries_dir = Path("/home/user/monitoring/summaries")
        summary_files = list(summaries_dir.glob("summary_*.json"))
        import re
        pattern = re.compile(r"summary_\d{8}_\d{2}\.json")
        for summary_file in summary_files:
            assert pattern.match(summary_file.name), \
                f"Summary file {summary_file.name} doesn't match expected pattern"

    def test_summary_file_contains_required_keys(self):
        """Verify summary files contain required keys."""
        summaries_dir = Path("/home/user/monitoring/summaries")
        summary_files = list(summaries_dir.glob("summary_*.json"))
        assert len(summary_files) > 0, "No summary files found"

        # Check first summary file
        summary_file = sorted(summary_files)[0]
        with open(summary_file, 'r') as f:
            data = json.load(f)
            required_keys = ["hour", "total", "errors", "error_rate"]
            for key in required_keys:
                assert key in data, \
                    f"Summary file {summary_file} missing required key '{key}'"

    def test_high_error_rate_summary_exists_20250610_14(self):
        """Verify summary for high error rate hour exists."""
        summary_path = Path("/home/user/monitoring/summaries/summary_20250610_14.json")
        assert summary_path.exists(), \
            f"Expected summary file {summary_path} does not exist"

    def test_high_error_rate_summary_has_high_rate_20250610_14(self):
        """Verify the 20250610_14 summary has error_rate > 0.05."""
        summary_path = Path("/home/user/monitoring/summaries/summary_20250610_14.json")
        with open(summary_path, 'r') as f:
            data = json.load(f)
            error_rate = float(data['error_rate'])
            assert error_rate > 0.05, \
                f"Expected error_rate > 0.05 for 20250610_14, got {error_rate}"

    def test_high_error_rate_summary_exists_20250611_09(self):
        """Verify summary for high error rate hour exists."""
        summary_path = Path("/home/user/monitoring/summaries/summary_20250611_09.json")
        assert summary_path.exists(), \
            f"Expected summary file {summary_path} does not exist"

    def test_high_error_rate_summary_has_high_rate_20250611_09(self):
        """Verify the 20250611_09 summary has error_rate > 0.05."""
        summary_path = Path("/home/user/monitoring/summaries/summary_20250611_09.json")
        with open(summary_path, 'r') as f:
            data = json.load(f)
            error_rate = float(data['error_rate'])
            assert error_rate > 0.05, \
                f"Expected error_rate > 0.05 for 20250611_09, got {error_rate}"


class TestAlertsLog:
    """Test the alerts.log file state."""

    def test_alerts_log_exists(self):
        """Verify alerts.log exists."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        assert alerts_path.exists(), \
            f"Alerts log {alerts_path} does not exist"

    def test_alerts_log_is_empty(self):
        """Verify alerts.log is empty (0 bytes) - this is the bug symptom."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        size = alerts_path.stat().st_size
        assert size == 0, \
            f"alerts.log should be empty (0 bytes), but has {size} bytes"


class TestAlerterBug:
    """Test that the alerter has the known bug (typo in config key)."""

    def test_alerter_has_treshold_typo(self):
        """Verify alerter.py contains the 'treshold' typo (missing 'h')."""
        alerter_path = Path("/home/user/monitoring/alerter.py")
        content = alerter_path.read_text()
        assert "treshold" in content, \
            "alerter.py should contain 'treshold' typo (the bug to fix)"

    def test_alerter_uses_dict_get_with_default(self):
        """Verify alerter.py uses .get() with a default value for the typo key."""
        alerter_path = Path("/home/user/monitoring/alerter.py")
        content = alerter_path.read_text()
        # Should have something like config.get('treshold', 0.5) or similar
        assert ".get(" in content and "treshold" in content, \
            "alerter.py should use .get() method with 'treshold' key"

    def test_alerter_threshold_not_hardcoded(self):
        """Verify threshold is not hardcoded as 0.05 in alerter.py."""
        result = subprocess.run(
            ["grep", "-E", r"threshold.*=.*0\.05|THRESHOLD.*=.*0\.05", 
             "/home/user/monitoring/alerter.py"],
            capture_output=True, text=True
        )
        assert result.returncode != 0, \
            "alerter.py should not have threshold hardcoded as 0.05"


class TestParserBug:
    """Test the secondary bug - error_rate stored as string."""

    def test_summary_error_rate_is_string(self):
        """Verify error_rate in summaries is stored as string (secondary bug)."""
        summary_path = Path("/home/user/monitoring/summaries/summary_20250610_14.json")
        with open(summary_path, 'r') as f:
            content = f.read()
            data = json.loads(content)
            # The error_rate should be a string like "0.12" not a float
            assert isinstance(data['error_rate'], str), \
                f"error_rate should be stored as string (bug), but is {type(data['error_rate'])}"


class TestEnvironment:
    """Test the environment requirements."""

    def test_python3_available(self):
        """Verify Python 3 is available."""
        result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
        assert result.returncode == 0, "python3 is not available"
        assert "Python 3" in result.stdout, f"Expected Python 3, got: {result.stdout}"

    def test_pyyaml_installed(self):
        """Verify PyYAML is installed."""
        result = subprocess.run(
            ["python3", "-c", "import yaml; print(yaml.__version__)"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"PyYAML is not installed: {result.stderr}"

    def test_jq_available(self):
        """Verify jq is available."""
        result = subprocess.run(["which", "jq"], capture_output=True, text=True)
        assert result.returncode == 0, "jq is not available"

    def test_monitoring_directory_writable(self):
        """Verify /home/user/monitoring/ is writable."""
        test_file = Path("/home/user/monitoring/.write_test")
        try:
            test_file.touch()
            test_file.unlink()
        except PermissionError:
            pytest.fail("/home/user/monitoring/ should be writable")


class TestAlerterRuns:
    """Test that alerter.py runs without exceptions."""

    def test_alerter_runs_without_error(self):
        """Verify alerter.py runs and exits 0 (even though it doesn't produce alerts due to bug)."""
        result = subprocess.run(
            ["python3", "/home/user/monitoring/alerter.py"],
            capture_output=True, text=True,
            cwd="/home/user/monitoring"
        )
        assert result.returncode == 0, \
            f"alerter.py failed with return code {result.returncode}: {result.stderr}"
