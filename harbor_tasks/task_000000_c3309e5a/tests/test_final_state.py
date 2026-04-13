# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has completed the build log analysis task.
"""

import os
import pytest


class TestOutputFileExists:
    """Test that the failure report file exists."""

    def test_failure_report_file_exists(self):
        """The failure_report.txt file must exist in /home/user/builds/."""
        report_file = "/home/user/builds/failure_report.txt"
        assert os.path.isfile(report_file), (
            f"Output file '{report_file}' does not exist. "
            "The failure_report.txt file must be created as part of the task."
        )

    def test_failure_report_is_not_empty(self):
        """The failure report file must not be empty."""
        report_file = "/home/user/builds/failure_report.txt"
        assert os.path.getsize(report_file) > 0, (
            f"Output file '{report_file}' is empty. "
            "The failure report must contain the count and list of failed components."
        )


class TestFailureReportContent:
    """Test that the failure report has the correct content."""

    @pytest.fixture
    def report_file_path(self):
        return "/home/user/builds/failure_report.txt"

    @pytest.fixture
    def report_content(self, report_file_path):
        with open(report_file_path, "r") as f:
            return f.read()

    @pytest.fixture
    def report_lines(self, report_content):
        # Split by newlines, preserving empty lines
        return report_content.split("\n")

    def test_first_line_has_correct_count(self, report_lines):
        """First line must be exactly 'FAILED_COMPONENTS_COUNT: 3'."""
        expected_first_line = "FAILED_COMPONENTS_COUNT: 3"
        actual_first_line = report_lines[0] if report_lines else ""
        assert actual_first_line == expected_first_line, (
            f"First line is incorrect. "
            f"Expected: '{expected_first_line}', "
            f"Got: '{actual_first_line}'. "
            "The first line must show the exact count of failed components."
        )

    def test_second_line_is_blank(self, report_lines):
        """Second line must be empty (blank line)."""
        assert len(report_lines) >= 2, (
            "Report file has fewer than 2 lines. "
            "The report must have a count line, a blank line, and component names."
        )
        second_line = report_lines[1]
        assert second_line == "", (
            f"Second line is not blank. "
            f"Got: '{second_line}'. "
            "The second line must be empty."
        )

    def test_third_line_is_auth_module(self, report_lines):
        """Third line must be 'auth-module' (first alphabetically)."""
        assert len(report_lines) >= 3, (
            "Report file has fewer than 3 lines. "
            "The report must include the failed component names starting from line 3."
        )
        third_line = report_lines[2]
        assert third_line == "auth-module", (
            f"Third line is incorrect. "
            f"Expected: 'auth-module', Got: '{third_line}'. "
            "Components must be sorted alphabetically."
        )

    def test_fourth_line_is_database_connector(self, report_lines):
        """Fourth line must be 'database-connector' (second alphabetically)."""
        assert len(report_lines) >= 4, (
            "Report file has fewer than 4 lines. "
            "The report must include all 3 failed component names."
        )
        fourth_line = report_lines[3]
        assert fourth_line == "database-connector", (
            f"Fourth line is incorrect. "
            f"Expected: 'database-connector', Got: '{fourth_line}'. "
            "Components must be sorted alphabetically."
        )

    def test_fifth_line_is_payment_gateway(self, report_lines):
        """Fifth line must be 'payment-gateway' (third alphabetically)."""
        assert len(report_lines) >= 5, (
            "Report file has fewer than 5 lines. "
            "The report must include all 3 failed component names."
        )
        fifth_line = report_lines[4]
        assert fifth_line == "payment-gateway", (
            f"Fifth line is incorrect. "
            f"Expected: 'payment-gateway', Got: '{fifth_line}'. "
            "Components must be sorted alphabetically."
        )

    def test_no_trailing_content(self, report_lines):
        """There should be no extra content after the last component."""
        # After removing trailing empty strings from split, we should have exactly 5 lines
        # or the file ends with exactly one newline (resulting in one empty string at end)
        non_empty_after_components = [
            line for line in report_lines[5:] if line.strip()
        ]
        assert len(non_empty_after_components) == 0, (
            f"Found unexpected content after the last component: {non_empty_after_components}. "
            "The report should end after listing all failed components."
        )

    def test_exact_content_match(self, report_content):
        """The entire file content must match the expected output exactly."""
        expected_content = "FAILED_COMPONENTS_COUNT: 3\n\nauth-module\ndatabase-connector\npayment-gateway\n"
        # Also accept without trailing newline
        expected_content_no_trailing = "FAILED_COMPONENTS_COUNT: 3\n\nauth-module\ndatabase-connector\npayment-gateway"

        assert report_content == expected_content or report_content == expected_content_no_trailing, (
            f"File content does not match expected format exactly.\n"
            f"Expected:\n{repr(expected_content)}\n"
            f"Got:\n{repr(report_content)}\n"
            "Ensure the format matches: count line, blank line, then sorted component names."
        )


class TestFailedComponentsExtraction:
    """Test that the correct failed components were identified."""

    @pytest.fixture
    def report_file_path(self):
        return "/home/user/builds/failure_report.txt"

    @pytest.fixture
    def report_content(self, report_file_path):
        with open(report_file_path, "r") as f:
            return f.read()

    @pytest.fixture
    def extracted_components(self, report_content):
        lines = report_content.strip().split("\n")
        # Skip first line (count) and second line (blank), get remaining
        if len(lines) > 2:
            return [line.strip() for line in lines[2:] if line.strip()]
        return []

    def test_correct_number_of_components_listed(self, extracted_components):
        """Exactly 3 failed components should be listed."""
        assert len(extracted_components) == 3, (
            f"Expected 3 failed components listed, but found {len(extracted_components)}: "
            f"{extracted_components}. "
            "The report must list exactly the 3 failed components from the log."
        )

    def test_auth_module_is_included(self, extracted_components):
        """auth-module must be in the list of failed components."""
        assert "auth-module" in extracted_components, (
            f"'auth-module' is missing from the failed components list: {extracted_components}. "
            "This component has a FAILED status in the log file."
        )

    def test_database_connector_is_included(self, extracted_components):
        """database-connector must be in the list of failed components."""
        assert "database-connector" in extracted_components, (
            f"'database-connector' is missing from the failed components list: {extracted_components}. "
            "This component has a FAILED status in the log file."
        )

    def test_payment_gateway_is_included(self, extracted_components):
        """payment-gateway must be in the list of failed components."""
        assert "payment-gateway" in extracted_components, (
            f"'payment-gateway' is missing from the failed components list: {extracted_components}. "
            "This component has a FAILED status in the log file."
        )

    def test_components_are_sorted_alphabetically(self, extracted_components):
        """The failed components must be sorted in alphabetical order."""
        expected_order = ["auth-module", "database-connector", "payment-gateway"]
        assert extracted_components == expected_order, (
            f"Components are not in alphabetical order. "
            f"Expected: {expected_order}, Got: {extracted_components}. "
            "The failed components must be listed in alphabetical order."
        )

    def test_no_success_components_included(self, extracted_components):
        """No SUCCESS components should be in the failed list."""
        success_components = [
            "user-service",
            "notification-service", 
            "logging-service",
            "cache-manager",
            "api-router"
        ]
        for component in success_components:
            assert component not in extracted_components, (
                f"'{component}' should not be in the failed components list. "
                f"This component has SUCCESS status in the log file. "
                f"Current list: {extracted_components}"
            )


class TestOriginalLogFileUnchanged:
    """Test that the original log file still exists and is unchanged."""

    def test_log_file_still_exists(self):
        """The original artifact_build.log file must still exist."""
        log_file = "/home/user/builds/artifact_build.log"
        assert os.path.isfile(log_file), (
            f"Original log file '{log_file}' no longer exists. "
            "The log file should not be deleted or moved during the task."
        )

    def test_log_file_has_expected_failed_entries(self):
        """The log file should still have the 3 FAILED entries."""
        log_file = "/home/user/builds/artifact_build.log"
        with open(log_file, "r") as f:
            content = f.read()

        failed_count = content.count("[FAILED]")
        assert failed_count == 3, (
            f"Log file should have 3 FAILED entries, but has {failed_count}. "
            "The original log file should not be modified."
        )
