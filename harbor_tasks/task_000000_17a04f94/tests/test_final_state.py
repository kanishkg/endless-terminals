# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the backup log analysis task.
"""

import os
import pytest


class TestFinalState:
    """Test the final state after the task is performed."""

    def test_output_file_exists(self):
        """Verify /home/user/failed_counts.txt exists."""
        assert os.path.isfile("/home/user/failed_counts.txt"), \
            "Output file /home/user/failed_counts.txt does not exist. " \
            "The task requires creating this file with failed job counts."

    def test_output_file_readable(self):
        """Verify /home/user/failed_counts.txt is readable."""
        assert os.access("/home/user/failed_counts.txt", os.R_OK), \
            "Output file /home/user/failed_counts.txt is not readable."

    def test_output_file_has_six_lines(self):
        """Verify output file contains exactly 6 lines (one per unique failed job)."""
        with open("/home/user/failed_counts.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) == 6, \
            f"Output file should have exactly 6 lines (one per failed job), " \
            f"but has {len(lines)} non-empty lines."

    def test_output_contains_all_job_names(self):
        """Verify output file contains all expected job names."""
        expected_jobs = {"db-prod", "db-staging", "web-assets", 
                         "user-uploads", "config-backup", "logs-archive"}

        with open("/home/user/failed_counts.txt", "r") as f:
            content = f.read()

        missing_jobs = []
        for job in expected_jobs:
            if job not in content:
                missing_jobs.append(job)

        assert not missing_jobs, \
            f"Output file is missing the following job names: {missing_jobs}"

    def test_output_has_correct_counts(self):
        """Verify output file has correct counts for each job."""
        expected_counts = {
            "db-prod": 23,
            "db-staging": 18,
            "web-assets": 15,
            "user-uploads": 12,
            "config-backup": 7,
            "logs-archive": 5
        }

        with open("/home/user/failed_counts.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        found_counts = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    count = int(parts[0])
                    job_name = parts[1]
                    found_counts[job_name] = count
                except ValueError:
                    # Try reverse order (job count)
                    try:
                        count = int(parts[-1])
                        job_name = parts[0]
                        found_counts[job_name] = count
                    except ValueError:
                        pass

        errors = []
        for job, expected_count in expected_counts.items():
            actual_count = found_counts.get(job)
            if actual_count is None:
                errors.append(f"Job '{job}' not found in output")
            elif actual_count != expected_count:
                errors.append(f"Job '{job}' has count {actual_count}, expected {expected_count}")

        assert not errors, \
            "Incorrect counts in output file:\n" + "\n".join(errors)

    def test_output_sorted_descending_by_count(self):
        """Verify output is sorted by count in descending order (highest first)."""
        with open("/home/user/failed_counts.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        counts = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    count = int(parts[0])
                    counts.append(count)
                except ValueError:
                    # Try reverse order
                    try:
                        count = int(parts[-1])
                        counts.append(count)
                    except ValueError:
                        pass

        assert len(counts) == 6, \
            f"Could not parse counts from all 6 lines. Found {len(counts)} counts."

        # Check descending order
        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i + 1], \
                f"Output is not sorted in descending order. " \
                f"Count {counts[i]} at position {i} should be >= count {counts[i + 1]} at position {i + 1}. " \
                f"Full order of counts: {counts}"

    def test_output_order_matches_expected(self):
        """Verify the exact order of jobs matches expected (by count descending)."""
        expected_order = ["db-prod", "db-staging", "web-assets", 
                         "user-uploads", "config-backup", "logs-archive"]

        with open("/home/user/failed_counts.txt", "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        actual_order = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                # Assume format is "count jobname" (standard uniq -c output)
                try:
                    int(parts[0])
                    actual_order.append(parts[1])
                except ValueError:
                    # Maybe format is "jobname count"
                    actual_order.append(parts[0])

        assert actual_order == expected_order, \
            f"Job order is incorrect.\n" \
            f"Expected: {expected_order}\n" \
            f"Actual:   {actual_order}\n" \
            f"Jobs should be sorted by failure count (highest first)."

    def test_log_file_unchanged(self):
        """Verify the original log file is unchanged (invariant)."""
        assert os.path.isfile("/var/log/backup/march.log"), \
            "Original log file /var/log/backup/march.log should still exist."

        # Verify it still has the expected content by checking FAILED counts
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
                f"Log file appears to have been modified. " \
                f"Job '{job}' should have {expected_count} FAILED entries, but has {actual_count}."

    def test_output_format_parseable(self):
        """Verify output format has count and job name on each line."""
        with open("/home/user/failed_counts.txt", "r") as f:
            lines = [line for line in f.readlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            parts = line.split()
            assert len(parts) >= 2, \
                f"Line {i} does not have at least 2 fields (count and job name): '{line.strip()}'"

            # Check that one of the fields is a number
            has_number = False
            for part in parts:
                try:
                    int(part)
                    has_number = True
                    break
                except ValueError:
                    pass

            assert has_number, \
                f"Line {i} does not contain a count number: '{line.strip()}'"
