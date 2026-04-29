# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the cleanup script debugging task.

The student should have fixed the clean.sql script to properly handle:
1. NULL email rows (14 rows that should be preserved as distinct unknown respondents)
2. Deduplication of non-NULL emails using MIN(submitted_at)

Expected final state:
- responses_clean table has exactly 312 rows
- 298 distinct non-NULL emails (each appearing exactly once)
- 14 NULL email rows (all preserved)
- Original responses table unchanged (847 rows)
"""

import pytest
import sqlite3
import os
import subprocess


DATABASE_PATH = "/home/user/data/survey.db"
SQL_SCRIPT_PATH = "/home/user/data/clean.sql"
DATA_DIR = "/home/user/data"


class TestOriginalDataPreserved:
    """Test that the original responses table is unchanged."""

    def test_responses_table_still_exists(self):
        """The original responses table must still exist."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='responses'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, (
            "Original 'responses' table no longer exists. "
            "The original data should be preserved."
        )

    def test_responses_table_has_847_rows(self):
        """The original responses table must still have exactly 847 rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 847, (
            f"Original 'responses' table has {count} rows, expected 847. "
            "The original data should not be modified."
        )

    def test_responses_still_has_298_distinct_non_null_emails(self):
        """The original table should still have 298 distinct non-NULL emails."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT email) FROM responses WHERE email IS NOT NULL")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 298, (
            f"Original 'responses' table has {count} distinct non-NULL emails, expected 298. "
            "The original data should not be modified."
        )

    def test_responses_still_has_14_null_email_rows(self):
        """The original table should still have 14 NULL email rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses WHERE email IS NULL")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 14, (
            f"Original 'responses' table has {count} NULL email rows, expected 14. "
            "The original data should not be modified."
        )


class TestResponsesCleanTableExists:
    """Test that responses_clean table exists with correct structure."""

    def test_responses_clean_table_exists(self):
        """The responses_clean table must exist after running the fixed script."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='responses_clean'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None, (
            "Table 'responses_clean' does not exist. "
            "The fixed clean.sql script should create this table."
        )

    def test_responses_clean_has_required_columns(self):
        """The responses_clean table must have the same columns as responses."""
        required_columns = {"id", "email", "response", "submitted_at"}
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(responses_clean)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        missing = required_columns - columns
        assert not missing, (
            f"Table 'responses_clean' is missing required columns: {missing}. "
            f"Found columns: {columns}"
        )


class TestResponsesCleanRowCount:
    """Test that responses_clean has exactly 312 rows."""

    def test_responses_clean_has_312_rows(self):
        """The responses_clean table must have exactly 312 rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses_clean")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 312, (
            f"Table 'responses_clean' has {count} rows, expected 312. "
            "The fixed script should produce 298 deduplicated non-NULL emails "
            "plus 14 preserved NULL email rows = 312 total."
        )

    def test_sqlite3_cli_returns_312(self):
        """Running sqlite3 CLI count query should return 312."""
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, "SELECT COUNT(*) FROM responses_clean"],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0, (
            f"sqlite3 CLI command failed with return code {result.returncode}: "
            f"{result.stderr}"
        )
        count = int(result.stdout.strip())
        assert count == 312, (
            f"sqlite3 CLI reports {count} rows in responses_clean, expected 312."
        )


class TestNullEmailRowsPreserved:
    """Test that all 14 NULL email rows are preserved."""

    def test_responses_clean_has_14_null_email_rows(self):
        """The responses_clean table must have exactly 14 NULL email rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses_clean WHERE email IS NULL")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 14, (
            f"Table 'responses_clean' has {count} NULL email rows, expected 14. "
            "All NULL email rows should be preserved as distinct unknown respondents. "
            "The bug was that NULL = NULL evaluates to unknown in SQL, "
            "causing the INNER JOIN to drop all NULL rows."
        )

    def test_all_original_null_rows_preserved(self):
        """All original NULL email rows should be in responses_clean."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get IDs of NULL email rows from original table
        cursor.execute("SELECT id FROM responses WHERE email IS NULL ORDER BY id")
        original_null_ids = {row[0] for row in cursor.fetchall()}

        # Get IDs of NULL email rows from cleaned table
        cursor.execute("SELECT id FROM responses_clean WHERE email IS NULL ORDER BY id")
        clean_null_ids = {row[0] for row in cursor.fetchall()}

        conn.close()

        missing_ids = original_null_ids - clean_null_ids
        assert not missing_ids, (
            f"NULL email rows with IDs {missing_ids} are missing from responses_clean. "
            "All 14 NULL email rows should be preserved."
        )


class TestNonNullEmailDeduplication:
    """Test that non-NULL emails are properly deduplicated."""

    def test_responses_clean_has_298_distinct_non_null_emails(self):
        """The responses_clean table must have exactly 298 distinct non-NULL emails."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(DISTINCT email) FROM responses_clean WHERE email IS NOT NULL"
        )
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 298, (
            f"Table 'responses_clean' has {count} distinct non-NULL emails, expected 298. "
            "Each unique non-NULL email should appear exactly once."
        )

    def test_each_non_null_email_appears_exactly_once(self):
        """Each non-NULL email must appear exactly once (no duplicates)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT email, COUNT(*) as c 
            FROM responses_clean 
            WHERE email IS NOT NULL 
            GROUP BY email 
            HAVING c > 1
        """)
        duplicates = cursor.fetchall()
        conn.close()

        assert len(duplicates) == 0, (
            f"Found {len(duplicates)} emails with duplicates in responses_clean: "
            f"{duplicates[:5]}{'...' if len(duplicates) > 5 else ''}. "
            "Each non-NULL email should appear exactly once after deduplication."
        )

    def test_non_null_email_count_is_298(self):
        """There should be exactly 298 non-NULL email rows."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses_clean WHERE email IS NOT NULL")
        count = cursor.fetchone()[0]
        conn.close()
        assert count == 298, (
            f"Table 'responses_clean' has {count} non-NULL email rows, expected 298. "
            "Combined with 14 NULL rows, this should total 312."
        )


class TestDeduplicationUsesEarliestSubmission:
    """Test that deduplication keeps the earliest submission per email."""

    def test_kept_rows_have_earliest_timestamp(self):
        """For each non-NULL email, the kept row should have the earliest submitted_at."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Get the earliest submission for each email from original table
        cursor.execute("""
            SELECT email, MIN(submitted_at) as earliest
            FROM responses 
            WHERE email IS NOT NULL
            GROUP BY email
        """)
        expected_earliest = {row[0]: row[1] for row in cursor.fetchall()}

        # Get what's actually in responses_clean
        cursor.execute("""
            SELECT email, submitted_at 
            FROM responses_clean 
            WHERE email IS NOT NULL
        """)
        actual_timestamps = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        mismatches = []
        for email, expected_ts in expected_earliest.items():
            if email in actual_timestamps:
                actual_ts = actual_timestamps[email]
                if actual_ts != expected_ts:
                    mismatches.append((email, expected_ts, actual_ts))

        assert len(mismatches) == 0, (
            f"Found {len(mismatches)} emails where the kept row is not the earliest: "
            f"{mismatches[:3]}{'...' if len(mismatches) > 3 else ''}. "
            "Deduplication should keep the row with MIN(submitted_at) for each email."
        )

    def test_all_non_null_emails_represented(self):
        """Every distinct non-NULL email from responses should be in responses_clean."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT email FROM responses WHERE email IS NOT NULL")
        original_emails = {row[0] for row in cursor.fetchall()}

        cursor.execute("SELECT DISTINCT email FROM responses_clean WHERE email IS NOT NULL")
        clean_emails = {row[0] for row in cursor.fetchall()}

        conn.close()

        missing_emails = original_emails - clean_emails
        assert len(missing_emails) == 0, (
            f"Found {len(missing_emails)} emails missing from responses_clean: "
            f"{list(missing_emails)[:5]}{'...' if len(missing_emails) > 5 else ''}. "
            "Every distinct non-NULL email should be represented."
        )


class TestSQLScriptFixed:
    """Test that the SQL script has been modified to fix the bug."""

    def test_sql_script_still_exists(self):
        """The clean.sql script should still exist."""
        assert os.path.isfile(SQL_SCRIPT_PATH), (
            f"SQL script {SQL_SCRIPT_PATH} no longer exists. "
            "The script should be fixed, not deleted."
        )

    def test_running_script_produces_correct_result(self):
        """Running the fixed script should produce 312 rows."""
        # First, drop responses_clean if it exists
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS responses_clean")
        conn.commit()
        conn.close()

        # Run the script via sqlite3 CLI
        result = subprocess.run(
            ["sqlite3", DATABASE_PATH, f".read {SQL_SCRIPT_PATH}"],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check the result
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses_clean")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 312, (
            f"Running the script produces {count} rows, expected 312. "
            f"Script stderr: {result.stderr}"
        )

    def test_script_is_idempotent(self):
        """Running the script multiple times should produce the same result."""
        # Run twice
        for _ in range(2):
            subprocess.run(
                ["sqlite3", DATABASE_PATH, f".read {SQL_SCRIPT_PATH}"],
                capture_output=True,
                text=True,
                timeout=30
            )

        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses_clean")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 312, (
            f"After running script twice, got {count} rows, expected 312. "
            "The script should be idempotent (DROP TABLE IF EXISTS should handle this)."
        )


class TestDataIntegrity:
    """Test overall data integrity of the cleaned table."""

    def test_no_data_loss(self):
        """Total unique respondents should be preserved (298 non-NULL + 14 NULL = 312)."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses_clean")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 312, (
            f"responses_clean has {count} rows, expected 312. "
            "No data should be lost: 298 unique non-NULL emails + 14 NULL email rows."
        )

    def test_all_rows_have_valid_data(self):
        """All rows in responses_clean should have valid id, response, and submitted_at."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM responses_clean 
            WHERE id IS NULL OR response IS NULL OR submitted_at IS NULL
        """)
        invalid_count = cursor.fetchone()[0]
        conn.close()

        assert invalid_count == 0, (
            f"Found {invalid_count} rows with NULL id, response, or submitted_at. "
            "Only the email column should have NULL values (for unknown respondents)."
        )

    def test_all_ids_exist_in_original(self):
        """All IDs in responses_clean should exist in the original responses table."""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM responses_clean 
            WHERE id NOT IN (SELECT id FROM responses)
        """)
        orphan_count = cursor.fetchone()[0]
        conn.close()

        assert orphan_count == 0, (
            f"Found {orphan_count} rows in responses_clean with IDs not in responses. "
            "All cleaned rows should come from the original data."
        )
