# test_final_state.py
"""
Tests to validate the final state of the system after the student has fixed the CPLEX memory issue.
This verifies that:
1. The wrapper script no longer has the restrictive ulimit
2. CPLEX can run to completion
3. A valid solution file is generated
4. The original dispatch.lp file is unchanged
"""

import os
import subprocess
import pytest
import hashlib
import re


class TestWrapperScriptFixed:
    """Tests to verify the wrapper script has been fixed."""

    def test_wrapper_script_exists(self):
        """Verify the wrapper script still exists."""
        script_path = "/home/user/solver/run_cplex.sh"
        assert os.path.isfile(script_path), (
            f"Wrapper script not found at {script_path}. "
            "The run_cplex.sh script should still exist after the fix."
        )

    def test_wrapper_script_is_executable(self):
        """Verify the wrapper script is still executable."""
        script_path = "/home/user/solver/run_cplex.sh"
        assert os.access(script_path, os.X_OK), (
            f"Wrapper script at {script_path} is not executable. "
            "The script should remain executable after the fix."
        )

    def test_restrictive_ulimit_removed(self):
        """Verify the restrictive ulimit -v 2097152 has been removed or changed."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # The specific restrictive limit should not be present
        has_restrictive_limit = 'ulimit -v 2097152' in content or 'ulimit -v2097152' in content
        assert not has_restrictive_limit, (
            f"Wrapper script at {script_path} still contains the restrictive "
            "'ulimit -v 2097152' (2GB virtual memory limit). "
            "This limit must be removed, increased substantially, or set to unlimited."
        )

    def test_restrictive_ulimit_not_in_bash_trace(self):
        """Verify bash -x doesn't show the restrictive ulimit when tracing."""
        # Run bash -x on the script and check the trace output
        result = subprocess.run(
            ['bash', '-x', '/home/user/solver/run_cplex.sh'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout for CPLEX
        )

        # Check that the restrictive ulimit is not in the trace
        trace_output = result.stderr  # bash -x outputs to stderr
        assert 'ulimit -v 2097152' not in trace_output, (
            "The restrictive 'ulimit -v 2097152' is still being executed. "
            "The fix must remove or change this limit."
        )

    def test_wrapper_still_invokes_cplex(self):
        """Verify the wrapper script still invokes CPLEX."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert '/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex' in content or 'cplex' in content.lower(), (
            f"Wrapper script at {script_path} no longer invokes CPLEX. "
            "The script must still call the CPLEX solver."
        )

    def test_wrapper_still_reads_dispatch_lp(self):
        """Verify the wrapper script still reads dispatch.lp."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'dispatch.lp' in content, (
            f"Wrapper script at {script_path} no longer references dispatch.lp. "
            "The script must still read the dispatch.lp file."
        )

    def test_wrapper_still_writes_solution_sol(self):
        """Verify the wrapper script still writes to solution.sol."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'solution.sol' in content, (
            f"Wrapper script at {script_path} no longer references solution.sol. "
            "The script must still write the solution to solution.sol."
        )


class TestDispatchLPUnchanged:
    """Tests to verify the dispatch.lp file is unchanged."""

    def test_dispatch_lp_exists(self):
        """Verify the dispatch.lp file still exists."""
        lp_file = "/home/user/solver/dispatch.lp"
        assert os.path.isfile(lp_file), (
            f"LP file not found at {lp_file}. "
            "The dispatch.lp file must not be deleted."
        )

    def test_dispatch_lp_is_valid_lp_format(self):
        """Verify the dispatch.lp file is still a valid LP format file."""
        lp_file = "/home/user/solver/dispatch.lp"
        with open(lp_file, 'r') as f:
            content = f.read(1000)

        lp_keywords = ['minimize', 'maximize', 'min', 'max', 'subject to', 'st', 'bounds', 'binary', 'general', '\\']
        content_lower = content.lower()
        has_lp_keyword = any(kw in content_lower for kw in lp_keywords)

        assert has_lp_keyword, (
            f"File {lp_file} does not appear to be a valid CPLEX LP format file. "
            "The dispatch.lp file must remain unchanged."
        )

    def test_dispatch_lp_has_reasonable_size(self):
        """Verify the dispatch.lp file still has reasonable size."""
        lp_file = "/home/user/solver/dispatch.lp"
        file_size = os.path.getsize(lp_file)

        min_expected_size = 1_000_000  # 1MB minimum
        assert file_size >= min_expected_size, (
            f"LP file at {lp_file} is too small ({file_size} bytes). "
            "The dispatch.lp file appears to have been modified or truncated."
        )


class TestCPLEXInstallationUnchanged:
    """Tests to verify CPLEX installation is unchanged."""

    def test_cplex_installation_exists(self):
        """Verify CPLEX installation still exists."""
        cplex_dir = "/opt/ibm/ILOG/CPLEX_Studio221"
        assert os.path.isdir(cplex_dir), (
            f"CPLEX installation directory not found at {cplex_dir}. "
            "The CPLEX installation must remain unchanged."
        )

    def test_cplex_binary_exists(self):
        """Verify the CPLEX binary still exists."""
        cplex_binary = "/opt/ibm/ILOG/CPLEX_Studio221/cplex/bin/x86-64_linux/cplex"
        assert os.path.isfile(cplex_binary), (
            f"CPLEX binary not found at {cplex_binary}. "
            "The CPLEX installation must remain unchanged."
        )


class TestSolutionFileGenerated:
    """Tests to verify a valid solution file was generated."""

    def test_solution_file_exists(self):
        """Verify the solution.sol file exists."""
        solution_file = "/home/user/solver/solution.sol"
        assert os.path.isfile(solution_file), (
            f"Solution file not found at {solution_file}. "
            "Running the wrapper script should generate a solution file."
        )

    def test_solution_file_not_empty(self):
        """Verify the solution.sol file is not empty."""
        solution_file = "/home/user/solver/solution.sol"
        file_size = os.path.getsize(solution_file)
        assert file_size > 0, (
            f"Solution file at {solution_file} is empty. "
            "A valid CPLEX solution should have content."
        )

    def test_solution_file_has_valid_content(self):
        """Verify the solution.sol file contains valid CPLEX solution data."""
        solution_file = "/home/user/solver/solution.sol"
        with open(solution_file, 'r') as f:
            content = f.read()

        # Check for indicators of a valid CPLEX solution file
        # CPLEX can write solutions in different formats (XML, SOL text format)
        valid_indicators = [
            'objective',
            'ObjVal',
            'value=',
            '<?xml',
            'CPLEXSolution',
            'objectiveValue',
            'Objective',
            'OBJVAL',
            'solution'
        ]

        content_lower = content.lower()
        has_valid_content = any(ind.lower() in content_lower for ind in valid_indicators)

        assert has_valid_content, (
            f"Solution file at {solution_file} does not contain valid CPLEX solution data. "
            "The file should contain objective values and/or variable assignments. "
            f"File content preview: {content[:500]}"
        )

    def test_solution_file_contains_objective_or_values(self):
        """Verify the solution file contains objective value or variable values."""
        solution_file = "/home/user/solver/solution.sol"

        # Use grep to check for solution content
        result = subprocess.run(
            ['grep', '-E', '(objective|ObjVal|value=|objectiveValue)', solution_file],
            capture_output=True,
            text=True
        )

        # grep returns 0 if matches found, 1 if no matches
        assert result.returncode == 0, (
            f"Solution file at {solution_file} does not contain expected solution markers. "
            "A valid CPLEX solution should contain objective values or variable assignments. "
            "This suggests the solution was not generated by CPLEX solving dispatch.lp."
        )


class TestWrapperScriptRuns:
    """Tests to verify the wrapper script runs successfully."""

    def test_wrapper_script_completes_without_memory_error(self):
        """Verify running the wrapper script completes without CPXERR_NO_MEMORY."""
        # First, remove existing solution to test fresh run
        solution_file = "/home/user/solver/solution.sol"
        if os.path.exists(solution_file):
            os.remove(solution_file)

        # Run the wrapper script
        result = subprocess.run(
            ['/home/user/solver/run_cplex.sh'],
            capture_output=True,
            text=True,
            timeout=900,  # 15 minute timeout
            cwd='/home/user/solver'
        )

        combined_output = result.stdout + result.stderr

        # Check that there's no memory error
        assert 'CPXERR_NO_MEMORY' not in combined_output, (
            "The wrapper script still produces CPXERR_NO_MEMORY error. "
            "The memory limit fix was not effective. "
            f"Output: {combined_output[:1000]}"
        )

        assert 'Out of memory' not in combined_output or 'out of memory' not in combined_output.lower(), (
            "The wrapper script still produces an 'Out of memory' error. "
            "The memory limit fix was not effective."
        )

    def test_wrapper_script_exits_successfully(self):
        """Verify the wrapper script exits with code 0."""
        # Run the wrapper script
        result = subprocess.run(
            ['/home/user/solver/run_cplex.sh'],
            capture_output=True,
            text=True,
            timeout=900,
            cwd='/home/user/solver'
        )

        assert result.returncode == 0, (
            f"Wrapper script exited with code {result.returncode} instead of 0. "
            f"stdout: {result.stdout[:500]}\n"
            f"stderr: {result.stderr[:500]}"
        )

    def test_solution_generated_after_run(self):
        """Verify a solution file is generated after running the wrapper."""
        solution_file = "/home/user/solver/solution.sol"

        # Remove existing solution
        if os.path.exists(solution_file):
            os.remove(solution_file)

        # Run the wrapper
        result = subprocess.run(
            ['/home/user/solver/run_cplex.sh'],
            capture_output=True,
            text=True,
            timeout=900,
            cwd='/home/user/solver'
        )

        assert os.path.isfile(solution_file), (
            f"Solution file was not created at {solution_file} after running the wrapper. "
            f"Exit code: {result.returncode}\n"
            f"stdout: {result.stdout[:500]}\n"
            f"stderr: {result.stderr[:500]}"
        )

        # Verify it has content
        with open(solution_file, 'r') as f:
            content = f.read()

        assert len(content) > 100, (
            f"Solution file at {solution_file} is too small ({len(content)} bytes). "
            "A valid CPLEX solution should have substantial content."
        )


class TestMemoryLimitAdequate:
    """Tests to verify the memory limit is now adequate."""

    def test_no_small_ulimit_in_script(self):
        """Verify there's no small ulimit -v value in the script."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Look for ulimit -v with a small value (less than 16GB = 16777216 KB)
        # Pattern matches ulimit -v followed by a number
        ulimit_pattern = re.compile(r'ulimit\s+-v\s+(\d+)')
        matches = ulimit_pattern.findall(content)

        for match in matches:
            limit_kb = int(match)
            limit_gb = limit_kb / (1024 * 1024)
            assert limit_gb >= 16 or limit_kb == 0, (  # 0 might mean unlimited in some contexts
                f"Script still contains a restrictive ulimit -v {match} ({limit_gb:.1f}GB). "
                "The limit should be at least 16GB or removed entirely."
            )

    def test_ulimit_unlimited_or_large(self):
        """Verify ulimit is either removed, set to unlimited, or set to a large value."""
        script_path = "/home/user/solver/run_cplex.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check if ulimit -v is present at all
        if 'ulimit -v' in content or 'ulimit  -v' in content:
            # If present, should be unlimited or a large value
            has_unlimited = 'ulimit -v unlimited' in content or 'ulimit -v  unlimited' in content

            # Check for large numeric values (>= 16GB in KB)
            ulimit_pattern = re.compile(r'ulimit\s+-v\s+(\d+)')
            matches = ulimit_pattern.findall(content)
            has_large_value = any(int(m) >= 16777216 for m in matches) if matches else False

            # Check if the line is commented out
            lines = content.split('\n')
            ulimit_commented = all(
                line.strip().startswith('#') 
                for line in lines 
                if 'ulimit' in line and '-v' in line
            )

            assert has_unlimited or has_large_value or ulimit_commented, (
                "The ulimit -v in the script is not set to 'unlimited', "
                "a large value (>=16GB), or commented out. "
                "CPLEX needs adequate virtual memory for presolve."
            )
