# test_initial_state.py
"""
Tests to validate the initial state before the student fixes the Python 2 script.
"""

import os
import subprocess
import pytest


class TestInitialState:
    """Validate the initial state of the system before the task is performed."""

    def test_reports_directory_exists(self):
        """Check that /home/user/reports/ directory exists."""
        reports_dir = "/home/user/reports"
        assert os.path.isdir(reports_dir), f"Directory {reports_dir} does not exist"

    def test_generate_script_exists(self):
        """Check that generate.py exists in the reports directory."""
        script_path = "/home/user/reports/generate.py"
        assert os.path.isfile(script_path), f"Script {script_path} does not exist"

    def test_data_directory_exists(self):
        """Check that the data directory exists."""
        data_dir = "/home/user/reports/data"
        assert os.path.isdir(data_dir), f"Data directory {data_dir} does not exist"

    def test_csv_files_present(self):
        """Check that CSV files are present in the data directory."""
        data_dir = "/home/user/reports/data"
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        assert len(csv_files) >= 2, f"Expected at least 2 CSV files in {data_dir}, found {len(csv_files)}"

    def test_python3_available(self):
        """Check that Python 3 is installed and available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python 3 is not available on this system"
        # Check it's Python 3.10+
        version_output = result.stdout.strip()
        assert "Python 3" in version_output, f"Expected Python 3, got: {version_output}"

    def test_python2_not_available(self):
        """Check that Python 2 interpreter is not available."""
        result = subprocess.run(
            ["which", "python2"],
            capture_output=True,
            text=True
        )
        # python2 should not be found
        assert result.returncode != 0, "Python 2 should not be available on this system"

    def test_script_contains_python2_print_statements(self):
        """Check that the script contains Python 2 style print statements (no parentheses)."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for Python 2 print statements without parentheses
        # Looking for patterns like 'print "something"' or "print 'something'"
        import re
        # Match print followed by space and then a quote (not parenthesis)
        py2_print_pattern = r'\bprint\s+["\']'
        py2_print_matches = re.findall(py2_print_pattern, content)

        assert len(py2_print_matches) > 0, (
            "Script should contain Python 2 style print statements (print \"...\"), "
            "but none were found"
        )

    def test_script_has_exactly_four_print_statements(self):
        """Check that the script contains exactly 4 print statements needing fixes."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        import re
        # Count print statements (Python 2 style without parentheses)
        # This matches 'print' followed by whitespace and not an opening paren
        py2_print_pattern = r'\bprint\s+(?!\()'
        py2_print_matches = re.findall(py2_print_pattern, content)

        assert len(py2_print_matches) == 4, (
            f"Expected exactly 4 Python 2 print statements, found {len(py2_print_matches)}"
        )

    def test_script_fails_with_python3(self):
        """Check that running the script with Python 3 fails with SyntaxError."""
        script_path = "/home/user/reports/generate.py"
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            cwd="/home/user/reports"
        )
        assert result.returncode != 0, (
            "Script should fail when run with Python 3 (due to Python 2 syntax)"
        )
        # Check for SyntaxError in stderr
        assert "SyntaxError" in result.stderr, (
            f"Expected SyntaxError in output, got: {result.stderr}"
        )

    def test_reports_directory_writable(self):
        """Check that the reports directory is writable."""
        reports_dir = "/home/user/reports"
        assert os.access(reports_dir, os.W_OK), f"Directory {reports_dir} is not writable"

    def test_script_contains_summary_report_string(self):
        """Check that the script contains 'Summary Report' string."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        assert "Summary Report" in content, (
            "Script should contain 'Summary Report' string"
        )

    def test_script_contains_total_string(self):
        """Check that the script contains 'Total:' string."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        assert "Total:" in content, (
            "Script should contain 'Total:' string"
        )

    def test_script_reads_from_data_directory(self):
        """Check that the script references the data directory."""
        script_path = "/home/user/reports/generate.py"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for references to data directory or CSV reading
        assert "data" in content.lower() or "csv" in content.lower(), (
            "Script should reference the data directory or CSV files"
        )
