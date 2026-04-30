# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the numpy deprecated aliases in the research scripts.
"""

import os
import subprocess
import re

import pytest


HOME = "/home/user"
RESEARCH_DIR = os.path.join(HOME, "research")
PREP_SCRIPT = os.path.join(RESEARCH_DIR, "prep_data.py")
RAW_DIR = os.path.join(RESEARCH_DIR, "raw")
CSV_FILE = os.path.join(RAW_DIR, "survey_responses.csv")
OUTPUT_DIR = os.path.join(RESEARCH_DIR, "output")
OUTPUT_PARQUET = os.path.join(OUTPUT_DIR, "cleaned_survey.parquet")
UTILS_DIR = os.path.join(RESEARCH_DIR, "utils")
CONVERTERS_FILE = os.path.join(UTILS_DIR, "converters.py")


class TestScriptExecutesSuccessfully:
    """Test that the prep_data.py script now runs without errors."""

    def test_prep_data_script_exits_zero(self):
        """Running prep_data.py should exit with code 0."""
        result = subprocess.run(
            ['python3', PREP_SCRIPT],
            capture_output=True,
            text=True,
            cwd=RESEARCH_DIR
        )
        assert result.returncode == 0, \
            f"prep_data.py should exit with code 0 but exited with {result.returncode}.\n" \
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"


class TestOutputParquetFile:
    """Test that the output parquet file exists and is valid."""

    def test_parquet_file_exists(self):
        """The output parquet file should exist."""
        assert os.path.isfile(OUTPUT_PARQUET), \
            f"Output parquet file {OUTPUT_PARQUET} does not exist. " \
            f"The script should generate this file."

    def test_parquet_file_is_readable(self):
        """The parquet file should be readable by pandas."""
        result = subprocess.run(
            ['python3', '-c', 
             f"import pandas as pd; df = pd.read_parquet('{OUTPUT_PARQUET}'); print('OK')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Failed to read parquet file with pandas.\n" \
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        assert 'OK' in result.stdout, \
            f"Parquet file could not be read successfully."

    def test_parquet_has_500_rows(self):
        """The parquet file should contain 500 rows."""
        result = subprocess.run(
            ['python3', '-c',
             f"import pandas as pd; df = pd.read_parquet('{OUTPUT_PARQUET}'); print(len(df))"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Failed to read parquet file.\nSTDERR: {result.stderr}"

        row_count = int(result.stdout.strip())
        assert row_count == 500, \
            f"Parquet file should have 500 rows but has {row_count} rows."

    def test_parquet_has_columns_from_csv(self):
        """The parquet file should contain columns from the original CSV."""
        # First get CSV columns
        csv_cols_result = subprocess.run(
            ['python3', '-c',
             f"import pandas as pd; df = pd.read_csv('{CSV_FILE}'); print(','.join(df.columns.tolist()))"],
            capture_output=True,
            text=True
        )
        assert csv_cols_result.returncode == 0, \
            f"Failed to read CSV columns.\nSTDERR: {csv_cols_result.stderr}"
        csv_columns = set(csv_cols_result.stdout.strip().split(','))

        # Then get parquet columns
        parquet_cols_result = subprocess.run(
            ['python3', '-c',
             f"import pandas as pd; df = pd.read_parquet('{OUTPUT_PARQUET}'); print(','.join(df.columns.tolist()))"],
            capture_output=True,
            text=True
        )
        assert parquet_cols_result.returncode == 0, \
            f"Failed to read parquet columns.\nSTDERR: {parquet_cols_result.stderr}"
        parquet_columns = set(parquet_cols_result.stdout.strip().split(','))

        # Check that parquet contains all CSV columns
        assert csv_columns == parquet_columns, \
            f"Parquet columns should match CSV columns.\n" \
            f"CSV columns: {csv_columns}\nParquet columns: {parquet_columns}"


class TestNumpyVersionNotDowngraded:
    """Test that numpy was not downgraded below 1.24.0."""

    def test_numpy_version_is_1_24_or_higher(self):
        """numpy should still be version 1.24.0 or higher."""
        result = subprocess.run(['pip', 'show', 'numpy'], capture_output=True, text=True)
        assert result.returncode == 0, "numpy is not installed"

        # Parse version from pip show output
        version_line = [line for line in result.stdout.split('\n') if line.startswith('Version:')]
        assert version_line, "Could not find numpy version"
        version = version_line[0].split(':')[1].strip()

        # Parse version numbers
        version_parts = version.split('.')
        major = int(version_parts[0])
        minor = int(version_parts[1])

        assert (major, minor) >= (1, 24), \
            f"numpy version should be 1.24.0 or higher, but is {version}. " \
            f"The task specified not to downgrade numpy."


class TestScriptsStillUseRequiredLibraries:
    """Test that scripts still use numpy/pandas/pyarrow (not rewritten to avoid them)."""

    def test_prep_data_still_imports_numpy(self):
        """prep_data.py should still import numpy."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()
        assert 'import numpy' in content or 'from numpy' in content, \
            f"{PREP_SCRIPT} should still import numpy (script should not be rewritten to avoid numpy)"

    def test_prep_data_still_imports_pandas(self):
        """prep_data.py should still import pandas."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()
        assert 'import pandas' in content or 'from pandas' in content, \
            f"{PREP_SCRIPT} should still import pandas"

    def test_prep_data_still_uses_converters(self):
        """prep_data.py should still import/use converters module."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()
        # Check for import of converters
        uses_converters = ('from utils' in content and 'converter' in content.lower()) or \
                          ('import' in content and 'converter' in content.lower()) or \
                          ('converters' in content)
        assert uses_converters, \
            f"{PREP_SCRIPT} should still use the converters module (cannot simply remove the import)"


class TestDeprecatedAliasesFixed:
    """Test that deprecated numpy aliases have been fixed."""

    def test_prep_data_no_deprecated_np_float(self):
        """prep_data.py should not use deprecated np.float alias."""
        with open(PREP_SCRIPT, 'r') as f:
            content = f.read()

        # Look for np.float that's not part of np.float64, np.float32, etc.
        # Use regex to find np.float followed by non-alphanumeric (end of identifier)
        deprecated_pattern = r'np\.float(?![0-9a-zA-Z_])'
        matches = re.findall(deprecated_pattern, content)

        assert len(matches) == 0, \
            f"{PREP_SCRIPT} still contains deprecated np.float alias. " \
            f"This should be replaced with float or np.float64."

    def test_converters_no_deprecated_np_int(self):
        """converters.py should not use deprecated np.int alias."""
        with open(CONVERTERS_FILE, 'r') as f:
            content = f.read()

        # Look for np.int that's not part of np.int64, np.int32, etc.
        deprecated_pattern = r'np\.int(?![0-9a-zA-Z_])'
        matches = re.findall(deprecated_pattern, content)

        assert len(matches) == 0, \
            f"{CONVERTERS_FILE} still contains deprecated np.int alias. " \
            f"This should be replaced with int or np.int64."

    def test_converters_no_deprecated_np_object(self):
        """converters.py should not use deprecated np.object alias."""
        with open(CONVERTERS_FILE, 'r') as f:
            content = f.read()

        # Look for np.object that's not part of np.object_ etc.
        deprecated_pattern = r'np\.object(?![0-9a-zA-Z_])'
        matches = re.findall(deprecated_pattern, content)

        assert len(matches) == 0, \
            f"{CONVERTERS_FILE} still contains deprecated np.object alias. " \
            f"This should be replaced with object or np.object_."

    def test_converters_no_deprecated_np_bool(self):
        """converters.py should not use deprecated np.bool alias."""
        with open(CONVERTERS_FILE, 'r') as f:
            content = f.read()

        # Look for np.bool that's not part of np.bool_ etc.
        deprecated_pattern = r'np\.bool(?![0-9a-zA-Z_])'
        matches = re.findall(deprecated_pattern, content)

        assert len(matches) == 0, \
            f"{CONVERTERS_FILE} still contains deprecated np.bool alias. " \
            f"This should be replaced with bool or np.bool_."


class TestCSVUnchanged:
    """Test that the source CSV file was not modified."""

    def test_csv_still_exists(self):
        """The source CSV file should still exist."""
        assert os.path.isfile(CSV_FILE), \
            f"Source CSV file {CSV_FILE} should not be deleted."

    def test_csv_still_has_500_rows(self):
        """The source CSV should still have ~500 rows."""
        with open(CSV_FILE, 'r') as f:
            lines = f.readlines()
        # Account for header row
        data_rows = len(lines) - 1
        assert 450 <= data_rows <= 550, \
            f"Source CSV should still have ~500 rows but has {data_rows} data rows. " \
            f"The source file should not be modified."


class TestConvertersModuleStillFunctional:
    """Test that the converters module can be imported and used."""

    def test_converters_module_importable(self):
        """The converters module should be importable without errors."""
        result = subprocess.run(
            ['python3', '-c', 
             'import sys; sys.path.insert(0, "/home/user/research"); from utils import converters; print("OK")'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Failed to import converters module.\n" \
            f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        assert 'OK' in result.stdout, \
            "Converters module import did not complete successfully."
