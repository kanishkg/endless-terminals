# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student performs
the build pipeline data analysis task.
"""

import os
import csv
import json
import pytest


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_pipelines_directory_exists(self):
        """The /home/user/pipelines/ directory must exist."""
        pipelines_dir = "/home/user/pipelines"
        assert os.path.isdir(pipelines_dir), (
            f"Directory '{pipelines_dir}' does not exist. "
            "Please create the pipelines directory before starting the task."
        )


class TestIOSBuildsCSV:
    """Test the iOS builds CSV file exists and has correct structure."""

    @pytest.fixture
    def ios_csv_path(self):
        return "/home/user/pipelines/ios_builds.csv"

    def test_ios_csv_file_exists(self, ios_csv_path):
        """The iOS builds CSV file must exist."""
        assert os.path.isfile(ios_csv_path), (
            f"File '{ios_csv_path}' does not exist. "
            "The iOS builds CSV file is required for this task."
        )

    def test_ios_csv_is_readable(self, ios_csv_path):
        """The iOS builds CSV file must be readable."""
        assert os.access(ios_csv_path, os.R_OK), (
            f"File '{ios_csv_path}' is not readable. "
            "Please check file permissions."
        )

    def test_ios_csv_has_correct_headers(self, ios_csv_path):
        """The iOS builds CSV must have the expected column headers."""
        expected_headers = ['build_id', 'app_name', 'build_time_seconds', 'status', 'branch', 'timestamp']

        with open(ios_csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader, None)

        assert headers is not None, (
            f"File '{ios_csv_path}' appears to be empty or has no headers."
        )
        assert headers == expected_headers, (
            f"CSV headers mismatch. Expected: {expected_headers}, Got: {headers}"
        )

    def test_ios_csv_has_data_rows(self, ios_csv_path):
        """The iOS builds CSV must have data rows (not just headers)."""
        with open(ios_csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            data_rows = list(reader)

        assert len(data_rows) > 0, (
            f"File '{ios_csv_path}' has no data rows. "
            "The CSV file should contain iOS build records."
        )

    def test_ios_csv_has_expected_row_count(self, ios_csv_path):
        """The iOS builds CSV should have exactly 7 data rows."""
        with open(ios_csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            data_rows = list(reader)

        assert len(data_rows) == 7, (
            f"Expected 7 data rows in iOS CSV, but found {len(data_rows)}."
        )

    def test_ios_csv_contains_failed_builds(self, ios_csv_path):
        """The iOS builds CSV must contain some FAILED builds."""
        with open(ios_csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            failed_count = sum(1 for row in reader if row.get('status') == 'FAILED')

        assert failed_count > 0, (
            f"File '{ios_csv_path}' contains no FAILED builds. "
            "The task requires processing failed builds."
        )

    def test_ios_csv_has_exactly_3_failed_builds(self, ios_csv_path):
        """The iOS builds CSV should have exactly 3 FAILED builds."""
        with open(ios_csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            failed_count = sum(1 for row in reader if row.get('status') == 'FAILED')

        assert failed_count == 3, (
            f"Expected 3 FAILED builds in iOS CSV, but found {failed_count}."
        )


class TestAndroidBuildsJSON:
    """Test the Android builds JSON file exists and has correct structure."""

    @pytest.fixture
    def android_json_path(self):
        return "/home/user/pipelines/android_builds.json"

    def test_android_json_file_exists(self, android_json_path):
        """The Android builds JSON file must exist."""
        assert os.path.isfile(android_json_path), (
            f"File '{android_json_path}' does not exist. "
            "The Android builds JSON file is required for this task."
        )

    def test_android_json_is_readable(self, android_json_path):
        """The Android builds JSON file must be readable."""
        assert os.access(android_json_path, os.R_OK), (
            f"File '{android_json_path}' is not readable. "
            "Please check file permissions."
        )

    def test_android_json_is_valid_json(self, android_json_path):
        """The Android builds JSON file must contain valid JSON."""
        try:
            with open(android_json_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File '{android_json_path}' contains invalid JSON: {e}"
            )

    def test_android_json_is_array(self, android_json_path):
        """The Android builds JSON must be an array."""
        with open(android_json_path, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list), (
            f"File '{android_json_path}' should contain a JSON array, "
            f"but found {type(data).__name__}."
        )

    def test_android_json_has_records(self, android_json_path):
        """The Android builds JSON must have build records."""
        with open(android_json_path, 'r') as f:
            data = json.load(f)

        assert len(data) > 0, (
            f"File '{android_json_path}' is an empty array. "
            "The JSON file should contain Android build records."
        )

    def test_android_json_has_expected_record_count(self, android_json_path):
        """The Android builds JSON should have exactly 5 records."""
        with open(android_json_path, 'r') as f:
            data = json.load(f)

        assert len(data) == 5, (
            f"Expected 5 records in Android JSON, but found {len(data)}."
        )

    def test_android_json_records_have_required_fields(self, android_json_path):
        """Each Android build record must have the required fields."""
        required_fields = ['buildId', 'appName', 'buildDuration', 'result', 'branch', 'date']

        with open(android_json_path, 'r') as f:
            data = json.load(f)

        for i, record in enumerate(data):
            for field in required_fields:
                assert field in record, (
                    f"Record {i} in '{android_json_path}' is missing required field '{field}'. "
                    f"Record: {record}"
                )

    def test_android_json_contains_failed_builds(self, android_json_path):
        """The Android builds JSON must contain some FAILED builds."""
        with open(android_json_path, 'r') as f:
            data = json.load(f)

        failed_count = sum(1 for record in data if record.get('result') == 'FAILED')

        assert failed_count > 0, (
            f"File '{android_json_path}' contains no FAILED builds. "
            "The task requires processing failed builds."
        )

    def test_android_json_has_exactly_3_failed_builds(self, android_json_path):
        """The Android builds JSON should have exactly 3 FAILED builds."""
        with open(android_json_path, 'r') as f:
            data = json.load(f)

        failed_count = sum(1 for record in data if record.get('result') == 'FAILED')

        assert failed_count == 3, (
            f"Expected 3 FAILED builds in Android JSON, but found {failed_count}."
        )


class TestOutputFilesDoNotExist:
    """Test that output files do not exist yet (clean state)."""

    def test_failed_builds_report_does_not_exist(self):
        """The output report file should not exist before the task."""
        output_path = "/home/user/pipelines/failed_builds_report.json"
        assert not os.path.exists(output_path), (
            f"Output file '{output_path}' already exists. "
            "Please remove it to start with a clean state."
        )

    def test_failure_summary_does_not_exist(self):
        """The output summary file should not exist before the task."""
        output_path = "/home/user/pipelines/failure_summary.txt"
        assert not os.path.exists(output_path), (
            f"Output file '{output_path}' already exists. "
            "Please remove it to start with a clean state."
        )
