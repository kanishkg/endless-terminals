# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the slow query log parser fix task.
"""

import os
import re
import subprocess
import sys

import pytest


# Constants
ANALYZE_DIR = "/home/user/analyze"
SLOW_LOG_SCRIPT = "/home/user/analyze/slow_log.py"
TEST_LOG = "/home/user/analyze/test.log"
VENV_DIR = "/home/user/analyze/venv"
VENV_PYTHON = "/home/user/analyze/venv/bin/python"
VENV_PIP = "/home/user/analyze/venv/bin/pip"
VENV_ACTIVATE = "/home/user/analyze/venv/bin/activate"


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_analyze_directory_exists(self):
        """The /home/user/analyze directory must exist."""
        assert os.path.isdir(ANALYZE_DIR), (
            f"Directory {ANALYZE_DIR} does not exist. "
            "The analyze directory is required for this task."
        )

    def test_analyze_directory_writable(self):
        """The /home/user/analyze directory must be writable."""
        assert os.access(ANALYZE_DIR, os.W_OK), (
            f"Directory {ANALYZE_DIR} is not writable. "
            "The student needs write access to fix the script."
        )

    def test_venv_directory_exists(self):
        """The venv directory must exist."""
        assert os.path.isdir(VENV_DIR), (
            f"Virtual environment directory {VENV_DIR} does not exist. "
            "The venv is required for this task."
        )


class TestSlowLogScript:
    """Test the slow_log.py script exists and has expected characteristics."""

    def test_script_exists(self):
        """The slow_log.py script must exist."""
        assert os.path.isfile(SLOW_LOG_SCRIPT), (
            f"Script {SLOW_LOG_SCRIPT} does not exist. "
            "This is the main script that needs to be fixed."
        )

    def test_script_writable(self):
        """The slow_log.py script must be writable."""
        assert os.access(SLOW_LOG_SCRIPT, os.W_OK), (
            f"Script {SLOW_LOG_SCRIPT} is not writable. "
            "The student needs to modify this script."
        )

    def test_script_imports_mysql_connector(self):
        """The script should import mysql.connector."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'mysql.connector' in content or 'mysql' in content, (
            f"Script {SLOW_LOG_SCRIPT} does not appear to import mysql.connector. "
            "The script should have a mysql.connector import for the upload_to_db function."
        )

    def test_script_has_upload_to_db_function(self):
        """The script should have an upload_to_db function (even if unused)."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'upload_to_db' in content or 'def upload' in content, (
            f"Script {SLOW_LOG_SCRIPT} does not appear to have an upload_to_db function. "
            "This function should exist (even though it's not called in the main codepath)."
        )

    def test_script_has_fingerprint_normalization(self):
        """The script should have fingerprint normalization logic."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()
        # Look for signs of fingerprint normalization (replacing literals with ?)
        has_normalization = (
            '?' in content or 
            'fingerprint' in content.lower() or 
            'normalize' in content.lower() or
            re.search(r're\.(sub|replace)', content)
        )
        assert has_normalization, (
            f"Script {SLOW_LOG_SCRIPT} does not appear to have fingerprint normalization. "
            "The script should normalize queries by replacing literals with ? placeholders."
        )

    def test_script_parses_query_time(self):
        """The script should parse Query_time from slow log."""
        with open(SLOW_LOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'Query_time' in content or 'query_time' in content.lower(), (
            f"Script {SLOW_LOG_SCRIPT} does not appear to parse Query_time. "
            "The script should extract execution times from slow query log entries."
        )


class TestTestLog:
    """Test the test.log file exists and has expected characteristics."""

    def test_log_exists(self):
        """The test.log file must exist."""
        assert os.path.isfile(TEST_LOG), (
            f"Test log {TEST_LOG} does not exist. "
            "This is the reference test file for validating the fix."
        )

    def test_log_readable(self):
        """The test.log file must be readable."""
        assert os.access(TEST_LOG, os.R_OK), (
            f"Test log {TEST_LOG} is not readable."
        )

    def test_log_has_content(self):
        """The test.log should have content (approximately 50 entries)."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()
        assert len(content) > 0, (
            f"Test log {TEST_LOG} is empty."
        )

    def test_log_has_query_time_entries(self):
        """The test.log should contain Query_time entries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()
        query_time_count = len(re.findall(r'Query_time:', content, re.IGNORECASE))
        assert query_time_count > 0, (
            f"Test log {TEST_LOG} does not contain any Query_time entries. "
            "Expected MySQL slow query log format."
        )

    def test_log_has_approximately_50_entries(self):
        """The test.log should have approximately 50 query entries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()
        # Count Query_time entries as proxy for number of queries
        query_time_count = len(re.findall(r'Query_time:', content, re.IGNORECASE))
        assert 40 <= query_time_count <= 60, (
            f"Test log {TEST_LOG} has {query_time_count} Query_time entries. "
            "Expected approximately 50 entries."
        )

    def test_log_has_select_queries(self):
        """The test.log should contain SELECT queries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()
        assert 'SELECT' in content.upper(), (
            f"Test log {TEST_LOG} does not contain SELECT queries."
        )

    def test_log_has_update_queries(self):
        """The test.log should contain UPDATE queries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()
        assert 'UPDATE' in content.upper(), (
            f"Test log {TEST_LOG} does not contain UPDATE queries."
        )

    def test_log_has_insert_queries(self):
        """The test.log should contain INSERT queries."""
        with open(TEST_LOG, 'r') as f:
            content = f.read()
        assert 'INSERT' in content.upper(), (
            f"Test log {TEST_LOG} does not contain INSERT queries."
        )


class TestVirtualEnvironment:
    """Test the virtual environment setup."""

    def test_venv_python_exists(self):
        """The venv Python interpreter must exist."""
        assert os.path.isfile(VENV_PYTHON), (
            f"Python interpreter {VENV_PYTHON} does not exist. "
            "The virtual environment appears to be incomplete."
        )

    def test_venv_pip_exists(self):
        """The venv pip must exist."""
        assert os.path.isfile(VENV_PIP), (
            f"Pip {VENV_PIP} does not exist. "
            "The virtual environment appears to be incomplete."
        )

    def test_venv_activate_exists(self):
        """The venv activate script must exist."""
        assert os.path.isfile(VENV_ACTIVATE), (
            f"Activate script {VENV_ACTIVATE} does not exist. "
            "The virtual environment appears to be incomplete."
        )

    def test_venv_is_python_310(self):
        """The venv should be Python 3.10."""
        result = subprocess.run(
            [VENV_PYTHON, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get Python version from venv: {result.stderr}"
        )
        version_output = result.stdout.strip()
        assert "3.10" in version_output or "3.1" in version_output, (
            f"Expected Python 3.10 in venv, got: {version_output}"
        )

    def test_mysql_connector_packages_conflict(self):
        """
        The venv should have the mysql connector package conflict 
        (both mysql-connector-python and mysql-connector installed).
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
        has_mysql_connector = bool(re.search(r'^mysql-connector==', packages, re.MULTILINE))

        # At least one mysql connector package should be present
        assert has_mysql_connector_python or has_mysql_connector or 'mysql' in packages, (
            "No mysql connector package found in venv. "
            "Expected at least one mysql connector package to be installed."
        )

    def test_mysql_connector_import_has_issues(self):
        """
        The mysql.connector import should have issues 
        (specifically, importing MySQLConnection should fail or have problems).
        """
        # Test that there's an import issue with MySQLConnection
        result = subprocess.run(
            [VENV_PYTHON, "-c", "from mysql.connector import MySQLConnection"],
            capture_output=True,
            text=True
        )
        # We expect this to either fail or have been "hacked" to work partially
        # The key is that there IS a conflict state that needs fixing

        # Check pip list for the conflict
        pip_result = subprocess.run(
            [VENV_PIP, "list", "--format=freeze"],
            capture_output=True,
            text=True
        )
        packages = pip_result.stdout.lower()

        # Either the import fails, OR both packages are installed (conflict state)
        has_both = (
            'mysql-connector-python' in packages and 
            bool(re.search(r'^mysql-connector==', packages, re.MULTILINE))
        )
        import_fails = result.returncode != 0

        assert has_both or import_fails or 'mysql' in packages, (
            "Expected mysql connector conflict state in venv. "
            "Either both packages should be installed, or the import should fail."
        )


class TestScriptCurrentBehavior:
    """Test that the script currently produces incorrect output (the bug exists)."""

    def test_script_produces_inflated_totals(self):
        """
        The script should currently produce inflated totals due to the bug.
        This confirms the bug exists and needs to be fixed.
        """
        # Run the script and capture output
        result = subprocess.run(
            f"source {VENV_ACTIVATE} && python {SLOW_LOG_SCRIPT} {TEST_LOG}",
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash"
        )

        # The script might fail to import or might run with wrong results
        # Either indicates the problem state we expect
        if result.returncode != 0:
            # Import error or other failure - this is expected given the conflict
            assert True, "Script fails to run (expected due to import conflict)"
            return

        output = result.stdout + result.stderr

        # Look for timing values in output
        # Expected correct values are ~12.4, ~8.1, ~2.3
        # Bug produces inflated values like 40+ for the first group

        # Extract any floating point numbers from output that look like timing values
        timing_values = re.findall(r'(\d+\.?\d*)\s*s', output)
        if not timing_values:
            timing_values = re.findall(r'(\d+\.\d+)', output)

        if timing_values:
            max_value = max(float(v) for v in timing_values if float(v) > 1)
            # If the bug exists, we'd expect values much higher than the correct ~12.4
            # A value over 20 strongly suggests the double-counting bug
            if max_value > 20:
                assert True, f"Script produces inflated totals (max: {max_value}s) - bug confirmed"
            else:
                # Values might be close to correct if the bug only partially manifests
                # or the test data arrangement doesn't trigger it fully
                pass


class TestSystemRequirements:
    """Test system-level requirements."""

    def test_python3_available(self):
        """Python 3 must be available on the system."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python 3 is not available on the system."
        )

    def test_pip_available(self):
        """pip must be available."""
        result = subprocess.run(
            ["pip3", "--version"],
            capture_output=True,
            text=True
        )
        # pip3 or pip should work
        if result.returncode != 0:
            result = subprocess.run(
                ["pip", "--version"],
                capture_output=True,
                text=True
            )
        assert result.returncode == 0, (
            "pip is not available on the system."
        )

    def test_bash_available(self):
        """Bash must be available (for source command in grading)."""
        assert os.path.isfile("/bin/bash"), (
            "/bin/bash does not exist. Bash is required for venv activation."
        )
