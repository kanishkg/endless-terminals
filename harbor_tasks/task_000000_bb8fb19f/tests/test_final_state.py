# test_final_state.py
"""
Tests to validate the final state after the student has added the gpu_hours column
to the runs table in /home/user/experiments/tracking.db
"""

import os
import sqlite3
import subprocess
import pytest


DATABASE_PATH = "/home/user/experiments/tracking.db"
EXPERIMENTS_DIR = "/home/user/experiments"


class TestDatabaseFileIntegrity:
    """Tests for database file integrity after modification."""

    def test_database_file_exists(self):
        """Verify tracking.db still exists."""
        assert os.path.isfile(DATABASE_PATH), (
            f"Database file {DATABASE_PATH} does not exist. "
            "The database file should not have been deleted."
        )

    def test_database_is_valid_sqlite(self):
        """Verify the file is still a valid SQLite database (not corrupted)."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            # Run integrity check
            cursor.execute("PRAGMA integrity_check;")
            result = cursor.fetchone()[0]
            conn.close()
            assert result == "ok", (
                f"Database integrity check failed: {result}. "
                "The database may be corrupted."
            )
        except sqlite3.DatabaseError as e:
            pytest.fail(
                f"File {DATABASE_PATH} is not a valid SQLite database: {e}"
            )


class TestRunsTableExists:
    """Tests to verify the runs table still exists."""

    def test_runs_table_exists(self):
        """Verify the runs table exists in the database."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='runs';"
        )
        result = cursor.fetchone()
        conn.close()

        assert result is not None, (
            "Table 'runs' does not exist in the database. "
            "The table should not have been dropped."
        )


class TestGpuHoursColumnAdded:
    """Tests for the gpu_hours column being added correctly."""

    def test_gpu_hours_column_exists(self):
        """Verify the gpu_hours column exists in the runs table."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        column_names = [col[1] for col in columns]

        assert "gpu_hours" in column_names, (
            f"Column 'gpu_hours' not found in runs table. "
            f"Found columns: {column_names}. "
            "The gpu_hours column must be added to the runs table."
        )

    def test_gpu_hours_column_is_float_type(self):
        """Verify the gpu_hours column has REAL/FLOAT type."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
        gpu_hours_column = None
        for col in columns:
            if col[1] == "gpu_hours":
                gpu_hours_column = col
                break

        assert gpu_hours_column is not None, (
            "Column 'gpu_hours' not found in runs table."
        )

        # SQLite stores float as REAL, but FLOAT is also acceptable as declared type
        column_type = gpu_hours_column[2].upper() if gpu_hours_column[2] else ""
        valid_float_types = ["REAL", "FLOAT", "DOUBLE", "DOUBLE PRECISION", "NUMERIC"]

        assert any(ft in column_type for ft in valid_float_types) or column_type == "", (
            f"Column 'gpu_hours' should be a float type (REAL or FLOAT), "
            f"found: '{gpu_hours_column[2]}'. "
            "SQLite uses REAL for floating-point numbers."
        )

    def test_gpu_hours_column_allows_null(self):
        """Verify the gpu_hours column allows NULL values."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
        gpu_hours_column = None
        for col in columns:
            if col[1] == "gpu_hours":
                gpu_hours_column = col
                break

        assert gpu_hours_column is not None, (
            "Column 'gpu_hours' not found in runs table."
        )

        # notnull is at index 3, should be 0 (allows NULL)
        assert gpu_hours_column[3] == 0, (
            "Column 'gpu_hours' should allow NULL values. "
            "ALTER TABLE ADD COLUMN creates nullable columns by default."
        )

    def test_gpu_hours_column_via_cli(self):
        """Verify gpu_hours column exists using sqlite3 CLI."""
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, "PRAGMA table_info(runs);"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"sqlite3 CLI failed: {result.stderr}"
        )

        output = result.stdout.lower()
        assert "gpu_hours" in output, (
            f"Column 'gpu_hours' not found in PRAGMA table_info output. "
            f"Output: {result.stdout}"
        )


class TestExistingDataPreserved:
    """Tests to verify existing data was preserved."""

    def test_row_count_is_47(self):
        """Verify the runs table still has exactly 47 rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM runs;")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 47, (
            f"Table 'runs' should have exactly 47 rows, found {count}. "
            "Existing data must be preserved. "
            "If count is 0, the table may have been dropped and recreated."
        )

    def test_row_count_via_cli(self):
        """Verify row count using sqlite3 CLI."""
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, "SELECT COUNT(*) FROM runs;"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"sqlite3 CLI failed: {result.stderr}"
        )

        count = int(result.stdout.strip())
        assert count == 47, (
            f"Table 'runs' should have exactly 47 rows, found {count}. "
            "Existing data must be preserved."
        )

    def test_existing_columns_still_exist(self):
        """Verify all original columns still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        column_names = [col[1] for col in columns]
        expected_columns = [
            "id", "experiment_name", "started_at", "ended_at", "status", "metrics_json"
        ]

        for expected_col in expected_columns:
            assert expected_col in column_names, (
                f"Original column '{expected_col}' not found in runs table. "
                f"Found columns: {column_names}. "
                "All original columns must be preserved."
            )

    def test_existing_data_has_values(self):
        """Verify existing rows still have their data."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM runs WHERE experiment_name IS NOT NULL;"
        )
        count_with_name = cursor.fetchone()[0]
        conn.close()

        assert count_with_name > 0, (
            "No rows with experiment_name data found. "
            "The existing experiment data should be preserved."
        )

    def test_id_column_still_primary_key(self):
        """Verify id column is still INTEGER PRIMARY KEY."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        id_column = None
        for col in columns:
            if col[1] == "id":
                id_column = col
                break

        assert id_column is not None, "Column 'id' not found in runs table."
        assert id_column[2].upper() == "INTEGER", (
            f"Column 'id' should be INTEGER type, found: {id_column[2]}"
        )
        assert id_column[5] == 1, (
            "Column 'id' should still be PRIMARY KEY"
        )


class TestCanInsertWithGpuHours:
    """Tests to verify the new column works correctly."""

    def test_can_query_gpu_hours_column(self):
        """Verify we can query the gpu_hours column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT gpu_hours FROM runs LIMIT 1;")
            cursor.fetchone()
        except sqlite3.OperationalError as e:
            pytest.fail(
                f"Cannot query gpu_hours column: {e}"
            )
        finally:
            conn.close()

    def test_existing_rows_have_null_gpu_hours(self):
        """Verify existing rows have NULL for gpu_hours (default behavior)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM runs WHERE gpu_hours IS NULL;"
        )
        null_count = cursor.fetchone()[0]
        conn.close()

        # All 47 existing rows should have NULL for the new column
        assert null_count == 47, (
            f"Expected all 47 existing rows to have NULL gpu_hours, "
            f"but found {null_count} rows with NULL. "
            "ALTER TABLE ADD COLUMN sets NULL for existing rows by default."
        )
