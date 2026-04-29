# test_final_state.py
"""
Tests to validate the final state of the system after the student
has completed the CPLEX MIP gap tolerance update task.
"""

import os
import subprocess
import pytest


class TestCplexConfigFinalState:
    """Tests for the final state of the CPLEX configuration file."""

    CONFIG_PATH = "/home/user/optim/cplex.prm"

    def test_cplex_config_file_exists(self):
        """Verify the cplex.prm file still exists after modification."""
        assert os.path.exists(self.CONFIG_PATH), (
            f"File {self.CONFIG_PATH} does not exist. "
            "The file should still exist after the modification."
        )

    def test_cplex_config_is_file(self):
        """Verify cplex.prm is still a regular file."""
        assert os.path.isfile(self.CONFIG_PATH), (
            f"{self.CONFIG_PATH} is not a regular file. "
            "The file type should not have changed."
        )

    def test_cplex_config_is_readable(self):
        """Verify the cplex.prm file is still readable."""
        assert os.access(self.CONFIG_PATH, os.R_OK), (
            f"File {self.CONFIG_PATH} is not readable. "
            "The file should remain readable after modification."
        )

    def test_mipgap_has_correct_value(self):
        """Verify the MIPGap parameter is now set to exactly 0.001."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        mipgap_lines = [
            line.strip() for line in lines 
            if line.strip().startswith("CPXPARAM_MIP_Tolerances_MIPGap")
        ]

        assert len(mipgap_lines) == 1, (
            f"Expected exactly one line with CPXPARAM_MIP_Tolerances_MIPGap, "
            f"found {len(mipgap_lines)}. The parameter should appear exactly once."
        )

        expected_line = "CPXPARAM_MIP_Tolerances_MIPGap 0.001"
        assert mipgap_lines[0] == expected_line, (
            f"Expected the MIPGap line to be exactly '{expected_line}', "
            f"but found '{mipgap_lines[0]}'. "
            "The value must be exactly '0.001' (not 0.0010, not 1e-3, not .001)."
        )

    def test_mipgap_grep_exact_match(self):
        """Use grep to verify exactly one line matches the expected pattern."""
        result = subprocess.run(
            ["grep", "-c", "CPXPARAM_MIP_Tolerances_MIPGap 0.001", self.CONFIG_PATH],
            capture_output=True,
            text=True
        )

        # grep -c returns the count of matching lines
        match_count = int(result.stdout.strip()) if result.returncode == 0 else 0

        assert match_count == 1, (
            f"Expected exactly 1 line matching 'CPXPARAM_MIP_Tolerances_MIPGap 0.001', "
            f"but found {match_count}. "
            "The MIPGap parameter must be set to exactly 0.001."
        )

    def test_old_value_not_present(self):
        """Verify the old value 0.01 is no longer present for MIPGap."""
        with open(self.CONFIG_PATH, 'r') as f:
            content = f.read()

        # Check that the old incorrect line is not present
        old_line = "CPXPARAM_MIP_Tolerances_MIPGap 0.01"
        # We need to be careful: 0.001 contains "0.01" as a substring
        # So we check for the exact old line format
        lines = content.strip().split('\n')
        old_value_lines = [
            line for line in lines 
            if line.strip() == old_line
        ]

        assert len(old_value_lines) == 0, (
            f"The old value 'CPXPARAM_MIP_Tolerances_MIPGap 0.01' is still present. "
            "The MIPGap parameter should be updated to 0.001."
        )

    def test_other_parameters_preserved(self):
        """Verify other CPLEX parameters are still present in the file."""
        with open(self.CONFIG_PATH, 'r') as f:
            content = f.read()

        # Check that other common parameters are still present
        # At minimum, there should be other CPXPARAM_ entries
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        cpxparam_lines = [line for line in lines if line.startswith("CPXPARAM_")]

        # Should have more than just the MIPGap line
        assert len(cpxparam_lines) >= 1, (
            "Expected CPLEX parameters in the file. "
            "The file should contain valid CPLEX parameter entries."
        )

    def test_file_has_valid_key_value_format(self):
        """Verify all lines in the file follow KEY VALUE format."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        non_empty_lines = [line.strip() for line in lines if line.strip()]

        for line in non_empty_lines:
            parts = line.split()
            assert len(parts) >= 2, (
                f"Line '{line}' does not follow 'KEY VALUE' format. "
                "Each parameter line should have a key and value separated by space. "
                "The file may have been corrupted during editing."
            )

    def test_no_syntax_errors_introduced(self):
        """Verify no obvious syntax errors were introduced."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped:
                # Check for common errors
                assert not stripped.startswith('='), (
                    f"Line {i} starts with '=', which is invalid CPLEX parameter syntax: '{stripped}'"
                )
                # Ensure CPXPARAM lines have proper format
                if stripped.startswith("CPXPARAM_"):
                    parts = stripped.split()
                    assert len(parts) == 2, (
                        f"Line {i} has invalid format. CPLEX parameters should be 'KEY VALUE': '{stripped}'"
                    )

    def test_mipgap_value_is_numeric(self):
        """Verify the MIPGap value can be parsed as a float equal to 0.001."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("CPXPARAM_MIP_Tolerances_MIPGap"):
                parts = stripped.split()
                assert len(parts) == 2, (
                    f"MIPGap line has wrong format: '{stripped}'"
                )
                try:
                    value = float(parts[1])
                except ValueError:
                    pytest.fail(f"MIPGap value '{parts[1]}' is not a valid number")

                assert abs(value - 0.001) < 1e-10, (
                    f"MIPGap numeric value is {value}, expected 0.001"
                )

                # Also verify the string representation is exactly "0.001"
                assert parts[1] == "0.001", (
                    f"MIPGap value must be exactly '0.001', not '{parts[1]}'. "
                    "Do not use scientific notation or alternative representations."
                )
                break
        else:
            pytest.fail("CPXPARAM_MIP_Tolerances_MIPGap line not found in file")

    def test_file_not_empty(self):
        """Verify the file is not empty after modification."""
        file_size = os.path.getsize(self.CONFIG_PATH)
        assert file_size > 0, (
            f"File {self.CONFIG_PATH} is empty. "
            "The file should contain CPLEX parameters."
        )

    def test_file_contains_mipgap_parameter(self):
        """Verify the file still contains the MIPGap parameter."""
        with open(self.CONFIG_PATH, 'r') as f:
            content = f.read()

        assert "CPXPARAM_MIP_Tolerances_MIPGap" in content, (
            f"File {self.CONFIG_PATH} does not contain the "
            "CPXPARAM_MIP_Tolerances_MIPGap parameter. "
            "The parameter should still be present after modification."
        )
