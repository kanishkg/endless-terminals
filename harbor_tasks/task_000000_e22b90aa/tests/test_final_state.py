# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the NaT timestamp issue in the pipeline.
"""

import os
import subprocess
import pytest

# Base paths
PIPELINE_DIR = "/home/user/pipeline"
RAW_DIR = os.path.join(PIPELINE_DIR, "raw")
OUTPUT_DIR = os.path.join(PIPELINE_DIR, "output")
MERGED_PARQUET = os.path.join(OUTPUT_DIR, "merged.parquet")
RUN_SCRIPT = os.path.join(PIPELINE_DIR, "run.sh")

# Expected CSV files
EXPECTED_CSVS = ["sensor_a.csv", "sensor_b.csv", "sensor_c.csv", "sensor_d.csv", "sensor_e.csv"]


class TestPipelineExecution:
    """Test that the pipeline runs successfully."""

    def test_run_script_exits_zero(self):
        """Verify that running the pipeline script exits with code 0."""
        result = subprocess.run(
            [RUN_SCRIPT],
            cwd=PIPELINE_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"run.sh exited with code {result.returncode}. stderr: {result.stderr}"


class TestMergedParquetExists:
    """Test that the output file exists after pipeline run."""

    def test_merged_parquet_exists(self):
        """Verify merged.parquet exists at the expected location."""
        assert os.path.isfile(MERGED_PARQUET), \
            f"merged.parquet not found at {MERGED_PARQUET}"


class TestNoNaTValues:
    """Test that there are no NaT values in the recorded_at column."""

    def test_zero_nat_values_in_recorded_at(self):
        """Verify that recorded_at column has zero NaT values."""
        result = subprocess.run(
            ["python3", "-c",
             f"import pandas as pd; df = pd.read_parquet('{MERGED_PARQUET}'); print(df['recorded_at'].isna().sum())"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to read merged.parquet: {result.stderr}"
        nat_count = int(result.stdout.strip())
        assert nat_count == 0, \
            f"recorded_at column still has {nat_count} NaT values. Expected 0."


class TestRowCount:
    """Test that all rows are preserved."""

    def test_merged_parquet_has_200_rows(self):
        """Verify merged.parquet has exactly 200 rows (no rows dropped)."""
        result = subprocess.run(
            ["python3", "-c",
             f"import pandas as pd; df = pd.read_parquet('{MERGED_PARQUET}'); print(len(df))"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to read merged.parquet: {result.stderr}"
        row_count = int(result.stdout.strip())
        assert row_count == 200, \
            f"merged.parquet should have 200 rows, got {row_count}. Rows may have been dropped."


class TestSensorCRowsPreserved:
    """Test that sensor_c rows are preserved and not dropped."""

    def test_sensor_c_has_40_rows(self):
        """Verify that sensor_c data has exactly 40 rows (not dropped as a shortcut)."""
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
sensor_c_count = len(df[df['sensor_id'].str.contains('sensor_c')])
print(sensor_c_count)"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to count sensor_c rows: {result.stderr}"
        sensor_c_count = int(result.stdout.strip())
        assert sensor_c_count == 40, \
            f"sensor_c should have 40 rows, got {sensor_c_count}. Rows may have been dropped instead of fixed."

    def test_sensor_c_rows_have_valid_timestamps(self):
        """Verify that all sensor_c rows have valid (non-NaT) timestamps."""
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
sensor_c_df = df[df['sensor_id'].str.contains('sensor_c')]
nat_count = sensor_c_df['recorded_at'].isna().sum()
print(nat_count)"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check sensor_c timestamps: {result.stderr}"
        nat_count = int(result.stdout.strip())
        assert nat_count == 0, \
            f"sensor_c rows still have {nat_count} NaT values in recorded_at."


class TestTimestampParsedCorrectly:
    """Test that European date format was parsed correctly (not transposed)."""

    def test_european_date_parsed_correctly(self):
        """
        Verify that a known sensor_c timestamp was parsed correctly.
        European format DD/MM/YYYY should become YYYY-MM-DD, not YYYY-DD-MM.
        """
        # Check if any sensor_c row has a timestamp that looks correctly parsed
        # The original CSV has "25/03/2024 14:30:00" which should become 2024-03-25 14:30:00
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
sensor_c_df = df[df['sensor_id'].str.contains('sensor_c')]
# Check that timestamps are valid datetime objects
all_valid = sensor_c_df['recorded_at'].notna().all()
# Check that at least one timestamp has month=3 and day=25 (from 25/03/2024)
# This verifies the date wasn't transposed to month=25 (invalid) or similar
has_march_dates = any(sensor_c_df['recorded_at'].dt.month == 3)
print(f"{{all_valid}},{{has_march_dates}}")"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to verify timestamp parsing: {result.stderr}"
        output = result.stdout.strip()
        all_valid, has_march = output.split(',')
        assert all_valid == "True", "Not all sensor_c timestamps are valid"
        assert has_march == "True", \
            "No March dates found in sensor_c data - European format may have been parsed incorrectly"

    def test_specific_timestamp_value(self):
        """
        Check that the specific timestamp '25/03/2024 14:30:00' was parsed to 2024-03-25 14:30:00.
        """
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
sensor_c_df = df[df['sensor_id'].str.contains('sensor_c')]
# Look for the expected parsed timestamp
expected_ts = pd.Timestamp('2024-03-25 14:30:00')
found = any(sensor_c_df['recorded_at'] == expected_ts)
print(found)"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check specific timestamp: {result.stderr}"
        found = result.stdout.strip()
        assert found == "True", \
            "Expected timestamp 2024-03-25 14:30:00 not found. The European date format '25/03/2024 14:30:00' may have been parsed incorrectly."


class TestColumnsPreserved:
    """Test that all required columns are still present."""

    def test_all_columns_present(self):
        """Verify merged.parquet has all required columns."""
        result = subprocess.run(
            ["python3", "-c",
             f"import pandas as pd; df = pd.read_parquet('{MERGED_PARQUET}'); print(','.join(sorted(df.columns.tolist())))"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to read columns: {result.stderr}"
        columns = set(result.stdout.strip().split(','))
        expected = {"sensor_id", "recorded_at", "value", "unit"}
        assert expected.issubset(columns), \
            f"Missing columns. Expected at least: {expected}, Got: {columns}"


class TestSourceFilesUnchanged:
    """Test that source CSV files were not modified."""

    def test_all_source_csvs_exist(self):
        """Verify all source CSV files still exist."""
        for csv_file in EXPECTED_CSVS:
            csv_path = os.path.join(RAW_DIR, csv_file)
            assert os.path.isfile(csv_path), \
                f"Source CSV file {csv_path} is missing. Source files should not be deleted."

    def test_sensor_c_still_has_european_format(self):
        """Verify sensor_c.csv still has European date format (source unchanged)."""
        import csv
        csv_path = os.path.join(RAW_DIR, "sensor_c.csv")
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            row = next(reader)
            timestamp = row['recorded_at']
            # Should still have "/" separators indicating European format
            assert "/" in timestamp, \
                f"sensor_c.csv appears to have been modified. Original European format should be preserved in source."


class TestDataIntegrity:
    """Test overall data integrity of the output."""

    def test_all_timestamps_are_datetime_type(self):
        """Verify recorded_at column has datetime dtype."""
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
dtype = str(df['recorded_at'].dtype)
is_datetime = 'datetime' in dtype.lower()
print(is_datetime)"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check dtype: {result.stderr}"
        is_datetime = result.stdout.strip()
        assert is_datetime == "True", \
            "recorded_at column is not datetime type"

    def test_no_future_dates(self):
        """Verify no timestamps are unreasonably in the future (sanity check for parsing)."""
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
from datetime import datetime
df = pd.read_parquet('{MERGED_PARQUET}')
future_cutoff = pd.Timestamp('2030-01-01')
future_count = (df['recorded_at'] > future_cutoff).sum()
print(future_count)"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check future dates: {result.stderr}"
        future_count = int(result.stdout.strip())
        assert future_count == 0, \
            f"Found {future_count} timestamps after 2030, suggesting incorrect date parsing."

    def test_timestamps_in_reasonable_range(self):
        """Verify timestamps are in a reasonable range (2020-2025)."""
        result = subprocess.run(
            ["python3", "-c",
             f"""import pandas as pd
df = pd.read_parquet('{MERGED_PARQUET}')
min_date = pd.Timestamp('2020-01-01')
max_date = pd.Timestamp('2025-12-31')
in_range = ((df['recorded_at'] >= min_date) & (df['recorded_at'] <= max_date)).all()
print(in_range)"""],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Failed to check date range: {result.stderr}"
        in_range = result.stdout.strip()
        assert in_range == "True", \
            "Some timestamps are outside the expected range (2020-2025), suggesting parsing errors."
