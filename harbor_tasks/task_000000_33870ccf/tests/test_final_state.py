# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student
has completed the disk usage analysis task and generated the incident report.
"""

import os
import re
import pytest
from pathlib import Path


REPORT_PATH = "/home/user/incident_report.txt"
APP_DATA_DIR = "/home/user/app_data"


class TestReportFileExists:
    """Test that the incident report file exists."""

    def test_incident_report_exists(self):
        """Verify the incident report file exists at the expected location."""
        assert os.path.isfile(REPORT_PATH), \
            f"Incident report file does not exist at {REPORT_PATH}. Student must create this file."

    def test_incident_report_is_not_empty(self):
        """Verify the incident report is not empty."""
        assert os.path.isfile(REPORT_PATH), f"Report file {REPORT_PATH} does not exist"
        size = os.path.getsize(REPORT_PATH)
        assert size > 0, f"Incident report at {REPORT_PATH} is empty"


class TestReportStructure:
    """Test that the report has the required structure and sections."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    def test_report_has_header(self, report_content):
        """Verify report contains the main header."""
        assert "=== DISK USAGE INCIDENT REPORT ===" in report_content, \
            "Report is missing header '=== DISK USAGE INCIDENT REPORT ==='"

    def test_report_has_generated_timestamp(self, report_content):
        """Verify report contains a Generated timestamp line."""
        # Look for pattern like "Generated: YYYY-MM-DD HH:MM:SS" or similar
        pattern = r"Generated:\s*\d{4}-\d{2}-\d{2}"
        assert re.search(pattern, report_content), \
            "Report is missing 'Generated:' timestamp with date format YYYY-MM-DD"

    def test_report_has_top_directories_section(self, report_content):
        """Verify report contains the top 5 largest directories section."""
        assert "--- TOP 5 LARGEST DIRECTORIES ---" in report_content, \
            "Report is missing section '--- TOP 5 LARGEST DIRECTORIES ---'"

    def test_report_has_large_files_section(self, report_content):
        """Verify report contains the files larger than 50MB section."""
        assert "--- FILES LARGER THAN 50MB ---" in report_content, \
            "Report is missing section '--- FILES LARGER THAN 50MB ---'"

    def test_report_has_old_log_files_section(self, report_content):
        """Verify report contains the old log files section."""
        assert "--- OLD LOG FILES (>7 days) ---" in report_content, \
            "Report is missing section '--- OLD LOG FILES (>7 days) ---'"

    def test_report_has_file_type_distribution_section(self, report_content):
        """Verify report contains the file type distribution section."""
        assert "--- FILE TYPE DISTRIBUTION ---" in report_content, \
            "Report is missing section '--- FILE TYPE DISTRIBUTION ---'"

    def test_report_has_summary_section(self, report_content):
        """Verify report contains the summary section."""
        assert "--- SUMMARY ---" in report_content, \
            "Report is missing section '--- SUMMARY ---'"

    def test_report_has_end_marker(self, report_content):
        """Verify report ends with the correct marker."""
        assert "=== END REPORT ===" in report_content, \
            "Report is missing end marker '=== END REPORT ==='"


class TestLargeFilesContent:
    """Test that the large files section contains the expected files."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    @pytest.fixture
    def large_files_section(self, report_content):
        """Extract the large files section from the report."""
        # Find content between "--- FILES LARGER THAN 50MB ---" and the next section
        pattern = r"--- FILES LARGER THAN 50MB ---\s*(.*?)(?=---|\Z)"
        match = re.search(pattern, report_content, re.DOTALL)
        if match:
            return match.group(1)
        return ""

    @pytest.mark.parametrize("filename", [
        "banner.png",
        "demo.mp4",
        "tutorial.mp4",
        "query_cache.dat",
        "db_backup_old.sql",
        "db_backup_recent.sql",
    ])
    def test_large_file_listed(self, large_files_section, filename):
        """Verify each expected large file is listed in the report."""
        assert filename in large_files_section, \
            f"Large file '{filename}' is not listed in the FILES LARGER THAN 50MB section"

    def test_large_files_count_is_six(self, report_content):
        """Verify the summary shows 6 large files found."""
        # Look for "Large files found: 6" in the summary
        pattern = r"Large files found:\s*6\b"
        assert re.search(pattern, report_content), \
            "Summary should show 'Large files found: 6' - there are exactly 6 files larger than 50MB"


class TestOldLogFilesContent:
    """Test that the old log files section contains the expected files."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    @pytest.fixture
    def old_logs_section(self, report_content):
        """Extract the old log files section from the report."""
        pattern = r"--- OLD LOG FILES \(>7 days\) ---\s*(.*?)(?=---|\Z)"
        match = re.search(pattern, report_content, re.DOTALL)
        if match:
            return match.group(1)
        return ""

    @pytest.mark.parametrize("logfile", [
        "app.log",
        "error.log",
        "debug.log",
    ])
    def test_old_log_file_listed(self, old_logs_section, logfile):
        """Verify each expected old log file is listed in the report."""
        assert logfile in old_logs_section, \
            f"Old log file '{logfile}' is not listed in the OLD LOG FILES section"

    def test_access_log_not_in_old_logs(self, old_logs_section):
        """Verify access.log is NOT listed as an old log (it's recent)."""
        # access.log should not appear in the old logs section since it's only 2 days old
        # However, it might appear if the path contains it, so we need to be careful
        # Check that access.log is not listed as an old log file
        lines = old_logs_section.strip().split('\n')
        for line in lines:
            if 'access.log' in line and '/home/user/app_data/logs/access.log' in line:
                pytest.fail("access.log should NOT be in OLD LOG FILES section (it's only 2 days old)")

    def test_old_log_files_count_is_three(self, report_content):
        """Verify the summary shows 3 old log files found."""
        pattern = r"Old log files found:\s*3\b"
        assert re.search(pattern, report_content), \
            "Summary should show 'Old log files found: 3' - there are exactly 3 log files older than 7 days"


class TestFileTypeDistribution:
    """Test that the file type distribution section contains expected extensions."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    @pytest.fixture
    def distribution_section(self, report_content):
        """Extract the file type distribution section from the report."""
        pattern = r"--- FILE TYPE DISTRIBUTION ---\s*(.*?)(?=---|\Z)"
        match = re.search(pattern, report_content, re.DOTALL)
        if match:
            return match.group(1)
        return ""

    @pytest.mark.parametrize("extension", [
        ".log",
        ".jpg",
        ".png",
        ".mp4",
        ".pdf",
        ".csv",
        ".dat",
        ".tmp",
        ".sql",
        ".gz",
        ".conf",
        ".yml",
        ".json",
    ])
    def test_extension_listed(self, distribution_section, extension):
        """Verify each expected file extension is listed in the distribution."""
        # Check for the extension (with or without the dot, case insensitive)
        ext_pattern = re.escape(extension)
        if not re.search(ext_pattern, distribution_section, re.IGNORECASE):
            # Try without the leading dot
            ext_no_dot = extension.lstrip('.')
            assert ext_no_dot.lower() in distribution_section.lower(), \
                f"File extension '{extension}' is not listed in the FILE TYPE DISTRIBUTION section"


class TestSummarySection:
    """Test that the summary section contains required information."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    def test_summary_has_total_directories(self, report_content):
        """Verify summary contains total directories analyzed."""
        pattern = r"Total directories analyzed:\s*\d+"
        assert re.search(pattern, report_content), \
            "Summary is missing 'Total directories analyzed:' with a number"

    def test_summary_has_large_files_count(self, report_content):
        """Verify summary contains large files count."""
        pattern = r"Large files found:\s*\d+"
        assert re.search(pattern, report_content), \
            "Summary is missing 'Large files found:' with a number"

    def test_summary_has_old_log_files_count(self, report_content):
        """Verify summary contains old log files count."""
        pattern = r"Old log files found:\s*\d+"
        assert re.search(pattern, report_content), \
            "Summary is missing 'Old log files found:' with a number"


class TestTopDirectoriesSection:
    """Test that the top directories section has meaningful content."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    @pytest.fixture
    def top_dirs_section(self, report_content):
        """Extract the top directories section from the report."""
        pattern = r"--- TOP 5 LARGEST DIRECTORIES ---\s*(.*?)(?=---|\Z)"
        match = re.search(pattern, report_content, re.DOTALL)
        if match:
            return match.group(1)
        return ""

    def test_top_directories_has_content(self, top_dirs_section):
        """Verify the top directories section has some content."""
        # Should have at least some directory paths
        assert len(top_dirs_section.strip()) > 0, \
            "TOP 5 LARGEST DIRECTORIES section is empty"

    def test_top_directories_contains_paths(self, top_dirs_section):
        """Verify the section contains paths from app_data."""
        # Should contain at least one path from app_data
        assert "/home/user/app_data" in top_dirs_section or "app_data" in top_dirs_section, \
            "TOP 5 LARGEST DIRECTORIES section should contain paths from /home/user/app_data"

    def test_backups_directory_likely_listed(self, top_dirs_section):
        """Verify backups directory is likely in top directories (it has ~380MB)."""
        # backups has db_backup_old.sql (200MB) + db_backup_recent.sql (180MB) = ~380MB
        assert "backup" in top_dirs_section.lower(), \
            "backups directory should be listed in TOP 5 LARGEST DIRECTORIES (it contains ~380MB)"


class TestReportCompleteness:
    """Test overall report completeness and format."""

    @pytest.fixture
    def report_content(self):
        """Read and return the report content."""
        if not os.path.isfile(REPORT_PATH):
            pytest.fail(f"Report file {REPORT_PATH} does not exist")
        with open(REPORT_PATH, 'r') as f:
            return f.read()

    def test_report_sections_in_order(self, report_content):
        """Verify report sections appear in the correct order."""
        header_pos = report_content.find("=== DISK USAGE INCIDENT REPORT ===")
        top_dirs_pos = report_content.find("--- TOP 5 LARGEST DIRECTORIES ---")
        large_files_pos = report_content.find("--- FILES LARGER THAN 50MB ---")
        old_logs_pos = report_content.find("--- OLD LOG FILES (>7 days) ---")
        distribution_pos = report_content.find("--- FILE TYPE DISTRIBUTION ---")
        summary_pos = report_content.find("--- SUMMARY ---")
        end_pos = report_content.find("=== END REPORT ===")

        assert header_pos >= 0, "Missing header"
        assert top_dirs_pos > header_pos, "TOP 5 LARGEST DIRECTORIES should come after header"
        assert large_files_pos > top_dirs_pos, "FILES LARGER THAN 50MB should come after TOP 5 LARGEST DIRECTORIES"
        assert old_logs_pos > large_files_pos, "OLD LOG FILES should come after FILES LARGER THAN 50MB"
        assert distribution_pos > old_logs_pos, "FILE TYPE DISTRIBUTION should come after OLD LOG FILES"
        assert summary_pos > distribution_pos, "SUMMARY should come after FILE TYPE DISTRIBUTION"
        assert end_pos > summary_pos, "END REPORT should come after SUMMARY"

    def test_report_has_reasonable_length(self, report_content):
        """Verify report has reasonable content length."""
        # A complete report should have at least several hundred characters
        assert len(report_content) > 500, \
            f"Report seems too short ({len(report_content)} chars). Expected a comprehensive report."

    def test_sizes_use_human_readable_format(self, report_content):
        """Verify sizes are in human-readable format (K, M, G)."""
        # Look for size patterns like "120M", "55M", "200M", etc.
        size_pattern = r'\d+[KMG]\b|\d+\.\d+[KMG]\b'
        matches = re.findall(size_pattern, report_content)
        assert len(matches) > 0, \
            "Report should contain human-readable sizes (e.g., 120M, 55M, 200M)"
