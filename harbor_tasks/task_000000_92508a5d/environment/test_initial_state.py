# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the numpy deprecated aliases in the research scripts.
"""

import os
import subprocess
import sys

import pytest


HOME = "/home/user"
RESEARCH_DIR = os.path.join(HOME, "research")
PREP_SCRIPT = os.path.join(RESEARCH_DIR, "prep_data.py")
RAW_DIR = os.path.join(RESEARCH_DIR, "raw")
CSV_FILE = os.path.join(RAW_DIR, "survey_responses.csv")
OUTPUT_DIR = os.path.join(RESEARCH_DIR, "output")
UTILS_DIR = os.path.join(RESEARCH_DIR, "utils")
UTILS_INIT = os.path.join(UTILS_DIR, "__init__.py")
CONVERTERS_FILE = os.path.join(UTILS_DIR, "converters.py")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_research_directory_exists(self):
        assert os.path.isdir(RESEARCH_DIR), f"Research directory {RESEARCH_DIR} does not exist"

    def test_raw_directory_exists(self):
        assert os.path.isdir(RAW_DIR), f"Raw data directory {RAW_DIR} does not exist"

    def test_output_directory_exists(self):
        assert os.path.isdir(OUTPUT_DIR), f"Output directory {OUTPUT_DIR} does not exist"

    def test_utils_directory_exists(self):
        assert os.path.isdir(UTILS_DIR), f"Utils directory {UTILS_DIR} does not exist"

    def test_output_directory_is_empty(self):
        """Output directory should be empty initially."""
        contents = os.listdir(OUTPUT_DIR)
        assert len(contents) == 0, f"Output directory {OUTPUT_DIR} should be empty but contains: {contents}"


class TestRequiredFiles:
    """Test that required files exist."""

    def test_prep_data_script_exists(self):
        assert os.path.isfile(PREP_SCRIPT), f"Prep data script {PREP_SCRIPT} does not exist"

    def test_csv_file_exists(self):
        assert os.path.isfile(CSV_FILE), f"CSV file {CSV_FILE} does not exist"

    def test_utils_init_exists(self):
        assert os.path.isfile(UTILS_INIT), f"Utils __init__.py {UTILS_INIT} does not exist"

    def test_converters_file_exists(self):
        assert os.path.isfile(CONVERTERS_FILE), f"Converters file {CONVERTERS_FILE} does not exist"


class TestCSVFile:
    """Test the CSV file has expected content."""

    def test_csv_has_approximately_500_rows(self):
        """CSV should have ~500 rows of data."""
        with open(CSV_FILE, 'r') as f:
            lines = f.readlines()
        # Account for header row
        data_rows = len(lines) - 1
        assert 450 <= data_rows <= 550, f"CSV should have ~500 rows but has {data_rows} data rows"


class TestScriptContent:
    """Test that scripts contain the expected deprecated numpy aliases."""

    def test_prep_data_imports_numpy(self):
        """prep_data.py should import numpy."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()
        assert 'import numpy' in content or 'from numpy' in content, \
            f"{PREP_SCRIPT} should import numpy"

    def test_prep_data_imports_pandas(self):
        """prep_data.py should import pandas."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()
        assert 'import pandas' in content or 'from pandas' in content, \
            f"{PREP_SCRIPT} should import pandas"

    def test_prep_data_uses_deprecated_np_float(self):
        """prep_data.py should contain np.float (the bug to fix)."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()
        assert 'np.float' in content, \
            f"{PREP_SCRIPT} should contain deprecated np.float alias (this is the bug to fix)"

    def test_converters_uses_deprecated_aliases(self):
        """converters.py should contain deprecated numpy aliases."""
        with open(CONVERTERS_FILE, 'r') as f:
            content = f.read()
        # Check for at least one deprecated alias
        has_deprecated = any(alias in content for alias in ['np.int', 'np.object', 'np.bool'])
        assert has_deprecated, \
            f"{CONVERTERS_FILE} should contain deprecated numpy aliases (np.int, np.object, or np.bool)"


class TestPythonEnvironment:
    """Test the Python environment is set up correctly."""

    def test_python3_available(self):
        """Python 3 should be available."""
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "Python 3 is not available"
        assert 'Python 3' in result.stdout, f"Expected Python 3, got: {result.stdout}"

    def test_pip_available(self):
        """pip should be available."""
        result = subprocess.run(['pip', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "pip is not available"

    def test_numpy_version_is_1_24_or_higher(self):
        """numpy should be version 1.24.0 or higher."""
        result = subprocess.run(['pip', 'show', 'numpy'], capture_output=True, text=True)
        assert result.returncode == 0, "numpy is not installed"

        # Parse version from pip show output
        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        assert version_line, "Could not find numpy version"
        version = version_line[0].split(':')[1].strip()

        # Parse version numbers
        major, minor = map(int, version.split('.')[:2])
        assert (major, minor) >= (1, 24), \
            f"numpy version should be 1.24.0 or higher, but is {version}"

    def test_pandas_installed(self):
        """pandas should be installed."""
        result = subprocess.run(['pip', 'show', 'pandas'], capture_output=True, text=True)
        assert result.returncode == 0, "pandas is not installed"

    def test_pyarrow_installed(self):
        """pyarrow should be installed."""
        result = subprocess.run(['pip', 'show', 'pyarrow'], capture_output=True, text=True)
        assert result.returncode == 0, "pyarrow is not installed"


class TestScriptFailsInitially:
    """Test that the script fails with the expected error before fixes."""

    def test_prep_data_script_fails_with_numpy_error(self):
        """Running prep_data.py should fail with numpy attribute error."""
        result = subprocess.run(
            ['python3', PREP_SCRIPT],
            capture_output=True,
            text=True,
            cwd=RESEARCH_DIR
        )
        assert result.returncode != 0, \
            "prep_data.py should fail initially (before fixes are applied)"

        # Check for the expected error message
        error_output = result.stderr
        assert 'AttributeError' in error_output or 'attribute' in error_output.lower(), \
            f"Expected AttributeError about numpy, got: {error_output}"
        assert 'numpy' in error_output.lower(), \
            f"Error should mention numpy, got: {error_output}"
