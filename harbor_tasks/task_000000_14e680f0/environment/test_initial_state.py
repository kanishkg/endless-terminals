# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the buildbot agent that keeps dying mid-compile.
"""

import os
import pytest
import subprocess
import re


BUILDBOT_DIR = "/home/user/buildbot"
RUN_AGENT_SCRIPT = os.path.join(BUILDBOT_DIR, "run_agent.sh")
WORKER_PY = os.path.join(BUILDBOT_DIR, "worker.py")
WATCHDOG_SCRIPT = os.path.join(BUILDBOT_DIR, "watchdog.sh")
MOCK_BUILD_SCRIPT = os.path.join(BUILDBOT_DIR, "mock_build.sh")
CONFIG_INI = os.path.join(BUILDBOT_DIR, "config.ini")


class TestBuildBotDirectoryExists:
    """Test that the buildbot directory and required files exist."""

    def test_buildbot_directory_exists(self):
        """The /home/user/buildbot directory must exist."""
        assert os.path.isdir(BUILDBOT_DIR), (
            f"Directory {BUILDBOT_DIR} does not exist. "
            "The buildbot directory is required for this task."
        )

    def test_run_agent_script_exists(self):
        """The run_agent.sh wrapper script must exist."""
        assert os.path.isfile(RUN_AGENT_SCRIPT), (
            f"File {RUN_AGENT_SCRIPT} does not exist. "
            "This is the wrapper script that launches the worker."
        )

    def test_worker_py_exists(self):
        """The worker.py Python script must exist."""
        assert os.path.isfile(WORKER_PY), (
            f"File {WORKER_PY} does not exist. "
            "This is the Python worker script that runs builds."
        )

    def test_watchdog_script_exists(self):
        """The watchdog.sh script must exist."""
        assert os.path.isfile(WATCHDOG_SCRIPT), (
            f"File {WATCHDOG_SCRIPT} does not exist. "
            "This is the watchdog script that monitors heartbeats."
        )

    def test_mock_build_script_exists(self):
        """The mock_build.sh script must exist."""
        assert os.path.isfile(MOCK_BUILD_SCRIPT), (
            f"File {MOCK_BUILD_SCRIPT} does not exist. "
            "This is the mock build script that simulates the timing."
        )

    def test_config_ini_exists(self):
        """The config.ini configuration file must exist."""
        assert os.path.isfile(CONFIG_INI), (
            f"File {CONFIG_INI} does not exist. "
            "This is the configuration file for the buildbot."
        )


class TestFilesAreExecutable:
    """Test that shell scripts are executable."""

    def test_run_agent_is_executable(self):
        """run_agent.sh must be executable."""
        assert os.access(RUN_AGENT_SCRIPT, os.X_OK), (
            f"{RUN_AGENT_SCRIPT} is not executable. "
            "The wrapper script must be executable to run."
        )

    def test_watchdog_is_executable(self):
        """watchdog.sh must be executable."""
        assert os.access(WATCHDOG_SCRIPT, os.X_OK), (
            f"{WATCHDOG_SCRIPT} is not executable. "
            "The watchdog script must be executable."
        )

    def test_mock_build_is_executable(self):
        """mock_build.sh must be executable."""
        assert os.access(MOCK_BUILD_SCRIPT, os.X_OK), (
            f"{MOCK_BUILD_SCRIPT} is not executable. "
            "The mock build script must be executable."
        )


class TestFilesAreWritable:
    """Test that files in buildbot directory are writable."""

    def test_run_agent_is_writable(self):
        """run_agent.sh must be writable."""
        assert os.access(RUN_AGENT_SCRIPT, os.W_OK), (
            f"{RUN_AGENT_SCRIPT} is not writable. "
            "The student needs to be able to modify this file."
        )

    def test_worker_py_is_writable(self):
        """worker.py must be writable."""
        assert os.access(WORKER_PY, os.W_OK), (
            f"{WORKER_PY} is not writable. "
            "The student needs to be able to modify this file."
        )

    def test_watchdog_is_writable(self):
        """watchdog.sh must be writable."""
        assert os.access(WATCHDOG_SCRIPT, os.W_OK), (
            f"{WATCHDOG_SCRIPT} is not writable. "
            "The student needs to be able to modify this file."
        )


class TestRunAgentScriptContent:
    """Test that run_agent.sh has the expected structure."""

    def test_run_agent_invokes_watchdog(self):
        """run_agent.sh must invoke watchdog.sh."""
        with open(RUN_AGENT_SCRIPT, 'r') as f:
            content = f.read()
        assert 'watchdog.sh' in content, (
            f"{RUN_AGENT_SCRIPT} does not contain 'watchdog.sh'. "
            "The run_agent.sh script must invoke the watchdog."
        )

    def test_run_agent_invokes_worker(self):
        """run_agent.sh must invoke worker.py."""
        with open(RUN_AGENT_SCRIPT, 'r') as f:
            content = f.read()
        assert 'worker.py' in content, (
            f"{RUN_AGENT_SCRIPT} does not contain 'worker.py'. "
            "The run_agent.sh script must invoke the worker."
        )

    def test_run_agent_is_bash_script(self):
        """run_agent.sh must be a bash script."""
        with open(RUN_AGENT_SCRIPT, 'r') as f:
            first_line = f.readline()
        assert first_line.strip().startswith('#!') and 'bash' in first_line, (
            f"{RUN_AGENT_SCRIPT} does not appear to be a bash script. "
            f"First line: {first_line.strip()}"
        )


class TestWatchdogScriptContent:
    """Test that watchdog.sh has the expected structure."""

    def test_watchdog_checks_heartbeat_file(self):
        """watchdog.sh must check /tmp/buildbot_heartbeat."""
        with open(WATCHDOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'buildbot_heartbeat' in content, (
            f"{WATCHDOG_SCRIPT} does not contain 'buildbot_heartbeat'. "
            "The watchdog must check the heartbeat file."
        )

    def test_watchdog_has_kill_logic(self):
        """watchdog.sh must have logic to kill the worker."""
        with open(WATCHDOG_SCRIPT, 'r') as f:
            content = f.read()
        assert 'kill' in content, (
            f"{WATCHDOG_SCRIPT} does not contain 'kill'. "
            "The watchdog must be able to kill the worker."
        )

    def test_watchdog_is_bash_script(self):
        """watchdog.sh must be a bash script."""
        with open(WATCHDOG_SCRIPT, 'r') as f:
            first_line = f.readline()
        assert first_line.strip().startswith('#!') and 'bash' in first_line, (
            f"{WATCHDOG_SCRIPT} does not appear to be a bash script. "
            f"First line: {first_line.strip()}"
        )


class TestWorkerPyContent:
    """Test that worker.py has the expected structure with the bug."""

    def test_worker_has_validate_build_artifacts_function(self):
        """worker.py must have a validate_build_artifacts function."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'def validate_build_artifacts' in content, (
            f"{WORKER_PY} does not contain 'def validate_build_artifacts'. "
            "The validation function must exist."
        )

    def test_worker_calls_validate_build_artifacts(self):
        """worker.py must call validate_build_artifacts."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        # Look for a call to validate_build_artifacts (not just the definition)
        # Pattern: validate_build_artifacts( but not def validate_build_artifacts
        lines = content.split('\n')
        has_call = False
        for line in lines:
            if 'validate_build_artifacts(' in line and 'def validate_build_artifacts' not in line:
                has_call = True
                break
        assert has_call, (
            f"{WORKER_PY} does not call validate_build_artifacts(). "
            "The validation function must be called during builds."
        )

    def test_worker_has_file_lock(self):
        """worker.py must have a file_lock for thread synchronization."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'file_lock' in content, (
            f"{WORKER_PY} does not contain 'file_lock'. "
            "The file lock is required for thread synchronization."
        )

    def test_worker_has_threading_import(self):
        """worker.py must import threading."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'import threading' in content or 'from threading' in content, (
            f"{WORKER_PY} does not import threading. "
            "Threading is required for the heartbeat mechanism."
        )

    def test_worker_has_heartbeat_logic(self):
        """worker.py must have heartbeat writing logic."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'heartbeat' in content.lower(), (
            f"{WORKER_PY} does not contain heartbeat-related code. "
            "The worker must write heartbeats."
        )

    def test_worker_references_mock_build(self):
        """worker.py must reference mock_build.sh."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'mock_build.sh' in content, (
            f"{WORKER_PY} does not reference 'mock_build.sh'. "
            "The worker must run the mock build script."
        )

    def test_worker_has_subprocess(self):
        """worker.py must use subprocess for running builds."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()
        assert 'subprocess' in content, (
            f"{WORKER_PY} does not import/use subprocess. "
            "Subprocess is required for running builds."
        )


class TestMockBuildScript:
    """Test that mock_build.sh has the expected structure."""

    def test_mock_build_is_bash_script(self):
        """mock_build.sh must be a bash script."""
        with open(MOCK_BUILD_SCRIPT, 'r') as f:
            first_line = f.readline()
        assert first_line.strip().startswith('#!') and 'bash' in first_line, (
            f"{MOCK_BUILD_SCRIPT} does not appear to be a bash script. "
            f"First line: {first_line.strip()}"
        )

    def test_mock_build_has_sleep_or_timing(self):
        """mock_build.sh must have timing/sleep logic to simulate build duration."""
        with open(MOCK_BUILD_SCRIPT, 'r') as f:
            content = f.read()
        assert 'sleep' in content, (
            f"{MOCK_BUILD_SCRIPT} does not contain 'sleep'. "
            "The mock build must simulate timing with sleep commands."
        )


class TestRequiredToolsAvailable:
    """Test that required system tools are available."""

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(['which', 'python3'], capture_output=True)
        assert result.returncode == 0, (
            "python3 is not available in PATH. "
            "Python 3 is required to run worker.py."
        )

    def test_bash_available(self):
        """Bash must be available."""
        result = subprocess.run(['which', 'bash'], capture_output=True)
        assert result.returncode == 0, (
            "bash is not available in PATH. "
            "Bash is required to run the shell scripts."
        )

    def test_bc_available(self):
        """bc (calculator) must be available for watchdog arithmetic."""
        result = subprocess.run(['which', 'bc'], capture_output=True)
        assert result.returncode == 0, (
            "bc is not available in PATH. "
            "bc is required by watchdog.sh for arithmetic."
        )


class TestTmpDirectoryWritable:
    """Test that /tmp is writable for heartbeat file."""

    def test_tmp_exists_and_writable(self):
        """/tmp must exist and be writable."""
        assert os.path.isdir('/tmp'), "/tmp directory does not exist."
        assert os.access('/tmp', os.W_OK), (
            "/tmp is not writable. "
            "The heartbeat file must be written to /tmp."
        )


class TestInitialBugConditions:
    """Test that the bug conditions are present in the initial state."""

    def test_validate_function_acquires_file_lock(self):
        """validate_build_artifacts must acquire file_lock (the bug)."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()

        # Find the validate_build_artifacts function and check if it uses file_lock
        # This is the bug - it holds the lock during long processing
        in_validate_func = False
        has_lock_in_validate = False
        brace_count = 0

        for line in content.split('\n'):
            if 'def validate_build_artifacts' in line:
                in_validate_func = True
                continue
            if in_validate_func:
                if 'def ' in line and 'validate_build_artifacts' not in line:
                    # Hit another function definition
                    break
                if 'file_lock' in line:
                    has_lock_in_validate = True
                    break

        assert has_lock_in_validate, (
            "validate_build_artifacts does not appear to use file_lock. "
            "The initial bug condition requires the validation function to hold the lock."
        )

    def test_heartbeat_function_uses_file_lock(self):
        """The heartbeat writing function must also use file_lock."""
        with open(WORKER_PY, 'r') as f:
            content = f.read()

        # Check that heartbeat writing also uses file_lock
        # This creates the contention that causes the bug
        assert 'file_lock' in content, (
            "file_lock is not present in worker.py. "
            "Both heartbeat and validation must use the same lock for the bug to exist."
        )

        # Count occurrences of file_lock usage (should be at least 2 - heartbeat and validate)
        lock_usages = content.count('file_lock')
        assert lock_usages >= 2, (
            f"file_lock is only used {lock_usages} time(s). "
            "Both heartbeat and validation should use it for the bug condition."
        )
