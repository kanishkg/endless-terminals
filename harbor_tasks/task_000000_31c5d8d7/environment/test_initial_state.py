# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student performs
the incident log triage task.
"""

import os
import csv
import pytest


class TestInitialState:
    """Test the initial state of the filesystem for the incident triage task."""

    INCIDENTS_DIR = "/home/user/incidents"
    INCIDENT_LOG_FILE = "/home/user/incidents/incident_log.csv"

    # Expected CSV content
    EXPECTED_HEADERS = ["incident_id", "timestamp", "severity", "service", "status", "assigned_to"]
    EXPECTED_ROWS = [
        ["INC001", "2024-01-15T08:30:00Z", "critical", "payment-api", "open", "alice"],
        ["INC002", "2024-01-15T09:15:00Z", "low", "user-service", "closed", "bob"],
        ["INC003", "2024-01-15T10:00:00Z", "high", "payment-api", "open", "charlie"],
        ["INC004", "2024-01-15T10:45:00Z", "medium", "notification-service", "open", "alice"],
        ["INC005", "2024-01-15T11:30:00Z", "critical", "database-cluster", "open", "dave"],
        ["INC006", "2024-01-15T12:00:00Z", "high", "auth-service", "closed", "eve"],
        ["INC007", "2024-01-15T12:45:00Z", "high", "inventory-service", "open", "frank"],
        ["INC008", "2024-01-15T13:30:00Z", "critical", "payment-api", "closed", "alice"],
    ]

    def test_incidents_directory_exists(self):
        """Test that the incidents directory exists."""
        assert os.path.exists(self.INCIDENTS_DIR), (
            f"Directory {self.INCIDENTS_DIR} does not exist. "
            "Please create the incidents directory before running the task."
        )
        assert os.path.isdir(self.INCIDENTS_DIR), (
            f"{self.INCIDENTS_DIR} exists but is not a directory."
        )

    def test_incident_log_file_exists(self):
        """Test that the incident_log.csv file exists."""
        assert os.path.exists(self.INCIDENT_LOG_FILE), (
            f"File {self.INCIDENT_LOG_FILE} does not exist. "
            "Please create the incident log CSV file before running the task."
        )
        assert os.path.isfile(self.INCIDENT_LOG_FILE), (
            f"{self.INCIDENT_LOG_FILE} exists but is not a regular file."
        )

    def test_incident_log_is_readable(self):
        """Test that the incident_log.csv file is readable."""
        assert os.access(self.INCIDENT_LOG_FILE, os.R_OK), (
            f"File {self.INCIDENT_LOG_FILE} is not readable. "
            "Please check file permissions."
        )

    def test_incident_log_has_correct_headers(self):
        """Test that the CSV file has the correct headers."""
        with open(self.INCIDENT_LOG_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)

        assert headers is not None, (
            f"File {self.INCIDENT_LOG_FILE} is empty or has no headers."
        )
        assert headers == self.EXPECTED_HEADERS, (
            f"CSV headers do not match expected headers.\n"
            f"Expected: {self.EXPECTED_HEADERS}\n"
            f"Found: {headers}"
        )

    def test_incident_log_has_correct_row_count(self):
        """Test that the CSV file has the expected number of data rows."""
        with open(self.INCIDENT_LOG_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)

        expected_count = len(self.EXPECTED_ROWS)
        actual_count = len(rows)

        assert actual_count == expected_count, (
            f"CSV file has {actual_count} data rows, expected {expected_count} rows."
        )

    def test_incident_log_has_correct_content(self):
        """Test that the CSV file contains the expected incident data."""
        with open(self.INCIDENT_LOG_FILE, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            rows = list(reader)

        for i, (expected_row, actual_row) in enumerate(zip(self.EXPECTED_ROWS, rows)):
            assert actual_row == expected_row, (
                f"Row {i + 1} does not match expected content.\n"
                f"Expected: {expected_row}\n"
                f"Found: {actual_row}"
            )

    def test_incident_log_contains_required_severities(self):
        """Test that the CSV contains incidents with critical and high severities."""
        with open(self.INCIDENT_LOG_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            severities = {row['severity'] for row in reader}

        assert 'critical' in severities, (
            "CSV file does not contain any 'critical' severity incidents."
        )
        assert 'high' in severities, (
            "CSV file does not contain any 'high' severity incidents."
        )

    def test_incident_log_contains_required_statuses(self):
        """Test that the CSV contains incidents with both open and closed statuses."""
        with open(self.INCIDENT_LOG_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            statuses = {row['status'] for row in reader}

        assert 'open' in statuses, (
            "CSV file does not contain any 'open' status incidents."
        )
        assert 'closed' in statuses, (
            "CSV file does not contain any 'closed' status incidents."
        )

    def test_incident_log_contains_expected_services(self):
        """Test that the CSV contains the expected services."""
        expected_services = {
            'payment-api', 'user-service', 'notification-service',
            'database-cluster', 'auth-service', 'inventory-service'
        }

        with open(self.INCIDENT_LOG_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            actual_services = {row['service'] for row in reader}

        assert actual_services == expected_services, (
            f"Services in CSV do not match expected services.\n"
            f"Expected: {sorted(expected_services)}\n"
            f"Found: {sorted(actual_services)}"
        )

    def test_output_files_do_not_exist_yet(self):
        """Test that the output files do not exist yet (clean state)."""
        output_json = "/home/user/incidents/priority_incidents.json"
        output_txt = "/home/user/incidents/triage_summary.txt"

        # These are warnings, not failures - the task should work even if they exist
        # But we note if they already exist
        if os.path.exists(output_json):
            pytest.skip(
                f"Warning: Output file {output_json} already exists. "
                "This may indicate the task was already attempted."
            )
        if os.path.exists(output_txt):
            pytest.skip(
                f"Warning: Output file {output_txt} already exists. "
                "This may indicate the task was already attempted."
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
