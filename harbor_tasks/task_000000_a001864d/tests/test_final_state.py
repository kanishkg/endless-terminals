# test_final_state.py
"""
Tests to validate the final state of the system after the student
has commented out the log rotation cron job in /etc/cron.d/logrotate-daily.
"""

import os
import subprocess
import pytest


CRON_FILE_PATH = "/etc/cron.d/logrotate-daily"


class TestFinalState:
    """Tests to verify the system is in the expected final state."""

    def test_cron_file_still_exists(self):
        """Verify that /etc/cron.d/logrotate-daily still exists (not deleted)."""
        assert os.path.exists(CRON_FILE_PATH), (
            f"File {CRON_FILE_PATH} does not exist. "
            "The task requires commenting out the line, not deleting the file."
        )

    def test_cron_file_is_regular_file(self):
        """Verify that /etc/cron.d/logrotate-daily is still a regular file."""
        assert os.path.isfile(CRON_FILE_PATH), (
            f"{CRON_FILE_PATH} exists but is not a regular file. "
            "The file should remain a regular file."
        )

    def test_cron_file_not_empty(self):
        """Verify that the cron file is not empty."""
        file_size = os.path.getsize(CRON_FILE_PATH)
        assert file_size > 0, (
            f"{CRON_FILE_PATH} is empty. "
            "The file should still contain the commented-out cron job."
        )

    def test_original_comment_preserved(self):
        """Verify the original '# Daily log rotation' comment is preserved."""
        with open(CRON_FILE_PATH, 'r') as f:
            content = f.read()

        assert "# Daily log rotation" in content, (
            f"{CRON_FILE_PATH} does not contain the original comment "
            "'# Daily log rotation'. The original comment should be preserved."
        )

    def test_logrotate_text_still_present(self):
        """Verify that 'logrotate' text is still present in the file (just commented)."""
        with open(CRON_FILE_PATH, 'r') as f:
            content = f.read()

        assert "logrotate" in content, (
            f"{CRON_FILE_PATH} does not contain 'logrotate'. "
            "The logrotate command should still be in the file, just commented out."
        )

    def test_no_uncommented_logrotate_lines(self):
        """Verify there are no uncommented lines containing 'logrotate'."""
        # Use grep to check for uncommented logrotate lines
        result = subprocess.run(
            ["grep", "-E", "^[^#]*logrotate", CRON_FILE_PATH],
            capture_output=True,
            text=True
        )

        # grep returns 0 if matches found, 1 if no matches, 2 if error
        assert result.returncode == 1, (
            f"Found uncommented logrotate line(s) in {CRON_FILE_PATH}. "
            f"The cron job should be commented out. Found: {result.stdout.strip()}"
        )

    def test_cron_schedule_line_is_commented(self):
        """Verify the '0 2 * * *' cron schedule line is now commented out."""
        with open(CRON_FILE_PATH, 'r') as f:
            lines = f.readlines()

        # Check that any line containing "0 2" and "logrotate" starts with #
        for line in lines:
            stripped = line.strip()
            if "0 2" in stripped and "logrotate" in stripped.lower():
                assert stripped.startswith("#"), (
                    f"Found uncommented cron schedule line: '{stripped}'. "
                    "The line should be commented out (start with #)."
                )

    def test_cron_job_content_preserved_but_commented(self):
        """Verify the cron job content is preserved but commented."""
        with open(CRON_FILE_PATH, 'r') as f:
            content = f.read()

        # The file should still contain the key parts of the cron job
        assert "0 2 * * *" in content, (
            f"{CRON_FILE_PATH} does not contain '0 2 * * *'. "
            "The cron schedule should still be in the file, just commented."
        )

    def test_no_active_cron_entries(self):
        """Verify there are no active (uncommented) cron entries in the file."""
        with open(CRON_FILE_PATH, 'r') as f:
            lines = f.readlines()

        # A cron entry line typically starts with a number (minute field)
        # or special string like @daily, @hourly, etc.
        for line in lines:
            stripped = line.strip()
            # Skip empty lines and comment lines
            if not stripped or stripped.startswith("#"):
                continue
            # Check if this looks like a cron entry (starts with digit or @)
            if stripped[0].isdigit() or stripped.startswith("@"):
                pytest.fail(
                    f"Found active cron entry in {CRON_FILE_PATH}: '{stripped}'. "
                    "All cron entries should be commented out."
                )

    def test_file_has_reasonable_structure(self):
        """Verify the file has a reasonable structure after modification."""
        with open(CRON_FILE_PATH, 'r') as f:
            lines = f.readlines()

        # Should have at least 2 lines (comment + commented cron job)
        non_empty_lines = [l for l in lines if l.strip()]
        assert len(non_empty_lines) >= 2, (
            f"{CRON_FILE_PATH} has fewer than 2 non-empty lines. "
            "Expected at least the header comment and the commented-out cron job."
        )
