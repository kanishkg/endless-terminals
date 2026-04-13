# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student has completed
the build pipeline data analysis task.
"""

import os
import json
import pytest


class TestOutputFilesExist:
    """Test that required output files exist."""

    def test_failed_builds_report_exists(self):
        """The failed builds report JSON file must exist."""
        report_path = "/home/user/pipelines/failed_builds_report.json"
        assert os.path.isfile(report_path), (
            f"Output file '{report_path}' does not exist. "
            "The task requires creating this JSON report file."
        )

    def test_failure_summary_exists(self):
        """The failure summary text file must exist."""
        summary_path = "/home/user/pipelines/failure_summary.txt"
        assert os.path.isfile(summary_path), (
            f"Output file '{summary_path}' does not exist. "
            "The task requires creating this summary file."
        )


class TestFailedBuildsReportJSON:
    """Test the failed builds report JSON file content and structure."""

    @pytest.fixture
    def report_path(self):
        return "/home/user/pipelines/failed_builds_report.json"

    @pytest.fixture
    def report_data(self, report_path):
        """Load and return the JSON report data."""
        with open(report_path, 'r') as f:
            return json.load(f)

    def test_report_is_valid_json(self, report_path):
        """The report file must contain valid JSON."""
        try:
            with open(report_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File '{report_path}' contains invalid JSON: {e}"
            )

    def test_report_is_array(self, report_data):
        """The report must be a JSON array."""
        assert isinstance(report_data, list), (
            f"Report should be a JSON array, but found {type(report_data).__name__}."
        )

    def test_report_has_exactly_6_objects(self, report_data):
        """The report must contain exactly 6 failed build objects."""
        assert len(report_data) == 6, (
            f"Expected exactly 6 failed build objects in report, but found {len(report_data)}."
        )

    def test_all_objects_have_required_fields(self, report_data):
        """Each object must have all required fields."""
        required_fields = ['platform', 'build_id', 'app_name', 'duration_minutes', 'branch']

        for i, obj in enumerate(report_data):
            for field in required_fields:
                assert field in obj, (
                    f"Object at index {i} is missing required field '{field}'. "
                    f"Object: {obj}"
                )

    def test_platform_values_are_valid(self, report_data):
        """Platform values must be either 'ios' or 'android'."""
        for i, obj in enumerate(report_data):
            platform = obj.get('platform')
            assert platform in ['ios', 'android'], (
                f"Object at index {i} has invalid platform '{platform}'. "
                "Must be 'ios' or 'android'."
            )

    def test_build_id_is_string(self, report_data):
        """Build IDs must be strings."""
        for i, obj in enumerate(report_data):
            build_id = obj.get('build_id')
            assert isinstance(build_id, str), (
                f"Object at index {i} has build_id of type {type(build_id).__name__}, "
                "but it should be a string."
            )

    def test_duration_minutes_is_number(self, report_data):
        """Duration minutes must be a number."""
        for i, obj in enumerate(report_data):
            duration = obj.get('duration_minutes')
            assert isinstance(duration, (int, float)), (
                f"Object at index {i} has duration_minutes of type {type(duration).__name__}, "
                "but it should be a number."
            )

    def test_ios_failure_count(self, report_data):
        """There should be exactly 3 iOS failures."""
        ios_count = sum(1 for obj in report_data if obj.get('platform') == 'ios')
        assert ios_count == 3, (
            f"Expected 3 iOS failures in report, but found {ios_count}."
        )

    def test_android_failure_count(self, report_data):
        """There should be exactly 3 Android failures."""
        android_count = sum(1 for obj in report_data if obj.get('platform') == 'android')
        assert android_count == 3, (
            f"Expected 3 Android failures in report, but found {android_count}."
        )

    def test_sorted_by_app_name_then_build_id(self, report_data):
        """The array must be sorted by app_name alphabetically, then by build_id."""
        sorted_data = sorted(report_data, key=lambda x: (x['app_name'], x['build_id']))

        for i, (actual, expected) in enumerate(zip(report_data, sorted_data)):
            assert actual['app_name'] == expected['app_name'] and actual['build_id'] == expected['build_id'], (
                f"Array is not properly sorted. At index {i}, found app_name='{actual['app_name']}', "
                f"build_id='{actual['build_id']}' but expected app_name='{expected['app_name']}', "
                f"build_id='{expected['build_id']}'. "
                "Array should be sorted by app_name alphabetically, then by build_id ascending."
            )

    def test_specific_duration_calculations(self, report_data):
        """Verify specific duration calculations are correct (seconds / 60, rounded to 2 decimal places)."""
        expected_durations = {
            'IOS002': 5.2,    # 312 / 60 = 5.2
            'IOS004': 7.6,    # 456 / 60 = 7.6
            'IOS006': 8.72,   # 523 / 60 = 8.7166... -> 8.72
            'AND002': 6.87,   # 412 / 60 = 6.8666... -> 6.87
            'AND004': 6.3,    # 378 / 60 = 6.3
            'AND005': 7.42,   # 445 / 60 = 7.4166... -> 7.42
        }

        for obj in report_data:
            build_id = obj.get('build_id')
            if build_id in expected_durations:
                expected = expected_durations[build_id]
                actual = obj.get('duration_minutes')
                assert abs(actual - expected) < 0.01, (
                    f"Duration for build_id '{build_id}' is incorrect. "
                    f"Expected {expected}, but got {actual}."
                )

    def test_expected_build_ids_present(self, report_data):
        """All expected failed build IDs must be present."""
        expected_build_ids = {'IOS002', 'IOS004', 'IOS006', 'AND002', 'AND004', 'AND005'}
        actual_build_ids = {obj.get('build_id') for obj in report_data}

        missing = expected_build_ids - actual_build_ids
        extra = actual_build_ids - expected_build_ids

        assert not missing, (
            f"Missing expected failed build IDs: {missing}"
        )
        assert not extra, (
            f"Unexpected build IDs in report: {extra}"
        )

    def test_exact_first_record(self, report_data):
        """First record should be Analytics iOS build (alphabetically first app_name)."""
        first = report_data[0]
        assert first['app_name'] == 'Analytics', (
            f"First record should have app_name 'Analytics' (alphabetically first), "
            f"but found '{first['app_name']}'."
        )
        assert first['platform'] == 'ios', (
            f"First record (Analytics) should be iOS platform, but found '{first['platform']}'."
        )
        assert first['build_id'] == 'IOS004', (
            f"First record should have build_id 'IOS004', but found '{first['build_id']}'."
        )

    def test_json_formatting_with_2_space_indent(self, report_path):
        """The JSON file should be formatted with 2-space indentation."""
        with open(report_path, 'r') as f:
            content = f.read()

        # Check that the file uses 2-space indentation (lines starting with exactly 2 spaces)
        lines = content.split('\n')
        # Find lines that are indented (object properties)
        indented_lines = [line for line in lines if line.startswith('  ') and not line.startswith('    ')]

        # There should be indented lines with 2 spaces
        assert len(indented_lines) > 0 or '  "' in content, (
            "JSON file does not appear to use 2-space indentation."
        )


class TestFailureSummaryTxt:
    """Test the failure summary text file content."""

    @pytest.fixture
    def summary_path(self):
        return "/home/user/pipelines/failure_summary.txt"

    @pytest.fixture
    def summary_lines(self, summary_path):
        """Load and return the summary file lines."""
        with open(summary_path, 'r') as f:
            return f.read().splitlines()

    def test_summary_has_exactly_3_lines(self, summary_lines):
        """The summary file must have exactly 3 lines."""
        # Filter out empty lines at the end if any
        non_empty_lines = [line for line in summary_lines if line.strip()]
        assert len(non_empty_lines) == 3, (
            f"Summary file should have exactly 3 lines, but found {len(non_empty_lines)}. "
            f"Lines found: {non_empty_lines}"
        )

    def test_line1_total_failed_builds(self, summary_lines):
        """Line 1 must be 'Total failed builds: 6'."""
        expected = "Total failed builds: 6"
        actual = summary_lines[0] if len(summary_lines) > 0 else ""
        assert actual == expected, (
            f"Line 1 should be '{expected}', but found '{actual}'."
        )

    def test_line2_ios_failures(self, summary_lines):
        """Line 2 must be 'iOS failures: 3'."""
        expected = "iOS failures: 3"
        actual = summary_lines[1] if len(summary_lines) > 1 else ""
        assert actual == expected, (
            f"Line 2 should be '{expected}', but found '{actual}'."
        )

    def test_line3_android_failures(self, summary_lines):
        """Line 3 must be 'Android failures: 3'."""
        expected = "Android failures: 3"
        actual = summary_lines[2] if len(summary_lines) > 2 else ""
        assert actual == expected, (
            f"Line 3 should be '{expected}', but found '{actual}'."
        )

    def test_exact_summary_content(self, summary_path):
        """Verify the exact content of the summary file."""
        expected_content = """Total failed builds: 6
iOS failures: 3
Android failures: 3"""

        with open(summary_path, 'r') as f:
            actual_content = f.read().rstrip('\n')

        assert actual_content == expected_content, (
            f"Summary file content does not match expected.\n"
            f"Expected:\n{expected_content}\n\n"
            f"Actual:\n{actual_content}"
        )


class TestCompleteReportContent:
    """Test the complete content of the report matches expected output."""

    def test_exact_report_content(self):
        """Verify the exact content of the failed builds report."""
        report_path = "/home/user/pipelines/failed_builds_report.json"

        expected_data = [
            {
                "platform": "ios",
                "build_id": "IOS004",
                "app_name": "Analytics",
                "duration_minutes": 7.6,
                "branch": "develop"
            },
            {
                "platform": "android",
                "build_id": "AND004",
                "app_name": "ChatModule",
                "duration_minutes": 6.3,
                "branch": "develop"
            },
            {
                "platform": "ios",
                "build_id": "IOS006",
                "app_name": "ChatModule",
                "duration_minutes": 8.72,
                "branch": "feature/push"
            },
            {
                "platform": "android",
                "build_id": "AND002",
                "app_name": "MobileApp",
                "duration_minutes": 6.87,
                "branch": "feature/login"
            },
            {
                "platform": "ios",
                "build_id": "IOS002",
                "app_name": "MobileApp",
                "duration_minutes": 5.2,
                "branch": "feature/login"
            },
            {
                "platform": "android",
                "build_id": "AND005",
                "app_name": "PaymentSDK",
                "duration_minutes": 7.42,
                "branch": "feature/checkout"
            }
        ]

        with open(report_path, 'r') as f:
            actual_data = json.load(f)

        assert len(actual_data) == len(expected_data), (
            f"Report has {len(actual_data)} items, expected {len(expected_data)}."
        )

        for i, (actual, expected) in enumerate(zip(actual_data, expected_data)):
            assert actual['platform'] == expected['platform'], (
                f"Item {i}: platform mismatch. Expected '{expected['platform']}', got '{actual['platform']}'."
            )
            assert actual['build_id'] == expected['build_id'], (
                f"Item {i}: build_id mismatch. Expected '{expected['build_id']}', got '{actual['build_id']}'."
            )
            assert actual['app_name'] == expected['app_name'], (
                f"Item {i}: app_name mismatch. Expected '{expected['app_name']}', got '{actual['app_name']}'."
            )
            assert abs(actual['duration_minutes'] - expected['duration_minutes']) < 0.01, (
                f"Item {i}: duration_minutes mismatch. Expected {expected['duration_minutes']}, got {actual['duration_minutes']}."
            )
            assert actual['branch'] == expected['branch'], (
                f"Item {i}: branch mismatch. Expected '{expected['branch']}', got '{actual['branch']}'."
            )
