# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the slow query log parser fix task.
"""

import os
import re
import subprocess
import hashlib

import pytest


# Constants
ANALYZE_DIR = "/home/user/analyze"
SLOW_LOG_SCRIPT = "/home/user/analyze/slow_log.py"
TEST_LOG = "/home/user/analyze/test.log"
VENV_DIR = "/home/user/analyze/venv"
VENV_PYTHON = "/home/user/analyze/venv/bin/python"
VENV_PIP = "/home/user/analyze/venv/bin/pip"
VENV_ACTIVATE = "/home/user/analyze/venv/bin/activate"

# Expected timing values with tolerance
EXPECTED_SELECT_TOTAL = 12.437
EXPECTED_UPDATE_TOTAL = 8.092
EXPECTED_INSERT_TOTAL = 2.341
TOLERANCE = 0.02  # ±0.02s tolerance


class TestMySQLConnectorImport:
    """Test that the mysql.connector import works correctly."""

    def test_mysql_connector_basic_import(self):
        """mysql.connector should import without error."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python -c 'import mysql.connector'",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Failed to import mysql.connector. "
            f"stderr: {result.stderr}\n"
            f"The mysql.connector package must be importable."
        )

    def test_mysql_connector_mysqlconnection_import(self):
        """from mysql.connector import MySQLConnection should work."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python -c 'from mysql.connector import MySQLConnection'",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Failed to import MySQLConnection from mysql.connector. "
            f"stderr: {result.stderr}\n"
            f"The import 'from mysql.connector import MySQLConnection' must succeed."
        )

    def test_no_conflicting_mysql_packages(self):
        """
        The venv should NOT have both mysql-connector-python and mysql-connector
        installed simultaneously.
        """
        result = subprocess.run(
            [VENV_PIP, "list", "--format=freeze"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to list pip packages: {result.stderr}"
        )

        packages = result.stdout.lower()
        has_mysql_connector_python = 'mysql-connector-python' in packages
        # Check for standalone mysql-connector (not mysql-connector-python)
        has_legacy_mysql_connector = bool(re.search(r'^mysql-connector==', packages, re.MULTILINE))

        assert not (has_mysql_connector_python and has_legacy_mysql_connector), (
            f"Both mysql-connector-python and mysql-connector are installed. "
            f"Only one should be present to avoid import conflicts.\n"
            f"Installed packages:\n{result.stdout}"
        )


class TestSlowLogScriptExecution:
    """Test that the slow_log.py script runs correctly and produces accurate output."""

    def test_script_exits_zero(self):
        """The script should exit with code 0 when run on test.log."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script exited with code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}\n"
            f"The script must exit 0 when processing {TEST_LOG}."
        )

    def test_script_output_contains_correct_select_total(self):
        """The SELECT fingerprint group should have total ~12.43-12.44s."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script failed to run: {result.stderr}"
        )

        output = result.stdout + result.stderr

        # Extract all floating point numbers from output
        numbers = re.findall(r'(\d+\.\d+)', output)
        float_numbers = [float(n) for n in numbers]

        # Check if any number is close to the expected SELECT total
        found_select = any(
            abs(n - EXPECTED_SELECT_TOTAL) < TOLERANCE
            for n in float_numbers
        )

        assert found_select, (
            f"Could not find SELECT fingerprint total close to {EXPECTED_SELECT_TOTAL}s (±{TOLERANCE}s) in output.\n"
            f"Found numbers: {float_numbers}\n"
            f"Full output:\n{output}"
        )

    def test_script_output_contains_correct_update_total(self):
        """The UPDATE fingerprint group should have total ~8.09-8.10s."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script failed to run: {result.stderr}"
        )

        output = result.stdout + result.stderr

        # Extract all floating point numbers from output
        numbers = re.findall(r'(\d+\.\d+)', output)
        float_numbers = [float(n) for n in numbers]

        # Check if any number is close to the expected UPDATE total
        found_update = any(
            abs(n - EXPECTED_UPDATE_TOTAL) < TOLERANCE
            for n in float_numbers
        )

        assert found_update, (
            f"Could not find UPDATE fingerprint total close to {EXPECTED_UPDATE_TOTAL}s (±{TOLERANCE}s) in output.\n"
            f"Found numbers: {float_numbers}\n"
            f"Full output:\n{output}"
        )

    def test_script_output_contains_correct_insert_total(self):
        """The INSERT fingerprint group should have total ~2.34-2.35s."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script failed to run: {result.stderr}"
        )

        output = result.stdout + result.stderr

        # Extract all floating point numbers from output
        numbers = re.findall(r'(\d+\.\d+)', output)
        float_numbers = [float(n) for n in numbers]

        # Check if any number is close to the expected INSERT total
        found_insert = any(
            abs(n - EXPECTED_INSERT_TOTAL) < TOLERANCE
            for n in float_numbers
        )

        assert found_insert, (
            f"Could not find INSERT fingerprint total close to {EXPECTED_INSERT_TOTAL}s (±{TOLERANCE}s) in output.\n"
            f"Found numbers: {float_numbers}\n"
            f"Full output:\n{output}"
        )

    def test_script_output_has_three_fingerprint_groups(self):
        """The output should show three distinct fingerprint groups."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script failed to run: {result.stderr}"
        )

        output = result.stdout + result.stderr

        # Check for presence of the three query types (normalized with ?)
        has_select = 'SELECT' in output.upper()
        has_update = 'UPDATE' in output.upper()
        has_insert = 'INSERT' in output.upper()

        assert has_select and has_update and has_insert, (
            f"Output should contain all three fingerprint types (SELECT, UPDATE, INSERT).\n"
            f"Found SELECT: {has_select}, UPDATE: {has_update}, INSERT: {has_insert}\n"
            f"Full output:\n{output}"
        )

    def test_script_no_inflated_totals(self):
        """The script should not produce inflated totals (no value > 15s)."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script failed to run: {result.stderr}"
        )

        output = result.stdout + result.stderr

        # Extract all floating point numbers from output
        numbers = re.findall(r'(\d+\.\d+)', output)
        float_numbers = [float(n) for n in numbers]

        # No timing value should exceed 15s (the max correct value is ~12.4s)
        # Values like 40+ would indicate the bug still exists
        inflated_values = [n for n in float_numbers if n > 15]

        assert not inflated_values, (
            f"Found inflated timing values: {inflated_values}\n"
            f"The maximum expected total is ~12.4s. Values over 15s indicate the double-counting bug.\n"
            f"Full output:\n{output}"
        )


class TestAntiShortcutGuards:
    """Tests to ensure the student didn't just hardcode the expected values."""

    def test_script_still_normalizes_fingerprints(self):
        """The script must still normalize fingerprints (replace literals with ?)."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()

        # Look for signs of fingerprint normalization
        has_normalization = (
            re.search(r're\.sub', content) or
            re.search(r'\.replace\s*\(', content) or
            'normalize' in content.lower() or
            'fingerprint' in content.lower()
        )

        # Also check that ? placeholder is used somewhere
        has_placeholder = '?' in content or 'placeholder' in content.lower()

        assert has_normalization or has_placeholder, (
            f"Script does not appear to normalize fingerprints. "
            f"The script must replace literals with ? placeholders."
        )

    def test_script_parses_test_log_dynamically(self):
        """
        Verify the script actually parses the log file rather than
        hardcoding the three expected values.
        """
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()

        # Check that the script reads from a file (sys.argv or argparse)
        reads_file = (
            'sys.argv' in content or
            'argparse' in content or
            'open(' in content or
            'read(' in content or
            'readlines' in content
        )

        assert reads_file, (
            f"Script does not appear to read from a file. "
            f"The script must parse the log file dynamically, not hardcode values."
        )

        # Check that the exact expected values aren't hardcoded
        hardcoded_patterns = [
            r'12\.437',
            r'8\.092',
            r'2\.341',
            r'12\.43[0-9]*\s*[,\)]',
            r'8\.09[0-9]*\s*[,\)]',
            r'2\.34[0-9]*\s*[,\)]',
        ]

        hardcoded_count = sum(
            1 for pattern in hardcoded_patterns
            if re.search(pattern, content)
        )

        # Allow at most 1 match (could be coincidental)
        assert hardcoded_count < 2, (
            f"Script appears to have hardcoded the expected timing values. "
            f"The script must compute totals dynamically from the log file."
        )

    def test_script_groups_by_fingerprint(self):
        """The script must still group queries by fingerprint."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()

        # Look for dictionary/grouping patterns
        has_grouping = (
            'dict' in content or
            '{}' in content or
            'defaultdict' in content or
            'Counter' in content or
            'group' in content.lower() or
            '[fingerprint]' in content or
            '.get(' in content or
            'setdefault' in content
        )

        assert has_grouping, (
            f"Script does not appear to group queries by fingerprint. "
            f"The script must aggregate timing stats per fingerprint group."
        )


class TestTestLogInvariant:
    """Test that the test.log file has not been modified."""

    def test_test_log_exists(self):
        """The test.log file must still exist."""
        assert os.path.isfile(TEST_LOG), (
            f"Test log {TEST_LOG} does not exist. "
            f"This file should not be deleted."
        )

    def test_test_log_has_50_entries(self):
        """The test.log should still have approximately 50 query entries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()

        query_time_count = len(re.findall(r'Query_time:', content, re.IGNORECASE))

        assert 45 <= query_time_count <= 55, (
            f"Test log {TEST_LOG} has {query_time_count} Query_time entries. "
            f"Expected approximately 50 entries. The test log should not be modified."
        )

    def test_test_log_has_all_query_types(self):
        """The test.log should still have SELECT, UPDATE, and INSERT queries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()

        assert 'SELECT' in content.upper(), (
            f"Test log missing SELECT queries. The test log should not be modified."
        )
        assert 'UPDATE' in content.upper(), (
            f"Test log missing UPDATE queries. The test log should not be modified."
        )
        assert 'INSERT' in content.upper(), (
            f"Test log missing INSERT queries. The test log should not be modified."
        )


class TestScriptStructure:
    """Test that the script maintains required structure."""

    def test_script_exists(self):
        """The slow_log.py script must still exist."""
        assert os.path.isfile(SLOW_LOG_SCRIPT), (
            f"Script {SLOW_LOG_SCRIPT} does not exist."
        )

    def test_script_has_mysql_import(self):
        """The script should still import mysql.connector (for upload_to_db)."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()

        assert 'mysql' in content.lower(), (
            f"Script no longer imports mysql.connector. "
            f"The mysql import should be retained (for the upload_to_db function)."
        )

    def test_script_is_valid_python(self):
        """The script should be valid Python syntax."""
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python -m py_compile {SLOW_LOG_SCRIPT}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script has Python syntax errors: {result.stderr}"
        )


class TestIndependentVerification:
    """
    Independently verify the script computes correct totals by comparing
    against values computed from test.log.
    """

    def test_totals_match_independent_calculation(self):
        """
        Run the script and verify all three totals are within tolerance
        of the expected values.
        """
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )
        assert result.returncode == 0, (
            f"Script failed to run: {result.stderr}"
        )

        output = result.stdout + result.stderr

        # Extract all floating point numbers
        numbers = re.findall(r'(\d+\.\d+)', output)
        float_numbers = sorted([float(n) for n in numbers], reverse=True)

        # We need to find all three expected values
        expected_values = [
            (EXPECTED_SELECT_TOTAL, "SELECT"),
            (EXPECTED_UPDATE_TOTAL, "UPDATE"),
            (EXPECTED_INSERT_TOTAL, "INSERT"),
        ]

        found_all = True
        missing = []

        for expected, name in expected_values:
            found = any(abs(n - expected) < TOLERANCE for n in float_numbers)
            if not found:
                found_all = False
                missing.append(f"{name}: expected ~{expected}s")

        assert found_all, (
            f"Not all expected totals found in output.\n"
            f"Missing: {', '.join(missing)}\n"
            f"Found numbers: {float_numbers}\n"
            f"Full output:\n{output}"
        )
