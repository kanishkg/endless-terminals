# test_final_state.py
"""
Tests to validate the final state of the filesystem after the student
has completed the JSON to CSV conversion task.
"""

import os
import pytest


class TestFinalState:
    """Tests to verify the final filesystem state after task execution."""

    def test_output_directory_exists(self):
        """Verify that /home/user/output/ directory was created."""
        output_dir = "/home/user/output"
        assert os.path.exists(output_dir), (
            f"Directory {output_dir} does not exist. "
            "The output directory must be created as part of the task."
        )
        assert os.path.isdir(output_dir), (
            f"{output_dir} exists but is not a directory. "
            "Expected a directory at this path."
        )

    def test_output_csv_file_exists(self):
        """Verify that the output CSV file exists at the expected location."""
        output_file = "/home/user/output/users.csv"
        assert os.path.exists(output_file), (
            f"Output file {output_file} does not exist. "
            "The users.csv file must be created at /home/user/output/users.csv"
        )
        assert os.path.isfile(output_file), (
            f"{output_file} exists but is not a regular file. "
            "Expected a file at this path."
        )

    def test_output_csv_is_readable(self):
        """Verify that the output CSV file has read permissions."""
        output_file = "/home/user/output/users.csv"
        assert os.access(output_file, os.R_OK), (
            f"File {output_file} is not readable. "
            "The output file must have read permissions."
        )

    def test_csv_has_exactly_four_lines(self):
        """Verify that the CSV file has exactly 4 lines (1 header + 3 data rows)."""
        output_file = "/home/user/output/users.csv"
        with open(output_file, 'r') as f:
            lines = f.readlines()

        # Count non-empty lines (handling potential trailing newline)
        content = open(output_file, 'r').read()
        # Split by newline and filter out empty strings that might result from trailing newline
        actual_lines = [line for line in content.split('\n') if line]

        assert len(actual_lines) == 4, (
            f"The CSV file should have exactly 4 lines (1 header + 3 data rows). "
            f"Found {len(actual_lines)} non-empty lines.\n"
            f"Content:\n{content}"
        )

    def test_csv_header_row_is_correct(self):
        """Verify that the first line is exactly: id,name,email,signup_date"""
        output_file = "/home/user/output/users.csv"
        expected_header = "id,name,email,signup_date"

        with open(output_file, 'r') as f:
            first_line = f.readline().rstrip('\n\r')

        assert first_line == expected_header, (
            f"The header row is incorrect.\n"
            f"Expected: '{expected_header}'\n"
            f"Found:    '{first_line}'"
        )

    def test_csv_line_2_is_correct(self):
        """Verify that line 2 is exactly: 1,Alice Johnson,alice@example.com,2024-01-15"""
        output_file = "/home/user/output/users.csv"
        expected_line = "1,Alice Johnson,alice@example.com,2024-01-15"

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 2, (
            f"The CSV file has fewer than 2 lines. Cannot check line 2."
        )

        actual_line = lines[1].rstrip('\n\r')
        assert actual_line == expected_line, (
            f"Line 2 (first data row) is incorrect.\n"
            f"Expected: '{expected_line}'\n"
            f"Found:    '{actual_line}'"
        )

    def test_csv_line_3_is_correct(self):
        """Verify that line 3 is exactly: 2,Bob Smith,bob@example.com,2024-02-20"""
        output_file = "/home/user/output/users.csv"
        expected_line = "2,Bob Smith,bob@example.com,2024-02-20"

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 3, (
            f"The CSV file has fewer than 3 lines. Cannot check line 3."
        )

        actual_line = lines[2].rstrip('\n\r')
        assert actual_line == expected_line, (
            f"Line 3 (second data row) is incorrect.\n"
            f"Expected: '{expected_line}'\n"
            f"Found:    '{actual_line}'"
        )

    def test_csv_line_4_is_correct(self):
        """Verify that line 4 is exactly: 3,Carol Davis,carol@example.com,2024-03-10"""
        output_file = "/home/user/output/users.csv"
        expected_line = "3,Carol Davis,carol@example.com,2024-03-10"

        with open(output_file, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 4, (
            f"The CSV file has fewer than 4 lines. Cannot check line 4."
        )

        actual_line = lines[3].rstrip('\n\r')
        assert actual_line == expected_line, (
            f"Line 4 (third data row) is incorrect.\n"
            f"Expected: '{expected_line}'\n"
            f"Found:    '{actual_line}'"
        )

    def test_csv_complete_content(self):
        """Verify the complete content of the CSV file matches expected output."""
        output_file = "/home/user/output/users.csv"

        expected_content = """id,name,email,signup_date
1,Alice Johnson,alice@example.com,2024-01-15
2,Bob Smith,bob@example.com,2024-02-20
3,Carol Davis,carol@example.com,2024-03-10
"""

        with open(output_file, 'r') as f:
            actual_content = f.read()

        # Normalize line endings for comparison
        expected_normalized = expected_content.replace('\r\n', '\n')
        actual_normalized = actual_content.replace('\r\n', '\n')

        assert actual_normalized == expected_normalized, (
            f"The complete CSV content does not match expected output.\n"
            f"Expected:\n{repr(expected_normalized)}\n"
            f"Found:\n{repr(actual_normalized)}"
        )

    def test_csv_no_extra_whitespace(self):
        """Verify there are no extra spaces after commas in the CSV."""
        output_file = "/home/user/output/users.csv"

        with open(output_file, 'r') as f:
            content = f.read()

        # Check for ", " pattern which would indicate space after comma
        if ", " in content:
            # Find the line with the issue
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if ", " in line:
                    pytest.fail(
                        f"Line {i} contains space(s) after comma(s): '{line}'\n"
                        f"The CSV should have no spaces after commas."
                    )

    def test_csv_no_unnecessary_quotes(self):
        """Verify there are no unnecessary quotes around fields."""
        output_file = "/home/user/output/users.csv"

        with open(output_file, 'r') as f:
            content = f.read()

        # None of the expected fields contain commas, so there should be no quotes
        if '"' in content:
            pytest.fail(
                f"The CSV contains quote characters but none of the fields "
                f"contain commas, so quotes should not be present.\n"
                f"Content:\n{content}"
            )

    def test_csv_ends_with_newline(self):
        """Verify the CSV file ends with a newline character."""
        output_file = "/home/user/output/users.csv"

        with open(output_file, 'r') as f:
            content = f.read()

        assert content.endswith('\n'), (
            f"The CSV file should end with a newline character after the last data row.\n"
            f"Last characters: {repr(content[-20:] if len(content) >= 20 else content)}"
        )

    def test_csv_no_trailing_empty_lines(self):
        """Verify there are no extra trailing empty lines."""
        output_file = "/home/user/output/users.csv"

        with open(output_file, 'r') as f:
            content = f.read()

        # Should end with exactly one newline after the last data row
        # Check for multiple trailing newlines
        if content.endswith('\n\n'):
            pytest.fail(
                f"The CSV file has extra trailing empty lines.\n"
                f"The file should end with exactly one newline after the last data row."
            )

    def test_original_json_file_still_exists(self):
        """Verify that the original JSON file was not deleted or modified."""
        json_file = "/home/user/data/users.json"
        assert os.path.exists(json_file), (
            f"Original input file {json_file} no longer exists. "
            "The input file should not be deleted during the conversion."
        )
