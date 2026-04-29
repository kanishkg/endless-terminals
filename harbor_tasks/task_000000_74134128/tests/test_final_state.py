# test_final_state.py
"""
Tests to validate the final state after the student has fixed the DST bug
in the monitoring script.
"""

import os
import subprocess
import socket
import re
import pytest
import tempfile
import shutil


class TestSystemTimezoneUnchanged:
    """Verify system timezone configuration was NOT changed (it was never the problem)."""

    def test_etc_timezone_still_america_new_york(self):
        """The /etc/timezone file must still contain America/New_York."""
        timezone_file = "/etc/timezone"
        assert os.path.isfile(timezone_file), (
            f"File {timezone_file} does not exist."
        )
        with open(timezone_file, 'r') as f:
            tz_content = f.read().strip()
        assert tz_content == "America/New_York", (
            f"/etc/timezone contains '{tz_content}' but should still contain 'America/New_York'. "
            "The fix should NOT change the system timezone - the bug was in the Python code."
        )

    def test_etc_localtime_unchanged(self):
        """The /etc/localtime should still point to America/New_York."""
        localtime_path = "/etc/localtime"
        assert os.path.exists(localtime_path), (
            f"{localtime_path} does not exist."
        )
        if os.path.islink(localtime_path):
            target = os.readlink(localtime_path)
            assert "America/New_York" in target or "US/Eastern" in target, (
                f"/etc/localtime points to '{target}' but should still point to America/New_York. "
                "The fix should NOT change system timezone configuration."
            )


class TestMockServicesStillRunning:
    """Test that the three mock services are still running."""

    @pytest.mark.parametrize("port", [8001, 8002, 8003])
    def test_service_port_listening(self, port):
        """Mock service must still be listening on the specified port."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        try:
            result = sock.connect_ex(('localhost', port))
            assert result == 0, (
                f"No service listening on localhost:{port}. "
                f"The mock service on port {port} should still be running."
            )
        finally:
            sock.close()


class TestScriptStillMonitorsCorrectly:
    """Test that the script still monitors the same services with same threshold."""

    def test_script_still_monitors_three_services(self):
        """The script should still monitor services on ports 8001, 8002, 8003."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        assert '8001' in content, "Script should still monitor service on port 8001."
        assert '8002' in content, "Script should still monitor service on port 8002."
        assert '8003' in content, "Script should still monitor service on port 8003."

    def test_script_still_has_15_minute_threshold(self):
        """The script should still have a 15-minute alert threshold (not increased to mask bug)."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for 15 minute threshold - should not be increased to 60+ to mask the bug
        # Look for patterns like 15, 900 (seconds), or timedelta with 15
        has_15_threshold = bool(re.search(r'\b15\b', content) or re.search(r'\b900\b', content))

        # Make sure threshold wasn't raised to 60+ minutes to hide the bug
        # Check for suspicious large thresholds like 60, 3600, etc. as the ONLY threshold
        suspicious_high = bool(re.search(r'threshold.*[=:]\s*(60|3600|65|70|75|80|90)', content, re.IGNORECASE))

        assert has_15_threshold or not suspicious_high, (
            "The alert threshold should still be 15 minutes. "
            "Do not increase the threshold to mask the DST bug."
        )


class TestScriptFixedDSTHandling:
    """Test that the script now handles DST correctly with timezone-aware datetimes."""

    def test_script_uses_timezone_aware_approach(self):
        """The script should use timezone-aware datetimes or UTC conversion."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for indicators of proper timezone handling
        # Could use: ZoneInfo, pytz, dateutil.tz, timezone.utc, astimezone, etc.
        tz_aware_indicators = [
            'ZoneInfo',
            'pytz',
            'dateutil.tz',
            'timezone.utc',
            'astimezone',
            'tzinfo',
            'tz=',
            'timezone(',
            '.utc',
            'UTC',
            'localize',
            'replace(tzinfo',
        ]

        has_tz_handling = any(indicator in content for indicator in tz_aware_indicators)

        assert has_tz_handling, (
            "The script should use timezone-aware datetimes (e.g., ZoneInfo, pytz, dateutil.tz, "
            "or UTC conversion) to properly handle DST transitions. "
            "No timezone-aware datetime handling detected in the script."
        )

    def test_script_not_using_naive_datetime_now_alone(self):
        """The script should not use bare datetime.now() without timezone context."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check if datetime.now() is used without any timezone argument
        # Acceptable: datetime.now(tz), datetime.now(ZoneInfo(...)), datetime.now(timezone.utc)
        # Not acceptable: datetime.now() alone for time comparisons

        # Look for datetime.now() with empty parens (naive)
        naive_now_pattern = r'datetime\.now\(\s*\)'
        naive_matches = re.findall(naive_now_pattern, content)

        # If there are naive datetime.now() calls, check if they're in a context
        # that converts them to timezone-aware (like immediately calling astimezone)
        if naive_matches:
            # Check if the fix uses a different approach (like UTC throughout)
            uses_utc_approach = 'utcnow' in content or 'timezone.utc' in content or 'UTC' in content
            uses_tz_conversion = 'astimezone' in content or 'localize' in content
            uses_zoneinfo = 'ZoneInfo' in content
            uses_pytz = 'pytz' in content

            has_proper_handling = uses_utc_approach or uses_tz_conversion or uses_zoneinfo or uses_pytz

            assert has_proper_handling, (
                f"Found {len(naive_matches)} naive datetime.now() calls without apparent "
                "timezone handling. The fix should use timezone-aware datetimes."
            )


class TestNoDSTHardcoding:
    """Test that the fix doesn't hardcode DST transition dates to skip them."""

    def test_no_hardcoded_dst_dates(self):
        """The script should not hardcode specific DST transition dates."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for hardcoded DST dates (bad fix)
        hardcoded_patterns = [
            r'03-10',  # March 10 (spring forward)
            r'03-11',
            r'03-12',
            r'11-03',  # November 3 (fall back)
            r'11-04',
            r'11-05',
            r'skip.*dst',
            r'dst.*skip',
            r'ignore.*2am',
            r'ignore.*3am',
        ]

        for pattern in hardcoded_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Allow date patterns if they're in comments or log data, but flag suspicious usage
            if matches and 'skip' in pattern.lower() or 'ignore' in pattern.lower():
                pytest.fail(
                    f"Found suspicious DST-skipping pattern '{pattern}' in script. "
                    "The fix should handle DST properly, not skip specific dates."
                )


class TestAlertsNotDisabled:
    """Test that alerts haven't been disabled entirely."""

    def test_alerts_functionality_exists(self):
        """The script should still have alert functionality."""
        script_path = "/home/user/monitor/check_uptime.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check that alert-related code still exists
        alert_indicators = ['alert', 'Alert', 'ALERT', 'alerts.log', 'warning', 'Warning']
        has_alert_code = any(indicator in content for indicator in alert_indicators)

        assert has_alert_code, (
            "The script should still have alert functionality. "
            "Do not disable alerts to fix the DST bug."
        )


class TestSpringForwardDSTNoPhantomAlert:
    """Test that spring-forward DST transition doesn't cause phantom alerts."""

    def test_spring_forward_no_phantom_alert(self):
        """
        Running the script at 2024-03-10 03:05:00 America/New_York (just after spring-forward)
        should NOT produce a phantom alert when services are up.
        """
        # Check if faketime is available
        faketime_check = subprocess.run(['which', 'faketime'], capture_output=True)
        if faketime_check.returncode != 0:
            pytest.skip("faketime not available for DST simulation test")

        # Get current alerts.log content (or note it doesn't exist)
        alerts_log = "/home/user/monitor/alerts.log"
        alerts_before = ""
        if os.path.exists(alerts_log):
            with open(alerts_log, 'r') as f:
                alerts_before = f.read()

        # Run the script with simulated time just after spring-forward
        # 2024-03-10 03:05:00 is right after 2am jumped to 3am
        result = subprocess.run(
            ['faketime', '2024-03-10 03:05:00', 'python3', '/home/user/monitor/check_uptime.py'],
            capture_output=True,
            text=True,
            env={**os.environ, 'TZ': 'America/New_York'},
            timeout=30
        )

        # Script should exit successfully
        assert result.returncode == 0, (
            f"Script failed during spring-forward test. "
            f"Exit code: {result.returncode}, stderr: {result.stderr}"
        )

        # Check that no new alerts were added
        alerts_after = ""
        if os.path.exists(alerts_log):
            with open(alerts_log, 'r') as f:
                alerts_after = f.read()

        # New alerts would be additions to the file
        new_alerts = alerts_after[len(alerts_before):] if len(alerts_after) > len(alerts_before) else ""

        # Check for phantom alert indicators (downtime when services are up)
        phantom_indicators = ['down', 'Down', 'DOWN', 'alert', 'Alert', 'ALERT', 'offline', 'unreachable']
        has_phantom_alert = any(indicator in new_alerts for indicator in phantom_indicators)

        assert not has_phantom_alert, (
            f"Phantom alert detected during spring-forward DST transition! "
            f"New alerts content: {new_alerts[:500]}... "
            "The script should not alert when services are actually up during DST transitions."
        )


class TestFallBackDSTNoIncorrectAlert:
    """Test that fall-back DST transition doesn't cause incorrect alerts."""

    def test_fall_back_no_incorrect_alert(self):
        """
        Running the script at 2024-11-03 01:30:00 America/New_York (during fall-back ambiguous hour)
        should NOT produce incorrect alerts when services are up.
        """
        # Check if faketime is available
        faketime_check = subprocess.run(['which', 'faketime'], capture_output=True)
        if faketime_check.returncode != 0:
            pytest.skip("faketime not available for DST simulation test")

        # Get current alerts.log content
        alerts_log = "/home/user/monitor/alerts.log"
        alerts_before = ""
        if os.path.exists(alerts_log):
            with open(alerts_log, 'r') as f:
                alerts_before = f.read()

        # Run the script with simulated time during fall-back ambiguous hour
        result = subprocess.run(
            ['faketime', '2024-11-03 01:30:00', 'python3', '/home/user/monitor/check_uptime.py'],
            capture_output=True,
            text=True,
            env={**os.environ, 'TZ': 'America/New_York'},
            timeout=30
        )

        # Script should exit successfully
        assert result.returncode == 0, (
            f"Script failed during fall-back test. "
            f"Exit code: {result.returncode}, stderr: {result.stderr}"
        )

        # Check that no incorrect alerts were added
        alerts_after = ""
        if os.path.exists(alerts_log):
            with open(alerts_log, 'r') as f:
                alerts_after = f.read()

        new_alerts = alerts_after[len(alerts_before):] if len(alerts_after) > len(alerts_before) else ""

        phantom_indicators = ['down', 'Down', 'DOWN', 'alert', 'Alert', 'ALERT', 'offline', 'unreachable']
        has_phantom_alert = any(indicator in new_alerts for indicator in phantom_indicators)

        assert not has_phantom_alert, (
            f"Incorrect alert detected during fall-back DST transition! "
            f"New alerts content: {new_alerts[:500]}... "
            "The script should handle the ambiguous hour correctly."
        )


class TestNormalOperationStillWorks:
    """Test that normal operation (non-DST times) still works correctly."""

    def test_script_runs_successfully_normal_time(self):
        """The script should run successfully during normal (non-DST) times."""
        result = subprocess.run(
            ['python3', '/home/user/monitor/check_uptime.py'],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, (
            f"Script failed during normal operation. "
            f"Exit code: {result.returncode}, stderr: {result.stderr}"
        )

    def test_script_still_writes_to_uptime_log(self):
        """The script should still append entries to uptime.log."""
        log_path = "/home/user/monitor/uptime.log"

        # Get size before
        size_before = os.path.getsize(log_path) if os.path.exists(log_path) else 0

        # Run the script
        result = subprocess.run(
            ['python3', '/home/user/monitor/check_uptime.py'],
            capture_output=True,
            text=True,
            timeout=30
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        # Check size after
        size_after = os.path.getsize(log_path)

        assert size_after > size_before, (
            "The script should append new entries to uptime.log. "
            f"Size before: {size_before}, size after: {size_after}"
        )


class TestLogFormatStillParseable:
    """Test that log format remains parseable (ISO-ish with optional TZ info)."""

    def test_uptime_log_has_valid_format(self):
        """The uptime.log should have entries with parseable timestamp format."""
        log_path = "/home/user/monitor/uptime.log"

        with open(log_path, 'r') as f:
            lines = f.readlines()

        # Check last few lines (most recent entries)
        recent_lines = [l.strip() for l in lines[-10:] if l.strip()]

        assert len(recent_lines) > 0, "uptime.log should have entries"

        # Check that entries have some date-like format
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # ISO date
            r'\d{4}/\d{2}/\d{2}',  # Alternative date
            r'\d{2}:\d{2}:\d{2}',  # Time component
        ]

        for line in recent_lines:
            has_date = any(re.search(pattern, line) for pattern in date_patterns)
            if not has_date:
                # Allow empty lines or header lines
                if line and not line.startswith('#'):
                    pytest.fail(
                        f"Log entry doesn't appear to have a parseable timestamp: '{line}'. "
                        "Log format should remain ISO-ish or include TZ info."
                    )
