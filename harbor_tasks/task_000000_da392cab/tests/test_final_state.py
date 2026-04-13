# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student has
completed the log analysis task to find all 404 errors.
"""

import os
import pytest


class TestAnalysisDirectoryExists:
    """Tests for the /home/user/analysis directory."""

    def test_analysis_directory_exists(self):
        """The analysis directory must exist."""
        path = "/home/user/analysis"
        assert os.path.isdir(path), (
            f"Directory {path} does not exist. "
            "The task requires creating the /home/user/analysis directory."
        )

    def test_analysis_directory_is_directory(self):
        """The analysis path must be a directory, not a file."""
        path = "/home/user/analysis"
        assert not os.path.isfile(path), (
            f"{path} exists but is a file, not a directory. "
            "The analysis path must be a directory."
        )


class TestOutputFileExists:
    """Tests for the existence of the output file."""

    def test_404_errors_file_exists(self):
        """The 404_errors.txt file must exist."""
        path = "/home/user/analysis/404_errors.txt"
        assert os.path.exists(path), (
            f"File {path} does not exist. "
            "The task requires creating this file with all 404 error entries."
        )

    def test_404_errors_file_is_file(self):
        """The 404_errors.txt path must be a regular file."""
        path = "/home/user/analysis/404_errors.txt"
        assert os.path.isfile(path), (
            f"{path} exists but is not a regular file. "
            "The output must be a regular file."
        )


class TestOutputFileContent:
    """Tests for the content of the 404_errors.txt file."""

    def test_file_has_exactly_4_lines(self):
        """The output file must contain exactly 4 lines."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            lines = [line for line in f.read().splitlines() if line.strip()]

        assert len(lines) == 4, (
            f"Expected exactly 4 lines in {path}, but found {len(lines)}. "
            f"There are exactly 4 log entries with ' 404 ' pattern across all .log files."
        )

    def test_all_lines_contain_404_pattern(self):
        """Every line in the output file must contain the ' 404 ' pattern."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            lines = [line for line in f.read().splitlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            assert ' 404 ' in line, (
                f"Line {i} in {path} does not contain ' 404 ' pattern: {line!r}"
            )

    def test_contains_missing_page_entry(self):
        """The output must contain the missing-page.html 404 entry."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert 'missing-page.html' in content, (
            f"File {path} is missing the 404 entry for missing-page.html from access_2024_01_15.log"
        )
        assert '192.168.1.101' in content, (
            f"File {path} is missing the 404 entry with IP 192.168.1.101"
        )

    def test_contains_old_link_entry(self):
        """The output must contain the old-link.html 404 entry."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert 'old-link.html' in content, (
            f"File {path} is missing the 404 entry for old-link.html from access_2024_01_15.log"
        )
        assert '192.168.1.103' in content, (
            f"File {path} is missing the 404 entry with IP 192.168.1.103"
        )

    def test_contains_nonexistent_entry(self):
        """The output must contain the /nonexistent 404 entry."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert '/nonexistent' in content, (
            f"File {path} is missing the 404 entry for /nonexistent from access_2024_01_16.log"
        )
        assert '10.0.0.51' in content, (
            f"File {path} is missing the 404 entry with IP 10.0.0.51"
        )

    def test_contains_deleted_resource_entry(self):
        """The output must contain the /deleted-resource 404 entry."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert '/deleted-resource' in content, (
            f"File {path} is missing the 404 entry for /deleted-resource from access_2024_01_17.log"
        )
        assert '172.16.0.26' in content, (
            f"File {path} is missing the 404 entry with IP 172.16.0.26"
        )


class TestOutputFileExclusions:
    """Tests to verify that incorrect content is not included."""

    def test_does_not_contain_notes_txt_content(self):
        """The output must not contain content from notes.txt."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        # The notes.txt contains "Remember to check 404 errors weekly."
        assert 'Remember to check' not in content, (
            f"File {path} incorrectly contains content from notes.txt. "
            "Only .log files should be searched."
        )
        assert 'weekly' not in content, (
            f"File {path} incorrectly contains content from notes.txt. "
            "Only .log files should be searched."
        )

    def test_does_not_contain_200_status_entries(self):
        """The output must not contain any 200 status code entries."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            lines = f.read().splitlines()

        for line in lines:
            if line.strip():
                assert ' 200 ' not in line, (
                    f"File {path} incorrectly contains a 200 status entry: {line!r}"
                )

    def test_does_not_contain_500_status_entries(self):
        """The output must not contain any 500 status code entries."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            lines = f.read().splitlines()

        for line in lines:
            if line.strip():
                assert ' 500 ' not in line, (
                    f"File {path} incorrectly contains a 500 status entry: {line!r}"
                )

    def test_does_not_contain_index_html(self):
        """The output must not contain the index.html entry (200 status)."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert 'index.html' not in content, (
            f"File {path} incorrectly contains the index.html entry which has 200 status."
        )

    def test_does_not_contain_about_html(self):
        """The output must not contain the about.html entry (200 status)."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            content = f.read()

        assert 'about.html' not in content, (
            f"File {path} incorrectly contains the about.html entry which has 200 status."
        )


class TestOutputFileFormat:
    """Tests for the format of the output file."""

    def test_lines_are_valid_log_entries(self):
        """Each line should look like a valid Apache log entry."""
        path = "/home/user/analysis/404_errors.txt"
        with open(path, 'r') as f:
            lines = [line for line in f.read().splitlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            # Check for basic Apache log format components
            assert ' - - [' in line, (
                f"Line {i} in {path} does not appear to be a valid Apache log entry: {line!r}"
            )
            assert 'HTTP/1.1"' in line, (
                f"Line {i} in {path} does not appear to be a valid Apache log entry: {line!r}"
            )

    def test_file_is_readable(self):
        """The output file must be readable."""
        path = "/home/user/analysis/404_errors.txt"
        try:
            with open(path, 'r') as f:
                content = f.read()
            assert isinstance(content, str), (
                f"Could not read {path} as text"
            )
        except Exception as e:
            pytest.fail(f"Failed to read {path}: {e}")


class TestSourceFilesUnmodified:
    """Tests to verify source log files were not modified."""

    def test_source_log_files_still_exist(self):
        """All original .log files should still exist."""
        log_dir = "/home/user/server_logs"
        expected_files = [
            "access_2024_01_15.log",
            "access_2024_01_16.log",
            "access_2024_01_17.log"
        ]

        for filename in expected_files:
            filepath = os.path.join(log_dir, filename)
            assert os.path.isfile(filepath), (
                f"Source file {filepath} no longer exists. "
                "The original log files should not be deleted."
            )

    def test_notes_txt_still_exists(self):
        """The notes.txt file should still exist."""
        path = "/home/user/server_logs/notes.txt"
        assert os.path.isfile(path), (
            f"File {path} no longer exists. "
            "The original files should not be deleted."
        )
