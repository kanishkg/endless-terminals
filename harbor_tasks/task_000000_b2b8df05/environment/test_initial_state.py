# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the cleanup script debugging task.
"""

import pytest
import sqlite3
import os


DATABASE_PATH = "/home/user/data/survey.db"
SQL_SCRIPT_PATH = "/home/user/data/clean.sql"
DATA_DIR = "/home/user/data"


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_data_directory_exists(self):
        """The /home/user/data directory must exist."""
        assert os.path.isdir(DATA_DIR), (
            f"Directory {DATA_DIR} does not exist. "
            "The data directory is required for this task."
        )

    def test_data_directory_is_writable(self):
        """The /home/user/data directory must be writable."""
        assert os.access(DATA_DIR, os.W_OK), (
            f"Directory {DATA_DIR} is not writable. "
            "Write access is required to modify the database."
        )


class TestDatabaseFile:
    """Test that the SQLite database exists and has correct structure."""

    def test_database_file_exists(self):
        """The survey.db database file must exist."""
        assert os.path.isfile(DATABASE_PATH), (
            f"Database file {DATABASE_PATH} does not exist. "
            "The SQLite database is required for this task."
        )

    def test_database_is_valid_sqlite(self):
        """The database file must be a valid SQLite database."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version()")
            conn.close()
        except sqlite3.DatabaseError as e:
            pytest.fail(
                f"File {DATABASE_PATH} is not a valid SQLite database: {e}"
            )

    def test_responses_table_exists(self):
        """The responses table must exist in the database."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='responses'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, (
            "Table 'responses' does not exist in the database. "
            "This table is required for the deduplication task."
        )

    def test_responses_table_has_required_columns(self):
        """The responses table must have the required columns."""
        required_columns = {"id", "email", "response", "submitted_at"}
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(responses)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        missing = required_columns - columns
        assert not missing, (
            f"Table 'responses' is missing required columns: {missing}. "
            f"Found columns: {columns}"
        )

    def test_responses_table_has_847_rows(self):
        """The responses table must have exactly 847 rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 847, (
            f"Table 'responses' has {count} rows, expected 847. "
            "The initial data must have exactly 847 rows."
        )

    def test_responses_has_298_distinct_non_null_emails(self):
        """The responses table must have exactly 298 distinct non-NULL emails."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT email) FROM responses WHERE email IS NOT NULL")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 298, (
            f"Table 'responses' has {count} distinct non-NULL emails, expected 298. "
            "This is required for the deduplication bug to manifest correctly."
        )

    def test_responses_has_14_null_email_rows(self):
        """The responses table must have exactly 14 rows with NULL email."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses WHERE email IS NULL")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 14, (
            f"Table 'responses' has {count} rows with NULL email, expected 14. "
            "The NULL email rows are essential for demonstrating the bug."
        )

    def test_submitted_at_column_is_text(self):
        """The submitted_at column must be TEXT type (ISO format timestamps)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(responses)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        conn.close()

        assert "submitted_at" in columns, (
            "Column 'submitted_at' not found in responses table."
        )
        assert columns["submitted_at"].upper() == "TEXT", (
            f"Column 'submitted_at' has type '{columns['submitted_at']}', expected 'TEXT'. "
            "The column should be TEXT type as it came from CSV export."
        )

    def test_id_column_is_integer_primary_key(self):
        """The id column must be INTEGER PRIMARY KEY."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(responses)")
        columns = {row[1]: (row[2], row[5]) for row in cursor.fetchall()}  # name: (type, pk)
        conn.close()

        assert "id" in columns, "Column 'id' not found in responses table."
        col_type, is_pk = columns["id"]
        assert col_type.upper() == "INTEGER", (
            f"Column 'id' has type '{col_type}', expected 'INTEGER'."
        )
        assert is_pk == 1, "Column 'id' must be the PRIMARY KEY."


class TestSQLScriptFile:
    """Test that the SQL script file exists and has expected content."""

    def test_sql_script_exists(self):
        """The clean.sql script file must exist."""
        assert os.path.isfile(SQL_SCRIPT_PATH), (
            f"SQL script {SQL_SCRIPT_PATH} does not exist. "
            "This file contains the buggy deduplication query."
        )

    def test_sql_script_is_readable(self):
        """The clean.sql script must be readable."""
        assert os.access(SQL_SCRIPT_PATH, os.R_OK), (
            f"SQL script {SQL_SCRIPT_PATH} is not readable."
        )

    def test_sql_script_contains_drop_table(self):
        """The SQL script should contain DROP TABLE IF EXISTS."""
        with open(SQL_SCRIPT_PATH, 'r') as f:
            content = f.read().upper()
        assert "DROP TABLE IF EXISTS RESPONSES_CLEAN" in content.replace('\n', ' ').replace('  ', ' '), (
            "SQL script should contain 'DROP TABLE IF EXISTS responses_clean' statement."
        )

    def test_sql_script_contains_create_table(self):
        """The SQL script should contain CREATE TABLE responses_clean."""
        with open(SQL_SCRIPT_PATH, 'r') as f:
            content = f.read().upper()
        assert "CREATE TABLE RESPONSES_CLEAN" in content.replace('\n', ' ').replace('  ', ' '), (
            "SQL script should contain 'CREATE TABLE responses_clean' statement."
        )

    def test_sql_script_contains_min_submitted_at(self):
        """The SQL script should use MIN(submitted_at) for deduplication."""
        with open(SQL_SCRIPT_PATH, 'r') as f:
            content = f.read().upper()
        assert "MIN(SUBMITTED_AT)" in content.replace('\n', ' ').replace('  ', ' '), (
            "SQL script should contain 'MIN(submitted_at)' for finding earliest submission."
        )

    def test_sql_script_contains_group_by_email(self):
        """The SQL script should GROUP BY email."""
        with open(SQL_SCRIPT_PATH, 'r') as f:
            content = f.read().upper()
        assert "GROUP BY EMAIL" in content.replace('\n', ' ').replace('  ', ' '), (
            "SQL script should contain 'GROUP BY email' for deduplication."
        )

    def test_sql_script_contains_inner_join(self):
        """The SQL script should use INNER JOIN (the source of the bug)."""
        with open(SQL_SCRIPT_PATH, 'r') as f:
            content = f.read().upper()
        assert "INNER JOIN" in content.replace('\n', ' ').replace('  ', ' ') or "JOIN" in content, (
            "SQL script should contain a JOIN clause (this is where the NULL bug occurs)."
        )


class TestBugReproduction:
    """Test that running the current script produces the buggy result (298 rows)."""

    def test_running_script_produces_298_rows(self):
        """Running the buggy script should produce exactly 298 rows, not 312."""
        # Create a temporary copy to test without modifying original
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Read and execute the SQL script
        with open(SQL_SCRIPT_PATH, 'r') as f:
            sql_script = f.read()

        try:
            cursor.executescript(sql_script)
            cursor.execute("SELECT COUNT(*) FROM responses_clean")
            count = cursor.fetchone()[0]
        finally:
            # Clean up - drop the test table
            cursor.execute("DROP TABLE IF EXISTS responses_clean")
            conn.commit()
            conn.close()

        assert count == 298, (
            f"Running the buggy script produces {count} rows, expected 298. "
            "The bug should cause 14 NULL email rows to be dropped, "
            "resulting in 298 rows instead of the expected 312."
        )

    def test_null_rows_are_dropped_by_buggy_script(self):
        """The buggy script should drop all NULL email rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        with open(SQL_SCRIPT_PATH, 'r') as f:
            sql_script = f.read()

        try:
            cursor.executescript(sql_script)
            cursor.execute("SELECT COUNT(*) FROM responses_clean WHERE email IS NULL")
            null_count = cursor.fetchone()[0]
        finally:
            cursor.execute("DROP TABLE IF EXISTS responses_clean")
            conn.commit()
            conn.close()

        assert null_count == 0, (
            f"Buggy script kept {null_count} NULL email rows, expected 0. "
            "The bug is that NULL = NULL evaluates to unknown in SQL, "
            "causing all NULL email rows to be dropped by the INNER JOIN."
        )


class TestSqlite3Available:
    """Test that sqlite3 CLI is available."""

    def test_sqlite3_cli_available(self):
        """The sqlite3 command-line tool must be available."""
        import subprocess
        try:
            result = subprocess.run(
                ["sqlite3", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, (
                f"sqlite3 CLI returned non-zero exit code: {result.returncode}"
            )
        except FileNotFoundError:
            pytest.fail(
                "sqlite3 CLI is not installed or not in PATH. "
                "It is required for this task."
            )
        except subprocess.TimeoutExpired:
            pytest.fail("sqlite3 --version timed out.")
