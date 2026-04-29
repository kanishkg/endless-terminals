# test_final_state.py
"""
Tests to validate the final state after the student completes the jq task.
Validates that the correct jq command can extract and sum latency_p99 values.
"""

import json
import os
import subprocess
import pytest


class TestFinalState:
    """Test suite for validating final state after task completion."""

    METRICS_DIR = "/home/user/metrics"
    TRACES_FILE = "/home/user/metrics/traces.json"
    EXPECTED_SUM = 4827.6
    TOLERANCE = 0.001

    def test_traces_file_unchanged(self):
        """Verify /home/user/metrics/traces.json still exists and is valid."""
        assert os.path.exists(self.TRACES_FILE), (
            f"File {self.TRACES_FILE} no longer exists. "
            "The traces.json file should not be deleted or moved."
        )
        try:
            with open(self.TRACES_FILE, 'r') as f:
                data = json.load(f)
            assert isinstance(data, list), (
                f"File {self.TRACES_FILE} structure changed - root is no longer an array."
            )
            assert len(data) == 200, (
                f"File {self.TRACES_FILE} entry count changed from 200 to {len(data)}."
            )
        except json.JSONDecodeError as e:
            pytest.fail(f"File {self.TRACES_FILE} is no longer valid JSON: {e}")

    def test_jq_sum_command_produces_correct_output(self):
        """
        Verify that a jq command can correctly sum all latency_p99 values.
        This tests the expected solution approach.
        """
        # The canonical jq command to sum latency_p99 values
        result = subprocess.run(
            ["jq", "[.[].latency_p99] | add", self.TRACES_FILE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"jq command failed with error: {result.stderr}"
        )

        output = result.stdout.strip()
        try:
            computed_sum = float(output)
        except ValueError:
            pytest.fail(
                f"jq output '{output}' is not a valid number. "
                f"Expected a numeric sum around {self.EXPECTED_SUM}."
            )

        assert abs(computed_sum - self.EXPECTED_SUM) < self.TOLERANCE, (
            f"jq sum result {computed_sum} does not match expected {self.EXPECTED_SUM}. "
            f"Difference: {abs(computed_sum - self.EXPECTED_SUM)}"
        )

    def test_alternative_jq_map_add_produces_correct_output(self):
        """
        Verify alternative jq syntax also works (map + add).
        """
        result = subprocess.run(
            ["jq", "map(.latency_p99) | add", self.TRACES_FILE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Alternative jq command failed with error: {result.stderr}"
        )

        output = result.stdout.strip()
        try:
            computed_sum = float(output)
        except ValueError:
            pytest.fail(
                f"jq output '{output}' is not a valid number."
            )

        assert abs(computed_sum - self.EXPECTED_SUM) < self.TOLERANCE, (
            f"Alternative jq sum result {computed_sum} does not match expected {self.EXPECTED_SUM}."
        )

    def test_data_integrity_latency_sum_matches(self):
        """
        Verify the JSON file data integrity - sum of latency_p99 should be 4827.6.
        This ensures the file wasn't corrupted.
        """
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)

        total = sum(entry.get("latency_p99", 0) for entry in data)

        assert abs(total - self.EXPECTED_SUM) < self.TOLERANCE, (
            f"Sum of latency_p99 values in file is {total}, "
            f"expected {self.EXPECTED_SUM}. File may have been modified."
        )

    def test_all_entries_still_have_latency_p99(self):
        """
        Verify all 200 entries still have the latency_p99 field.
        """
        with open(self.TRACES_FILE, 'r') as f:
            data = json.load(f)

        missing_count = sum(1 for entry in data if "latency_p99" not in entry)

        assert missing_count == 0, (
            f"{missing_count} entries are missing 'latency_p99' field. "
            "The file structure should remain unchanged."
        )

    def test_jq_still_available(self):
        """
        Verify jq is still installed and functional.
        """
        result = subprocess.run(
            ["jq", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq is no longer available. It should remain installed."
        )

    def test_reduce_syntax_also_works(self):
        """
        Verify jq reduce syntax produces correct result (another valid approach).
        """
        result = subprocess.run(
            ["jq", "reduce .[].latency_p99 as $x (0; . + $x)", self.TRACES_FILE],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"jq reduce command failed with error: {result.stderr}"
        )

        output = result.stdout.strip()
        try:
            computed_sum = float(output)
        except ValueError:
            pytest.fail(
                f"jq reduce output '{output}' is not a valid number."
            )

        assert abs(computed_sum - self.EXPECTED_SUM) < self.TOLERANCE, (
            f"jq reduce result {computed_sum} does not match expected {self.EXPECTED_SUM}."
        )
