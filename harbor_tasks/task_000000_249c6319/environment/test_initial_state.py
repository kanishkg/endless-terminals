# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the ETL bug fix task.
"""

import pytest
import os
import json
import subprocess
import re


# Base paths
ETL_DIR = "/home/user/etl"
TRANSFORM_SCRIPT = os.path.join(ETL_DIR, "transform.py")
INPUT_JSON = os.path.join(ETL_DIR, "input/transactions.json")
OUTPUT_DIR = os.path.join(ETL_DIR, "output")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "transactions.csv")
LIB_DIR = os.path.join(ETL_DIR, "lib")
PARSERS_PY = os.path.join(LIB_DIR, "parsers.py")
LOGS_DIR = os.path.join(ETL_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "transform.log")
GIT_DIR = os.path.join(ETL_DIR, ".git")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_etl_directory_exists(self):
        assert os.path.isdir(ETL_DIR), f"ETL directory {ETL_DIR} does not exist"

    def test_input_directory_exists(self):
        input_dir = os.path.join(ETL_DIR, "input")
        assert os.path.isdir(input_dir), f"Input directory {input_dir} does not exist"

    def test_output_directory_exists(self):
        assert os.path.isdir(OUTPUT_DIR), f"Output directory {OUTPUT_DIR} does not exist"

    def test_lib_directory_exists(self):
        assert os.path.isdir(LIB_DIR), f"Lib directory {LIB_DIR} does not exist"

    def test_logs_directory_exists(self):
        assert os.path.isdir(LOGS_DIR), f"Logs directory {LOGS_DIR} does not exist"

    def test_git_directory_exists(self):
        assert os.path.isdir(GIT_DIR), f"Git directory {GIT_DIR} does not exist - repo should be version controlled"


class TestRequiredFiles:
    """Test that required files exist."""

    def test_transform_script_exists(self):
        assert os.path.isfile(TRANSFORM_SCRIPT), f"Transform script {TRANSFORM_SCRIPT} does not exist"

    def test_input_json_exists(self):
        assert os.path.isfile(INPUT_JSON), f"Input JSON file {INPUT_JSON} does not exist"

    def test_parsers_module_exists(self):
        assert os.path.isfile(PARSERS_PY), f"Parsers module {PARSERS_PY} does not exist"

    def test_log_file_exists(self):
        assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} does not exist"

    def test_stale_csv_exists(self):
        assert os.path.isfile(OUTPUT_CSV), f"Stale CSV file {OUTPUT_CSV} does not exist (should have previous run output)"


class TestTransformScript:
    """Test properties of the transform script."""

    def test_transform_script_is_readable(self):
        assert os.access(TRANSFORM_SCRIPT, os.R_OK), f"Transform script {TRANSFORM_SCRIPT} is not readable"

    def test_transform_script_is_python(self):
        with open(TRANSFORM_SCRIPT, 'r') as f:
            content = f.read()
        # Should be valid Python - check for common Python patterns
        assert 'import' in content or 'def ' in content or 'from ' in content, \
            f"Transform script {TRANSFORM_SCRIPT} does not appear to be a Python file"

    def test_transform_script_imports_parsers(self):
        with open(TRANSFORM_SCRIPT, 'r') as f:
            content = f.read()
        # Should import from lib/parsers
        assert 'parsers' in content or 'parse_amount' in content, \
            f"Transform script should import from parsers module"

    def test_transform_script_executable_with_python3(self):
        result = subprocess.run(
            ['python3', '-m', 'py_compile', TRANSFORM_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Transform script has syntax errors: {result.stderr}"


class TestInputJson:
    """Test properties of the input JSON file."""

    def test_input_json_is_valid_json(self):
        with open(INPUT_JSON, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"Input JSON file is not valid JSON: {e}")

    def test_input_json_is_array(self):
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)
        assert isinstance(data, list), "Input JSON should contain an array of transactions"

    def test_input_json_has_247_transactions(self):
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)
        assert len(data) == 247, f"Input JSON should have 247 transactions, found {len(data)}"

    def test_transactions_have_required_fields(self):
        required_fields = {'id', 'date', 'amount', 'currency', 'department', 'description'}
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)

        for i, transaction in enumerate(data):
            missing = required_fields - set(transaction.keys())
            assert not missing, f"Transaction {i} missing fields: {missing}"

    def test_transactions_have_usd_and_eur_currencies(self):
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)

        currencies = set(t['currency'] for t in data)
        assert 'USD' in currencies, "Input should contain USD transactions"
        assert 'EUR' in currencies, "Input should contain EUR transactions"

    def test_amount_format_includes_currency_symbols(self):
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)

        usd_amounts = [t['amount'] for t in data if t['currency'] == 'USD']
        eur_amounts = [t['amount'] for t in data if t['currency'] == 'EUR']

        # Check USD amounts have $ symbol
        assert any('$' in a for a in usd_amounts), "USD amounts should contain $ symbol"
        # Check EUR amounts have € symbol
        assert any('€' in a for a in eur_amounts), "EUR amounts should contain € symbol"

    def test_eur_transaction_count(self):
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)

        eur_count = sum(1 for t in data if t['currency'] == 'EUR')
        assert eur_count == 41, f"Should have 41 EUR transactions, found {eur_count}"


class TestParsersModule:
    """Test properties of the parsers module."""

    def test_parsers_has_parse_amount_function(self):
        with open(PARSERS_PY, 'r') as f:
            content = f.read()
        assert 'def parse_amount' in content, "parsers.py should have a parse_amount function"

    def test_parsers_uses_regex_for_dollar_only(self):
        """Verify the bug exists - regex only handles $ not €"""
        with open(PARSERS_PY, 'r') as f:
            content = f.read()

        # Look for the buggy regex pattern that only handles $
        # Should find something like r'[\$,]' or r'\$' without €
        has_dollar_regex = bool(re.search(r"r['\"].*\\\$.*['\"]", content))
        has_euro_in_regex = bool(re.search(r"r['\"].*€.*['\"]", content))

        assert has_dollar_regex, "parsers.py should have a regex handling $ symbol"
        assert not has_euro_in_regex, "parsers.py should NOT handle € symbol (this is the bug)"


class TestLogFile:
    """Test properties of the log file."""

    def test_log_file_contains_warnings(self):
        with open(LOG_FILE, 'r') as f:
            content = f.read()
        assert 'WARN' in content or 'warn' in content.lower(), \
            "Log file should contain warning messages"

    def test_log_file_shows_euro_parsing_errors(self):
        with open(LOG_FILE, 'r') as f:
            content = f.read()
        assert '€' in content, \
            "Log file should show errors related to € symbol parsing"

    def test_log_file_has_41_skipped_rows(self):
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()

        skip_lines = [l for l in lines if 'skip' in l.lower()]
        assert len(skip_lines) == 41, \
            f"Log file should have 41 skipped row warnings, found {len(skip_lines)}"


class TestStaleCSV:
    """Test properties of the stale CSV output."""

    def test_stale_csv_has_header(self):
        with open(OUTPUT_CSV, 'r') as f:
            header = f.readline().strip()

        expected_columns = ['id', 'date', 'amount', 'currency', 'department', 'description']
        for col in expected_columns:
            assert col in header.lower(), f"CSV header should contain '{col}' column"

    def test_stale_csv_missing_rows(self):
        """Verify the CSV is missing EUR transactions (the bug symptom)"""
        with open(OUTPUT_CSV, 'r') as f:
            lines = f.readlines()

        # Should have header + 206 data rows (missing 41 EUR transactions)
        # Actually 205 data rows + 1 header = 206 lines
        data_rows = len(lines) - 1  # subtract header
        assert data_rows < 247, \
            f"Stale CSV should be missing rows (has {data_rows}, should have fewer than 247)"
        assert data_rows == 206, \
            f"Stale CSV should have exactly 206 data rows (247 - 41 EUR), found {data_rows}"


class TestGitRepository:
    """Test git repository state."""

    def test_git_is_installed(self):
        result = subprocess.run(['which', 'git'], capture_output=True, text=True)
        assert result.returncode == 0, "git should be installed"

    def test_git_repo_has_commits(self):
        result = subprocess.run(
            ['git', 'log', '--oneline'],
            cwd=ETL_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Should be able to run git log in ETL directory"

        commits = [l for l in result.stdout.strip().split('\n') if l]
        assert len(commits) >= 4, f"Git repo should have at least 4 commits, found {len(commits)}"


class TestPythonEnvironment:
    """Test Python environment."""

    def test_python3_available(self):
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "python3 should be available"

    def test_python3_version_adequate(self):
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        version_str = result.stdout.strip()
        # Extract version number
        match = re.search(r'(\d+)\.(\d+)', version_str)
        assert match, f"Could not parse Python version from: {version_str}"

        major, minor = int(match.group(1)), int(match.group(2))
        assert major == 3 and minor >= 10, \
            f"Python 3.10+ required, found {major}.{minor}"


class TestWritePermissions:
    """Test that required directories are writable."""

    def test_etl_directory_writable(self):
        assert os.access(ETL_DIR, os.W_OK), f"{ETL_DIR} should be writable"

    def test_output_directory_writable(self):
        assert os.access(OUTPUT_DIR, os.W_OK), f"{OUTPUT_DIR} should be writable"

    def test_lib_directory_writable(self):
        assert os.access(LIB_DIR, os.W_OK), f"{LIB_DIR} should be writable"


class TestScriptRunsWithoutCrash:
    """Test that the script runs (even with the bug)."""

    def test_script_completes_without_error(self):
        """The script should complete without raising an exception (it silently skips bad rows)"""
        result = subprocess.run(
            ['python3', TRANSFORM_SCRIPT],
            cwd=ETL_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Script should complete without error (exit 0), got {result.returncode}. Stderr: {result.stderr}"
