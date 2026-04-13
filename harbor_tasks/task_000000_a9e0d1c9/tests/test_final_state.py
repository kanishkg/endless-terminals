# test_final_state.py
"""
Tests to validate the FINAL state of the operating system/filesystem
AFTER the student has completed the web scraping task.
"""

import pytest
import os
import re


class TestFinalState:
    """Test the final state after the scraping task is completed."""

    # Define paths as class constants for consistency
    SCRAPED_DATA_DIR = "/home/user/project/scraped_data"
    HN_TITLES_PATH = "/home/user/project/scraped_data/hn_titles.txt"
    SCRAPE_LOG_PATH = "/home/user/project/scraped_data/scrape_log.txt"

    def test_scraped_data_directory_exists(self):
        """Verify that the scraped_data directory was created."""
        assert os.path.isdir(self.SCRAPED_DATA_DIR), (
            f"Directory {self.SCRAPED_DATA_DIR} does not exist. "
            "The student should have created this directory structure."
        )

    def test_hn_titles_file_exists(self):
        """Verify that the hn_titles.txt file was created."""
        assert os.path.isfile(self.HN_TITLES_PATH), (
            f"File {self.HN_TITLES_PATH} does not exist. "
            "The student should have created this file with the scraped titles."
        )

    def test_scrape_log_file_exists(self):
        """Verify that the scrape_log.txt file was created."""
        assert os.path.isfile(self.SCRAPE_LOG_PATH), (
            f"File {self.SCRAPE_LOG_PATH} does not exist. "
            "The student should have created this log file."
        )

    def test_hn_titles_has_exactly_5_lines(self):
        """Verify that hn_titles.txt contains exactly 5 lines."""
        assert os.path.isfile(self.HN_TITLES_PATH), (
            f"File {self.HN_TITLES_PATH} does not exist."
        )

        with open(self.HN_TITLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Remove trailing whitespace/newlines and split
        lines = content.rstrip('\n').split('\n')

        # Filter out any completely empty lines that might result from splitting
        non_empty_lines = [line for line in lines if line.strip()]

        assert len(non_empty_lines) == 5, (
            f"hn_titles.txt should contain exactly 5 lines, but found {len(non_empty_lines)} non-empty lines. "
            f"Content:\n{content}"
        )

    def test_hn_titles_line_format(self):
        """Verify that each line in hn_titles.txt follows the correct format."""
        assert os.path.isfile(self.HN_TITLES_PATH), (
            f"File {self.HN_TITLES_PATH} does not exist."
        )

        with open(self.HN_TITLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.rstrip('\n').split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        # Check each line matches the expected pattern
        for i, line in enumerate(non_empty_lines, start=1):
            expected_prefix = f"{i}. "
            assert line.startswith(expected_prefix), (
                f"Line {i} should start with '{expected_prefix}' but got: '{line[:20]}...'"
            )

            # Verify there's actual content after the number prefix
            title_part = line[len(expected_prefix):]
            assert len(title_part.strip()) > 0, (
                f"Line {i} has no title content after the number prefix. Line: '{line}'"
            )

    def test_hn_titles_numbered_correctly(self):
        """Verify that lines are numbered 1 through 5 in order."""
        assert os.path.isfile(self.HN_TITLES_PATH), (
            f"File {self.HN_TITLES_PATH} does not exist."
        )

        with open(self.HN_TITLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.rstrip('\n').split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        expected_numbers = ["1", "2", "3", "4", "5"]

        for i, line in enumerate(non_empty_lines):
            # Extract the number at the start of the line
            match = re.match(r'^(\d+)\.\s', line)
            assert match is not None, (
                f"Line {i+1} does not match the expected format 'NUMBER. TITLE'. "
                f"Got: '{line}'"
            )

            actual_number = match.group(1)
            expected_number = expected_numbers[i]
            assert actual_number == expected_number, (
                f"Line {i+1} should be numbered '{expected_number}' but is numbered '{actual_number}'. "
                f"Line: '{line}'"
            )

    def test_hn_titles_no_trailing_empty_lines(self):
        """Verify that hn_titles.txt has no trailing empty lines or extra whitespace."""
        assert os.path.isfile(self.HN_TITLES_PATH), (
            f"File {self.HN_TITLES_PATH} does not exist."
        )

        with open(self.HN_TITLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # Check for multiple trailing newlines
        if content.endswith('\n\n'):
            pytest.fail(
                "hn_titles.txt has trailing empty lines. "
                "There should be no empty lines after the 5th title."
            )

        # Split and check
        lines = content.split('\n')

        # If file ends with single newline, last element will be empty string
        # That's acceptable, but multiple empty strings at end are not
        trailing_empty = 0
        for line in reversed(lines):
            if line == '':
                trailing_empty += 1
            else:
                break

        assert trailing_empty <= 1, (
            f"hn_titles.txt has {trailing_empty} trailing empty lines. "
            "There should be at most one trailing newline (no empty lines after line 5)."
        )

    def test_scrape_log_line_1_status(self):
        """Verify that scrape_log.txt line 1 is exactly 'STATUS: SUCCESS'."""
        assert os.path.isfile(self.SCRAPE_LOG_PATH), (
            f"File {self.SCRAPE_LOG_PATH} does not exist."
        )

        with open(self.SCRAPE_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.read().rstrip('\n').split('\n')

        assert len(lines) >= 1, (
            f"scrape_log.txt should have at least 1 line, but is empty."
        )

        expected_line_1 = "STATUS: SUCCESS"
        actual_line_1 = lines[0].rstrip()

        assert actual_line_1 == expected_line_1, (
            f"Line 1 of scrape_log.txt should be exactly '{expected_line_1}' "
            f"but got: '{actual_line_1}'"
        )

    def test_scrape_log_line_2_items_scraped(self):
        """Verify that scrape_log.txt line 2 is exactly 'ITEMS_SCRAPED: 5'."""
        assert os.path.isfile(self.SCRAPE_LOG_PATH), (
            f"File {self.SCRAPE_LOG_PATH} does not exist."
        )

        with open(self.SCRAPE_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.read().rstrip('\n').split('\n')

        assert len(lines) >= 2, (
            f"scrape_log.txt should have at least 2 lines, but has {len(lines)}."
        )

        expected_line_2 = "ITEMS_SCRAPED: 5"
        actual_line_2 = lines[1].rstrip()

        assert actual_line_2 == expected_line_2, (
            f"Line 2 of scrape_log.txt should be exactly '{expected_line_2}' "
            f"but got: '{actual_line_2}'"
        )

    def test_scrape_log_line_3_source(self):
        """Verify that scrape_log.txt line 3 is exactly 'SOURCE: https://news.ycombinator.com'."""
        assert os.path.isfile(self.SCRAPE_LOG_PATH), (
            f"File {self.SCRAPE_LOG_PATH} does not exist."
        )

        with open(self.SCRAPE_LOG_PATH, "r", encoding="utf-8") as f:
            lines = f.read().rstrip('\n').split('\n')

        assert len(lines) >= 3, (
            f"scrape_log.txt should have at least 3 lines, but has {len(lines)}."
        )

        expected_line_3 = "SOURCE: https://news.ycombinator.com"
        actual_line_3 = lines[2].rstrip()

        assert actual_line_3 == expected_line_3, (
            f"Line 3 of scrape_log.txt should be exactly '{expected_line_3}' "
            f"but got: '{actual_line_3}'"
        )

    def test_scrape_log_has_exactly_3_lines(self):
        """Verify that scrape_log.txt contains exactly 3 lines."""
        assert os.path.isfile(self.SCRAPE_LOG_PATH), (
            f"File {self.SCRAPE_LOG_PATH} does not exist."
        )

        with open(self.SCRAPE_LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.rstrip('\n').split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        assert len(non_empty_lines) == 3, (
            f"scrape_log.txt should contain exactly 3 lines, but found {len(non_empty_lines)}. "
            f"Content:\n{content}"
        )

    def test_titles_contain_meaningful_content(self):
        """Verify that the scraped titles appear to be real content (not error messages)."""
        assert os.path.isfile(self.HN_TITLES_PATH), (
            f"File {self.HN_TITLES_PATH} does not exist."
        )

        with open(self.HN_TITLES_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.rstrip('\n').split('\n')

        # Check that titles are reasonably long (not just placeholders)
        for i, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            # Extract title part (after "N. ")
            match = re.match(r'^\d+\.\s+(.+)$', line)
            if match:
                title = match.group(1)

                # Title should be at least a few characters
                assert len(title) >= 3, (
                    f"Title on line {i} seems too short to be a real title: '{title}'"
                )

                # Title shouldn't be common error indicators
                error_indicators = ['error', 'failed', 'null', 'undefined', 'none', 'n/a']
                title_lower = title.lower().strip()

                for indicator in error_indicators:
                    if title_lower == indicator:
                        pytest.fail(
                            f"Title on line {i} appears to be an error indicator: '{title}'. "
                            "The scraping may have failed to extract actual titles."
                        )
