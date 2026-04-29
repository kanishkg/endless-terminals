# test_initial_state.py
"""
Tests to validate the initial state of the system before the student fixes the DST bug
in the monitoring script.
"""

import os
import subprocess
import socket
import pytest


class TestMonitoringDirectoryAndFiles:
    """Test that the monitoring directory and required files exist."""

    def test_monitor_directory_exists(self):
        """The /home/user/monitor directory must exist."""
        monitor_dir = "/home/user/monitor"
        assert os.path.isdir(monitor_dir), (
            f"Directory {monitor_dir} does not exist. "
            "The monitoring directory should be present."
        )

    def test_check_uptime_script_exists(self):
        """The check_uptime.py script must exist."""
        script_path = "/home/user/monitor/check_uptime.py"
        assert os.path.isfile(script_path), (
            f"File {script_path} does not exist. "
            "The monitoring script should be present."
        )

    def test_check_uptime_script_readable(self):
        """The check_uptime.py script must be readable."""
        script_path = "/home/user/monitor/check_uptime.py"
        assert os.access(script_path, os.R_OK), (
            f"File {script_path} is not readable. "
            "The monitoring script should be readable."
        )

    def test_uptime_log_exists(self):
        """The uptime.log file must exist with historical data."""
        log_path = "/home/user/monitor/uptime.log"
        assert os.path.isfile(log_path), (
            f"File {log_path} does not exist. "
            "The uptime log with historical data should be present."
        )

    def test_monitor_directory_writable(self):
        """The /home/user/monitor directory must be writable."""
        monitor_dir = "/home/user/monitor"
        assert os.access(monitor_dir, os.W_OK), (
            f"Directory {monitor_dir} is not writable. "
            "The monitoring directory should be writable."
        )


class TestSystemTimezoneConfiguration:
    """Test that system timezone is configured as America/New_York."""

    def test_etc_timezone_is_america_new_york(self):
        """The /etc/timezone file must contain America/New_York."""
        timezone_file = "/etc/timezone"
        assert os.path.isfile(timezone_file), (
            f"File {timezone_file} does not exist."
        )
        with open(timezone_file, 'r') as f:
            tz_content = f.read().strip()
        assert tz_content == "America/New_York", (
            f"/etc/timezone contains '{tz_content}' but should contain 'America/New_York'. "
            "The system timezone configuration should be America/New_York."
        )

    def test_etc_localtime_is_symlink(self):
        """The /etc/localtime should be a symlink to the correct zoneinfo."""
        localtime_path = "/etc/localtime"
        assert os.path.exists(localtime_path), (
            f"{localtime_path} does not exist."
        )
        # Check if it's a symlink pointing to America/New_York
        if os.path.islink(localtime_path):
            target = os.readlink(localtime_path)
            assert "America/New_York" in target or "US/Eastern" in target, (
                f"/etc/localtime points to '{target}' but should point to America/New_York zoneinfo."
            )
        else:
            # If not a symlink, check content matches (some systems copy instead of symlink)
            # This is acceptable as long as timezone works correctly
            pass

    def test_tz_env_not_set(self):
        """The TZ environment variable should NOT be set (use system TZ)."""
        tz_env = os.environ.get('TZ')
        # TZ being unset or empty is the expected state
        assert tz_env is None or tz_env == "", (
            f"TZ environment variable is set to '{tz_env}'. "
            "It should not be set so the system timezone is used."
        )


class TestMockServicesRunning:
    """Test that the three mock services are running on ports 8001, 8002, 8003."""

    @pytest.mark.parametrize("port", [8001, 8002, 8003])
    def test_service_port_listening(self, port):
        """Mock service must be listening on the specified port."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex(('localhost', port))
            assert result == 0, (
                f"No service listening on localhost:{port}. "
                f"The mock service on port {port} should be running."
            )
        finally:
            sock.close()

    @pytest.mark.parametrize("port", [8001, 8002, 8003])
    def test_service_responds_http(self, port):
        """Mock service should respond to HTTP requests."""
        import http.client
        try:
            conn = http.client.HTTPConnection('localhost', port, timeout=5)
            conn.request('GET', '/')
            response = conn.getresponse()
            assert response.status == 200, (
                f"Service on port {port} returned status {response.status}, expected 200. "
                f"The mock service should return 200 OK."
            )
            conn.close()
        except Exception as e:
            pytest.fail(
                f"Failed to connect to mock service on port {port}: {e}. "
                f"The mock service should be running and responding to HTTP requests."
            )


class TestPythonDependencies:
    """Test that required Python packages are installed."""

    def test_pytz_installed(self):
        """pytz package must be installed."""
        result = subprocess.run(
            ['python3', '-c', 'import pytz'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"pytz is not installed. Error: {result.stderr}. "
            "The pytz package should be available for timezone handling."
        )

    def test_dateutil_installed(self):
        """python-dateutil package must be installed."""
        result = subprocess.run(
            ['python3', '-c', 'import dateutil'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"python-dateutil is not installed. Error: {result.stderr}. "
            "The dateutil package should be available for timezone handling."
        )

    def test_python_version(self):
        """Python version must be 3.10 or higher."""
        result = subprocess.run(
            ['python3', '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Failed to get Python version."
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        assert (major, minor) >= (3, 10), (
            f"Python version is {version} but should be 3.10 or higher."
        )


class TestScriptContainsBug:
    """Test that the script contains the known bug patterns (naive datetime handling)."""

    def test_script_uses_naive_datetime_now(self):
        """The script should use datetime.now() without timezone (the bug)."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for naive datetime.now() usage (the bug)
        # The script should have datetime.now() without timezone argument
        has_datetime_now = 'datetime.now()' in content or 'datetime.now(' in content
        assert has_datetime_now, (
            "The script should contain datetime.now() calls (the bug to be fixed)."
        )

    def test_script_uses_timedelta_hours(self):
        """The script should use timedelta(hours=1) for the 'last hour' calculation."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'timedelta' in content, (
            "The script should use timedelta for time calculations."
        )

    def test_script_has_strptime_without_tz(self):
        """The script should parse timestamps with strptime (naive, the bug)."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'strptime' in content, (
            "The script should use strptime to parse log timestamps."
        )

    def test_script_monitors_three_services(self):
        """The script should monitor services on ports 8001, 8002, 8003."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        assert '8001' in content, "Script should monitor service on port 8001."
        assert '8002' in content, "Script should monitor service on port 8002."
        assert '8003' in content, "Script should monitor service on port 8003."

    def test_script_has_15_minute_threshold(self):
        """The script should have a 15-minute alert threshold."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for 15 minute threshold (could be 15, 900 seconds, etc.)
        has_15_min = '15' in content or '900' in content
        assert has_15_min, (
            "The script should have a 15-minute (or 900 second) alert threshold."
        )


class TestUptimeLogContent:
    """Test that uptime.log contains appropriate historical data."""

    def test_uptime_log_not_empty(self):
        """The uptime.log file should contain historical data."""
        log_path = "/home/user/monitor/uptime.log"
        with open(log_path, 'r') as f:
            content = f.read()

        assert len(content.strip()) > 0, (
            "uptime.log is empty but should contain historical data including "
            "entries around DST transitions."
        )

    def test_uptime_log_has_timestamp_format(self):
        """The uptime.log should have entries with timestamp format."""
        log_path = "/home/user/monitor/uptime.log"
        with open(log_path, 'r') as f:
            first_line = f.readline().strip()

        # Should have some date-like content
        import re
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        assert re.search(date_pattern, first_line), (
            f"First line of uptime.log doesn't appear to have a date: '{first_line}'. "
            "Log entries should have timestamps."
        )
