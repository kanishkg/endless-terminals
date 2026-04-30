# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the backup log analysis task.
"""

import os
import pytest
import subprocess


class TestInitialState:
    """Test the initial state before the task is performed."""

    def test_log_directory_exists(self):
        """Verify /var/log/backup directory exists."""
        assert os.path.isdir("/var/log/backup"), \
            "Directory /var/log/backup does not exist"

    def test_log_file_exists(self):
        """Verify /var/log/backup/march.log exists."""
        assert os.path.isfile("/var/log/backup/march.log"), \
            "Log file /var/log/backup/march.log does not exist"

    def test_log_file_readable(self):
        """Verify /var/log/backup/march.log is readable."""
        assert os.access("/var/log/backup/march.log", os.R_OK), \
            "Log file /var/log/backup/march.log is not readable"

    def test_log_file_has_content(self):
        """Verify log file has approximately 500 lines."""
        with open("/var/log/backup/march.log", "r") as f:
            lines = f.readlines()
        # Allow some tolerance around 500 lines
        assert 400 <= len(lines) <= 600, \
            f"Log file should have ~500 lines, but has {len(lines)} lines"

    def test_log_file_has_failed_lines(self):
        """Verify log file contains approximately 80 FAILED lines."""
        with open("/var/log/backup/march.log", "r") as f:
            content = f.read()
        failed_count = content.count("FAILED")
        # Allow some tolerance around 80 FAILED lines
        assert 70 <= failed_count <= 90, \
            f"Log file should have ~80 FAILED lines, but has {failed_count}"

    def test_log_file_format(self):
        """Verify log file lines have expected format with job name as third field."""
        with open("/var/log/backup/march.log", "r") as f:
            lines = f.readlines()

        # Check at least some lines have the expected format
        valid_lines = 0
        for line in lines[:50]:  # Check first 50 lines
            fields = line.strip().split()
            if len(fields) >= 4:
                # Check date format (should start with 2024-03-)
                if fields[0].startswith("2024-03-"):
                    # Check time format (HH:MM:SS)
                    if ":" in fields[1]:
                        # Check status is SUCCESS or FAILED
                        if fields[3] in ("SUCCESS", "FAILED"):
                            valid_lines += 1

        assert valid_lines >= 40, \
            f"Log file format incorrect. Expected lines like '2024-03-XX HH:MM:SS jobname STATUS message...', but only {valid_lines}/50 lines matched"

    def test_expected_job_names_in_failed_lines(self):
        """Verify expected job names appear in FAILED lines."""
        expected_jobs = {"db-prod", "db-staging", "web-assets", "user-uploads", "config-backup", "logs-archive"}

        with open("/var/log/backup/march.log", "r") as f:
            lines = f.readlines()

        found_jobs = set()
        for line in lines:
            if "FAILED" in line:
                fields = line.strip().split()
                if len(fields) >= 3:
                    found_jobs.add(fields[2])

        missing_jobs = expected_jobs - found_jobs
        assert not missing_jobs, \
            f"Expected job names missing from FAILED lines: {missing_jobs}"

    def test_home_user_directory_exists(self):
        """Verify /home/user directory exists."""
        assert os.path.isdir("/home/user"), \
            "Directory /home/user does not exist"

    def test_home_user_directory_writable(self):
        """Verify /home/user directory is writable."""
        assert os.access("/home/user", os.W_OK), \
            "Directory /home/user is not writable"

    def test_output_file_does_not_exist(self):
        """Verify /home/user/failed_counts.txt does not exist initially."""
        assert not os.path.exists("/home/user/failed_counts.txt"), \
            "Output file /home/user/failed_counts.txt should not exist initially"

    def test_coreutils_grep_available(self):
        """Verify grep is available."""
        result = subprocess.run(["which", "grep"], capture_output=True)
        assert result.returncode == 0, \
            "grep command is not available"

    def test_coreutils_awk_available(self):
        """Verify awk is available."""
        result = subprocess.run(["which", "awk"], capture_output=True)
        assert result.returncode == 0, \
            "awk command is not available"

    def test_coreutils_cut_available(self):
        """Verify cut is available."""
        result = subprocess.run(["which", "cut"], capture_output=True)
        assert result.returncode == 0, \
            "cut command is not available"

    def test_coreutils_sort_available(self):
        """Verify sort is available."""
        result = subprocess.run(["which", "sort"], capture_output=True)
        assert result.returncode == 0, \
            "sort command is not available"

    def test_coreutils_uniq_available(self):
        """Verify uniq is available."""
        result = subprocess.run(["which", "uniq"], capture_output=True)
        assert result.returncode == 0, \
            "uniq command is not available"

    def test_failed_job_counts_match_expected(self):
        """Verify the actual FAILED line counts match expected values."""
        expected_counts = {
            "db-prod": 23,
            "db-staging": 18,
            "web-assets": 15,
            "user-uploads": 12,
            "config-backup": 7,
            "logs-archive": 5
        }

        with open("/var/log/backup/march.log", "r") as f:
            lines = f.readlines()

        actual_counts = {}
        for line in lines:
            if "FAILED" in line:
                fields = line.strip().split()
                if len(fields) >= 3:
                    job_name = fields[2]
                    actual_counts[job_name] = actual_counts.get(job_name, 0) + 1

        for job, expected_count in expected_counts.items():
            actual_count = actual_counts.get(job, 0)
            assert actual_count == expected_count, \
                f"Job '{job}' should have {expected_count} FAILED entries, but has {actual_count}"
