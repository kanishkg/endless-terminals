# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student has
completed the Kubernetes manifest analysis task.
"""

import os
import pytest


class TestOutputFileExists:
    """Test that the output report file exists."""

    def test_report_file_exists(self):
        """The output report file must exist after task completion."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        assert os.path.isfile(path), f"Output file {path} does not exist. The task requires creating this report file."

    def test_report_file_is_readable(self):
        """The output report file must be readable."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        assert os.access(path, os.R_OK), f"Output file {path} is not readable."


class TestReportFileContent:
    """Test that the report file has the correct content."""

    @pytest.fixture
    def report_content(self):
        """Read and return the content of the report file."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        with open(path, 'r') as f:
            return f.read()

    @pytest.fixture
    def report_lines(self, report_content):
        """Return the non-empty lines of the report."""
        # Split by newlines and filter out empty lines for line count
        # But we also need to check there are no empty lines in the middle
        return report_content.rstrip('\n').split('\n') if report_content.rstrip('\n') else []

    def test_report_has_correct_number_of_lines(self, report_lines):
        """The report must have exactly 7 lines (one per resource type)."""
        expected_lines = 7
        actual_lines = len(report_lines)
        assert actual_lines == expected_lines, (
            f"Expected {expected_lines} lines in report, found {actual_lines}. "
            f"Lines found: {report_lines}"
        )

    def test_report_has_no_empty_lines(self, report_content):
        """The report must not contain empty lines."""
        lines = report_content.rstrip('\n').split('\n')
        for i, line in enumerate(lines):
            assert line != '', f"Empty line found at line {i + 1}. Report should have no empty lines."

    def test_no_leading_spaces_on_lines(self, report_lines):
        """No line should have leading spaces."""
        for i, line in enumerate(report_lines):
            assert not line.startswith(' '), (
                f"Line {i + 1} has leading spaces: '{line}'. "
                "Lines must not have leading spaces."
            )

    def test_no_trailing_spaces_on_lines(self, report_lines):
        """No line should have trailing spaces."""
        for i, line in enumerate(report_lines):
            assert not line.endswith(' '), (
                f"Line {i + 1} has trailing spaces: '{line}'. "
                "Lines must not have trailing spaces."
            )

    def test_line_format_count_space_resourcetype(self, report_lines):
        """Each line must be formatted as 'COUNT RESOURCETYPE' (number, single space, resource name)."""
        for i, line in enumerate(report_lines):
            parts = line.split(' ')
            assert len(parts) == 2, (
                f"Line {i + 1} does not have exactly two parts separated by single space: '{line}'. "
                "Expected format: 'COUNT RESOURCETYPE'"
            )
            count_str, resource_type = parts
            assert count_str.isdigit(), (
                f"Line {i + 1} has invalid count '{count_str}': '{line}'. "
                "The count must be a number."
            )
            assert resource_type.isalpha() or resource_type.replace('PodAutoscaler', '').replace('VolumeClaim', '').isalpha(), (
                f"Line {i + 1} has invalid resource type '{resource_type}': '{line}'."
            )


class TestReportExactContent:
    """Test that the report has the exact expected content."""

    @pytest.fixture
    def expected_content(self):
        """Return the exact expected content of the report."""
        return """6 Deployment
6 Service
4 ConfigMap
2 Ingress
2 Secret
1 HorizontalPodAutoscaler
1 PersistentVolumeClaim"""

    @pytest.fixture
    def report_content(self):
        """Read and return the content of the report file."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        with open(path, 'r') as f:
            return f.read()

    def test_exact_content_match(self, report_content, expected_content):
        """The report content must match exactly."""
        # Normalize by stripping trailing newline for comparison
        actual = report_content.rstrip('\n')
        expected = expected_content.rstrip('\n')
        assert actual == expected, (
            f"Report content does not match expected.\n"
            f"Expected:\n{expected}\n\n"
            f"Actual:\n{actual}"
        )


class TestIndividualResourceEntries:
    """Test each individual resource entry in the report."""

    @pytest.fixture
    def report_lines(self):
        """Read and return the lines of the report file."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        with open(path, 'r') as f:
            content = f.read()
        return content.rstrip('\n').split('\n')

    def test_deployment_entry(self, report_lines):
        """Deployment should appear with count 6."""
        assert "6 Deployment" in report_lines, (
            f"Expected '6 Deployment' in report. Found lines: {report_lines}"
        )

    def test_service_entry(self, report_lines):
        """Service should appear with count 6."""
        assert "6 Service" in report_lines, (
            f"Expected '6 Service' in report. Found lines: {report_lines}"
        )

    def test_configmap_entry(self, report_lines):
        """ConfigMap should appear with count 4."""
        assert "4 ConfigMap" in report_lines, (
            f"Expected '4 ConfigMap' in report. Found lines: {report_lines}"
        )

    def test_ingress_entry(self, report_lines):
        """Ingress should appear with count 2."""
        assert "2 Ingress" in report_lines, (
            f"Expected '2 Ingress' in report. Found lines: {report_lines}"
        )

    def test_secret_entry(self, report_lines):
        """Secret should appear with count 2."""
        assert "2 Secret" in report_lines, (
            f"Expected '2 Secret' in report. Found lines: {report_lines}"
        )

    def test_hpa_entry(self, report_lines):
        """HorizontalPodAutoscaler should appear with count 1."""
        assert "1 HorizontalPodAutoscaler" in report_lines, (
            f"Expected '1 HorizontalPodAutoscaler' in report. Found lines: {report_lines}"
        )

    def test_pvc_entry(self, report_lines):
        """PersistentVolumeClaim should appear with count 1."""
        assert "1 PersistentVolumeClaim" in report_lines, (
            f"Expected '1 PersistentVolumeClaim' in report. Found lines: {report_lines}"
        )


class TestSortOrder:
    """Test that the report is sorted correctly."""

    @pytest.fixture
    def report_lines(self):
        """Read and return the lines of the report file."""
        path = "/home/user/k8s-manifests/resource-frequency-report.txt"
        with open(path, 'r') as f:
            content = f.read()
        return content.rstrip('\n').split('\n')

    def test_first_line_is_deployment(self, report_lines):
        """First line should be '6 Deployment' (highest count, alphabetically first among ties)."""
        assert report_lines[0] == "6 Deployment", (
            f"First line should be '6 Deployment', found '{report_lines[0]}'. "
            "Deployment and Service both have count 6, Deployment comes first alphabetically."
        )

    def test_second_line_is_service(self, report_lines):
        """Second line should be '6 Service' (same count as Deployment, but S comes after D)."""
        assert report_lines[1] == "6 Service", (
            f"Second line should be '6 Service', found '{report_lines[1]}'. "
            "Deployment and Service both have count 6, Service comes after Deployment alphabetically."
        )

    def test_third_line_is_configmap(self, report_lines):
        """Third line should be '4 ConfigMap'."""
        assert report_lines[2] == "4 ConfigMap", (
            f"Third line should be '4 ConfigMap', found '{report_lines[2]}'."
        )

    def test_fourth_line_is_ingress(self, report_lines):
        """Fourth line should be '2 Ingress' (count 2, I comes before S)."""
        assert report_lines[3] == "2 Ingress", (
            f"Fourth line should be '2 Ingress', found '{report_lines[3]}'. "
            "Ingress and Secret both have count 2, Ingress comes first alphabetically."
        )

    def test_fifth_line_is_secret(self, report_lines):
        """Fifth line should be '2 Secret' (count 2, S comes after I)."""
        assert report_lines[4] == "2 Secret", (
            f"Fifth line should be '2 Secret', found '{report_lines[4]}'. "
            "Ingress and Secret both have count 2, Secret comes after Ingress alphabetically."
        )

    def test_sixth_line_is_hpa(self, report_lines):
        """Sixth line should be '1 HorizontalPodAutoscaler' (count 1, H comes before P)."""
        assert report_lines[5] == "1 HorizontalPodAutoscaler", (
            f"Sixth line should be '1 HorizontalPodAutoscaler', found '{report_lines[5]}'. "
            "HorizontalPodAutoscaler and PersistentVolumeClaim both have count 1, H comes before P."
        )

    def test_seventh_line_is_pvc(self, report_lines):
        """Seventh line should be '1 PersistentVolumeClaim' (count 1, P comes after H)."""
        assert report_lines[6] == "1 PersistentVolumeClaim", (
            f"Seventh line should be '1 PersistentVolumeClaim', found '{report_lines[6]}'. "
            "HorizontalPodAutoscaler and PersistentVolumeClaim both have count 1, P comes after H."
        )

    def test_descending_count_order(self, report_lines):
        """Counts should be in descending order."""
        counts = []
        for line in report_lines:
            parts = line.split(' ')
            if len(parts) >= 1 and parts[0].isdigit():
                counts.append(int(parts[0]))

        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i + 1], (
                f"Counts are not in descending order. "
                f"Count at position {i} ({counts[i]}) is less than count at position {i + 1} ({counts[i + 1]}). "
                f"All counts: {counts}"
            )


class TestSourceFilesUnmodified:
    """Test that the source manifest files still exist and are unmodified."""

    def test_dev_app_yaml_still_exists(self):
        """The dev/app.yaml file should still exist."""
        path = "/home/user/k8s-manifests/dev/app.yaml"
        assert os.path.isfile(path), f"Source file {path} should still exist after task completion."

    def test_dev_database_yaml_still_exists(self):
        """The dev/database.yaml file should still exist."""
        path = "/home/user/k8s-manifests/dev/database.yaml"
        assert os.path.isfile(path), f"Source file {path} should still exist after task completion."

    def test_staging_app_yaml_still_exists(self):
        """The staging/app.yaml file should still exist."""
        path = "/home/user/k8s-manifests/staging/app.yaml"
        assert os.path.isfile(path), f"Source file {path} should still exist after task completion."

    def test_staging_monitoring_yaml_still_exists(self):
        """The staging/monitoring.yaml file should still exist."""
        path = "/home/user/k8s-manifests/staging/monitoring.yaml"
        assert os.path.isfile(path), f"Source file {path} should still exist after task completion."

    def test_prod_app_yaml_still_exists(self):
        """The prod/app.yaml file should still exist."""
        path = "/home/user/k8s-manifests/prod/app.yaml"
        assert os.path.isfile(path), f"Source file {path} should still exist after task completion."

    def test_prod_database_yaml_still_exists(self):
        """The prod/database.yaml file should still exist."""
        path = "/home/user/k8s-manifests/prod/database.yaml"
        assert os.path.isfile(path), f"Source file {path} should still exist after task completion."
