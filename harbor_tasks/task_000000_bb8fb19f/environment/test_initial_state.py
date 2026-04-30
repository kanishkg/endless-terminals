# test_initial_state.py
"""
Tests to validate the initial state before the student adds the gpu_hours column
to the runs table in /home/user/experiments/tracking.db
"""

import os
import sqlite3
import subprocess
import pytest


DATABASE_PATH = "/home/user/experiments/tracking.db"
EXPERIMENTS_DIR = "/home/user/experiments"


class TestDirectoryState:
    """Tests for the experiments directory state."""

    def test_experiments_directory_exists(self):
        """Verify /home/user/experiments/ directory exists."""
        assert os.path.isdir(EXPERIMENTS_DIR), (
            f"Directory {EXPERIMENTS_DIR} does not exist. "
            "The experiments directory must exist before the task."
        )

    def test_experiments_directory_is_writable(self):
        """Verify /home/user/experiments/ directory is writable."""
        assert os.access(EXPERIMENTS_DIR, os.W_OK), (
            f"Directory {EXPERIMENTS_DIR} is not writable. "
            "The agent needs write access to modify the database."
        )


class TestDatabaseFileState:
    """Tests for the database file state."""

    def test_database_file_exists(self):
        """Verify tracking.db exists."""
        assert os.path.isfile(DATABASE_PATH), (
            f"Database file {DATABASE_PATH} does not exist. "
            "The SQLite database must exist before the task."
        )

    def test_database_is_valid_sqlite(self):
        """Verify the file is a valid SQLite database."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
        except sqlite3.DatabaseError as e:
            pytest.fail(
                f"File {DATABASE_PATH} is not a valid SQLite database: {e}"
            )


class TestSqlite3CliAvailable:
    """Tests for sqlite3 CLI availability."""

    def test_sqlite3_cli_exists(self):
        """Verify sqlite3 CLI is available."""
        result = subprocess.run(
            ["which", "sqlite3"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "sqlite3 CLI is not available in PATH. "
            "The sqlite3 command-line tool must be installed."
        )

    def test_sqlite3_cli_works(self):
        """Verify sqlite3 CLI can query the database."""
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, "SELECT 1;"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"sqlite3 CLI failed to query {DATABASE_PATH}: {result.stderr}"
        )


class TestRunsTableSchema:
    """Tests for the runs table schema."""

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
            "The runs table must exist before adding the gpu_hours column."
        )

    def test_runs_table_has_expected_columns(self):
        """Verify the runs table has the expected schema columns."""
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
                f"Column '{expected_col}' not found in runs table. "
                f"Found columns: {column_names}. "
                "The runs table must have the expected schema."
            )

    def test_runs_table_does_not_have_gpu_hours_column(self):
        """Verify the runs table does NOT yet have the gpu_hours column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        column_names = [col[1] for col in columns]

        assert "gpu_hours" not in column_names, (
            "Column 'gpu_hours' already exists in runs table. "
            "The task is to ADD this column, so it should not exist initially."
        )

    def test_id_column_is_integer_primary_key(self):
        """Verify id column is INTEGER PRIMARY KEY."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(runs);")
        columns = cursor.fetchall()
        conn.close()

        # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
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
            "Column 'id' should be PRIMARY KEY"
        )


class TestRunsTableData:
    """Tests for the runs table data."""

    def test_runs_table_has_47_rows(self):
        """Verify the runs table has exactly 47 rows of existing data."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM runs;")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 47, (
            f"Table 'runs' should have exactly 47 rows, found {count}. "
            "The existing experiment data must be present before the task."
        )

    def test_runs_table_has_data_in_all_columns(self):
        """Verify that the existing rows have data (not all NULL)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM runs WHERE experiment_name IS NOT NULL;"
        )
        count_with_name = cursor.fetchone()[0]
        conn.close()

        assert count_with_name > 0, (
            "No rows with experiment_name data found. "
            "The table should contain actual experiment data."
        )
