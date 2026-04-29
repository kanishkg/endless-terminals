# test_initial_state.py
"""
Tests to validate the initial state before the student performs the jq task.
Validates that the metrics file exists, has correct structure, and jq is available.
"""

import json
import os
import subprocess
import pytest


class TestInitialState:
    """Test suite for validating initial OS/filesystem state."""

    METRICS_DIR = "/home/user/metrics"
    TRACES_FILE = "/home/user/metrics/traces.json"
    EXPECTED_ENTRY_COUNT = 200
    EXPECTED_SUM = 4827.6

    def test_metrics_directory_exists(self):
        """Verify /home/user/metrics directory exists."""
        assert os.path.exists(self.METRICS_DIR), (
            f"Directory {self.METRICS_DIR} does not exist. "
            "The metrics directory must be present for this task."
        )

    def test_metrics_directory_is_readable(self):
        """Verify /home/user/metrics directory is readable."""
        assert os.access(self.METRICS_DIR, os.R_OK), (
            f"Directory {self.METRICS_DIR} is not readable. "
            "The agent must be able to read this directory."
        )

    def test_traces_file_exists(self):
        """Verify /home/user/metrics/traces.json exists."""
        assert os.path.exists(self.TRACES_FILE), (
            f"File {self.TRACES_FILE} does not exist. "
            "The traces.json file must be present for this task."
        )

    def test_traces_file_is_regular_file(self):
        """Verify traces.json is a regular file."""
        assert os.path.isfile(self.TRACES_FILE), (
            f"{self.TRACES_FILE} exists but is not a regular file. "
            "It must be a regular JSON file."
        )

    def test_traces_file_is_readable(self):
        """Verify traces.json is readable."""
        assert os.access(self.TRACES_FILE, os.R_OK), (
            f"File {self.TRACES_FILE} is not readable. "
            "The agent must be able to read this file."
        )

    def test_traces_file_is_valid_json(self):
        """Verify traces.json contains valid JSON."""
        try:
            with open(self.TRACES_FILE, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {self.TRACES_FILE} is not valid JSON: {e}. "
                "The file must contain valid JSON data."
            )

    def test_traces_file_is_array(self):
        """Verify traces.json root element is an array."""
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)
        assert isinstance(data, list), (
            f"File {self.TRACES_FILE} root element is not an array. "
            f"Expected list, got {type(data).__name__}."
        )

    def test_traces_file_has_200_entries(self):
        """Verify traces.json has exactly 200 entries."""
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)
        assert len(data) == self.EXPECTED_ENTRY_COUNT, (
            f"File {self.TRACES_FILE} has {len(data)} entries, "
            f"expected exactly {self.EXPECTED_ENTRY_COUNT} entries."
        )

    def test_all_entries_have_service_field(self):
        """Verify all entries have a 'service' string field."""
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)
        for i, entry in enumerate(data):
            assert isinstance(entry, dict), (
                f"Entry {i} is not an object, got {type(entry).__name__}."
            )
            assert "service" in entry, (
                f"Entry {i} is missing 'service' field."
            )
            assert isinstance(entry["service"], str), (
                f"Entry {i} 'service' field is not a string, "
                f"got {type(entry['service']).__name__}."
            )

    def test_all_entries_have_latency_p99_field(self):
        """Verify all entries have a 'latency_p99' numeric field."""
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)
        for i, entry in enumerate(data):
            assert isinstance(entry, dict), (
                f"Entry {i} is not an object, got {type(entry).__name__}."
            )
            assert "latency_p99" in entry, (
                f"Entry {i} is missing 'latency_p99' field."
            )
            assert isinstance(entry["latency_p99"], (int, float)), (
                f"Entry {i} 'latency_p99' field is not numeric, "
                f"got {type(entry['latency_p99']).__name__}."
            )

    def test_latency_p99_sum_is_correct(self):
        """Verify the sum of all latency_p99 values is exactly 4827.6."""
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)
        total = sum(entry["latency_p99"] for entry in data)
        # Use approximate comparison for floating point
        assert abs(total - self.EXPECTED_SUM) < 0.001, (
            f"Sum of latency_p99 values is {total}, "
            f"expected {self.EXPECTED_SUM}."
        )

    def test_jq_is_installed(self):
        """Verify jq is installed and available in PATH."""
        result = subprocess.run(
            ["which", "jq"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq is not installed or not in PATH. "
            "jq must be available for this task."
        )

    def test_jq_version_is_adequate(self):
        """Verify jq version is 1.6 or higher."""
        result = subprocess.run(
            ["jq", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Failed to get jq version. jq must be properly installed."
        )
        version_output = result.stdout.strip()
        # jq outputs version like "jq-1.6" or "jq-1.7"
        try:
            version_str = version_output.replace("jq-", "")
            version_parts = version_str.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            version_ok = (major > 1) or (major == 1 and minor >= 6)
            assert version_ok, (
                f"jq version {version_output} is too old. "
                "jq 1.6+ is required for this task."
            )
        except (ValueError, IndexError):
            # If we can't parse version, just check jq works
            pass

    def test_jq_can_read_traces_file(self):
        """Verify jq can successfully parse the traces.json file."""
        result = subprocess.run(
            ["jq", ".", self.TRACES_FILE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"jq failed to parse {self.TRACES_FILE}: {result.stderr}. "
            "The file must be valid JSON that jq can process."
        )
