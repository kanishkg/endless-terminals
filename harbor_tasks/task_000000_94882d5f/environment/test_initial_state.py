# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of extracting server names and memory values from JSON to CSV.
"""

import json
import os
import subprocess
import pytest


class TestInitialState:
    """Test suite to verify the initial state before task execution."""

    def test_inventory_directory_exists(self):
        """Verify /home/user/inventory directory exists."""
        inventory_dir = "/home/user/inventory"
        assert os.path.isdir(inventory_dir), (
            f"Directory {inventory_dir} does not exist. "
            "The inventory directory must exist before the task can be performed."
        )

    def test_hosts_json_exists(self):
        """Verify /home/user/inventory/hosts.json file exists."""
        hosts_file = "/home/user/inventory/hosts.json"
        assert os.path.isfile(hosts_file), (
            f"File {hosts_file} does not exist. "
            "The hosts.json file must exist as the source data for the task."
        )

    def test_hosts_json_is_readable(self):
        """Verify /home/user/inventory/hosts.json is readable."""
        hosts_file = "/home/user/inventory/hosts.json"
        assert os.access(hosts_file, os.R_OK), (
            f"File {hosts_file} is not readable. "
            "The hosts.json file must be readable to extract data."
        )

    def test_hosts_json_contains_valid_json(self):
        """Verify /home/user/inventory/hosts.json contains valid JSON."""
        hosts_file = "/home/user/inventory/hosts.json"
        try:
            with open(hosts_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {hosts_file} does not contain valid JSON: {e}"
            )
        except Exception as e:
            pytest.fail(
                f"Error reading {hosts_file}: {e}"
            )

    def test_hosts_json_is_a_list(self):
        """Verify hosts.json contains a JSON array (list)."""
        hosts_file = "/home/user/inventory/hosts.json"
        with open(hosts_file, 'r') as f:
            data = json.load(f)
        assert isinstance(data, list), (
            f"File {hosts_file} should contain a JSON array, "
            f"but found type {type(data).__name__}."
        )

    def test_hosts_json_has_five_entries(self):
        """Verify hosts.json contains exactly 5 host entries."""
        hosts_file = "/home/user/inventory/hosts.json"
        with open(hosts_file, 'r') as f:
            data = json.load(f)
        assert len(data) == 5, (
            f"File {hosts_file} should contain exactly 5 host entries, "
            f"but found {len(data)}."
        )

    def test_hosts_json_entries_have_required_fields(self):
        """Verify each entry in hosts.json has hostname and memory_gb fields."""
        hosts_file = "/home/user/inventory/hosts.json"
        with open(hosts_file, 'r') as f:
            data = json.load(f)

        for i, entry in enumerate(data):
            assert 'hostname' in entry, (
                f"Entry {i} in {hosts_file} is missing 'hostname' field."
            )
            assert 'memory_gb' in entry, (
                f"Entry {i} in {hosts_file} is missing 'memory_gb' field."
            )

    def test_hosts_json_has_expected_hostnames(self):
        """Verify hosts.json contains the expected hostnames."""
        hosts_file = "/home/user/inventory/hosts.json"
        expected_hostnames = {
            "web-prod-01", "web-prod-02", "db-primary", "db-replica", "cache-01"
        }

        with open(hosts_file, 'r') as f:
            data = json.load(f)

        actual_hostnames = {entry['hostname'] for entry in data}
        assert actual_hostnames == expected_hostnames, (
            f"Hostnames in {hosts_file} do not match expected. "
            f"Expected: {expected_hostnames}, Found: {actual_hostnames}"
        )

    def test_hosts_json_has_expected_memory_values(self):
        """Verify hosts.json contains the expected memory values for each host."""
        hosts_file = "/home/user/inventory/hosts.json"
        expected_memory = {
            "web-prod-01": 32,
            "web-prod-02": 32,
            "db-primary": 128,
            "db-replica": 128,
            "cache-01": 16
        }

        with open(hosts_file, 'r') as f:
            data = json.load(f)

        for entry in data:
            hostname = entry['hostname']
            memory = entry['memory_gb']
            assert hostname in expected_memory, (
                f"Unexpected hostname '{hostname}' in {hosts_file}."
            )
            assert memory == expected_memory[hostname], (
                f"Memory for {hostname} should be {expected_memory[hostname]}, "
                f"but found {memory}."
            )

    def test_reports_directory_exists(self):
        """Verify /home/user/reports directory exists."""
        reports_dir = "/home/user/reports"
        assert os.path.isdir(reports_dir), (
            f"Directory {reports_dir} does not exist. "
            "The reports directory must exist for the output CSV."
        )

    def test_reports_directory_is_writable(self):
        """Verify /home/user/reports directory is writable."""
        reports_dir = "/home/user/reports"
        assert os.access(reports_dir, os.W_OK), (
            f"Directory {reports_dir} is not writable. "
            "The reports directory must be writable to create the output CSV."
        )

    def test_mem_csv_does_not_exist(self):
        """Verify /home/user/reports/mem.csv does not exist yet."""
        mem_csv = "/home/user/reports/mem.csv"
        assert not os.path.exists(mem_csv), (
            f"File {mem_csv} already exists. "
            "The output file should not exist before the task is performed."
        )

    def test_python3_available(self):
        """Verify python3 is available."""
        result = subprocess.run(
            ['which', 'python3'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "python3 is not available in PATH. "
            "Python 3 is required for this task."
        )

    def test_python3_json_module_available(self):
        """Verify python3 json module is available."""
        result = subprocess.run(
            ['python3', '-c', 'import json'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python json module is not available. "
            f"Error: {result.stderr}"
        )

    def test_python3_csv_module_available(self):
        """Verify python3 csv module is available."""
        result = subprocess.run(
            ['python3', '-c', 'import csv'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python csv module is not available. "
            f"Error: {result.stderr}"
        )

    def test_jq_available(self):
        """Verify jq is installed and available."""
        result = subprocess.run(
            ['which', 'jq'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq is not available in PATH. "
            "jq should be installed as an alternative tool for JSON processing."
        )

    def test_jq_works(self):
        """Verify jq can parse the hosts.json file."""
        hosts_file = "/home/user/inventory/hosts.json"
        result = subprocess.run(
            ['jq', '.', hosts_file],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"jq failed to parse {hosts_file}. "
            f"Error: {result.stderr}"
        )
