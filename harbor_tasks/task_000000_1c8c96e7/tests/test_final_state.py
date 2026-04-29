# test_final_state.py
"""
Tests to validate the final state after the student fixes the Python 2 script.
"""

import os
import subprocess
import pytest


class TestFinalState:
    """Validate the final state of the system after the task is performed."""

    def test_generate_script_exists(self):
        """Check that generate.py still exists in the reports directory."""
        script_path = "/home/user/reports/generate.py"
        assert os.path.isfile(script_path), f"Script {script_path} does not exist"

    def test_script_runs_successfully_with_python3(self):
        """Check that running the script with Python 3 exits with code 0."""
        script_path = "/home/user/reports/generate.py"
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            cwd="/home/user/reports"
        )
        assert result.returncode == 0, (
            f"Script should exit with code 0, but got {result.returncode}.\n"
            f"stderr: {result.stderr}\n"
            f"stdout: {result.stdout}"
        )

    def test_script_output_contains_summary_report(self):
        """Check that the script output contains 'Summary Report'."""
        script_path = "/home/user/reports/generate.py"
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            cwd="/home/user/reports"
        )
        assert result.returncode == 0, (
            f"Script failed to run. stderr: {result.stderr}"
        )
        assert "Summary Report" in result.stdout, (
            f"Output should contain 'Summary Report', but got:\n{result.stdout}"
        )

    def test_script_output_contains_total(self):
        """Check that the script output contains 'Total:'."""
        script_path = "/home/user/reports/generate.py"
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            cwd="/home/user/reports"
        )
        assert result.returncode == 0, (
            f"Script failed to run. stderr: {result.stderr}"
        )
        assert "Total:" in result.stdout, (
            f"Output should contain 'Total:', but got:\n{result.stdout}"
        )

    def test_csv_files_unchanged(self):
        """Check that CSV files still exist in the data directory."""
        data_dir = "/home/user/reports/data"
        assert os.path.isdir(data_dir), f"Data directory {data_dir} does not exist"
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        assert len(csv_files) >= 2, (
            f"Expected at least 2 CSV files in {data_dir}, found {len(csv_files)}. "
            "CSV files should remain unchanged."
        )

    def test_script_is_valid_python3_syntax(self):
        """Check that the script has valid Python 3 syntax by compiling it."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        try:
            compile(content, script_path, 'exec')
        except SyntaxError as e:
            pytest.fail(f"Script has invalid Python 3 syntax: {e}")

    def test_script_still_references_data_directory(self):
        """Check that the script still references the data directory."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for references to data directory or CSV reading
        assert "data" in content.lower() or "csv" in content.lower(), (
            "Script should still reference the data directory or CSV files"
        )

    def test_fix_is_in_python_file_not_wrapper(self):
        """Check that the fix is in the Python file itself, not a wrapper script."""
        script_path = "/home/user/reports/generate.py"

        # Check that the file is a regular Python script, not a shell wrapper
        with open(script_path, 'r') as f:
            first_line = f.readline()
            content = f.read()

        # Should not be a shell script that calls 2to3 or preprocesses
        full_content = first_line + content
        assert "2to3" not in full_content, (
            "The fix should be in the Python file itself, not using 2to3 at runtime"
        )
        assert "#!/bin/bash" not in first_line and "#!/bin/sh" not in first_line, (
            "The file should be a Python script, not a shell wrapper"
        )

    def test_script_uses_python3_print_function(self):
        """Check that print statements now use Python 3 function syntax."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        import re
        # Check for Python 2 style print statements (should not exist)
        py2_print_pattern = r'\bprint\s+["\']'
        py2_print_matches = re.findall(py2_print_pattern, content)

        assert len(py2_print_matches) == 0, (
            f"Script still contains {len(py2_print_matches)} Python 2 style print statements. "
            "All print statements should use Python 3 syntax with parentheses."
        )

        # Check that print function calls exist (with parentheses)
        py3_print_pattern = r'\bprint\s*\('
        py3_print_matches = re.findall(py3_print_pattern, content)

        assert len(py3_print_matches) >= 4, (
            f"Expected at least 4 Python 3 style print() calls, found {len(py3_print_matches)}"
        )

    def test_no_syntax_error_on_execution(self):
        """Explicitly verify no SyntaxError occurs when running the script."""
        script_path = "/home/user/reports/generate.py"
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            cwd="/home/user/reports"
        )

        assert "SyntaxError" not in result.stderr, (
            f"Script still has syntax errors:\n{result.stderr}"
        )
