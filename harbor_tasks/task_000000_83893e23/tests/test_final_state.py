# test_final_state.py
"""
Tests to validate the final state after the student has fixed the capacity
forecasting bug in /home/user/capacity/forecast.py.

The fix should address the merge logic that was causing ~3x inflation of
cpu_hours due to duplicating rows when joining hosts with reservations.
"""

import os
import subprocess
import pytest
import csv
import hashlib
from pathlib import Path


HOME_DIR = Path("/home/user")
CAPACITY_DIR = HOME_DIR / "capacity"
DATA_DIR = CAPACITY_DIR / "data"
OUTPUT_DIR = CAPACITY_DIR / "output"

FORECAST_SCRIPT = CAPACITY_DIR / "forecast.py"
HOSTS_CSV = DATA_DIR / "hosts.csv"
RESERVATIONS_CSV = DATA_DIR / "reservations.csv"
OUTPUT_FORECAST_CSV = OUTPUT_DIR / "forecast.csv"


def get_file_hash(filepath):
    """Calculate MD5 hash of a file."""
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_forecast_script():
    """Run the forecast script and return the result."""
    result = subprocess.run(
        ['python3', str(FORECAST_SCRIPT)],
        capture_output=True,
        text=True,
        cwd=str(CAPACITY_DIR)
    )
    return result


def parse_forecast_csv():
    """Parse the forecast CSV and return rows with week and cpu_hours."""
    rows = []
    with open(OUTPUT_FORECAST_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def extract_cpu_hours_values(rows):
    """Extract cpu_hours values from forecast CSV rows."""
    if not rows:
        return []

    # Try to find the cpu_hours column
    cpu_hours_col = None
    for col in rows[0].keys():
        col_lower = col.lower()
        if 'cpu' in col_lower and 'hour' in col_lower:
            cpu_hours_col = col
            break

    if cpu_hours_col is None:
        # Try just 'cpu_hours'
        for col in rows[0].keys():
            if col.lower() == 'cpu_hours':
                cpu_hours_col = col
                break

    if cpu_hours_col is None:
        # Try any column with numeric values that could be cpu_hours
        for col in rows[0].keys():
            if 'week' not in col.lower() and 'forecast' not in col.lower():
                try:
                    float(rows[0][col])
                    cpu_hours_col = col
                    break
                except (ValueError, TypeError):
                    continue

    if cpu_hours_col is None:
        return []

    values = []
    for row in rows:
        try:
            val = float(row[cpu_hours_col])
            values.append(val)
        except (ValueError, TypeError):
            continue

    return values


def extract_week_and_cpu_hours(rows):
    """Extract (week, cpu_hours) tuples from forecast CSV rows."""
    if not rows:
        return []

    # Find week column
    week_col = None
    for col in rows[0].keys():
        if 'week' in col.lower():
            week_col = col
            break

    # Find cpu_hours column
    cpu_hours_col = None
    for col in rows[0].keys():
        col_lower = col.lower()
        if 'cpu' in col_lower and 'hour' in col_lower:
            cpu_hours_col = col
            break

    if cpu_hours_col is None:
        for col in rows[0].keys():
            if col.lower() == 'cpu_hours':
                cpu_hours_col = col
                break

    if week_col is None or cpu_hours_col is None:
        return []

    results = []
    for row in rows:
        try:
            week = int(float(row[week_col]))
            cpu_hours = float(row[cpu_hours_col])
            results.append((week, cpu_hours))
        except (ValueError, TypeError, KeyError):
            continue

    return results


class TestScriptExecutesSuccessfully:
    """Test that the fixed script runs without errors."""

    def test_forecast_script_runs_without_error(self):
        """The fixed script should run without Python errors."""
        result = run_forecast_script()
        assert result.returncode == 0, (
            f"forecast.py failed to run after fix:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_output_file_is_regenerated(self):
        """The output file should exist after running the script."""
        run_forecast_script()
        assert OUTPUT_FORECAST_CSV.exists(), (
            f"Output file {OUTPUT_FORECAST_CSV} does not exist after running forecast.py"
        )


class TestSourceFilesUnchanged:
    """Test that source data files were not modified."""

    def test_hosts_csv_exists(self):
        """hosts.csv should still exist."""
        assert HOSTS_CSV.exists(), f"hosts.csv was deleted or moved"

    def test_reservations_csv_exists(self):
        """reservations.csv should still exist."""
        assert RESERVATIONS_CSV.exists(), f"reservations.csv was deleted or moved"

    def test_hosts_csv_row_count_unchanged(self):
        """hosts.csv should have the same number of rows (26208 + header)."""
        with open(HOSTS_CSV, 'r') as f:
            row_count = sum(1 for _ in f) - 1
        assert row_count == 26208, (
            f"hosts.csv has {row_count} data rows, expected 26208. "
            "Source file should not be modified."
        )

    def test_reservations_csv_has_data(self):
        """reservations.csv should still have reservation data."""
        with open(RESERVATIONS_CSV, 'r') as f:
            row_count = sum(1 for _ in f) - 1
        assert 100 <= row_count <= 200, (
            f"reservations.csv has {row_count} rows, expected ~150. "
            "Source file should not be significantly modified."
        )


class TestOutputHasCorrectStructure:
    """Test that the output file has the expected structure."""

    def test_output_has_data_rows(self):
        """Output should have data rows."""
        run_forecast_script()
        rows = parse_forecast_csv()
        assert len(rows) > 0, "output/forecast.csv has no data rows"

    def test_output_has_historical_and_forecast_rows(self):
        """Output should contain both historical and forecast data."""
        run_forecast_script()
        rows = parse_forecast_csv()
        # Should have at least 52 historical weeks + some forecast weeks
        assert len(rows) >= 52, (
            f"output/forecast.csv has only {len(rows)} rows, "
            "expected at least 52 (historical) + forecast weeks"
        )


class TestHistoricalValuesAreCorrect:
    """Test that historical cpu_hours values are in the correct range."""

    def test_historical_values_not_inflated(self):
        """Historical weeks should show ~847 average, not 2500+."""
        run_forecast_script()
        rows = parse_forecast_csv()
        values = extract_cpu_hours_values(rows)

        assert len(values) > 0, "Could not extract cpu_hours values from output"

        # Get historical values (first 52 or so)
        historical_values = values[:52] if len(values) >= 52 else values

        avg = sum(historical_values) / len(historical_values)
        assert 700 <= avg <= 1000, (
            f"Historical average cpu_hours is {avg:.1f}, expected ~847 (700-1000 range). "
            f"If avg > 2000, the merge bug is likely still present."
        )

    def test_no_historical_week_exceeds_1000(self):
        """No historical week should exceed 1000 cpu_hours."""
        run_forecast_script()
        rows = parse_forecast_csv()
        values = extract_cpu_hours_values(rows)

        assert len(values) > 0, "Could not extract cpu_hours values from output"

        # Check historical values (first 52)
        historical_values = values[:52] if len(values) >= 52 else values

        max_val = max(historical_values)
        assert max_val <= 1000, (
            f"Historical week has cpu_hours={max_val:.1f}, which exceeds 1000. "
            "This suggests the merge inflation bug is still present."
        )

    def test_q4_weeks_average_around_847(self):
        """Weeks 40-52 should average between 800 and 900 cpu_hours."""
        run_forecast_script()
        rows = parse_forecast_csv()
        week_data = extract_week_and_cpu_hours(rows)

        if not week_data:
            # Fall back to checking last 13 values as Q4 proxy
            values = extract_cpu_hours_values(rows)
            if len(values) >= 52:
                q4_values = values[39:52]  # weeks 40-52 (0-indexed 39-51)
            else:
                q4_values = values[-13:] if len(values) >= 13 else values
        else:
            q4_values = [cpu for week, cpu in week_data if 40 <= week <= 52]

        if len(q4_values) == 0:
            pytest.skip("Could not identify Q4 weeks in output")

        avg = sum(q4_values) / len(q4_values)
        assert 800 <= avg <= 900, (
            f"Q4 (weeks 40-52) average is {avg:.1f}, expected 800-900. "
            f"Known correct baseline is ~847."
        )


class TestForecastValuesArePlausible:
    """Test that forecast (projected) values are reasonable extrapolations."""

    def test_forecast_values_exist(self):
        """There should be forecast values beyond the historical data."""
        run_forecast_script()
        rows = parse_forecast_csv()

        # Should have more than 52 rows (historical + forecast)
        assert len(rows) > 52, (
            f"Output has only {len(rows)} rows. "
            "Expected historical (52 weeks) + forecast weeks."
        )

    def test_no_forecast_week_exceeds_1200(self):
        """No forecast week should exceed 1200 cpu_hours."""
        run_forecast_script()
        rows = parse_forecast_csv()
        values = extract_cpu_hours_values(rows)

        assert len(values) > 0, "Could not extract cpu_hours values from output"

        # Forecast values are typically after week 52
        forecast_values = values[52:] if len(values) > 52 else []

        if len(forecast_values) == 0:
            # Maybe all values are in one list, check the last few
            forecast_values = values[-8:] if len(values) >= 60 else values[-4:]

        if len(forecast_values) > 0:
            max_forecast = max(forecast_values)
            assert max_forecast <= 1200, (
                f"Forecast week has cpu_hours={max_forecast:.1f}, which exceeds 1200. "
                "Forecast should be a sensible extrapolation from ~847 baseline, not 3x inflated."
            )

    def test_forecast_values_are_reasonable_extrapolation(self):
        """Forecast values should be reasonable extrapolations (not 3x inflated)."""
        run_forecast_script()
        rows = parse_forecast_csv()
        values = extract_cpu_hours_values(rows)

        if len(values) < 52:
            pytest.skip("Not enough data to validate forecast extrapolation")

        # Historical average
        historical_values = values[:52]
        hist_avg = sum(historical_values) / len(historical_values)

        # Forecast values
        forecast_values = values[52:] if len(values) > 52 else []

        if len(forecast_values) > 0:
            forecast_avg = sum(forecast_values) / len(forecast_values)
            # Forecast should be within reasonable range of historical
            # Allow up to 50% growth for extrapolation, but not 3x
            assert forecast_avg < hist_avg * 2, (
                f"Forecast average ({forecast_avg:.1f}) is more than 2x historical ({hist_avg:.1f}). "
                "This suggests the fix did not properly address the inflation bug."
            )


class TestMergeBugIsFixed:
    """Test that the merge bug is actually fixed, not just post-hoc adjusted."""

    def test_script_still_reads_source_files(self):
        """The script should still read from the source CSV files."""
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()

        # Should still reference the data files
        assert 'hosts' in content.lower(), (
            "forecast.py no longer references hosts data. "
            "Fix should modify merge logic, not replace data sources."
        )

    def test_output_not_hardcoded(self):
        """Verify output is computed, not hardcoded."""
        # Run the script twice and check output is consistent
        run_forecast_script()
        rows1 = parse_forecast_csv()
        values1 = extract_cpu_hours_values(rows1)

        run_forecast_script()
        rows2 = parse_forecast_csv()
        values2 = extract_cpu_hours_values(rows2)

        # Values should be identical (deterministic computation)
        assert len(values1) == len(values2), "Output row count differs between runs"

        for i, (v1, v2) in enumerate(zip(values1, values2)):
            assert abs(v1 - v2) < 0.01, (
                f"Value at row {i} differs between runs: {v1} vs {v2}. "
                "Output should be deterministic."
            )

    def test_historical_sum_is_correct_magnitude(self):
        """Total historical cpu_hours should be in correct range."""
        run_forecast_script()
        rows = parse_forecast_csv()
        values = extract_cpu_hours_values(rows)

        if len(values) < 52:
            pytest.skip("Not enough historical data")

        historical_values = values[:52]
        total = sum(historical_values)

        # 52 weeks * ~847 avg = ~44,000 total
        # Allow range of 40,000 - 50,000
        assert 40000 <= total <= 50000, (
            f"Historical total cpu_hours is {total:.1f}, expected ~44,000 (40k-50k range). "
            f"If total > 100,000, the merge bug is likely still present."
        )


class TestScriptLogicIsFixed:
    """Test that the script's merge logic has been corrected."""

    def test_no_obvious_division_hack(self):
        """The fix should not be a post-hoc division by a magic constant."""
        with open(FORECAST_SCRIPT, 'r') as f:
            content = f.read()

        # Look for suspicious division patterns that might indicate a hack
        # This is a heuristic check - not foolproof
        suspicious_patterns = [
            '/ 3',
            '/3',
            '* 0.33',
            '*0.33',
            '/ 2.5',
            '/2.5',
            '/ 50',  # dividing by number of reservations
            '/50',
        ]

        # These patterns in isolation don't prove a hack, but combined with
        # other evidence they might indicate the wrong approach
        hack_indicators = sum(1 for p in suspicious_patterns if p in content)

        # Allow some numeric operations, but flag if there are many suspicious patterns
        # This is a soft check - the real validation is in the output values
        if hack_indicators >= 3:
            pytest.fail(
                "Script contains multiple suspicious division patterns. "
                "Fix should address merge logic, not divide output by a constant."
            )


class TestEndToEndCorrectness:
    """Integration tests for overall correctness."""

    def test_full_pipeline_produces_correct_output(self):
        """Run the full pipeline and validate the output comprehensively."""
        result = run_forecast_script()
        assert result.returncode == 0, f"Script failed: {result.stderr}"

        rows = parse_forecast_csv()
        assert len(rows) >= 52, f"Too few rows: {len(rows)}"

        values = extract_cpu_hours_values(rows)
        assert len(values) >= 52, f"Too few cpu_hours values: {len(values)}"

        # Historical checks
        historical = values[:52]
        hist_avg = sum(historical) / len(historical)
        hist_max = max(historical)

        assert 700 <= hist_avg <= 1000, f"Historical avg {hist_avg:.1f} out of range"
        assert hist_max <= 1000, f"Historical max {hist_max:.1f} exceeds 1000"

        # Forecast checks (if present)
        if len(values) > 52:
            forecast = values[52:]
            forecast_max = max(forecast)
            assert forecast_max <= 1200, f"Forecast max {forecast_max:.1f} exceeds 1200"

        # Overall sanity check - no value should be anywhere near the buggy 2500+
        all_max = max(values)
        assert all_max < 1500, (
            f"Maximum value {all_max:.1f} is too high. "
            "The merge inflation bug appears to still be present."
        )
