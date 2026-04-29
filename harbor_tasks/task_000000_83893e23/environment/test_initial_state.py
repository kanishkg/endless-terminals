# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
performs the capacity forecasting bug fix task.
"""

import os
import subprocess
import pytest
import csv
from pathlib import Path


HOME_DIR = Path("/home/user")
CAPACITY_DIR = HOME_DIR / "capacity"
DATA_DIR = CAPACITY_DIR / "data"
OUTPUT_DIR = CAPACITY_DIR / "output"

FORECAST_SCRIPT = CAPACITY_DIR / "forecast.py"
HOSTS_CSV = DATA_DIR / "hosts.csv"
RESERVATIONS_CSV = DATA_DIR / "reservations.csv"
OUTPUT_FORECAST_CSV = OUTPUT_DIR / "forecast.csv"


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_home_directory_exists(self):
        assert HOME_DIR.exists(), f"Home directory {HOME_DIR} does not exist"
        assert HOME_DIR.is_dir(), f"{HOME_DIR} is not a directory"

    def test_capacity_directory_exists(self):
        assert CAPACITY_DIR.exists(), f"Capacity directory {CAPACITY_DIR} does not exist"
        assert CAPACITY_DIR.is_dir(), f"{CAPACITY_DIR} is not a directory"

    def test_data_directory_exists(self):
        assert DATA_DIR.exists(), f"Data directory {DATA_DIR} does not exist"
        assert DATA_DIR.is_dir(), f"{DATA_DIR} is not a directory"

    def test_output_directory_exists(self):
        assert OUTPUT_DIR.exists(), f"Output directory {OUTPUT_DIR} does not exist"
        assert OUTPUT_DIR.is_dir(), f"{OUTPUT_DIR} is not a directory"


class TestRequiredFilesExist:
    """Test that all required input files exist."""

    def test_forecast_script_exists(self):
        assert FORECAST_SCRIPT.exists(), f"Forecast script {FORECAST_SCRIPT} does not exist"
        assert FORECAST_SCRIPT.is_file(), f"{FORECAST_SCRIPT} is not a file"

    def test_hosts_csv_exists(self):
        assert HOSTS_CSV.exists(), f"Hosts CSV {HOSTS_CSV} does not exist"
        assert HOSTS_CSV.is_file(), f"{HOSTS_CSV} is not a file"

    def test_reservations_csv_exists(self):
        assert RESERVATIONS_CSV.exists(), f"Reservations CSV {RESERVATIONS_CSV} does not exist"
        assert RESERVATIONS_CSV.is_file(), f"{RESERVATIONS_CSV} is not a file"

    def test_output_forecast_csv_exists(self):
        assert OUTPUT_FORECAST_CSV.exists(), f"Output forecast CSV {OUTPUT_FORECAST_CSV} does not exist (should exist with incorrect data)"
        assert OUTPUT_FORECAST_CSV.is_file(), f"{OUTPUT_FORECAST_CSV} is not a file"


class TestHostsCSVStructure:
    """Test that hosts.csv has the expected structure and content."""

    def test_hosts_csv_has_correct_headers(self):
        with open(HOSTS_CSV, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
        expected_headers = ['host_id', 'timestamp', 'cpu_hours', 'mem_gb_hours']
        assert headers == expected_headers, f"hosts.csv headers {headers} do not match expected {expected_headers}"

    def test_hosts_csv_has_expected_row_count(self):
        """52 weeks of hourly data = 8736 rows per host, 3 hosts = 26208 rows + 1 header"""
        with open(HOSTS_CSV, 'r') as f:
            row_count = sum(1 for _ in f) - 1  # subtract header
        # 52 weeks * 7 days * 24 hours = 8736 hours per host
        # 3 hosts * 8736 = 26208 rows
        expected_rows = 26208
        assert row_count == expected_rows, f"hosts.csv has {row_count} data rows, expected {expected_rows}"

    def test_hosts_csv_has_three_hosts(self):
        host_ids = set()
        with open(HOSTS_CSV, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                host_ids.add(row['host_id'])
        assert len(host_ids) == 3, f"hosts.csv has {len(host_ids)} unique hosts, expected 3"


class TestReservationsCSVStructure:
    """Test that reservations.csv has the expected structure and content."""

    def test_reservations_csv_has_correct_headers(self):
        with open(RESERVATIONS_CSV, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
        expected_headers = ['reservation_id', 'host_id', 'start_time', 'end_time', 'requested_cpu_hours']
        assert headers == expected_headers, f"reservations.csv headers {headers} do not match expected {expected_headers}"

    def test_reservations_csv_has_approximately_150_reservations(self):
        """~150 reservations spread across the year"""
        with open(RESERVATIONS_CSV, 'r') as f:
            row_count = sum(1 for _ in f) - 1  # subtract header
        # Allow some tolerance: 100-200 reservations
        assert 100 <= row_count <= 200, f"reservations.csv has {row_count} reservations, expected ~150 (100-200)"


class TestForecastScriptContent:
    """Test that forecast.py contains the expected buggy merge logic."""

    def test_forecast_script_is_readable(self):
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()
        assert len(content) > 0, "forecast.py is empty"

    def test_forecast_script_imports_pandas(self):
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()
        assert 'pandas' in content or 'pd' in content, "forecast.py does not appear to use pandas"

    def test_forecast_script_reads_hosts_csv(self):
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()
        assert 'hosts.csv' in content or 'hosts' in content.lower(), "forecast.py does not appear to read hosts.csv"

    def test_forecast_script_reads_reservations_csv(self):
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()
        assert 'reservations.csv' in content or 'reservations' in content.lower(), "forecast.py does not appear to read reservations.csv"

    def test_forecast_script_contains_merge_on_host_id(self):
        """The buggy merge should be present: merge on host_id alone"""
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()
        # Look for the buggy merge pattern
        assert 'merge' in content.lower(), "forecast.py does not contain a merge operation"
        assert 'host_id' in content, "forecast.py does not reference host_id"

    def test_forecast_script_writes_to_output(self):
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()
        assert 'forecast.csv' in content or 'output' in content, "forecast.py does not appear to write to output/forecast.csv"


class TestCurrentOutputIsIncorrect:
    """Test that the current output shows the inflated (incorrect) values."""

    def test_output_forecast_has_data(self):
        with open(OUTPUT_FORECAST_CSV, 'r') as f:
            row_count = sum(1 for _ in f)
        assert row_count > 1, "output/forecast.csv has no data rows"

    def test_output_shows_inflated_values(self):
        """Current output should show ~2500+ cpu_hours/week (inflated by ~3x)"""
        with open(OUTPUT_FORECAST_CSV, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # Find the cpu_hours column (might be named differently)
        if len(rows) == 0:
            pytest.fail("output/forecast.csv has no data rows")

        # Try to find a column that contains cpu_hours values
        cpu_hours_col = None
        for col in rows[0].keys():
            if 'cpu' in col.lower() or 'hours' in col.lower():
                cpu_hours_col = col
                break

        if cpu_hours_col is None:
            # Try to find any numeric column
            for col in rows[0].keys():
                try:
                    float(rows[0][col])
                    cpu_hours_col = col
                    break
                except (ValueError, TypeError):
                    continue

        assert cpu_hours_col is not None, "Could not find cpu_hours column in output/forecast.csv"

        # Check that at least some values are inflated (> 2000)
        values = []
        for row in rows:
            try:
                val = float(row[cpu_hours_col])
                values.append(val)
            except (ValueError, TypeError):
                continue

        assert len(values) > 0, "No numeric values found in output/forecast.csv"

        # The buggy output should have values around 2500+ (inflated)
        # At least some values should be > 2000 to confirm the bug exists
        inflated_values = [v for v in values if v > 2000]
        assert len(inflated_values) > 0, (
            f"Expected inflated values (>2000) in output/forecast.csv but found max={max(values):.1f}. "
            "The initial state should have the buggy (inflated) output."
        )


class TestPythonEnvironment:
    """Test that required Python packages are available."""

    def test_python3_available(self):
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "python3 is not available"

    def test_pandas_importable(self):
        result = subprocess.run(
            ['python3', '-c', 'import pandas; print(pandas.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"pandas is not importable: {result.stderr}"

    def test_numpy_importable(self):
        result = subprocess.run(
            ['python3', '-c', 'import numpy; print(numpy.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"numpy is not importable: {result.stderr}"

    def test_scipy_importable(self):
        result = subprocess.run(
            ['python3', '-c', 'import scipy; print(scipy.__version__)'],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"scipy is not importable: {result.stderr}"


class TestForecastScriptRunsWithoutError:
    """Test that the forecast script can be executed (even with buggy output)."""

    def test_forecast_script_is_executable_by_python(self):
        """The script should run without Python errors (the bug is logical, not syntactic)."""
        result = subprocess.run(
            ['python3', str(FORECAST_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(CAPACITY_DIR)
        )
        assert result.returncode == 0, (
            f"forecast.py failed to run:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestDirectoryWritable:
    """Test that required directories are writable."""

    def test_capacity_directory_writable(self):
        assert os.access(CAPACITY_DIR, os.W_OK), f"{CAPACITY_DIR} is not writable"

    def test_output_directory_writable(self):
        assert os.access(OUTPUT_DIR, os.W_OK), f"{OUTPUT_DIR} is not writable"
