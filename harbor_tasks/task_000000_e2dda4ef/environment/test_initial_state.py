# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the JSON validator performance issue.
"""

import os
import subprocess
import sys
import pytest


# Base paths
VALIDATOR_DIR = "/home/user/validator"
SCHEMAS_DIR = os.path.join(VALIDATOR_DIR, "schemas")
TESTDATA_DIR = os.path.join(VALIDATOR_DIR, "testdata")
CACHE_DIR = os.path.join(VALIDATOR_DIR, "cache")
VALIDATE_PY = os.path.join(VALIDATOR_DIR, "validate.py")


class TestDirectoryStructure:
    """Test that the required directory structure exists."""

    def test_validator_directory_exists(self):
        """The /home/user/validator directory must exist."""
        assert os.path.isdir(VALIDATOR_DIR), (
            f"Directory {VALIDATOR_DIR} does not exist. "
            "The validator project directory is required."
        )

    def test_schemas_directory_exists(self):
        """The schemas/ subdirectory must exist."""
        assert os.path.isdir(SCHEMAS_DIR), (
            f"Directory {SCHEMAS_DIR} does not exist. "
            "The schemas directory containing JSON schema files is required."
        )

    def test_testdata_directory_exists(self):
        """The testdata/ subdirectory must exist."""
        assert os.path.isdir(TESTDATA_DIR), (
            f"Directory {TESTDATA_DIR} does not exist. "
            "The testdata directory containing JSON documents to validate is required."
        )

    def test_cache_directory_exists(self):
        """The cache/ subdirectory must exist (from failed optimization attempt)."""
        assert os.path.isdir(CACHE_DIR), (
            f"Directory {CACHE_DIR} does not exist. "
            "The cache directory should exist from the agent's failed optimization attempt."
        )

    def test_validate_py_exists(self):
        """The validate.py script must exist."""
        assert os.path.isfile(VALIDATE_PY), (
            f"File {VALIDATE_PY} does not exist. "
            "The main validator script is required."
        )


class TestSchemaFiles:
    """Test that schema files are present and properly structured."""

    def test_schemas_directory_has_files(self):
        """The schemas/ directory must contain JSON schema files."""
        if not os.path.isdir(SCHEMAS_DIR):
            pytest.skip("Schemas directory does not exist")

        schema_files = [f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.json')]
        assert len(schema_files) >= 50, (
            f"Expected at least 50 JSON schema files in {SCHEMAS_DIR}, "
            f"found {len(schema_files)}. The benchmark requires 50 schema files."
        )

    def test_schema_files_are_readable(self):
        """Schema files must be readable."""
        if not os.path.isdir(SCHEMAS_DIR):
            pytest.skip("Schemas directory does not exist")

        schema_files = [f for f in os.listdir(SCHEMAS_DIR) if f.endswith('.json')]
        for schema_file in schema_files[:5]:  # Check first 5 as a sample
            path = os.path.join(SCHEMAS_DIR, schema_file)
            assert os.access(path, os.R_OK), (
                f"Schema file {path} is not readable."
            )


class TestTestdataFiles:
    """Test that test data files are present."""

    def test_testdata_directory_has_files(self):
        """The testdata/ directory must contain JSON documents."""
        if not os.path.isdir(TESTDATA_DIR):
            pytest.skip("Testdata directory does not exist")

        json_files = [f for f in os.listdir(TESTDATA_DIR) if f.endswith('.json')]
        assert len(json_files) >= 200, (
            f"Expected at least 200 JSON documents in {TESTDATA_DIR}, "
            f"found {len(json_files)}. The benchmark requires 200 test documents."
        )

    def test_testdata_files_are_readable(self):
        """Test data files must be readable."""
        if not os.path.isdir(TESTDATA_DIR):
            pytest.skip("Testdata directory does not exist")

        json_files = [f for f in os.listdir(TESTDATA_DIR) if f.endswith('.json')]
        for json_file in json_files[:5]:  # Check first 5 as a sample
            path = os.path.join(TESTDATA_DIR, json_file)
            assert os.access(path, os.R_OK), (
                f"Test data file {path} is not readable."
            )


class TestValidateScript:
    """Test that the validate.py script has expected characteristics."""

    def test_validate_py_is_readable(self):
        """validate.py must be readable."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        assert os.access(VALIDATE_PY, os.R_OK), (
            f"File {VALIDATE_PY} is not readable."
        )

    def test_validate_py_contains_benchmark_flag(self):
        """validate.py must support --benchmark flag."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        assert '--benchmark' in content or 'benchmark' in content, (
            f"{VALIDATE_PY} does not appear to contain benchmark functionality. "
            "The script must support the --benchmark flag."
        )

    def test_validate_py_uses_draft7validator(self):
        """validate.py must use Draft7Validator from jsonschema."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        assert 'Draft7Validator' in content, (
            f"{VALIDATE_PY} does not contain 'Draft7Validator'. "
            "The script must use jsonschema's Draft7Validator."
        )

    def test_validate_py_uses_jsonschema(self):
        """validate.py must import jsonschema."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        with open(VALIDATE_PY, 'r') as f:
            content = f.read()

        assert 'jsonschema' in content, (
            f"{VALIDATE_PY} does not import 'jsonschema'. "
            "The script must use the jsonschema library."
        )

    def test_validate_py_is_writable(self):
        """validate.py must be writable for the fix."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        assert os.access(VALIDATE_PY, os.W_OK), (
            f"File {VALIDATE_PY} is not writable. "
            "The script needs to be modified to fix the performance issue."
        )


class TestDependencies:
    """Test that required dependencies are installed."""

    def test_python_version(self):
        """Python 3.11+ must be available."""
        result = subprocess.run(
            [sys.executable, '--version'],
            capture_output=True,
            text=True
        )
        version_str = result.stdout.strip()
        assert 'Python 3' in version_str, (
            f"Python 3 is required. Found: {version_str}"
        )

    def test_jq_installed(self):
        """jq must be installed."""
        result = subprocess.run(
            ['which', 'jq'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq is not installed. The validator requires jq for preprocessing schemas."
        )

    def test_jq_version(self):
        """jq version should be available."""
        result = subprocess.run(
            ['jq', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq --version failed. jq may not be properly installed."
        )
        # Check for jq 1.x
        version_output = result.stdout.strip() or result.stderr.strip()
        assert 'jq-1' in version_output or 'jq 1' in version_output.lower(), (
            f"Expected jq 1.x, got: {version_output}"
        )

    def test_jsonschema_installed(self):
        """jsonschema Python package must be installed."""
        result = subprocess.run(
            [sys.executable, '-c', 'import jsonschema; print(jsonschema.__version__)'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jsonschema Python package is not installed. "
            f"Error: {result.stderr}"
        )

    def test_jsonschema_has_draft7validator(self):
        """jsonschema must have Draft7Validator class."""
        result = subprocess.run(
            [sys.executable, '-c', 'from jsonschema import Draft7Validator; print("OK")'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0 and 'OK' in result.stdout, (
            "jsonschema.Draft7Validator is not available. "
            f"Error: {result.stderr}"
        )


class TestValidatorDirectoryWritable:
    """Test that the validator directory is writable."""

    def test_validator_dir_writable(self):
        """The validator directory must be writable."""
        if not os.path.isdir(VALIDATOR_DIR):
            pytest.skip("Validator directory does not exist")

        assert os.access(VALIDATOR_DIR, os.W_OK), (
            f"Directory {VALIDATOR_DIR} is not writable. "
            "The directory needs to be writable to fix the validator."
        )

    def test_cache_dir_writable(self):
        """The cache directory must be writable."""
        if not os.path.isdir(CACHE_DIR):
            pytest.skip("Cache directory does not exist")

        assert os.access(CACHE_DIR, os.W_OK), (
            f"Directory {CACHE_DIR} is not writable."
        )


class TestBenchmarkCanRun:
    """Test that the benchmark can at least start running."""

    def test_validate_py_syntax_valid(self):
        """validate.py must have valid Python syntax."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        result = subprocess.run(
            [sys.executable, '-m', 'py_compile', VALIDATE_PY],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"validate.py has syntax errors: {result.stderr}"
        )

    def test_validate_py_help_or_benchmark_flag_recognized(self):
        """validate.py should recognize --benchmark or --help flag."""
        if not os.path.isfile(VALIDATE_PY):
            pytest.skip("validate.py does not exist")

        # Try --help first to see if argparse is set up
        result = subprocess.run(
            [sys.executable, VALIDATE_PY, '--help'],
            capture_output=True,
            text=True,
            cwd=VALIDATOR_DIR,
            timeout=10
        )
        # Either help works or benchmark is mentioned somewhere
        help_works = result.returncode == 0
        benchmark_mentioned = 'benchmark' in result.stdout.lower() or 'benchmark' in result.stderr.lower()

        # This is a soft check - we just want to ensure the script is functional
        assert help_works or result.returncode in [0, 1, 2], (
            f"validate.py appears to crash on startup. "
            f"Return code: {result.returncode}, stderr: {result.stderr}"
        )
