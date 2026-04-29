# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the NaT timestamp issue in the pipeline.
"""

import os
import subprocess
import pytest

# Base paths
PIPELINE_DIR = "/home/user/pipeline"
RAW_DIR = os.path.join(PIPELINE_DIR, "raw")
STAGING_DIR = os.path.join(PIPELINE_DIR, "staging")
PROCESSED_DIR = os.path.join(PIPELINE_DIR, "processed")
OUTPUT_DIR = os.path.join(PIPELINE_DIR, "output")
MERGED_PARQUET = os.path.join(OUTPUT_DIR, "merged.parquet")

# Expected CSV files
EXPECTED_CSVS = ["sensor_a.csv", "sensor_b.csv", "sensor_c.csv", "sensor_d.csv", "sensor_e.csv"]

# Pipeline scripts
EXTRACT_SCRIPT = os.path.join(PIPELINE_DIR, "extract.py")
TRANSFORM_SCRIPT = os.path.join(PIPELINE_DIR, "transform.py")
LOAD_SCRIPT = os.path.join(PIPELINE_DIR, "load.py")
RUN_SCRIPT = os.path.join(PIPELINE_DIR, "run.sh")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_pipeline_directory_exists(self):
        assert os.path.isdir(PIPELINE_DIR), f"Pipeline directory {PIPELINE_DIR} does not exist"

    def test_raw_directory_exists(self):
        assert os.path.isdir(RAW_DIR), f"Raw data directory {RAW_DIR} does not exist"

    def test_staging_directory_exists(self):
        assert os.path.isdir(STAGING_DIR), f"Staging directory {STAGING_DIR} does not exist"

    def test_processed_directory_exists(self):
        assert os.path.isdir(PROCESSED_DIR), f"Processed directory {PROCESSED_DIR} does not exist"

    def test_output_directory_exists(self):
        assert os.path.isdir(OUTPUT_DIR), f"Output directory {OUTPUT_DIR} does not exist"


class TestSourceCSVFiles:
    """Test that source CSV files exist and have expected structure."""

    def test_all_csv_files_exist(self):
        for csv_file in EXPECTED_CSVS:
            csv_path = os.path.join(RAW_DIR, csv_file)
            assert os.path.isfile(csv_path), f"CSV file {csv_path} does not exist"

    def test_csv_files_have_expected_columns(self):
        """Verify each CSV has the required columns."""
        import csv
        expected_columns = {"sensor_id", "recorded_at", "value", "unit"}

        for csv_file in EXPECTED_CSVS:
            csv_path = os.path.join(RAW_DIR, csv_file)
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                actual_columns = set(header)
                assert expected_columns.issubset(actual_columns), \
                    f"{csv_file} missing columns. Expected: {expected_columns}, Got: {actual_columns}"

    def test_csv_files_have_data(self):
        """Verify each CSV has at least one data row."""
        import csv

        for csv_file in EXPECTED_CSVS:
            csv_path = os.path.join(RAW_DIR, csv_file)
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                data_rows = list(reader)
                assert len(data_rows) > 0, f"{csv_file} has no data rows"

    def test_sensor_c_has_european_date_format(self):
        """Verify sensor_c.csv has European date format (DD/MM/YYYY)."""
        import csv

        csv_path = os.path.join(RAW_DIR, "sensor_c.csv")
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            timestamp = row['recorded_at']
            # European format should have "/" separators in the date part
            assert "/" in timestamp, \
                f"sensor_c.csv timestamp '{timestamp}' doesn't appear to be in European format (DD/MM/YYYY)"
            # Check that it looks like DD/MM/YYYY (day/month/year)
            date_part = timestamp.split()[0] if " " in timestamp else timestamp
            parts = date_part.split("/")
            assert len(parts) == 3, \
                f"sensor_c.csv timestamp date part '{date_part}' doesn't have 3 parts separated by '/'"

    def test_other_csvs_have_iso_date_format(self):
        """Verify non-sensor_c CSVs have ISO date format (YYYY-MM-DD)."""
        import csv

        for csv_file in EXPECTED_CSVS:
            if csv_file == "sensor_c.csv":
                continue
            csv_path = os.path.join(RAW_DIR, csv_file)
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                row = next(reader)
                timestamp = row['recorded_at']
                # ISO format should have "-" separators in the date part
                date_part = timestamp.split()[0] if " " in timestamp else timestamp
                assert "-" in date_part, \
                    f"{csv_file} timestamp '{timestamp}' doesn't appear to be in ISO format (YYYY-MM-DD)"


class TestPipelineScripts:
    """Test that pipeline scripts exist and are valid Python."""

    def test_extract_script_exists(self):
        assert os.path.isfile(EXTRACT_SCRIPT), f"extract.py not found at {EXTRACT_SCRIPT}"

    def test_transform_script_exists(self):
        assert os.path.isfile(TRANSFORM_SCRIPT), f"transform.py not found at {TRANSFORM_SCRIPT}"

    def test_load_script_exists(self):
        assert os.path.isfile(LOAD_SCRIPT), f"load.py not found at {LOAD_SCRIPT}"

    def test_run_script_exists(self):
        assert os.path.isfile(RUN_SCRIPT), f"run.sh not found at {RUN_SCRIPT}"

    def test_run_script_is_executable(self):
        assert os.access(RUN_SCRIPT, os.X_OK), f"run.sh at {RUN_SCRIPT} is not executable"

    def test_extract_script_is_valid_python(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", EXTRACT_SCRIPT],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"extract.py has syntax errors: {result.stderr}"

    def test_transform_script_is_valid_python(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", TRANSFORM_SCRIPT],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"transform.py has syntax errors: {result.stderr}"

    def test_load_script_is_valid_python(self):
        result = subprocess.run(
            ["python3", "-m", "py_compile", LOAD_SCRIPT],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"load.py has syntax errors: {result.stderr}"

    def test_transform_script_has_hardcoded_format(self):
        """Verify transform.py contains the buggy hardcoded datetime format."""
        with open(TRANSFORM_SCRIPT, 'r') as f:
            content = f.read()
        # The bug is a hardcoded format string that doesn't handle European dates
        assert "%Y-%m-%d" in content or "strptime" in content or "to_datetime" in content, \
            "transform.py doesn't appear to have datetime parsing code"


class TestExistingOutput:
    """Test that existing output file has the expected buggy state."""

    def test_merged_parquet_exists(self):
        assert os.path.isfile(MERGED_PARQUET), f"merged.parquet not found at {MERGED_PARQUET}"

    def test_merged_parquet_has_200_rows(self):
        """Verify merged.parquet has exactly 200 rows."""
        result = subprocess.run(
            ["python3", "-c", 
             f"import pandas as pd; df = pd.read_parquet('{MERGED_PARQUET}'); print(len(df))"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to read merged.parquet: {result.stderr}"
        row_count = int(result.stdout.strip())
        assert row_count == 200, f"merged.parquet should have 200 rows, got {row_count}"

    def test_merged_parquet_has_nat_values(self):
        """Verify merged.parquet has NaT values in recorded_at (the bug we need to fix)."""
        result = subprocess.run(
            ["python3", "-c",
             f"import pandas as pd; df = pd.read_parquet('{MERGED_PARQUET}'); print(df['recorded_at'].isna().sum())"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check NaT values: {result.stderr}"
        nat_count = int(result.stdout.strip())
        assert nat_count == 40, f"merged.parquet should have 40 NaT values, got {nat_count}"

    def test_merged_parquet_has_expected_columns(self):
        """Verify merged.parquet has all required columns."""
        result = subprocess.run(
            ["python3", "-c",
             f"import pandas as pd; df = pd.read_parquet('{MERGED_PARQUET}'); print(','.join(df.columns.tolist()))"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to read columns: {result.stderr}"
        columns = set(result.stdout.strip().split(','))
        expected = {"sensor_id", "recorded_at", "value", "unit"}
        assert expected.issubset(columns), f"Missing columns. Expected: {expected}, Got: {columns}"

    def test_sensor_c_rows_have_nat(self):
        """Verify that the NaT values are specifically from sensor_c data."""
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
sensor_c_nat = df[df['sensor_id'].str.contains('sensor_c') & df['recorded_at'].isna()]
print(len(sensor_c_nat))"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check sensor_c NaT values: {result.stderr}"
        nat_count = int(result.stdout.strip())
        assert nat_count == 40, f"sensor_c should have 40 NaT values, got {nat_count}"


class TestPythonEnvironment:
    """Test that required Python packages are available."""

    def test_python_version(self):
        """Verify Python 3.11+ is available."""
        result = subprocess.run(
            ["python3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, "Failed to get Python version"
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        assert major >= 3 and minor >= 11, f"Python 3.11+ required, got {version}"

    def test_pandas_installed(self):
        """Verify pandas is installed."""
        result = subprocess.run(
            ["python3", "-c", "import pandas; print(pandas.__version__)"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"pandas not installed: {result.stderr}"

    def test_pyarrow_installed(self):
        """Verify pyarrow is installed (needed for parquet support)."""
        result = subprocess.run(
            ["python3", "-c", "import pyarrow; print(pyarrow.__version__)"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"pyarrow not installed: {result.stderr}"


class TestDirectoryWritability:
    """Test that the pipeline directory is writable."""

    def test_pipeline_dir_writable(self):
        assert os.access(PIPELINE_DIR, os.W_OK), f"{PIPELINE_DIR} is not writable"

    def test_staging_dir_writable(self):
        assert os.access(STAGING_DIR, os.W_OK), f"{STAGING_DIR} is not writable"

    def test_processed_dir_writable(self):
        assert os.access(PROCESSED_DIR, os.W_OK), f"{PROCESSED_DIR} is not writable"

    def test_output_dir_writable(self):
        assert os.access(OUTPUT_DIR, os.W_OK), f"{OUTPUT_DIR} is not writable"
