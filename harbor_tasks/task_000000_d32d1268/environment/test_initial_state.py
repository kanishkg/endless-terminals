# test_initial_state.py
"""
Tests to validate the initial state of the system before the student
adds a `last_seen` column to the `devices` table in telemetry.db.
"""

import os
import sqlite3
import subprocess
import pytest


DATABASE_PATH = "/home/user/fleet/telemetry.db"


class TestDatabaseFileExists:
    """Tests for the database file existence and permissions."""

    def test_fleet_directory_exists(self):
        """The /home/user/fleet directory must exist."""
        fleet_dir = "/home/user/fleet"
        assert os.path.isdir(fleet_dir), (
            f"Directory {fleet_dir} does not exist. "
            "The fleet directory must be present before adding the column."
        )

    def test_database_file_exists(self):
        """The telemetry.db file must exist."""
        assert os.path.isfile(DATABASE_PATH), (
            f"Database file {DATABASE_PATH} does not exist. "
            "The SQLite database must be present before adding the column."
        )

    def test_database_file_is_writable(self):
        """The telemetry.db file must be writable."""
        assert os.access(DATABASE_PATH, os.W_OK), (
            f"Database file {DATABASE_PATH} is not writable. "
            "The agent must have write permissions to modify the schema."
        )

    def test_database_is_valid_sqlite3(self):
        """The file must be a valid SQLite3 database."""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
        except sqlite3.DatabaseError as e:
            pytest.fail(
                f"{DATABASE_PATH} is not a valid SQLite3 database: {e}"
            )


class TestSqlite3CliAvailable:
    """Tests for sqlite3 CLI tool availability."""

    def test_sqlite3_cli_exists(self):
        """The sqlite3 CLI tool must be available."""
        result = subprocess.run(
            ["which", "sqlite3"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "sqlite3 CLI tool is not available in PATH. "
            "The sqlite3 command-line tool must be installed."
        )

    def test_sqlite3_cli_works(self):
        """The sqlite3 CLI tool must be functional."""
        result = subprocess.run(
            ["sqlite3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "sqlite3 CLI tool is not functional. "
            f"Error: {result.stderr}"
        )


class TestDevicesTableSchema:
    """Tests for the devices table schema."""

    def test_devices_table_exists(self):
        """The devices table must exist in the database."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='devices'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, (
            "Table 'devices' does not exist in the database. "
            "The devices table must be present before adding the column."
        )

    def test_devices_table_has_id_column(self):
        """The devices table must have an 'id' column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "id" in columns, (
            "Column 'id' is missing from the devices table. "
            "Expected schema includes: id INTEGER PRIMARY KEY"
        )

    def test_devices_table_has_device_id_column(self):
        """The devices table must have a 'device_id' column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "device_id" in columns, (
            "Column 'device_id' is missing from the devices table. "
            "Expected schema includes: device_id TEXT NOT NULL"
        )

    def test_devices_table_has_firmware_version_column(self):
        """The devices table must have a 'firmware_version' column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "firmware_version" in columns, (
            "Column 'firmware_version' is missing from the devices table. "
            "Expected schema includes: firmware_version TEXT"
        )

    def test_devices_table_has_last_ping_column(self):
        """The devices table must have a 'last_ping' column."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "last_ping" in columns, (
            "Column 'last_ping' is missing from the devices table. "
            "Expected schema includes: last_ping INTEGER"
        )

    def test_devices_table_does_not_have_last_seen_column(self):
        """The devices table must NOT have a 'last_seen' column yet."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "last_seen" not in columns, (
            "Column 'last_seen' already exists in the devices table. "
            "The initial state should not have this column - it needs to be added."
        )

    def test_devices_table_has_exactly_four_columns(self):
        """The devices table should have exactly 4 columns initially."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(devices)")
        columns = cursor.fetchall()
        conn.close()
        column_names = [col[1] for col in columns]
        assert len(columns) == 4, (
            f"Expected 4 columns in devices table, found {len(columns)}: {column_names}. "
            "Expected columns: id, device_id, firmware_version, last_ping"
        )


class TestDevicesTableData:
    """Tests for the devices table data."""

    def test_devices_table_has_200_rows(self):
        """The devices table must contain exactly 200 rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 200, (
            f"Expected 200 rows in devices table, found {count}. "
            "The table must contain exactly 200 rows of live device data."
        )

    def test_devices_table_has_valid_data(self):
        """The devices table must have valid data (non-null device_ids)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM devices WHERE device_id IS NULL")
        null_count = cursor.fetchone()[0]
        conn.close()
        assert null_count == 0, (
            f"Found {null_count} rows with NULL device_id. "
            "All rows should have valid device_id values."
        )

    def test_devices_table_first_five_rows_exist(self):
        """The first 5 rows must exist and have valid data for verification."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, device_id FROM devices ORDER BY id LIMIT 5"
        )
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) == 5, (
            f"Expected 5 rows when querying first 5, got {len(rows)}. "
            "The table must have at least 5 rows for anti-shortcut verification."
        )
        for row in rows:
            assert row[0] is not None, "id should not be NULL"
            assert row[1] is not None, "device_id should not be NULL"


class TestNoOtherTables:
    """Tests to verify table structure."""

    def test_only_devices_table_exists(self):
        """Only the devices table should exist (no extra tables)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        assert tables == ["devices"], (
            f"Expected only 'devices' table, found: {tables}. "
            "No other tables should exist in the database."
        )
