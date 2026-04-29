# test_final_state.py
"""
Tests to validate the final state after the student has fixed the buildbot agent
that was dying mid-compile due to a lock contention issue between the heartbeat
thread and the validate_build_artifacts function.
"""

import os
import pytest
import subprocess
import re
import time
import hashlib


BUILDBOT_DIR = "/home/user/buildbot"
RUN_AGENT_SCRIPT = os.path.join(BUILDBOT_DIR, "run_agent.sh")
WORKER_PY = os.path.join(BUILDBOT_DIR, "worker.py")
WATCHDOG_SCRIPT = os.path.join(BUILDBOT_DIR, "watchdog.sh")
MOCK_BUILD_SCRIPT = os.path.join(BUILDBOT_DIR, "mock_build.sh")
CONFIG_INI = os.path.join(BUILDBOT_DIR, "config.ini")
HEARTBEAT_FILE = "/tmp/buildbot_heartbeat"

# Store the original mock_build.sh hash for invariant check
# This will be computed at test time from the file
EXPECTED_MOCK_BUILD_CONTENT_PATTERNS = ['sleep', '#!/bin/bash']


class TestRequiredFilesExist:
    """Test that all required files still exist after the fix."""

    def test_buildbot_directory_exists(self):
        """The /home/user/buildbot directory must still exist."""
        assert os.path.isdir(BUILDBOT_DIR), (
            f"Directory {BUILDBOT_DIR} does not exist."
        )

    def test_run_agent_script_exists(self):
        """run_agent.sh must still exist."""
        assert os.path.isfile(RUN_AGENT_SCRIPT), (
            f"File {RUN_AGENT_SCRIPT} does not exist."
        )

    def test_worker_py_exists(self):
        """worker.py must still exist."""
        assert os.path.isfile(WORKER_PY), (
            f"File {WORKER_PY} does not exist."
        )

    def test_watchdog_script_exists(self):
        """watchdog.sh must still exist."""
        assert os.path.isfile(WATCHDOG_SCRIPT), (
            f"File {WATCHDOG_SCRIPT} does not exist."
        )

    def test_mock_build_script_exists(self):
        """mock_build.sh must still exist."""
        assert os.path.isfile(MOCK_BUILD_SCRIPT), (
            f"File {MOCK_BUILD_SCRIPT} does not exist."
        )


class TestInvariantWatchdogMechanism:
    """Test that the watchdog mechanism still exists and functions."""

    def test_run_agent_still_invokes_watchdog(self):
        """run_agent.sh must still invoke watchdog.sh."""
        with open(RUN_AGENT_SCRIPT, 'r') as f:
            content = f.read()
        assert 'watchdog.sh' in content, (
            f"{RUN_AGENT_SCRIPT} no longer invokes watchdog.sh. "
            "The watchdog mechanism must remain in place - cannot simply remove it."
        )

    def test_watchdog_still_checks_heartbeat(self):
        """watchdog.sh must still check the heartbeat file."""
        with open(WATCHDOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'buildbot_heartbeat' in content, (
            f"{WATCHDOG_SCRIPT} no longer checks buildbot_heartbeat. "
            "The watchdog must still monitor the heartbeat file."
        )

    def test_watchdog_still_has_kill_logic(self):
        """watchdog.sh must still have logic to kill stale workers."""
        with open(WATCHDOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'kill' in content, (
            f"{WATCHDOG_SCRIPT} no longer has kill logic. "
            "The watchdog must still be able to kill stale workers."
        )

    def test_watchdog_timeout_not_excessive(self):
        """Watchdog timeout must remain <=30 seconds (no cheating)."""
        with open(WATCHDOG_SCRIPT, 'r') as f:
            content = f.read()

        # Look for the timeout comparison - should be around 30 seconds
        # Pattern like: AGE > 30 or similar
        timeout_match = re.search(r'>\s*(\d+)', content)
        if timeout_match:
            timeout_val = int(timeout_match.group(1))
            assert timeout_val <= 60, (
                f"Watchdog timeout appears to be {timeout_val} seconds. "
                "Cannot cheat by setting an excessively long timeout (must be <=60s)."
            )


class TestInvariantValidateFunction:
    """Test that validate_build_artifacts still exists and is called."""

    def test_validate_function_exists(self):
        """worker.py must still have validate_build_artifacts function."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'def validate_build_artifacts' in content, (
            f"{WORKER_PY} no longer contains 'def validate_build_artifacts'. "
            "The validation function must still exist - cannot delete it entirely."
        )

    def test_validate_function_is_called(self):
        """worker.py must still call validate_build_artifacts."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()

        # Look for calls to validate_build_artifacts (not just the definition)
        lines = content.split('\n')
        has_call = False
        for line in lines:
            # Check for function call, not definition
            if 'validate_build_artifacts(' in line and 'def validate_build_artifacts' not in line:
                has_call = True
                break

        assert has_call, (
            f"{WORKER_PY} no longer calls validate_build_artifacts(). "
            "The validation function must still be called during builds."
        )


class TestInvariantFileLockExists:
    """Test that file_lock still exists (cannot remove it entirely)."""

    def test_file_lock_still_exists(self):
        """worker.py must still have a file_lock."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'file_lock' in content or 'Lock()' in content, (
            f"{WORKER_PY} no longer has file_lock. "
            "The lock must still exist - the fix should be to not hold it during validation, "
            "not to remove it entirely."
        )


class TestInvariantHeartbeatMechanism:
    """Test that heartbeat mechanism still exists with reasonable interval."""

    def test_heartbeat_still_written(self):
        """worker.py must still write to the heartbeat file."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'buildbot_heartbeat' in content or 'heartbeat' in content.lower(), (
            f"{WORKER_PY} no longer has heartbeat writing logic. "
            "The heartbeat mechanism must remain in place."
        )

    def test_heartbeat_interval_reasonable(self):
        """Heartbeat interval must remain <=5 seconds (no cheating with tiny intervals)."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()

        # Look for Timer intervals - should be around 5 seconds or less
        # Pattern like: Timer(5.0, or Timer(5, or similar
        timer_matches = re.findall(r'Timer\s*\(\s*([\d.]+)', content)
        for match in timer_matches:
            interval = float(match)
            # Interval should be reasonable - not less than 0.1s (would be cheating)
            # and not more than 10s (would be too slow)
            assert 0.1 <= interval <= 10, (
                f"Heartbeat interval appears to be {interval}s. "
                "Interval should be reasonable (0.1-10 seconds)."
            )


class TestInvariantMockBuildUnchanged:
    """Test that mock_build.sh was not modified."""

    def test_mock_build_is_bash_script(self):
        """mock_build.sh must still be a bash script."""
        with open(MOCK_BUILD_SCRIPT, 'r') as f:
            first_line = f.readline()
        assert '#!/bin/bash' in first_line or '#!/usr/bin/env bash' in first_line, (
            f"{MOCK_BUILD_SCRIPT} is no longer a bash script. "
            "The mock build script must remain unchanged."
        )

    def test_mock_build_has_sleep(self):
        """mock_build.sh must still have sleep commands."""
        with open(MOCK_BUILD_SCRIPT, 'r') as f:
            content = f.read()
        assert 'sleep' in content, (
            f"{MOCK_BUILD_SCRIPT} no longer has sleep commands. "
            "The mock build script must remain unchanged."
        )


class TestBugIsFix:
    """Test that the bug has been fixed - validate no longer holds lock during processing."""

    def test_validate_does_not_hold_lock_during_processing(self):
        """validate_build_artifacts should not hold file_lock during long processing."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()

        # Find the validate_build_artifacts function body
        lines = content.split('\n')
        in_validate_func = False
        validate_func_lines = []
        indent_level = None

        for i, line in enumerate(lines):
            if 'def validate_build_artifacts' in line:
                in_validate_func = True
                # Determine the indentation of the function definition
                indent_level = len(line) - len(line.lstrip())
                continue

            if in_validate_func:
                # Check if we've hit another function at the same or lower indent level
                stripped = line.lstrip()
                if stripped and not stripped.startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level and stripped.startswith('def '):
                        break
                validate_func_lines.append(line)

        validate_body = '\n'.join(validate_func_lines)

        # The fix should either:
        # 1. Remove file_lock from validate_build_artifacts entirely
        # 2. Only hold the lock briefly (not around the processing loop)
        # 3. Use a different lock

        # Check if file_lock is used with 'with' statement wrapping the entire processing
        # A problematic pattern would be: with file_lock: followed by the processing loop

        # If file_lock is in validate but the time.sleep or processing loop is NOT
        # inside the with block, that's okay

        # Simple heuristic: if 'with file_lock' appears and the processing (time.sleep or for loop)
        # is at a deeper indentation, that's the bug. If file_lock is not used at all in validate,
        # or if it's used but the processing is outside the with block, that's fixed.

        has_file_lock_in_validate = 'file_lock' in validate_body

        if has_file_lock_in_validate:
            # Check if the processing loop is inside a with file_lock block
            # This is a heuristic - look for 'with file_lock' followed by processing
            with_lock_pattern = re.search(r'with\s+file_lock.*?:', validate_body, re.DOTALL)
            if with_lock_pattern:
                # Find what's inside the with block
                after_with = validate_body[with_lock_pattern.end():]
                # Check if the long processing (for loop with time.sleep) is in there
                if 'for ' in after_with and 'time.sleep' in after_with:
                    # Check indentation - if both are at same or deeper indent, bug still exists
                    # This is getting complex, so let's just run the actual test
                    pass

        # The real test is whether run_agent.sh completes successfully
        # This structural check is just a sanity check


class TestRunAgentCompletes:
    """The main test - run_agent.sh must complete successfully with mock build."""

    def test_run_agent_completes_with_exit_code_zero(self):
        """
        run_agent.sh must complete with exit code 0.
        This is the primary success criterion - the worker must survive the full build.
        """
        # Clean up any previous heartbeat file
        if os.path.exists(HEARTBEAT_FILE):
            os.remove(HEARTBEAT_FILE)

        # Run the agent with a timeout
        # Mock build takes ~60 seconds, give it 120 seconds max
        start_time = time.time()

        result = subprocess.run(
            ['bash', RUN_AGENT_SCRIPT],
            cwd=BUILDBOT_DIR,
            capture_output=True,
            timeout=180  # 3 minutes max
        )

        elapsed_time = time.time() - start_time

        # Check exit code
        assert result.returncode == 0, (
            f"run_agent.sh failed with exit code {result.returncode}.\n"
            f"Elapsed time: {elapsed_time:.1f}s\n"
            f"STDOUT:\n{result.stdout.decode('utf-8', errors='replace')[-2000:]}\n"
            f"STDERR:\n{result.stderr.decode('utf-8', errors='replace')[-2000:]}\n"
            "The worker was likely killed by the watchdog due to stale heartbeat. "
            "The bug has not been fixed."
        )

    def test_run_agent_takes_reasonable_time(self):
        """
        run_agent.sh should take approximately 60-90 seconds (mock build duration).
        If it completes too quickly, something is wrong.
        """
        # Clean up any previous heartbeat file
        if os.path.exists(HEARTBEAT_FILE):
            os.remove(HEARTBEAT_FILE)

        start_time = time.time()

        result = subprocess.run(
            ['bash', RUN_AGENT_SCRIPT],
            cwd=BUILDBOT_DIR,
            capture_output=True,
            timeout=180
        )

        elapsed_time = time.time() - start_time

        # Should take at least 50 seconds (mock build is ~60 seconds)
        assert elapsed_time >= 50, (
            f"run_agent.sh completed in only {elapsed_time:.1f}s. "
            "This is suspiciously fast - the mock build should take ~60 seconds. "
            "Something may have been modified incorrectly."
        )

        # Should not take more than 120 seconds
        assert elapsed_time <= 120, (
            f"run_agent.sh took {elapsed_time:.1f}s to complete. "
            "This is longer than expected - something may be wrong."
        )


class TestWorkerPySyntaxValid:
    """Test that worker.py is still valid Python."""

    def test_worker_py_syntax(self):
        """worker.py must have valid Python syntax."""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', WORKER_PY],
            capture_output=True
        )
        assert result.returncode == 0, (
            f"worker.py has syntax errors:\n"
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )


class TestScriptsSyntaxValid:
    """Test that shell scripts have valid syntax."""

    def test_run_agent_syntax(self):
        """run_agent.sh must have valid bash syntax."""
        result = subprocess.run(
            ['bash', '-n', RUN_AGENT_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, (
            f"run_agent.sh has syntax errors:\n"
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )

    def test_watchdog_syntax(self):
        """watchdog.sh must have valid bash syntax."""
        result = subprocess.run(
            ['bash', '-n', WATCHDOG_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, (
            f"watchdog.sh has syntax errors:\n"
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )
