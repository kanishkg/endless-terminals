# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student has completed
the incident log triage task.
"""

import os
import json
import pytest


class TestFinalState:
    """Test the final state of the filesystem after the incident triage task."""

    INCIDENTS_DIR = "/home/user/incidents"
    PRIORITY_JSON_FILE = "/home/user/incidents/priority_incidents.json"
    TRIAGE_SUMMARY_FILE = "/home/user/incidents/triage_summary.txt"

    # Expected filtered incidents (critical/high AND open)
    EXPECTED_INCIDENTS = [
        {
            "incident_id": "INC001",
            "timestamp": "2024-01-15T08:30:00Z",
            "severity": "critical",
            "service": "payment-api",
            "status": "open",
            "assigned_to": "alice"
        },
        {
            "incident_id": "INC003",
            "timestamp": "2024-01-15T10:00:00Z",
            "severity": "high",
            "service": "payment-api",
            "status": "open",
            "assigned_to": "charlie"
        },
        {
            "incident_id": "INC005",
            "timestamp": "2024-01-15T11:30:00Z",
            "severity": "critical",
            "service": "database-cluster",
            "status": "open",
            "assigned_to": "dave"
        },
        {
            "incident_id": "INC007",
            "timestamp": "2024-01-15T12:45:00Z",
            "severity": "high",
            "service": "inventory-service",
            "status": "open",
            "assigned_to": "frank"
        }
    ]

    EXPECTED_SERVICES_SORTED = ["database-cluster", "inventory-service", "payment-api"]
    EXPECTED_INCIDENT_COUNT = 4

    # --- JSON File Tests ---

    def test_priority_json_file_exists(self):
        """Test that the priority_incidents.json file exists."""
        assert os.path.exists(self.PRIORITY_JSON_FILE), (
            f"File {self.PRIORITY_JSON_FILE} does not exist. "
            "Please create the JSON file with filtered priority incidents."
        )
        assert os.path.isfile(self.PRIORITY_JSON_FILE), (
            f"{self.PRIORITY_JSON_FILE} exists but is not a regular file."
        )

    def test_priority_json_is_valid_json(self):
        """Test that the JSON file contains valid JSON."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            content = f.read()

        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {self.PRIORITY_JSON_FILE} does not contain valid JSON.\n"
                f"JSON parsing error: {e}"
            )

    def test_priority_json_is_array(self):
        """Test that the JSON file contains an array at the root level."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list), (
            f"JSON file should contain an array at the root level, "
            f"but found {type(data).__name__}."
        )

    def test_priority_json_has_correct_count(self):
        """Test that the JSON file contains exactly 4 incidents."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        assert len(data) == self.EXPECTED_INCIDENT_COUNT, (
            f"JSON file should contain exactly {self.EXPECTED_INCIDENT_COUNT} incidents, "
            f"but found {len(data)}."
        )

    def test_priority_json_incidents_have_correct_fields(self):
        """Test that each incident object has all required fields."""
        expected_fields = {"incident_id", "timestamp", "severity", "service", "status", "assigned_to"}

        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        for i, incident in enumerate(data):
            assert isinstance(incident, dict), (
                f"Incident at index {i} is not an object, found {type(incident).__name__}."
            )
            actual_fields = set(incident.keys())
            assert actual_fields == expected_fields, (
                f"Incident at index {i} has incorrect fields.\n"
                f"Expected fields: {sorted(expected_fields)}\n"
                f"Found fields: {sorted(actual_fields)}"
            )

    def test_priority_json_all_values_are_strings(self):
        """Test that all field values in the JSON are strings."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        for i, incident in enumerate(data):
            for key, value in incident.items():
                assert isinstance(value, str), (
                    f"Incident at index {i}, field '{key}' should be a string, "
                    f"but found {type(value).__name__} with value {value!r}."
                )

    def test_priority_json_all_incidents_are_critical_or_high(self):
        """Test that all incidents in JSON have severity 'critical' or 'high'."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        valid_severities = {"critical", "high"}
        for i, incident in enumerate(data):
            severity = incident.get("severity", "")
            assert severity in valid_severities, (
                f"Incident at index {i} (ID: {incident.get('incident_id', 'unknown')}) "
                f"has severity '{severity}', but only 'critical' or 'high' should be included."
            )

    def test_priority_json_all_incidents_are_open(self):
        """Test that all incidents in JSON have status 'open'."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        for i, incident in enumerate(data):
            status = incident.get("status", "")
            assert status == "open", (
                f"Incident at index {i} (ID: {incident.get('incident_id', 'unknown')}) "
                f"has status '{status}', but only 'open' status incidents should be included."
            )

    def test_priority_json_contains_correct_incident_ids(self):
        """Test that the JSON contains the correct incident IDs."""
        expected_ids = {"INC001", "INC003", "INC005", "INC007"}

        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        actual_ids = {incident.get("incident_id") for incident in data}

        assert actual_ids == expected_ids, (
            f"JSON file contains incorrect incident IDs.\n"
            f"Expected IDs: {sorted(expected_ids)}\n"
            f"Found IDs: {sorted(actual_ids)}"
        )

    def test_priority_json_incidents_have_correct_data(self):
        """Test that each incident in JSON has the correct data values."""
        with open(self.PRIORITY_JSON_FILE, 'r') as f:
            data = json.load(f)

        # Create a lookup by incident_id for easier comparison
        actual_by_id = {incident["incident_id"]: incident for incident in data}
        expected_by_id = {incident["incident_id"]: incident for incident in self.EXPECTED_INCIDENTS}

        for incident_id, expected in expected_by_id.items():
            assert incident_id in actual_by_id, (
                f"Incident {incident_id} is missing from the JSON file."
            )
            actual = actual_by_id[incident_id]
            assert actual == expected, (
                f"Incident {incident_id} has incorrect data.\n"
                f"Expected: {expected}\n"
                f"Found: {actual}"
            )

    # --- Summary File Tests ---

    def test_triage_summary_file_exists(self):
        """Test that the triage_summary.txt file exists."""
        assert os.path.exists(self.TRIAGE_SUMMARY_FILE), (
            f"File {self.TRIAGE_SUMMARY_FILE} does not exist. "
            "Please create the triage summary text file."
        )
        assert os.path.isfile(self.TRIAGE_SUMMARY_FILE), (
            f"{self.TRIAGE_SUMMARY_FILE} exists but is not a regular file."
        )

    def test_triage_summary_line1_is_title(self):
        """Test that line 1 of the summary is 'Priority Incidents Report'."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 1, (
            f"File {self.TRIAGE_SUMMARY_FILE} is empty or has no lines."
        )

        line1 = lines[0].rstrip('\n\r')
        assert line1 == "Priority Incidents Report", (
            f"Line 1 should be 'Priority Incidents Report', but found: '{line1}'"
        )

    def test_triage_summary_line2_has_correct_count(self):
        """Test that line 2 contains the correct incident count."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 2, (
            f"File {self.TRIAGE_SUMMARY_FILE} has fewer than 2 lines."
        )

        line2 = lines[1].rstrip('\n\r')
        expected_line2 = "Total critical/high open incidents: 4"
        assert line2 == expected_line2, (
            f"Line 2 should be '{expected_line2}', but found: '{line2}'"
        )

    def test_triage_summary_line3_is_blank(self):
        """Test that line 3 is blank."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 3, (
            f"File {self.TRIAGE_SUMMARY_FILE} has fewer than 3 lines."
        )

        line3 = lines[2].rstrip('\n\r')
        assert line3 == "", (
            f"Line 3 should be blank, but found: '{line3}'"
        )

    def test_triage_summary_has_correct_services(self):
        """Test that the summary lists the correct services sorted alphabetically with no duplicates."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 6, (
            f"File {self.TRIAGE_SUMMARY_FILE} should have at least 6 lines "
            f"(title, count, blank, 3 services), but found {len(lines)} lines."
        )

        # Extract service lines (lines 4 onwards, index 3+)
        service_lines = [line.rstrip('\n\r') for line in lines[3:] if line.rstrip('\n\r')]

        assert service_lines == self.EXPECTED_SERVICES_SORTED, (
            f"Services listed do not match expected services.\n"
            f"Expected (sorted, no duplicates): {self.EXPECTED_SERVICES_SORTED}\n"
            f"Found: {service_lines}"
        )

    def test_triage_summary_services_are_sorted(self):
        """Test that services are listed in alphabetical order."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        # Extract service lines (lines 4 onwards, index 3+)
        service_lines = [line.rstrip('\n\r') for line in lines[3:] if line.rstrip('\n\r')]

        sorted_services = sorted(service_lines)
        assert service_lines == sorted_services, (
            f"Services are not sorted alphabetically.\n"
            f"Found order: {service_lines}\n"
            f"Expected order: {sorted_services}"
        )

    def test_triage_summary_no_duplicate_services(self):
        """Test that there are no duplicate services in the summary."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        # Extract service lines (lines 4 onwards, index 3+)
        service_lines = [line.rstrip('\n\r') for line in lines[3:] if line.rstrip('\n\r')]

        unique_services = set(service_lines)
        assert len(service_lines) == len(unique_services), (
            f"Duplicate services found in the summary.\n"
            f"Services listed: {service_lines}\n"
            f"Unique services: {sorted(unique_services)}"
        )

    def test_triage_summary_has_exactly_three_services(self):
        """Test that exactly 3 unique services are listed."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            lines = f.readlines()

        # Extract service lines (lines 4 onwards, index 3+)
        service_lines = [line.rstrip('\n\r') for line in lines[3:] if line.rstrip('\n\r')]

        assert len(service_lines) == 3, (
            f"Expected exactly 3 services (database-cluster, inventory-service, payment-api), "
            f"but found {len(service_lines)}: {service_lines}"
        )

    def test_triage_summary_complete_format(self):
        """Test the complete format of the triage summary file."""
        with open(self.TRIAGE_SUMMARY_FILE, 'r') as f:
            content = f.read()

        expected_content = """Priority Incidents Report
Total critical/high open incidents: 4

database-cluster
inventory-service
payment-api
"""
        # Normalize line endings for comparison
        normalized_content = content.replace('\r\n', '\n').rstrip('\n') + '\n'
        normalized_expected = expected_content.replace('\r\n', '\n')

        assert normalized_content == normalized_expected, (
            f"Triage summary file content does not match expected format.\n"
            f"Expected:\n{expected_content}\n"
            f"Found:\n{content}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
