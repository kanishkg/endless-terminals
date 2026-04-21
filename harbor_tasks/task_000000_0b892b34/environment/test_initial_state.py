# test_initial_state.py
"""
Tests to validate the initial state of the operating system / filesystem
before the student performs the LP audit task.
"""

import pytest
import os
import csv


class TestAuditDirectoryExists:
    """Test that the audit directory exists and is writable."""

    def test_audit_directory_exists(self):
        """The /home/user/audit directory must exist."""
        audit_dir = "/home/user/audit"
        assert os.path.exists(audit_dir), (
            f"Directory {audit_dir} does not exist. "
            "The audit directory must be present before running the task."
        )

    def test_audit_directory_is_directory(self):
        """The /home/user/audit path must be a directory."""
        audit_dir = "/home/user/audit"
        assert os.path.isdir(audit_dir), (
            f"{audit_dir} exists but is not a directory. "
            "It must be a directory for the audit task."
        )

    def test_audit_directory_is_writable(self):
        """The /home/user/audit directory must be writable."""
        audit_dir = "/home/user/audit"
        assert os.access(audit_dir, os.W_OK), (
            f"Directory {audit_dir} is not writable. "
            "The audit directory must be writable to create the compliance report."
        )


class TestConstraintsFileExists:
    """Test that the constraints.csv file exists and has proper format."""

    def test_constraints_file_exists(self):
        """The constraints.csv file must exist."""
        constraints_file = "/home/user/audit/constraints.csv"
        assert os.path.exists(constraints_file), (
            f"File {constraints_file} does not exist. "
            "The constraints definition file is required for the audit."
        )

    def test_constraints_file_is_file(self):
        """The constraints.csv path must be a regular file."""
        constraints_file = "/home/user/audit/constraints.csv"
        assert os.path.isfile(constraints_file), (
            f"{constraints_file} exists but is not a regular file. "
            "It must be a CSV file containing constraint definitions."
        )

    def test_constraints_file_is_readable(self):
        """The constraints.csv file must be readable."""
        constraints_file = "/home/user/audit/constraints.csv"
        assert os.access(constraints_file, os.R_OK), (
            f"File {constraints_file} is not readable. "
            "The constraints file must be readable for the audit."
        )

    def test_constraints_file_has_header(self):
        """The constraints.csv file must have the correct header."""
        constraints_file = "/home/user/audit/constraints.csv"
        with open(constraints_file, 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None)

        assert header is not None, (
            f"File {constraints_file} is empty. "
            "It must contain a header row and constraint definitions."
        )

        expected_header = ['constraint_name', 'type', 'coefficients', 'rhs']
        assert header == expected_header, (
            f"File {constraints_file} has incorrect header. "
            f"Expected: {expected_header}, Got: {header}"
        )

    def test_constraints_file_has_data_rows(self):
        """The constraints.csv file must have at least one data row."""
        constraints_file = "/home/user/audit/constraints.csv"
        with open(constraints_file, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header
            first_data_row = next(reader, None)

        assert first_data_row is not None, (
            f"File {constraints_file} has no data rows. "
            "It must contain constraint definitions after the header."
        )

    def test_constraints_have_valid_types(self):
        """All constraints must have valid type values (LE, GE, or EQ)."""
        constraints_file = "/home/user/audit/constraints.csv"
        valid_types = {'LE', 'GE', 'EQ'}

        with open(constraints_file, 'r') as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                constraint_type = row.get('type', '').strip()
                assert constraint_type in valid_types, (
                    f"Row {row_num} in {constraints_file} has invalid type '{constraint_type}'. "
                    f"Valid types are: {valid_types}"
                )


class TestSolverOutputFileExists:
    """Test that the solver_output.dat file exists and has proper format."""

    def test_solver_output_file_exists(self):
        """The solver_output.dat file must exist."""
        solver_file = "/home/user/audit/solver_output.dat"
        assert os.path.exists(solver_file), (
            f"File {solver_file} does not exist. "
            "The solver output file is required for the audit."
        )

    def test_solver_output_file_is_file(self):
        """The solver_output.dat path must be a regular file."""
        solver_file = "/home/user/audit/solver_output.dat"
        assert os.path.isfile(solver_file), (
            f"{solver_file} exists but is not a regular file. "
            "It must be a data file containing solver output."
        )

    def test_solver_output_file_is_readable(self):
        """The solver_output.dat file must be readable."""
        solver_file = "/home/user/audit/solver_output.dat"
        assert os.access(solver_file, os.R_OK), (
            f"File {solver_file} is not readable. "
            "The solver output file must be readable for the audit."
        )

    def test_solver_output_file_not_empty(self):
        """The solver_output.dat file must not be empty."""
        solver_file = "/home/user/audit/solver_output.dat"
        file_size = os.path.getsize(solver_file)
        assert file_size > 0, (
            f"File {solver_file} is empty. "
            "It must contain solver output values."
        )

    def test_solver_output_has_variable_assignments(self):
        """The solver_output.dat file must contain variable assignments in format 'xN = value'."""
        solver_file = "/home/user/audit/solver_output.dat"

        with open(solver_file, 'r') as f:
            content = f.read()

        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
        assert len(lines) > 0, (
            f"File {solver_file} contains no non-empty lines. "
            "It must contain variable assignments."
        )

        # Check that at least one line matches the expected format
        import re
        pattern = r'^x\d+\s*=\s*[\d.]+$'
        matching_lines = [line for line in lines if re.match(pattern, line)]

        assert len(matching_lines) > 0, (
            f"File {solver_file} contains no lines matching format 'xN = value'. "
            f"Found lines: {lines[:5]}..."
        )

    def test_solver_output_has_six_variables(self):
        """The solver_output.dat file must contain exactly 6 variable assignments (x1 through x6)."""
        solver_file = "/home/user/audit/solver_output.dat"

        with open(solver_file, 'r') as f:
            content = f.read()

        import re
        variables_found = set()
        for line in content.strip().split('\n'):
            line = line.strip()
            match = re.match(r'^(x\d+)\s*=\s*[\d.]+$', line)
            if match:
                variables_found.add(match.group(1))

        expected_vars = {'x1', 'x2', 'x3', 'x4', 'x5', 'x6'}
        missing_vars = expected_vars - variables_found

        assert missing_vars == set(), (
            f"File {solver_file} is missing variables: {missing_vars}. "
            f"Found variables: {variables_found}. "
            "All variables x1 through x6 must be present."
        )


class TestPythonEnvironment:
    """Test that the required Python environment is available."""

    def test_scipy_is_available(self):
        """scipy must be available for LP solving."""
        try:
            import scipy
        except ImportError:
            pytest.fail(
                "scipy is not installed. "
                "scipy is required for solving the linear programming problem."
            )

    def test_scipy_optimize_available(self):
        """scipy.optimize must be available for LP solving."""
        try:
            from scipy import optimize
        except ImportError:
            pytest.fail(
                "scipy.optimize is not available. "
                "scipy.optimize is required for the linprog function."
            )

    def test_scipy_linprog_available(self):
        """scipy.optimize.linprog must be available."""
        try:
            from scipy.optimize import linprog
        except ImportError:
            pytest.fail(
                "scipy.optimize.linprog is not available. "
                "linprog is required for solving the linear programming problem."
            )


class TestComplianceReportDoesNotExist:
    """Test that the output file does not exist yet (initial state)."""

    def test_compliance_report_does_not_exist(self):
        """The compliance_report.json should not exist in the initial state."""
        report_file = "/home/user/audit/compliance_report.json"
        # Note: This test is informational - the file should not exist initially
        # but if it does, the task can still proceed (it will be overwritten)
        if os.path.exists(report_file):
            pytest.skip(
                f"File {report_file} already exists. "
                "This is acceptable but the task will overwrite it."
            )
