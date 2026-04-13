# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the build log analysis task.
"""

import os
import pytest


class TestInitialDirectoryStructure:
    """Test that required directories exist."""

    def test_builds_directory_exists(self):
        """The /home/user/builds/ directory must exist."""
        builds_dir = "/home/user/builds"
        assert os.path.isdir(builds_dir), (
            f"Directory '{builds_dir}' does not exist. "
            "The builds directory must be created before starting the task."
        )


class TestLogFileExists:
    """Test that the build log file exists."""

    def test_artifact_build_log_exists(self):
        """The artifact_build.log file must exist in /home/user/builds/."""
        log_file = "/home/user/builds/artifact_build.log"
        assert os.path.isfile(log_file), (
            f"Log file '{log_file}' does not exist. "
            "The artifact_build.log file must be present before starting the task."
        )


class TestLogFileContent:
    """Test that the log file has the expected content."""

    @pytest.fixture
    def log_file_path(self):
        return "/home/user/builds/artifact_build.log"

    @pytest.fixture
    def log_content(self, log_file_path):
        with open(log_file_path, "r") as f:
            return f.read()

    @pytest.fixture
    def log_lines(self, log_content):
        return [line for line in log_content.strip().split("\n") if line]

    def test_log_file_is_not_empty(self, log_file_path):
        """The log file must not be empty."""
        assert os.path.getsize(log_file_path) > 0, (
            f"Log file '{log_file_path}' is empty. "
            "The log file must contain build entries."
        )

    def test_log_file_has_correct_number_of_entries(self, log_lines):
        """The log file should have 8 build entries."""
        assert len(log_lines) == 8, (
            f"Expected 8 log entries, but found {len(log_lines)}. "
            "The log file must contain exactly 8 build entries."
        )

    def test_log_file_contains_success_entries(self, log_content):
        """The log file must contain SUCCESS entries."""
        assert "[SUCCESS]" in log_content, (
            "Log file does not contain any [SUCCESS] entries. "
            "The log file must contain both SUCCESS and FAILED entries."
        )

    def test_log_file_contains_failed_entries(self, log_content):
        """The log file must contain FAILED entries."""
        assert "[FAILED]" in log_content, (
            "Log file does not contain any [FAILED] entries. "
            "The log file must contain both SUCCESS and FAILED entries."
        )

    def test_log_file_has_correct_failed_count(self, log_content):
        """The log file should have exactly 3 FAILED entries."""
        failed_count = log_content.count("[FAILED]")
        assert failed_count == 3, (
            f"Expected 3 FAILED entries, but found {failed_count}. "
            "The log file must contain exactly 3 failed component builds."
        )

    def test_log_file_has_correct_success_count(self, log_content):
        """The log file should have exactly 5 SUCCESS entries."""
        success_count = log_content.count("[SUCCESS]")
        assert success_count == 5, (
            f"Expected 5 SUCCESS entries, but found {success_count}. "
            "The log file must contain exactly 5 successful component builds."
        )

    def test_log_contains_payment_gateway_failure(self, log_content):
        """The log file must contain a FAILED entry for payment-gateway."""
        assert "[FAILED] payment-gateway" in log_content, (
            "Log file does not contain expected FAILED entry for 'payment-gateway'. "
            "This component must be present as a failed build."
        )

    def test_log_contains_auth_module_failure(self, log_content):
        """The log file must contain a FAILED entry for auth-module."""
        assert "[FAILED] auth-module" in log_content, (
            "Log file does not contain expected FAILED entry for 'auth-module'. "
            "This component must be present as a failed build."
        )

    def test_log_contains_database_connector_failure(self, log_content):
        """The log file must contain a FAILED entry for database-connector."""
        assert "[FAILED] database-connector" in log_content, (
            "Log file does not contain expected FAILED entry for 'database-connector'. "
            "This component must be present as a failed build."
        )

    def test_log_entries_have_correct_format(self, log_lines):
        """Each log entry must follow the expected format."""
        for line in log_lines:
            # Check that each line has the expected format components
            assert line.startswith("["), (
                f"Log entry does not start with timestamp: '{line}'. "
                "Each entry must start with [TIMESTAMP]."
            )
            assert "[SUCCESS]" in line or "[FAILED]" in line, (
                f"Log entry missing status: '{line}'. "
                "Each entry must contain [SUCCESS] or [FAILED]."
            )
            assert " - " in line, (
                f"Log entry missing separator: '{line}'. "
                "Each entry must contain ' - ' separator between component name and message."
            )


class TestOutputFileDoesNotExist:
    """Test that the output file does not exist yet (student needs to create it)."""

    def test_failure_report_does_not_exist(self):
        """The failure_report.txt should NOT exist before the task is performed."""
        report_file = "/home/user/builds/failure_report.txt"
        assert not os.path.exists(report_file), (
            f"Output file '{report_file}' already exists. "
            "This file should be created by the student as part of the task, "
            "not exist beforehand."
        )
