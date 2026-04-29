# test_initial_state.py
"""
Tests to validate the initial state of the system before the student performs the action.
This verifies the CPLEX memory issue scenario is properly set up.
"""

import os
import subprocess
import pytest


class TestCPLEXInstallation:
    """Tests for CPLEX installation and availability."""

    def test_cplex_installation_directory_exists(self):
        """Verify CPLEX is installed at the expected location."""
        cplex_dir = "/opt/ibm/ILOG/CPLEX_Studio221"
        assert os.path.isdir(cplex_dir), (
            f"CPLEX installation directory not found at {cplex_dir}. "
            "CPLEX 22.1.1 should be installed at this location."
        )

    def test_cplex_binary_exists(self):
        """Verify the CPLEX binary exists."""
        cplex_binary = "/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex"
        assert os.path.isfile(cplex_binary), (
            f"CPLEX binary not found at {cplex_binary}. "
            "The CPLEX executable should exist at this path."
        )

    def test_cplex_binary_is_executable(self):
        """Verify the CPLEX binary is executable."""
        cplex_binary = "/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex"
        assert os.access(cplex_binary, os.X_OK), (
            f"CPLEX binary at {cplex_binary} is not executable. "
            "The binary should have execute permissions."
        )


class TestSolverDirectory:
    """Tests for the solver directory structure."""

    def test_solver_directory_exists(self):
        """Verify the solver directory exists."""
        solver_dir = "/home/user/solver"
        assert os.path.isdir(solver_dir), (
            f"Solver directory not found at {solver_dir}. "
            "The solver directory should exist."
        )

    def test_solver_directory_is_writable(self):
        """Verify the solver directory is writable."""
        solver_dir = "/home/user/solver"
        assert os.access(solver_dir, os.W_OK), (
            f"Solver directory at {solver_dir} is not writable. "
            "The directory should be writable for output files."
        )

    def test_tmp_directory_exists(self):
        """Verify the CPLEX temp directory exists."""
        tmp_dir = "/home/user/solver/tmp"
        assert os.path.isdir(tmp_dir), (
            f"CPLEX temp directory not found at {tmp_dir}. "
            "The tmp directory should exist for CPLEX temporary files."
        )

    def test_tmp_directory_is_writable(self):
        """Verify the CPLEX temp directory is writable."""
        tmp_dir = "/home/user/solver/tmp"
        assert os.access(tmp_dir, os.W_OK), (
            f"CPLEX temp directory at {tmp_dir} is not writable. "
            "The tmp directory should be writable for CPLEX temporary files."
        )


class TestDispatchLPFile:
    """Tests for the dispatch.lp problem file."""

    def test_dispatch_lp_exists(self):
        """Verify the dispatch.lp file exists."""
        lp_file = "/home/user/solver/dispatch.lp"
        assert os.path.isfile(lp_file), (
            f"LP file not found at {lp_file}. "
            "The dispatch.lp file should exist for CPLEX to solve."
        )

    def test_dispatch_lp_is_readable(self):
        """Verify the dispatch.lp file is readable."""
        lp_file = "/home/user/solver/dispatch.lp"
        assert os.access(lp_file, os.R_OK), (
            f"LP file at {lp_file} is not readable. "
            "The file should be readable by CPLEX."
        )

    def test_dispatch_lp_is_valid_lp_format(self):
        """Verify the dispatch.lp file appears to be a valid LP format file."""
        lp_file = "/home/user/solver/dispatch.lp"
        with open(lp_file, 'r') as f:
            content = f.read(1000)  # Read first 1000 chars

        # LP files typically start with comments, objective, or section keywords
        lp_keywords = ['minimize', 'maximize', 'min', 'max', 'subject to', 'st', 'bounds', 'binary', 'general', '\\']
        content_lower = content.lower()
        has_lp_keyword = any(kw in content_lower for kw in lp_keywords)

        assert has_lp_keyword, (
            f"File {lp_file} does not appear to be a valid CPLEX LP format file. "
            "The file should contain LP format keywords like 'Minimize', 'Subject To', etc."
        )

    def test_dispatch_lp_has_reasonable_size(self):
        """Verify the dispatch.lp file has reasonable size for ~50k constraints."""
        lp_file = "/home/user/solver/dispatch.lp"
        file_size = os.path.getsize(lp_file)

        # A model with 50k constraints and 120k variables should be at least several MB
        min_expected_size = 1_000_000  # 1MB minimum
        max_expected_size = 500_000_000  # 500MB maximum (reasonable upper bound)

        assert file_size >= min_expected_size, (
            f"LP file at {lp_file} is too small ({file_size} bytes). "
            f"A model with ~50k constraints should be at least {min_expected_size} bytes."
        )
        assert file_size <= max_expected_size, (
            f"LP file at {lp_file} is unexpectedly large ({file_size} bytes). "
            "This may not be the expected dispatch.lp file."
        )


class TestWrapperScript:
    """Tests for the run_cplex.sh wrapper script."""

    def test_wrapper_script_exists(self):
        """Verify the wrapper script exists."""
        script_path = "/home/user/solver/run_cplex.sh"
        assert os.path.isfile(script_path), (
            f"Wrapper script not found at {script_path}. "
            "The run_cplex.sh script should exist."
        )

    def test_wrapper_script_is_executable(self):
        """Verify the wrapper script is executable."""
        script_path = "/home/user/solver/run_cplex.sh"
        assert os.access(script_path, os.X_OK), (
            f"Wrapper script at {script_path} is not executable. "
            "The script should have execute permissions."
        )

    def test_wrapper_script_is_writable(self):
        """Verify the wrapper script is writable (for fixing)."""
        script_path = "/home/user/solver/run_cplex.sh"
        assert os.access(script_path, os.W_OK), (
            f"Wrapper script at {script_path} is not writable. "
            "The script should be writable to allow fixing the issue."
        )

    def test_wrapper_script_is_bash_script(self):
        """Verify the wrapper script is a bash script."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()

        assert first_line.startswith('#!') and 'bash' in first_line, (
            f"Wrapper script at {script_path} does not appear to be a bash script. "
            f"First line is: {first_line}. Expected a bash shebang."
        )

    def test_wrapper_script_contains_ulimit_restriction(self):
        """Verify the wrapper script contains the problematic ulimit -v restriction."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check for the specific ulimit -v 2097152 (2GB limit)
        assert 'ulimit -v 2097152' in content or 'ulimit -v2097152' in content, (
            f"Wrapper script at {script_path} does not contain the expected "
            "'ulimit -v 2097152' restriction. This is the bug that needs to be fixed. "
            "The initial state should have this restrictive memory limit."
        )

    def test_wrapper_script_invokes_cplex(self):
        """Verify the wrapper script invokes CPLEX."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert '/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex' in content, (
            f"Wrapper script at {script_path} does not invoke CPLEX at the expected path. "
            "The script should call the CPLEX binary."
        )

    def test_wrapper_script_reads_dispatch_lp(self):
        """Verify the wrapper script reads dispatch.lp."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'dispatch.lp' in content, (
            f"Wrapper script at {script_path} does not reference dispatch.lp. "
            "The script should read the dispatch.lp file."
        )

    def test_wrapper_script_writes_solution(self):
        """Verify the wrapper script writes to solution.sol."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'solution.sol' in content, (
            f"Wrapper script at {script_path} does not reference solution.sol. "
            "The script should write the solution to solution.sol."
        )

    def test_wrapper_script_sets_tmpdir(self):
        """Verify the wrapper script sets CPLEX_TMPDIR."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'CPLEX_TMPDIR' in content, (
            f"Wrapper script at {script_path} does not set CPLEX_TMPDIR. "
            "The script should configure the temporary directory."
        )


class TestCPLEXLog:
    """Tests for the CPLEX log file showing the error."""

    def test_cplex_log_exists(self):
        """Verify the CPLEX log file exists."""
        log_file = "/home/user/solver/cplex.log"
        assert os.path.isfile(log_file), (
            f"CPLEX log file not found at {log_file}. "
            "The log file should exist showing the memory error."
        )

    def test_cplex_log_shows_memory_error(self):
        """Verify the CPLEX log shows the out of memory error."""
        log_file = "/home/user/solver/cplex.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert 'CPXERR_NO_MEMORY' in content or 'Out of memory' in content, (
            f"CPLEX log at {log_file} does not show the expected memory error. "
            "The log should contain 'CPXERR_NO_MEMORY' or 'Out of memory'."
        )

    def test_cplex_log_shows_successful_read(self):
        """Verify the CPLEX log shows the LP file was read successfully."""
        log_file = "/home/user/solver/cplex.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert 'read' in content.lower() and 'dispatch.lp' in content, (
            f"CPLEX log at {log_file} does not show successful reading of dispatch.lp. "
            "The log should show the file was read before the memory error."
        )


class TestSystemResources:
    """Tests for system resources (memory, etc.)."""

    def test_system_has_adequate_memory(self):
        """Verify the system has adequate physical memory."""
        # Read /proc/meminfo to get total memory
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()

        for line in meminfo.split('\n'):
            if line.startswith('MemTotal:'):
                # Extract memory in kB
                mem_kb = int(line.split()[1])
                mem_gb = mem_kb / (1024 * 1024)
                break
        else:
            pytest.fail("Could not read MemTotal from /proc/meminfo")

        # System should have at least 16GB (task says 32GB)
        assert mem_gb >= 16, (
            f"System has only {mem_gb:.1f}GB RAM. "
            "The system should have adequate memory (32GB expected)."
        )

    def test_python3_available(self):
        """Verify Python 3.11 is available."""
        result = subprocess.run(
            ['python3', '--version'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python 3 is not available. "
            f"Error: {result.stderr}"
        )
        assert 'Python 3' in result.stdout, (
            f"Unexpected Python version: {result.stdout}. "
            "Python 3 should be available."
        )


class TestSolutionFileDoesNotExist:
    """Tests to verify the solution file does not exist yet."""

    def test_solution_file_does_not_exist(self):
        """Verify the solution.sol file does not exist initially."""
        solution_file = "/home/user/solver/solution.sol"
        # Note: The solution file might exist from previous failed runs,
        # but it should not contain a valid solution
        if os.path.exists(solution_file):
            # If it exists, it should be empty or not contain valid solution data
            with open(solution_file, 'r') as f:
                content = f.read()
            # A valid solution would have objective values or variable assignments
            has_valid_solution = (
                'objective' in content.lower() or 
                'ObjVal' in content or 
                'value=' in content
            )
            assert not has_valid_solution, (
                f"Solution file at {solution_file} already contains a valid solution. "
                "The initial state should not have a solved solution."
            )
