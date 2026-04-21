# test_final_state.py
"""
Tests to validate the final state of the operating system / filesystem
after the student has completed the LP audit task.
"""

import pytest
import os
import json


class TestComplianceReportExists:
    """Test that the compliance report file exists and is valid JSON."""

    def test_compliance_report_exists(self):
        """The compliance_report.json file must exist."""
        report_file = "/home/user/audit/compliance_report.json"
        assert os.path.exists(report_file), (
            f"File {report_file} does not exist. "
            "The compliance report must be generated at this location."
        )

    def test_compliance_report_is_file(self):
        """The compliance_report.json path must be a regular file."""
        report_file = "/home/user/audit/compliance_report.json"
        assert os.path.isfile(report_file), (
            f"{report_file} exists but is not a regular file. "
            "It must be a JSON file containing the audit report."
        )

    def test_compliance_report_is_readable(self):
        """The compliance_report.json file must be readable."""
        report_file = "/home/user/audit/compliance_report.json"
        assert os.access(report_file, os.R_OK), (
            f"File {report_file} is not readable. "
            "The compliance report must be readable."
        )

    def test_compliance_report_is_valid_json(self):
        """The compliance_report.json file must contain valid JSON."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            content = f.read()

        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {report_file} does not contain valid JSON. "
                f"JSON parse error: {e}"
            )


class TestComplianceReportStructure:
    """Test that the compliance report has the required structure."""

    @pytest.fixture
    def report_data(self):
        """Load the compliance report JSON."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            return json.load(f)

    def test_has_audit_timestamp(self, report_data):
        """The report must have an audit_timestamp field."""
        assert "audit_timestamp" in report_data, (
            "Missing required key 'audit_timestamp' in compliance report."
        )

    def test_has_stored_solution(self, report_data):
        """The report must have a stored_solution field."""
        assert "stored_solution" in report_data, (
            "Missing required key 'stored_solution' in compliance report."
        )

    def test_has_feasibility_check(self, report_data):
        """The report must have a feasibility_check field."""
        assert "feasibility_check" in report_data, (
            "Missing required key 'feasibility_check' in compliance report."
        )

    def test_has_optimal_solution(self, report_data):
        """The report must have an optimal_solution field."""
        assert "optimal_solution" in report_data, (
            "Missing required key 'optimal_solution' in compliance report."
        )

    def test_has_optimality_gap(self, report_data):
        """The report must have an optimality_gap field."""
        assert "optimality_gap" in report_data, (
            "Missing required key 'optimality_gap' in compliance report."
        )

    def test_has_compliance_status(self, report_data):
        """The report must have a compliance_status field."""
        assert "compliance_status" in report_data, (
            "Missing required key 'compliance_status' in compliance report."
        )


class TestStoredSolutionStructure:
    """Test that the stored_solution has the required structure."""

    @pytest.fixture
    def stored_solution(self):
        """Load the stored_solution from the compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            data = json.load(f)
        return data.get("stored_solution", {})

    def test_stored_solution_has_x1(self, stored_solution):
        """stored_solution must have x1."""
        assert "x1" in stored_solution, (
            "Missing 'x1' in stored_solution."
        )

    def test_stored_solution_has_x2(self, stored_solution):
        """stored_solution must have x2."""
        assert "x2" in stored_solution, (
            "Missing 'x2' in stored_solution."
        )

    def test_stored_solution_has_x3(self, stored_solution):
        """stored_solution must have x3."""
        assert "x3" in stored_solution, (
            "Missing 'x3' in stored_solution."
        )

    def test_stored_solution_has_x4(self, stored_solution):
        """stored_solution must have x4."""
        assert "x4" in stored_solution, (
            "Missing 'x4' in stored_solution."
        )

    def test_stored_solution_has_x5(self, stored_solution):
        """stored_solution must have x5."""
        assert "x5" in stored_solution, (
            "Missing 'x5' in stored_solution."
        )

    def test_stored_solution_has_x6(self, stored_solution):
        """stored_solution must have x6."""
        assert "x6" in stored_solution, (
            "Missing 'x6' in stored_solution."
        )

    def test_stored_solution_has_objective_value(self, stored_solution):
        """stored_solution must have objective_value."""
        assert "objective_value" in stored_solution, (
            "Missing 'objective_value' in stored_solution."
        )

    def test_stored_solution_values_are_floats(self, stored_solution):
        """All stored_solution values must be numeric (int or float)."""
        for key in ["x1", "x2", "x3", "x4", "x5", "x6", "objective_value"]:
            if key in stored_solution:
                value = stored_solution[key]
                assert isinstance(value, (int, float)), (
                    f"stored_solution['{key}'] must be a number, got {type(value).__name__}: {value}"
                )


class TestFeasibilityCheckStructure:
    """Test that the feasibility_check has the required structure."""

    @pytest.fixture
    def feasibility_check(self):
        """Load the feasibility_check from the compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            data = json.load(f)
        return data.get("feasibility_check", {})

    def test_feasibility_check_has_is_feasible(self, feasibility_check):
        """feasibility_check must have is_feasible."""
        assert "is_feasible" in feasibility_check, (
            "Missing 'is_feasible' in feasibility_check."
        )

    def test_feasibility_check_has_violated_constraints(self, feasibility_check):
        """feasibility_check must have violated_constraints."""
        assert "violated_constraints" in feasibility_check, (
            "Missing 'violated_constraints' in feasibility_check."
        )

    def test_is_feasible_is_boolean(self, feasibility_check):
        """is_feasible must be a boolean."""
        is_feasible = feasibility_check.get("is_feasible")
        assert isinstance(is_feasible, bool), (
            f"is_feasible must be a boolean, got {type(is_feasible).__name__}: {is_feasible}"
        )

    def test_violated_constraints_is_list(self, feasibility_check):
        """violated_constraints must be a list."""
        violated = feasibility_check.get("violated_constraints")
        assert isinstance(violated, list), (
            f"violated_constraints must be a list, got {type(violated).__name__}: {violated}"
        )


class TestOptimalSolutionStructure:
    """Test that the optimal_solution has the required structure."""

    @pytest.fixture
    def optimal_solution(self):
        """Load the optimal_solution from the compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            data = json.load(f)
        return data.get("optimal_solution", {})

    def test_optimal_solution_has_x1(self, optimal_solution):
        """optimal_solution must have x1."""
        assert "x1" in optimal_solution, (
            "Missing 'x1' in optimal_solution."
        )

    def test_optimal_solution_has_x2(self, optimal_solution):
        """optimal_solution must have x2."""
        assert "x2" in optimal_solution, (
            "Missing 'x2' in optimal_solution."
        )

    def test_optimal_solution_has_x3(self, optimal_solution):
        """optimal_solution must have x3."""
        assert "x3" in optimal_solution, (
            "Missing 'x3' in optimal_solution."
        )

    def test_optimal_solution_has_x4(self, optimal_solution):
        """optimal_solution must have x4."""
        assert "x4" in optimal_solution, (
            "Missing 'x4' in optimal_solution."
        )

    def test_optimal_solution_has_x5(self, optimal_solution):
        """optimal_solution must have x5."""
        assert "x5" in optimal_solution, (
            "Missing 'x5' in optimal_solution."
        )

    def test_optimal_solution_has_x6(self, optimal_solution):
        """optimal_solution must have x6."""
        assert "x6" in optimal_solution, (
            "Missing 'x6' in optimal_solution."
        )

    def test_optimal_solution_has_objective_value(self, optimal_solution):
        """optimal_solution must have objective_value."""
        assert "objective_value" in optimal_solution, (
            "Missing 'objective_value' in optimal_solution."
        )

    def test_optimal_solution_values_are_floats(self, optimal_solution):
        """All optimal_solution values must be numeric (int or float)."""
        for key in ["x1", "x2", "x3", "x4", "x5", "x6", "objective_value"]:
            if key in optimal_solution:
                value = optimal_solution[key]
                assert isinstance(value, (int, float)), (
                    f"optimal_solution['{key}'] must be a number, got {type(value).__name__}: {value}"
                )


class TestStoredSolutionValues:
    """Test that the stored solution values match the expected values from solver_output.dat."""

    @pytest.fixture
    def stored_solution(self):
        """Load the stored_solution from the compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            data = json.load(f)
        return data.get("stored_solution", {})

    def test_stored_x1_value(self, stored_solution):
        """stored_solution x1 should be 10.0."""
        assert abs(stored_solution.get("x1", 0) - 10.0) < 0.01, (
            f"stored_solution x1 should be 10.0, got {stored_solution.get('x1')}"
        )

    def test_stored_x2_value(self, stored_solution):
        """stored_solution x2 should be 8.0."""
        assert abs(stored_solution.get("x2", 0) - 8.0) < 0.01, (
            f"stored_solution x2 should be 8.0, got {stored_solution.get('x2')}"
        )

    def test_stored_x3_value(self, stored_solution):
        """stored_solution x3 should be 7.0."""
        assert abs(stored_solution.get("x3", 0) - 7.0) < 0.01, (
            f"stored_solution x3 should be 7.0, got {stored_solution.get('x3')}"
        )

    def test_stored_x4_value(self, stored_solution):
        """stored_solution x4 should be 6.0."""
        assert abs(stored_solution.get("x4", 0) - 6.0) < 0.01, (
            f"stored_solution x4 should be 6.0, got {stored_solution.get('x4')}"
        )

    def test_stored_x5_value(self, stored_solution):
        """stored_solution x5 should be 4.0."""
        assert abs(stored_solution.get("x5", 0) - 4.0) < 0.01, (
            f"stored_solution x5 should be 4.0, got {stored_solution.get('x5')}"
        )

    def test_stored_x6_value(self, stored_solution):
        """stored_solution x6 should be 5.0."""
        assert abs(stored_solution.get("x6", 0) - 5.0) < 0.01, (
            f"stored_solution x6 should be 5.0, got {stored_solution.get('x6')}"
        )

    def test_stored_objective_value(self, stored_solution):
        """stored_solution objective_value should be approximately 157.9."""
        # 3.5*10 + 4.2*8 + 2.8*7 + 5.1*6 + 3.9*4 + 4.7*5 = 157.9
        expected_obj = 157.9
        actual_obj = stored_solution.get("objective_value", 0)
        assert abs(actual_obj - expected_obj) < 0.1, (
            f"stored_solution objective_value should be approximately {expected_obj}, got {actual_obj}"
        )


class TestFeasibilityCheckValues:
    """Test that the feasibility check values are correct."""

    @pytest.fixture
    def feasibility_check(self):
        """Load the feasibility_check from the compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            data = json.load(f)
        return data.get("feasibility_check", {})

    def test_solution_is_feasible(self, feasibility_check):
        """The stored solution should be feasible (is_feasible = true)."""
        is_feasible = feasibility_check.get("is_feasible")
        assert is_feasible is True, (
            f"The stored solution should be feasible (is_feasible should be true), "
            f"but got is_feasible = {is_feasible}. "
            "The stored solution satisfies all constraints."
        )

    def test_no_violated_constraints(self, feasibility_check):
        """violated_constraints should be an empty list since the solution is feasible."""
        violated = feasibility_check.get("violated_constraints", [])
        assert violated == [], (
            f"violated_constraints should be empty for a feasible solution, "
            f"but got: {violated}"
        )


class TestOptimalSolutionValues:
    """Test that the optimal solution values are reasonable."""

    @pytest.fixture
    def report_data(self):
        """Load the full compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            return json.load(f)

    def test_optimal_objective_greater_or_equal_stored(self, report_data):
        """The optimal objective value should be >= stored objective value."""
        stored_obj = report_data.get("stored_solution", {}).get("objective_value", 0)
        optimal_obj = report_data.get("optimal_solution", {}).get("objective_value", 0)

        # Allow small tolerance for floating point
        assert optimal_obj >= stored_obj - 0.01, (
            f"Optimal objective ({optimal_obj}) should be >= stored objective ({stored_obj}). "
            "The optimal solution cannot be worse than the stored solution."
        )

    def test_optimal_objective_approximately_158(self, report_data):
        """The optimal objective value should be approximately 158.3."""
        optimal_obj = report_data.get("optimal_solution", {}).get("objective_value", 0)

        # Allow some tolerance for different solver implementations
        assert 155.0 <= optimal_obj <= 165.0, (
            f"Optimal objective ({optimal_obj}) should be approximately 158.3. "
            "This suggests the LP solver may not have found the true optimum."
        )

    def test_optimal_solution_variables_non_negative(self, report_data):
        """All optimal solution variables should be non-negative."""
        optimal = report_data.get("optimal_solution", {})
        for var in ["x1", "x2", "x3", "x4", "x5", "x6"]:
            value = optimal.get(var, 0)
            assert value >= -0.0001, (
                f"optimal_solution['{var}'] = {value} is negative. "
                "Staff counts cannot be negative."
            )


class TestOptimalityGap:
    """Test that the optimality gap is calculated correctly."""

    @pytest.fixture
    def report_data(self):
        """Load the full compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            return json.load(f)

    def test_optimality_gap_is_numeric(self, report_data):
        """optimality_gap must be a number."""
        gap = report_data.get("optimality_gap")
        assert isinstance(gap, (int, float)), (
            f"optimality_gap must be a number, got {type(gap).__name__}: {gap}"
        )

    def test_optimality_gap_is_non_negative(self, report_data):
        """optimality_gap must be non-negative."""
        gap = report_data.get("optimality_gap", -1)
        assert gap >= 0, (
            f"optimality_gap must be non-negative, got {gap}"
        )

    def test_optimality_gap_less_than_one_percent(self, report_data):
        """optimality_gap should be less than 1.0% for this problem."""
        gap = report_data.get("optimality_gap", 100)
        assert gap < 1.0, (
            f"optimality_gap should be less than 1.0% for this problem, got {gap}%. "
            "The stored solution is very close to optimal."
        )

    def test_optimality_gap_calculation(self, report_data):
        """Verify the optimality gap is calculated correctly."""
        stored_obj = report_data.get("stored_solution", {}).get("objective_value", 0)
        optimal_obj = report_data.get("optimal_solution", {}).get("objective_value", 1)
        reported_gap = report_data.get("optimality_gap", -1)

        if optimal_obj > 0:
            expected_gap = 100 * abs(stored_obj - optimal_obj) / optimal_obj
            # Allow some tolerance for rounding
            assert abs(reported_gap - expected_gap) < 0.1, (
                f"optimality_gap calculation appears incorrect. "
                f"Expected approximately {expected_gap:.4f}%, got {reported_gap}%. "
                f"Formula: 100 * |{stored_obj} - {optimal_obj}| / {optimal_obj}"
            )


class TestComplianceStatus:
    """Test that the compliance status is determined correctly."""

    @pytest.fixture
    def report_data(self):
        """Load the full compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            return json.load(f)

    def test_compliance_status_is_string(self, report_data):
        """compliance_status must be a string."""
        status = report_data.get("compliance_status")
        assert isinstance(status, str), (
            f"compliance_status must be a string, got {type(status).__name__}: {status}"
        )

    def test_compliance_status_valid_value(self, report_data):
        """compliance_status must be either COMPLIANT or NON_COMPLIANT."""
        status = report_data.get("compliance_status", "")
        assert status in ["COMPLIANT", "NON_COMPLIANT"], (
            f"compliance_status must be 'COMPLIANT' or 'NON_COMPLIANT', got '{status}'"
        )

    def test_compliance_status_is_compliant(self, report_data):
        """compliance_status should be COMPLIANT for this problem."""
        status = report_data.get("compliance_status", "")
        is_feasible = report_data.get("feasibility_check", {}).get("is_feasible", False)
        gap = report_data.get("optimality_gap", 100)

        # The solution is feasible and gap <= 1.0%, so it should be COMPLIANT
        assert status == "COMPLIANT", (
            f"compliance_status should be 'COMPLIANT' because the solution is feasible "
            f"(is_feasible={is_feasible}) and optimality_gap ({gap}%) <= 1.0%. "
            f"Got compliance_status='{status}'"
        )


class TestFloatPrecision:
    """Test that float values are rounded to 4 decimal places."""

    @pytest.fixture
    def report_data(self):
        """Load the full compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            return json.load(f)

    def _check_decimal_places(self, value, max_places=4):
        """Check if a float has at most max_places decimal places."""
        if isinstance(value, int):
            return True
        str_val = str(value)
        if '.' not in str_val:
            return True
        decimal_part = str_val.split('.')[1]
        # Remove trailing zeros for comparison
        decimal_part = decimal_part.rstrip('0')
        return len(decimal_part) <= max_places

    def test_stored_solution_precision(self, report_data):
        """stored_solution float values should have at most 4 decimal places."""
        stored = report_data.get("stored_solution", {})
        for key in ["x1", "x2", "x3", "x4", "x5", "x6", "objective_value"]:
            value = stored.get(key)
            if value is not None and isinstance(value, float):
                # Check that the value matches when rounded to 4 decimal places
                rounded = round(value, 4)
                assert abs(value - rounded) < 1e-10, (
                    f"stored_solution['{key}'] = {value} should be rounded to 4 decimal places"
                )

    def test_optimal_solution_precision(self, report_data):
        """optimal_solution float values should have at most 4 decimal places."""
        optimal = report_data.get("optimal_solution", {})
        for key in ["x1", "x2", "x3", "x4", "x5", "x6", "objective_value"]:
            value = optimal.get(key)
            if value is not None and isinstance(value, float):
                rounded = round(value, 4)
                assert abs(value - rounded) < 1e-10, (
                    f"optimal_solution['{key}'] = {value} should be rounded to 4 decimal places"
                )

    def test_optimality_gap_precision(self, report_data):
        """optimality_gap should have at most 4 decimal places."""
        gap = report_data.get("optimality_gap")
        if gap is not None and isinstance(gap, float):
            rounded = round(gap, 4)
            assert abs(gap - rounded) < 1e-10, (
                f"optimality_gap = {gap} should be rounded to 4 decimal places"
            )


class TestAuditTimestamp:
    """Test that the audit timestamp is valid."""

    @pytest.fixture
    def report_data(self):
        """Load the full compliance report."""
        report_file = "/home/user/audit/compliance_report.json"
        with open(report_file, 'r') as f:
            return json.load(f)

    def test_timestamp_is_string(self, report_data):
        """audit_timestamp must be a string."""
        timestamp = report_data.get("audit_timestamp")
        assert isinstance(timestamp, str), (
            f"audit_timestamp must be a string, got {type(timestamp).__name__}: {timestamp}"
        )

    def test_timestamp_is_not_empty(self, report_data):
        """audit_timestamp must not be empty."""
        timestamp = report_data.get("audit_timestamp", "")
        assert len(timestamp) > 0, (
            "audit_timestamp must not be empty"
        )

    def test_timestamp_looks_like_iso8601(self, report_data):
        """audit_timestamp should look like an ISO 8601 timestamp."""
        timestamp = report_data.get("audit_timestamp", "")
        # Basic check for ISO 8601 format (should contain date-like pattern)
        import re
        # Match patterns like: 2024-01-15T10:30:00 or 2024-01-15 10:30:00 or similar
        iso_pattern = r'\d{4}-\d{2}-\d{2}'
        assert re.search(iso_pattern, timestamp), (
            f"audit_timestamp '{timestamp}' does not appear to be in ISO 8601 format. "
            "Expected format like '2024-01-15T10:30:00' or similar."
        )
