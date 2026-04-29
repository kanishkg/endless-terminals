# test_initial_state.py
"""
Tests to validate the initial state of the system before the student
performs the CPLEX MIP gap tolerance update task.
"""

import os
import pytest


class TestCplexConfigInitialState:
    """Tests for the initial state of the CPLEX configuration file."""

    CONFIG_PATH = "/home/user/optim/cplex.prm"

    def test_optim_directory_exists(self):
        """Verify the /home/user/optim directory exists."""
        dir_path = "/home/user/optim"
        assert os.path.isdir(dir_path), (
            f"Directory {dir_path} does not exist. "
            "The optim directory must be present before the task."
        )

    def test_cplex_config_file_exists(self):
        """Verify the cplex.prm file exists."""
        assert os.path.exists(self.CONFIG_PATH), (
            f"File {self.CONFIG_PATH} does not exist. "
            "The CPLEX configuration file must be present before the task."
        )

    def test_cplex_config_is_file(self):
        """Verify cplex.prm is a regular file, not a directory or symlink."""
        assert os.path.isfile(self.CONFIG_PATH), (
            f"{self.CONFIG_PATH} exists but is not a regular file. "
            "It must be a regular file."
        )

    def test_cplex_config_is_writable(self):
        """Verify the cplex.prm file is writable."""
        assert os.access(self.CONFIG_PATH, os.W_OK), (
            f"File {self.CONFIG_PATH} is not writable. "
            "The student needs write access to modify the file."
        )

    def test_cplex_config_is_readable(self):
        """Verify the cplex.prm file is readable."""
        assert os.access(self.CONFIG_PATH, os.R_OK), (
            f"File {self.CONFIG_PATH} is not readable. "
            "The student needs read access to view the file."
        )

    def test_cplex_config_contains_mipgap_parameter(self):
        """Verify the file contains the CPXPARAM_MIP_Tolerances_MIPGap parameter."""
        with open(self.CONFIG_PATH, 'r') as f:
            content = f.read()

        assert "CPXPARAM_MIP_Tolerances_MIPGap" in content, (
            f"File {self.CONFIG_PATH} does not contain the "
            "CPXPARAM_MIP_Tolerances_MIPGap parameter. "
            "This parameter must be present for the student to modify."
        )

    def test_cplex_config_has_current_wrong_value(self):
        """Verify the MIPGap parameter is currently set to 0.01 (the wrong value)."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        mipgap_lines = [
            line.strip() for line in lines 
            if line.strip().startswith("CPXPARAM_MIP_Tolerances_MIPGap")
        ]

        assert len(mipgap_lines) == 1, (
            f"Expected exactly one line with CPXPARAM_MIP_Tolerances_MIPGap, "
            f"found {len(mipgap_lines)}. The file may be malformed."
        )

        # Check that the current value is 0.01
        expected_line = "CPXPARAM_MIP_Tolerances_MIPGap 0.01"
        assert mipgap_lines[0] == expected_line, (
            f"Expected the MIPGap line to be '{expected_line}', "
            f"but found '{mipgap_lines[0]}'. "
            "The initial state should have the wrong value of 0.01."
        )

    def test_cplex_config_has_key_value_format(self):
        """Verify the file follows KEY VALUE format (one param per line)."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        non_empty_lines = [line.strip() for line in lines if line.strip()]

        assert len(non_empty_lines) > 0, (
            f"File {self.CONFIG_PATH} appears to be empty or contain only whitespace."
        )

        for line in non_empty_lines:
            parts = line.split()
            assert len(parts) >= 2, (
                f"Line '{line}' does not follow 'KEY VALUE' format. "
                "Each line should have at least a key and a value separated by space."
            )

    def test_cplex_config_has_other_parameters(self):
        """Verify the file contains other parameters that should remain unchanged."""
        with open(self.CONFIG_PATH, 'r') as f:
            content = f.read()

        # Check for at least one other common CPLEX parameter
        other_params_found = (
            "CPXPARAM_TimeLimit" in content or 
            "CPXPARAM_Threads" in content or
            "CPXPARAM_" in content.replace("CPXPARAM_MIP_Tolerances_MIPGap", "")
        )

        assert other_params_found, (
            f"File {self.CONFIG_PATH} should contain other CPLEX parameters "
            "besides CPXPARAM_MIP_Tolerances_MIPGap. "
            "The file appears to be missing expected content."
        )

    def test_cplex_config_line_count(self):
        """Record the initial line count for verification that it doesn't change."""
        with open(self.CONFIG_PATH, 'r') as f:
            lines = f.readlines()

        line_count = len(lines)
        assert line_count > 0, (
            f"File {self.CONFIG_PATH} has no lines. "
            "The configuration file should have content."
        )

        # Just verify it has a reasonable number of lines (at least the MIPGap line)
        assert line_count >= 1, (
            f"File {self.CONFIG_PATH} should have at least one line."
        )
