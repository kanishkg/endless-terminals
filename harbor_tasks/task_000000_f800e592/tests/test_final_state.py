# test_final_state.py
"""
Tests to validate the final state after the student fixes the timezone bug
in /home/user/scheduler/gen_report.py

The fixed script should:
1. Generate report filenames with correct Asia/Tokyo local time (UTC+9)
2. Still read timezone from /etc/timezone (not hardcoded)
3. Use stdlib zoneinfo (not pytz or subprocess)
4. Work correctly when /etc/timezone is changed to a different timezone
"""

import os
import subprocess
import re
import glob
import shutil
from datetime import datetime, timezone, timedelta
import pytest


class TestSystemStatePreserved:
    """Verify system timezone configuration is still intact"""

    def test_etc_timezone_still_asia_tokyo(self):
        """Check that /etc/timezone still contains Asia/Tokyo"""
        with open('/etc/timezone', 'r') as f:
            content = f.read()
        assert content.strip() == 'Asia/Tokyo', \
            f"/etc/timezone should still contain 'Asia/Tokyo', but contains: {content.strip()!r}"

    def test_etc_localtime_still_points_to_tokyo(self):
        """Check that /etc/localtime still points to Asia/Tokyo"""
        assert os.path.islink('/etc/localtime'), \
            "/etc/localtime should still be a symlink"
        target = os.readlink('/etc/localtime')
        assert 'Asia/Tokyo' in target, \
            f"/etc/localtime should still point to Asia/Tokyo, but points to: {target}"


class TestScriptStructure:
    """Verify the script meets structural requirements"""

    def test_script_exists_at_correct_path(self):
        """Check that script is still at /home/user/scheduler/gen_report.py"""
        assert os.path.exists('/home/user/scheduler/gen_report.py'), \
            "Script must remain at /home/user/scheduler/gen_report.py"

    def test_script_is_single_file(self):
        """Check that the solution is a single Python file"""
        assert os.path.isfile('/home/user/scheduler/gen_report.py'), \
            "gen_report.py must be a single file"

    def test_script_is_valid_python(self):
        """Check that the script has valid Python syntax"""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"Script has Python syntax errors: {result.stderr}"

    def test_script_still_reads_etc_timezone(self):
        """Check that script still reads from /etc/timezone (not hardcoded)"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        assert '/etc/timezone' in content, \
            "Script must still read timezone from /etc/timezone (not hardcoded)"

    def test_script_does_not_use_subprocess(self):
        """Check that script doesn't use subprocess to call date command"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        assert 'subprocess' not in content, \
            "Script must not use subprocess to call external commands like 'date'"

    def test_script_uses_zoneinfo_not_pytz(self):
        """Check that script uses stdlib zoneinfo, not pytz"""
        with open('/home/user/scheduler/gen_report.py', 'r') as f:
            content = f.read()
        # Should use zoneinfo
        assert 'zoneinfo' in content.lower() or 'ZoneInfo' in content, \
            "Script should use stdlib zoneinfo module for timezone handling"
        # Should not import pytz
        assert 'import pytz' not in content and 'from pytz' not in content, \
            "Script must not use pytz - must use stdlib zoneinfo"

    def test_pytz_still_not_installed(self):
        """Verify pytz was not installed as part of the fix"""
        result = subprocess.run(
            ['python3', '-c', 'import pytz'],
            capture_output=True, text=True
        )
        assert result.returncode != 0, \
            "pytz should NOT be installed - solution must use stdlib zoneinfo"


class TestScriptExecution:
    """Test that the script runs and produces correct output"""

    def test_script_runs_without_error(self):
        """Check that the script executes successfully"""
        result = subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            f"Script should run without errors. stderr: {result.stderr}"

    def test_script_creates_report_file(self):
        """Check that running the script creates a report file"""
        # Clean up any existing reports first
        for f in glob.glob('/home/user/reports/report_*.txt'):
            os.remove(f)

        result = subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        reports = glob.glob('/home/user/reports/report_*.txt')
        assert len(reports) >= 1, \
            "Script should create a report file in /home/user/reports/"

    def test_report_filename_format(self):
        """Check that report filename follows expected format"""
        # Clean up and run fresh
        for f in glob.glob('/home/user/reports/report_*.txt'):
            os.remove(f)

        subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )

        reports = glob.glob('/home/user/reports/report_*.txt')
        assert len(reports) >= 1, "No report file created"

        filename = os.path.basename(reports[0])
        # Should match pattern: report_YYYY-MM-DD_HH-MM-SS.txt
        pattern = r'^report_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.txt$'
        assert re.match(pattern, filename), \
            f"Report filename should match pattern 'report_YYYY-MM-DD_HH-MM-SS.txt', got: {filename}"


class TestTimezoneCorrectness:
    """Test that the script correctly uses Asia/Tokyo timezone"""

    def test_filename_reflects_jst_time(self):
        """Check that the filename timestamp is in JST (UTC+9)"""
        # Clean up
        for f in glob.glob('/home/user/reports/report_*.txt'):
            os.remove(f)

        # Get current UTC time
        utc_now = datetime.now(timezone.utc)
        # Calculate expected JST time (UTC+9)
        jst_offset = timedelta(hours=9)
        expected_jst = utc_now + jst_offset

        # Run the script
        result = subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        reports = glob.glob('/home/user/reports/report_*.txt')
        assert len(reports) >= 1, "No report file created"

        filename = os.path.basename(reports[0])
        # Extract timestamp from filename
        match = re.search(r'report_(\d{4})-(\d{2})-(\d{2})_(\d{2})-(\d{2})-(\d{2})\.txt', filename)
        assert match, f"Could not parse timestamp from filename: {filename}"

        file_year, file_month, file_day, file_hour, file_min, file_sec = map(int, match.groups())

        # Allow 2 minutes tolerance for test execution time
        # The hour should match JST hour
        expected_hour = expected_jst.hour

        # Handle day boundary cases - if we're within 2 minutes of hour change
        hour_diff = abs(file_hour - expected_hour)
        # Account for day wraparound (23 vs 0)
        if hour_diff > 12:
            hour_diff = 24 - hour_diff

        assert hour_diff <= 1, \
            f"Filename hour ({file_hour:02d}) should be close to JST hour ({expected_hour:02d}). " \
            f"UTC hour is {utc_now.hour:02d}. Filename: {filename}"

    def test_report_content_shows_jst_time(self):
        """Check that the report's Generated timestamp is in JST"""
        # Clean up
        for f in glob.glob('/home/user/reports/report_*.txt'):
            os.remove(f)

        # Get current UTC time
        utc_now = datetime.now(timezone.utc)
        expected_jst = utc_now + timedelta(hours=9)

        # Run the script
        subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )

        reports = glob.glob('/home/user/reports/report_*.txt')
        assert len(reports) >= 1, "No report file created"

        with open(reports[0], 'r') as f:
            content = f.read()

        # Look for Generated line with timestamp
        # Could be ISO format or similar
        generated_match = re.search(r'Generated:\s*(.+)', content)
        assert generated_match, \
            f"Report should contain 'Generated:' line. Content:\n{content}"

        generated_str = generated_match.group(1).strip()

        # Extract hour from the generated timestamp
        # Try to find hour in various formats
        hour_match = re.search(r'(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})', generated_str)
        if hour_match:
            gen_hour = int(hour_match.group(4))
            expected_hour = expected_jst.hour

            hour_diff = abs(gen_hour - expected_hour)
            if hour_diff > 12:
                hour_diff = 24 - hour_diff

            assert hour_diff <= 1, \
                f"Generated timestamp hour ({gen_hour:02d}) should be close to JST hour ({expected_hour:02d}). " \
                f"Generated line: {generated_str}"


class TestTimezoneFlexibility:
    """Test that the script respects /etc/timezone changes (not hardcoded)"""

    def test_script_adapts_to_different_timezone(self):
        """
        Verify script uses timezone from /etc/timezone, not hardcoded.
        Temporarily change /etc/timezone to America/New_York and verify output changes.
        """
        # Save original timezone
        with open('/etc/timezone', 'r') as f:
            original_tz = f.read()

        try:
            # Clean up reports
            for f in glob.glob('/home/user/reports/report_*.txt'):
                os.remove(f)

            # Change timezone to America/New_York (UTC-5 or UTC-4 depending on DST)
            with open('/etc/timezone', 'w') as f:
                f.write('America/New_York\n')

            # Get current UTC time
            utc_now = datetime.now(timezone.utc)

            # Run the script
            result = subprocess.run(
                ['python3', '/home/user/scheduler/gen_report.py'],
                capture_output=True, text=True
            )
            assert result.returncode == 0, \
                f"Script should work with America/New_York timezone: {result.stderr}"

            reports = glob.glob('/home/user/reports/report_*.txt')
            assert len(reports) >= 1, "No report file created with New York timezone"

            filename = os.path.basename(reports[0])
            match = re.search(r'report_\d{4}-\d{2}-\d{2}_(\d{2})-\d{2}-\d{2}\.txt', filename)
            assert match, f"Could not parse hour from filename: {filename}"

            ny_file_hour = int(match.group(1))

            # Clean up for second test
            for f in glob.glob('/home/user/reports/report_*.txt'):
                os.remove(f)

            # Restore Tokyo timezone
            with open('/etc/timezone', 'w') as f:
                f.write('Asia/Tokyo\n')

            # Run again
            result = subprocess.run(
                ['python3', '/home/user/scheduler/gen_report.py'],
                capture_output=True, text=True
            )

            reports = glob.glob('/home/user/reports/report_*.txt')
            assert len(reports) >= 1, "No report file created with Tokyo timezone"

            filename = os.path.basename(reports[0])
            match = re.search(r'report_\d{4}-\d{2}-\d{2}_(\d{2})-\d{2}-\d{2}\.txt', filename)
            tokyo_file_hour = int(match.group(1))

            # Tokyo is ~13-14 hours ahead of New York
            # The hours should be different (unless we happen to hit exact same hour by coincidence)
            # Calculate expected difference
            # Tokyo = UTC+9, New York = UTC-5 (EST) or UTC-4 (EDT)
            # Difference should be 13-14 hours
            hour_diff = (tokyo_file_hour - ny_file_hour) % 24

            # The difference should be approximately 13-14 hours
            # (accounting for DST variations)
            assert hour_diff >= 12 or hour_diff <= 2, \
                f"Tokyo hour ({tokyo_file_hour}) and NY hour ({ny_file_hour}) should differ by ~13-14 hours, " \
                f"but diff is {hour_diff}. Script may be hardcoding timezone instead of reading /etc/timezone"

        finally:
            # Always restore original timezone
            with open('/etc/timezone', 'w') as f:
                f.write(original_tz)


class TestReportContent:
    """Test the content of generated reports"""

    def test_report_contains_expected_sections(self):
        """Check that report has expected content structure"""
        # Clean up
        for f in glob.glob('/home/user/reports/report_*.txt'):
            os.remove(f)

        subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )

        reports = glob.glob('/home/user/reports/report_*.txt')
        assert len(reports) >= 1, "No report file created"

        with open(reports[0], 'r') as f:
            content = f.read()

        # Should contain basic report elements
        assert 'Report' in content, "Report should contain 'Report' header"
        assert 'Generated' in content, "Report should contain 'Generated' timestamp"

    def test_report_shows_timezone_info(self):
        """Check that report includes timezone information"""
        # Clean up
        for f in glob.glob('/home/user/reports/report_*.txt'):
            os.remove(f)

        subprocess.run(
            ['python3', '/home/user/scheduler/gen_report.py'],
            capture_output=True, text=True
        )

        reports = glob.glob('/home/user/reports/report_*.txt')
        assert len(reports) >= 1, "No report file created"

        with open(reports[0], 'r') as f:
            content = f.read()

        # Should mention timezone somewhere
        assert 'Timezone' in content or 'Asia/Tokyo' in content or 'JST' in content or '+09' in content, \
            f"Report should include timezone information. Content:\n{content}"
