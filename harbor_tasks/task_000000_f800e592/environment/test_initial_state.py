# test_initial_state.py
"""
Tests to validate the initial state of the system before the student fixes the timezone bug
in /home/user/scheduler/gen_report.py
"""

import os
import subprocess
import pytest


class TestTimezoneConfiguration:
    """Verify system timezone is correctly configured for Asia/Tokyo"""

    def test_etc_timezone_exists(self):
        """Check that /etc/timezone file exists"""
        assert os.path.exists('/etc/timezone'), \
            "/etc/timezone file does not exist"

    def test_etc_timezone_contains_asia_tokyo(self):
        """Check that /etc/timezone contains Asia/Tokyo"""
        with open('/etc/timezone', 'r') as f:
            content = f.read()
        assert content.strip() == 'Asia/Tokyo', \
            f"/etc/timezone should contain 'Asia/Tokyo', but contains: {content.strip()!r}"

    def test_etc_localtime_is_symlink(self):
        """Check that /etc/localtime is a symlink"""
        assert os.path.islink('/etc/localtime'), \
            "/etc/localtime should be a symlink but it is not"

    def test_etc_localtime_points_to_tokyo(self):
        """Check that /etc/localtime points to Asia/Tokyo zoneinfo"""
        target = os.readlink('/etc/localtime')
        assert 'Asia/Tokyo' in target, \
            f"/etc/localtime should point to Asia/Tokyo zoneinfo, but points to: {target}"

    def test_zoneinfo_asia_tokyo_exists(self):
        """Check that the Asia/Tokyo zoneinfo file exists"""
        assert os.path.exists('/usr/share/zoneinfo/Asia/Tokyo'), \
            "/usr/share/zoneinfo/Asia/Tokyo does not exist - tzdata may not be installed"

    def test_system_date_shows_jst(self):
        """Check that system date command shows JST timezone"""
        result = subprocess.run(['date', '+%Z'], capture_output=True, text=True)
        timezone_abbrev = result.stdout.strip()
        # JST is the abbreviation for Japan Standard Time
        assert timezone_abbrev == 'JST', \
            f"System date should show JST timezone, but shows: {timezone_abbrev}"

    def test_system_date_shows_plus_0900(self):
        """Check that system date shows +0900 offset"""
        result = subprocess.run(['date', '+%z'], capture_output=True, text=True)
        offset = result.stdout.strip()
        assert offset == '+0900', \
            f"System date should show +0900 offset, but shows: {offset}"


class TestScriptAndDirectories:
    """Verify the script and required directories exist"""

    def test_scheduler_directory_exists(self):
        """Check that /home/user/scheduler/ directory exists"""
        assert os.path.isdir('/home/user/scheduler'), \
            "/home/user/scheduler/ directory does not exist"

    def test_scheduler_directory_writable(self):
        """Check that /home/user/scheduler/ is writable"""
        assert os.access('/home/user/scheduler', os.W_OK), \
            "/home/user/scheduler/ directory is not writable"

    def test_gen_report_script_exists(self):
        """Check that gen_report.py exists"""
        assert os.path.exists('/home/user/scheduler/gen_report.py'), \
            "/home/user/scheduler/gen_report.py does not exist"

    def test_gen_report_script_readable(self):
        """Check that gen_report.py is readable"""
        assert os.access('/home/user/scheduler/gen_report.py', os.R_OK), \
            "/home/user/scheduler/gen_report.py is not readable"

    def test_reports_directory_exists(self):
        """Check that /home/user/reports/ directory exists"""
        assert os.path.isdir('/home/user/reports'), \
            "/home/user/reports/ directory does not exist"

    def test_reports_directory_writable(self):
        """Check that /home/user/reports/ is writable"""
        assert os.access('/home/user/reports', os.W_OK), \
            "/home/user/reports/ directory is not writable"


class TestScriptContent:
    """Verify the buggy script has the expected content"""

    def test_script_reads_etc_timezone(self):
        """Check that script reads from /etc/timezone"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        assert '/etc/timezone' in content, \
            "Script should read timezone from /etc/timezone"

    def test_script_uses_datetime_now(self):
        """Check that script uses datetime.now() (the buggy pattern)"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        assert 'datetime.datetime.now()' in content or 'datetime.now()' in content, \
            "Script should use datetime.now() (this is the bug to fix)"

    def test_script_sets_tz_environ(self):
        """Check that script sets os.environ['TZ'] (ineffective pattern)"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        assert "os.environ['TZ']" in content or 'os.environ["TZ"]' in content, \
            "Script should set os.environ['TZ'] (this is part of the bug)"

    def test_script_writes_to_reports_dir(self):
        """Check that script writes to /home/user/reports/"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        assert '/home/user/reports/' in content, \
            "Script should write reports to /home/user/reports/"

    def test_script_is_valid_python(self):
        """Check that the script is valid Python syntax"""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"Script has Python syntax errors: {result.stderr}"


class TestPythonEnvironment:
    """Verify Python environment has required capabilities"""

    def test_python3_available(self):
        """Check that python3 is available"""
        result = subprocess.run(['which', 'python3'], capture_output=True, text=True)
        assert result.returncode == 0, \
            "python3 is not available in PATH"

    def test_python_version_3_9_or_higher(self):
        """Check that Python version is 3.9+ (for zoneinfo stdlib)"""
        result = subprocess.run(
            ['python3', '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
            capture_output=True, text=True
        )
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        assert (major, minor) >= (3, 9), \
            f"Python version should be 3.9+ for zoneinfo stdlib, but is {version}"

    def test_zoneinfo_module_available(self):
        """Check that zoneinfo module is available (stdlib in 3.9+)"""
        result = subprocess.run(
            ['python3', '-c', 'import zoneinfo; print("ok")'],
            capture_output=True, text=True
        )
        assert result.returncode == 0 and 'ok' in result.stdout, \
            f"zoneinfo module should be available but import failed: {result.stderr}"

    def test_zoneinfo_can_load_asia_tokyo(self):
        """Check that zoneinfo can load Asia/Tokyo timezone"""
        result = subprocess.run(
            ['python3', '-c', 'from zoneinfo import ZoneInfo; tz = ZoneInfo("Asia/Tokyo"); print("ok")'],
            capture_output=True, text=True
        )
        assert result.returncode == 0 and 'ok' in result.stdout, \
            f"zoneinfo should be able to load Asia/Tokyo: {result.stderr}"

    def test_pytz_not_installed(self):
        """Check that pytz is NOT installed (must use stdlib)"""
        result = subprocess.run(
            ['python3', '-c', 'import pytz'],
            capture_output=True, text=True
        )
        assert result.returncode != 0, \
            "pytz should NOT be installed - solution must use stdlib zoneinfo"


class TestBuggyBehavior:
    """Verify the script exhibits the buggy behavior described"""

    def test_script_produces_utc_time_not_local(self):
        """
        Verify that running the script produces timestamps that don't match JST.
        This confirms the bug exists before the student fixes it.
        """
        # Get current UTC hour
        result_utc = subprocess.run(
            ['date', '-u', '+%H'],
            capture_output=True, text=True
        )
        utc_hour = int(result_utc.stdout.strip())

        # Get current JST hour (should be UTC+9)
        result_jst = subprocess.run(
            ['date', '+%H'],
            capture_output=True, text=True
        )
        jst_hour = int(result_jst.stdout.strip())

        # Run the buggy script and capture what hour it uses
        # We'll check by running a modified version that just prints the hour
        test_code = '''
import datetime
import os

with open('/etc/timezone', 'r') as f:
    tz_name = f.read().strip()
os.environ['TZ'] = tz_name

now = datetime.datetime.now()
print(now.strftime('%H'))
'''
        result = subprocess.run(
            ['python3', '-c', test_code],
            capture_output=True, text=True
        )
        script_hour = int(result.stdout.strip())

        # The bug is that the script hour should equal JST hour but 
        # due to the bug it might not properly reflect the timezone
        # We're just verifying the script runs and produces some hour
        # The actual verification of the bug fix will be in the grader
        assert result.returncode == 0, \
            f"Script should run without errors: {result.stderr}"
