# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the task of extracting server names and memory values from JSON to CSV.
"""

import csv
import json
import os
import pytest


class TestFinalState:
    """Test suite to verify the final state after task execution."""

    def test_mem_csv_exists(self):
        """Verify /home/user/reports/mem.csv exists."""
        mem_csv = "/home/user/reports/mem.csv"
        assert os.path.isfile(mem_csv), (
            f"File {mem_csv} does not exist. "
            "The output CSV file must be created by the task."
        )

    def test_mem_csv_is_readable(self):
        """Verify /home/user/reports/mem.csv is readable."""
        mem_csv = "/home/user/reports/mem.csv"
        assert os.access(mem_csv, os.R_OK), (
            f"File {mem_csv} is not readable."
        )

    def test_mem_csv_is_valid_csv(self):
        """Verify /home/user/reports/mem.csv is valid CSV."""
        mem_csv = "/home/user/reports/mem.csv"
        try:
            with open(mem_csv, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except csv.Error as e:
            pytest.fail(
                f"File {mem_csv} is not valid CSV: {e}"
            )
        except Exception as e:
            pytest.fail(
                f"Error reading {mem_csv}: {e}"
            )

    def test_mem_csv_has_header_row(self):
        """Verify mem.csv has a header row with hostname and memory columns."""
        mem_csv = "/home/user/reports/mem.csv"
        with open(mem_csv, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) > 0, (
            f"File {mem_csv} is empty. It should have a header row and data rows."
        )

        header = rows[0]
        assert len(header) == 2, (
            f"Header row should have exactly 2 columns, but found {len(header)}: {header}"
        )

        # Normalize header names for comparison (lowercase, strip whitespace)
        header_lower = [col.strip().lower() for col in header]

        # Check first column is hostname
        assert header_lower[0] == 'hostname', (
            f"First column header should be 'hostname', but found '{header[0]}'"
        )

        # Check second column is memory or memory_gb
        assert header_lower[1] in ('memory', 'memory_gb'), (
            f"Second column header should be 'memory' or 'memory_gb', but found '{header[1]}'"
        )

    def test_mem_csv_has_exactly_six_lines(self):
        """Verify mem.csv has exactly 6 lines (1 header + 5 data rows)."""
        mem_csv = "/home/user/reports/mem.csv"
        with open(mem_csv, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Filter out any completely empty rows that might exist
        non_empty_rows = [row for row in rows if any(cell.strip() for cell in row)]

        assert len(non_empty_rows) == 6, (
            f"File {mem_csv} should have exactly 6 rows (1 header + 5 data), "
            f"but found {len(non_empty_rows)} non-empty rows."
        )

    def test_mem_csv_contains_all_hostnames(self):
        """Verify mem.csv contains all 5 expected hostnames."""
        mem_csv = "/home/user/reports/mem.csv"
        expected_hostnames = {
            "web-prod-01", "web-prod-02", "db-primary", "db-replica", "cache-01"
        }

        with open(mem_csv, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Skip header, extract hostnames from first column
        data_rows = rows[1:]
        actual_hostnames = {row[0].strip() for row in data_rows if row}

        missing = expected_hostnames - actual_hostnames
        extra = actual_hostnames - expected_hostnames

        assert missing == set(), (
            f"Missing hostnames in {mem_csv}: {missing}"
        )
        assert extra == set(), (
            f"Unexpected hostnames in {mem_csv}: {extra}"
        )

    def test_mem_csv_has_correct_memory_values(self):
        """Verify mem.csv has correct memory values for each hostname."""
        mem_csv = "/home/user/reports/mem.csv"
        expected_memory = {
            "web-prod-01": 32,
            "web-prod-02": 32,
            "db-primary": 128,
            "db-replica": 128,
            "cache-01": 16
        }

        with open(mem_csv, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Skip header
        data_rows = rows[1:]

        for row in data_rows:
            if not row or len(row) < 2:
                continue

            hostname = row[0].strip()
            memory_str = row[1].strip()

            # Parse memory value (could be int or float representation)
            try:
                memory = int(float(memory_str))
            except ValueError:
                pytest.fail(
                    f"Invalid memory value '{memory_str}' for hostname '{hostname}'"
                )

            assert hostname in expected_memory, (
                f"Unexpected hostname '{hostname}' in CSV"
            )
            assert memory == expected_memory[hostname], (
                f"Memory for {hostname} should be {expected_memory[hostname]}, "
                f"but found {memory}"
            )

    def test_mem_csv_data_rows_have_two_columns(self):
        """Verify each data row in mem.csv has exactly 2 columns."""
        mem_csv = "/home/user/reports/mem.csv"

        with open(mem_csv, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)

        # Check each data row (skip header)
        for i, row in enumerate(rows[1:], start=2):
            if not row:
                continue
            assert len(row) == 2, (
                f"Row {i} should have exactly 2 columns, but found {len(row)}: {row}"
            )

    def test_hosts_json_unchanged(self):
        """Verify /home/user/inventory/hosts.json is unchanged."""
        hosts_file = "/home/user/inventory/hosts.json"
        expected_data = [
            {"hostname": "web-prod-01", "cpu_cores": 8, "memory_gb": 32, "datacenter": "us-east"},
            {"hostname": "web-prod-02", "cpu_cores": 8, "memory_gb": 32, "datacenter": "us-east"},
            {"hostname": "db-primary", "cpu_cores": 16, "memory_gb": 128, "datacenter": "us-east"},
            {"hostname": "db-replica", "cpu_cores": 16, "memory_gb": 128, "datacenter": "us-west"},
            {"hostname": "cache-01", "cpu_cores": 4, "memory_gb": 16, "datacenter": "us-west"}
        ]

        assert os.path.isfile(hosts_file), (
            f"File {hosts_file} no longer exists. It should not be modified or deleted."
        )

        with open(hosts_file, 'r') as f:
            actual_data = json.load(f)

        # Compare as sets of tuples for order-independent comparison
        def to_comparable(data):
            return {
                tuple(sorted(entry.items()))
                for entry in data
            }

        expected_set = to_comparable(expected_data)
        actual_set = to_comparable(actual_data)

        assert actual_set == expected_set, (
            f"File {hosts_file} has been modified. "
            "The source JSON file should remain unchanged."
        )

    def test_mem_csv_not_empty(self):
        """Verify mem.csv is not an empty file."""
        mem_csv = "/home/user/reports/mem.csv"
        file_size = os.path.getsize(mem_csv)
        assert file_size > 0, (
            f"File {mem_csv} is empty (0 bytes). It should contain CSV data."
        )

    def test_mem_csv_complete_data_integrity(self):
        """Comprehensive test to verify all data is correctly extracted."""
        mem_csv = "/home/user/reports/mem.csv"
        expected_data = {
            "web-prod-01": 32,
            "web-prod-02": 32,
            "db-primary": 128,
            "db-replica": 128,
            "cache-01": 16
        }

        with open(mem_csv, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 5, (
            f"Expected 5 data rows, found {len(rows)}"
        )

        # Get the fieldnames (header columns)
        fieldnames = reader.fieldnames
        assert fieldnames is not None and len(fieldnames) == 2, (
            f"Expected 2 columns in header, found: {fieldnames}"
        )

        # Determine which column name is used for memory
        hostname_col = fieldnames[0]
        memory_col = fieldnames[1]

        found_data = {}
        for row in rows:
            hostname = row[hostname_col].strip()
            memory_str = row[memory_col].strip()
            try:
                memory = int(float(memory_str))
            except ValueError:
                pytest.fail(f"Cannot parse memory value '{memory_str}' for {hostname}")
            found_data[hostname] = memory

        assert found_data == expected_data, (
            f"CSV data does not match expected. "
            f"Expected: {expected_data}, Found: {found_data}"
        )
