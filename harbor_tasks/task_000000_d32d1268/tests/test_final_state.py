# test_final_state.py
"""
Tests to validate the final state of the system after the student
has added a `last_seen` column to the `devices` table in telemetry.db.
"""

import os
import sqlite3
import subprocess
import pytest


DATABASE_PATH = "/home/user/fleet/telemetry.db"


class TestDatabaseFileIntegrity:
    """Tests for the database file existence and validity."""

    def test_database_file_exists(self):
        """The telemetry.db file must still exist."""
        assert os.path.isfile(DATABASE_PATH), (
            f"Database file {DATABASE_PATH} does not exist. "
            "The database file should not have been deleted."
        )

    def test_database_is_valid_sqlite3(self):
        """The file must still be a valid SQLite3 database."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
        except sqlite3.DatabaseError as e:
            pytest.fail(
                f"{DATABASE_PATH} is not a valid SQLite3 database: {e}"
            )


class TestLastSeenColumnAdded:
    """Tests for the new last_seen column."""

    def test_last_seen_column_exists(self):
        """The devices table must now have a 'last_seen' column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "last_seen" in columns, (
            "Column 'last_seen' was not added to the devices table. "
            "The task requires adding a last_seen column to the devices table."
        )

    def test_last_seen_column_is_nullable(self):
        """The last_seen column must be nullable (no NOT NULL constraint)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = cursor.fetchall()
        conn.close()

        last_seen_info = None
        for col in columns:
            if col[1] == "last_seen":
                last_seen_info = col
                break

        assert last_seen_info is not None, (
            "Column 'last_seen' not found in devices table."
        )

        # col[3] is the notnull flag (0 = nullable, 1 = not null)
        notnull_flag = last_seen_info[3]
        assert notnull_flag == 0, (
            "Column 'last_seen' has a NOT NULL constraint. "
            "The task requires the column to be nullable."
        )

    def test_last_seen_column_type_is_timestamp_compatible(self):
        """The last_seen column should have a timestamp-compatible type."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = cursor.fetchall()
        conn.close()

        last_seen_info = None
        for col in columns:
            if col[1] == "last_seen":
                last_seen_info = col
                break

        assert last_seen_info is not None, (
            "Column 'last_seen' not found in devices table."
        )

        # col[2] is the type
        col_type = last_seen_info[2].upper() if last_seen_info[2] else ""

        # SQLite type affinities that are compatible with timestamps
        timestamp_compatible_types = [
            "INTEGER", "INT", "TEXT", "DATETIME", "TIMESTAMP",
            "DATE", "TIME", "REAL", "NUMERIC", ""
        ]

        # Check if the type contains any of the compatible type keywords
        type_is_compatible = any(
            compat_type in col_type or col_type in compat_type or col_type == ""
            for compat_type in timestamp_compatible_types
        )

        assert type_is_compatible, (
            f"Column 'last_seen' has type '{last_seen_info[2]}' which may not be "
            "timestamp-compatible. Expected types like INTEGER, TEXT, DATETIME, "
            "TIMESTAMP, or similar SQLite type affinity."
        )


class TestOriginalColumnsPreserved:
    """Tests to verify original columns still exist."""

    def test_id_column_exists(self):
        """The 'id' column must still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "id" in columns, (
            "Column 'id' is missing from the devices table. "
            "Original columns must be preserved."
        )

    def test_device_id_column_exists(self):
        """The 'device_id' column must still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "device_id" in columns, (
            "Column 'device_id' is missing from the devices table. "
            "Original columns must be preserved."
        )

    def test_firmware_version_column_exists(self):
        """The 'firmware_version' column must still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "firmware_version" in columns, (
            "Column 'firmware_version' is missing from the devices table. "
            "Original columns must be preserved."
        )

    def test_last_ping_column_exists(self):
        """The 'last_ping' column must still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "last_ping" in columns, (
            "Column 'last_ping' is missing from the devices table. "
            "Original columns must be preserved."
        )

    def test_devices_table_has_five_columns(self):
        """The devices table should now have exactly 5 columns."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = cursor.fetchall()
        conn.close()
        column_names = [col[1] for col in columns]
        assert len(columns) == 5, (
            f"Expected 5 columns in devices table, found {len(columns)}: {column_names}. "
            "Expected columns: id, device_id, firmware_version, last_ping, last_seen"
        )


class TestDataPreserved:
    """Tests to verify all original data is preserved."""

    def test_row_count_is_200(self):
        """The devices table must still contain exactly 200 rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 200, (
            f"Expected 200 rows in devices table, found {count}. "
            "All original rows must be preserved - no data should be lost."
        )

    def test_device_ids_are_not_null(self):
        """All device_id values must still be non-null."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices WHERE device_id IS NULL")
        null_count = cursor.fetchone()[0]
        conn.close()
        assert null_count == 0, (
            f"Found {null_count} rows with NULL device_id. "
            "Original data must be preserved - device_id should not become NULL."
        )

    def test_first_five_rows_have_valid_data(self):
        """The first 5 rows must have valid id and device_id values."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, device_id, firmware_version, last_ping FROM devices ORDER BY id LIMIT 5"
        )
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 5, (
            f"Expected 5 rows when querying first 5, got {len(rows)}."
        )

        for i, row in enumerate(rows):
            assert row[0] is not None, f"Row {i+1}: id should not be NULL"
            assert row[1] is not None, f"Row {i+1}: device_id should not be NULL"

    def test_original_column_data_types_preserved(self):
        """Original column data should have reasonable values."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, device_id, firmware_version, last_ping FROM devices LIMIT 10"
        )
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            # id should be an integer
            assert isinstance(row[0], int), (
                f"id value '{row[0]}' is not an integer. Data may be corrupted."
            )
            # device_id should be a string
            assert isinstance(row[1], str), (
                f"device_id value '{row[1]}' is not a string. Data may be corrupted."
            )


class TestTableStructure:
    """Tests for overall table structure."""

    def test_devices_table_exists(self):
        """The devices table must still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='devices'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, (
            "Table 'devices' does not exist in the database. "
            "The table should not have been dropped."
        )

    def test_no_extra_tables_created(self):
        """No extra tables should have been created."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert tables == ["devices"], (
            f"Expected only 'devices' table, found: {tables}. "
            "No other tables should be created during this task."
        )


class TestSchemaViaCli:
    """Tests using sqlite3 CLI as specified in the truth."""

    def test_schema_shows_last_seen_column(self):
        """sqlite3 .schema command should show last_seen column."""
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, ".schema devices"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"sqlite3 .schema command failed: {result.stderr}"
        )

        schema_output = result.stdout.lower()
        assert "last_seen" in schema_output, (
            f"Schema does not show 'last_seen' column. "
            f"Schema output: {result.stdout}"
        )

    def test_cli_count_returns_200(self):
        """sqlite3 COUNT(*) should return 200."""
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, "SELECT COUNT(*) FROM devices;"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"sqlite3 COUNT query failed: {result.stderr}"
        )

        count = int(result.stdout.strip())
        assert count == 200, (
            f"Expected COUNT(*) to return 200, got {count}. "
            "All original rows must be preserved."
        )
