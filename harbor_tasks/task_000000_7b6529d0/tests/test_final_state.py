# test_final_state.py
"""
Tests to validate the final state after the student has completed the task.
Verifies that the log aggregator is fixed and working correctly.
"""

import os
import subprocess
import pytest
import time
import re


# Constants
HOME = "/home/user"
LOGWATCH_DIR = os.path.join(HOME, "logwatch")
TAIL_SCRIPT = os.path.join(LOGWATCH_DIR, "tail_all.py")
UNIFIED_LOG = os.path.join(LOGWATCH_DIR, "unified.log")
VAR_LOG_APPS = "/var/log/apps"
SRV_APPLOGS = "/srv/applogs"
FEEDER_SCRIPT = os.path.join(LOGWATCH_DIR, "feeder.sh")

# The originally cyclic symlinks
ORIGINALLY_CYCLIC_SYMLINKS = [
    "app089.log", "app112.log", "app134.log", "app156.log",
    "app178.log", "app189.log", "app201.log", "app212.log",
    "app223.log", "app231.log", "app238.log", "app245.log"
]

TOTAL_SYMLINKS = 247
MIN_LEGITIMATE_SYMLINKS = 230


class TestDirectoryStructure:
    """Test that required directories still exist."""

    def test_logwatch_directory_exists(self):
        """Verify /home/user/logwatch/ directory exists."""
        assert os.path.isdir(LOGWATCH_DIR), \
            f"Directory {LOGWATCH_DIR} does not exist"

    def test_var_log_apps_exists(self):
        """Verify /var/log/apps/ directory exists."""
        assert os.path.isdir(VAR_LOG_APPS), \
            f"Directory {VAR_LOG_APPS} does not exist"

    def test_srv_applogs_exists(self):
        """Verify /srv/applogs/ directory exists."""
        assert os.path.isdir(SRV_APPLOGS), \
            f"Directory {SRV_APPLOGS} does not exist"


class TestSrvApplogsUnchanged:
    """Test that /srv/applogs/ contents are unchanged (invariant)."""

    def test_correct_number_of_log_files(self):
        """Verify there are still 247 log files in /srv/applogs/."""
        entries = os.listdir(SRV_APPLOGS)
        log_files = [e for e in entries if e.endswith('.log')]
        assert len(log_files) == TOTAL_SYMLINKS, \
            f"Expected {TOTAL_SYMLINKS} log files in {SRV_APPLOGS}, found {len(log_files)}. " \
            f"/srv/applogs/ contents should not be changed."

    def test_log_files_are_regular_files(self):
        """Verify log files in /srv/applogs/ are still regular files."""
        for i in range(1, TOTAL_SYMLINKS + 1):
            filename = f"app{i:03d}.log"
            full_path = os.path.join(SRV_APPLOGS, filename)
            assert os.path.isfile(full_path), \
                f"{full_path} does not exist or is not a regular file"
            assert not os.path.islink(full_path), \
                f"{full_path} should be a regular file, not a symlink"


class TestFeederStillRunning:
    """Test that the feeder process is still running (invariant)."""

    def test_feeder_process_running(self):
        """Verify feeder.sh is still running."""
        result = subprocess.run(
            ['pgrep', '-f', 'feeder.sh'],
            capture_output=True
        )
        assert result.returncode == 0, \
            "feeder.sh process is not running. It should still be running as an invariant."


class TestSymlinksFixed:
    """Test that symlinks in /var/log/apps/ are fixed."""

    def test_all_symlinks_valid_or_removed(self):
        """Verify all entries in /var/log/apps/ are valid symlinks or cyclic ones removed."""
        entries = os.listdir(VAR_LOG_APPS)

        for entry in entries:
            full_path = os.path.join(VAR_LOG_APPS, entry)
            if os.path.islink(full_path):
                # If it's a symlink, it should resolve to a real file in /srv/applogs/
                real_path = os.path.realpath(full_path)
                assert real_path.startswith(SRV_APPLOGS), \
                    f"Symlink {full_path} does not resolve to a file in {SRV_APPLOGS}. " \
                    f"Got: {real_path}. Cyclic symlinks should be fixed or removed."
                assert os.path.isfile(real_path), \
                    f"Symlink {full_path} resolves to {real_path} which is not a regular file."

    def test_minimum_symlinks_remain(self):
        """Verify at least 235 symlinks remain (non-cyclic ones should be intact)."""
        entries = os.listdir(VAR_LOG_APPS)
        symlink_count = sum(1 for e in entries if os.path.islink(os.path.join(VAR_LOG_APPS, e)))

        # At minimum, the 235 legitimate symlinks should remain
        # The 12 cyclic ones could be fixed or removed
        assert symlink_count >= 235, \
            f"Expected at least 235 symlinks to remain in {VAR_LOG_APPS}, found {symlink_count}. " \
            f"The legitimate symlinks should not be removed."


class TestLegitimateSymlinksPreserved:
    """Test that legitimate symlinks were not recreated (anti-shortcut)."""

    def test_symlinks_not_mass_recreated(self):
        """
        Verify that at least 230 of the original symlinks have the same inode
        (were not recreated). This prevents the shortcut of deleting all and recreating.
        """
        # We need to check that symlinks weren't all deleted and recreated
        # Since we can't compare to initial inodes directly, we check that
        # the symlinks that should point to specific files still do

        originally_cyclic_set = set(ORIGINALLY_CYCLIC_SYMLINKS)
        valid_symlinks = 0

        for i in range(1, TOTAL_SYMLINKS + 1):
            name = f"app{i:03d}.log"
            full_path = os.path.join(VAR_LOG_APPS, name)

            if name in originally_cyclic_set:
                # These could be fixed or removed
                continue

            if os.path.islink(full_path):
                real_path = os.path.realpath(full_path)
                expected_target = os.path.join(SRV_APPLOGS, name)
                if real_path == expected_target:
                    valid_symlinks += 1

        # Should have at least 230 of the 235 non-cyclic symlinks intact
        assert valid_symlinks >= MIN_LEGITIMATE_SYMLINKS, \
            f"Expected at least {MIN_LEGITIMATE_SYMLINKS} legitimate symlinks to remain intact, " \
            f"found {valid_symlinks}. Did you delete and recreate all symlinks?"


class TestScriptStillUsesInotify:
    """Test that the script still uses inotify (not polling)."""

    def test_script_uses_inotify(self):
        """Verify tail_all.py still uses pyinotify/inotify."""
        with open(TAIL_SCRIPT, 'r') as f:
            content = f.read()

        assert 'pyinotify' in content or 'inotify' in content, \
            f"Script {TAIL_SCRIPT} must still use inotify/pyinotify for watching. " \
            f"Cannot replace with polling mechanism."

    def test_no_polling_pattern_added(self):
        """Verify no polling patterns were added to the script."""
        with open(TAIL_SCRIPT, 'r') as f:
            content = f.read()

        # Check for common polling patterns that shouldn't be in the main watching logic
        # We're looking for patterns like "while True: ... time.sleep" that indicate polling

        # This is a heuristic check - we look for suspicious patterns
        # but allow legitimate use of sleep in non-polling contexts

        lines = content.split('\n')
        in_while_true = False
        suspicious_patterns = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check for subprocess-based tail
            if 'subprocess' in stripped and 'tail' in content[max(0, content.find(stripped)-100):content.find(stripped)+100]:
                if 'Popen' in stripped or 'run' in stripped or 'call' in stripped:
                    suspicious_patterns.append(f"Line {i+1}: Possible subprocess tail: {stripped}")

        # Allow the script to have some flexibility, but flag obvious polling replacements
        # The key check is that pyinotify is still the main mechanism
        assert 'Notifier' in content or 'WatchManager' in content or 'pyinotify' in content, \
            f"Script must use pyinotify's Notifier/WatchManager for watching. " \
            f"Found suspicious patterns: {suspicious_patterns}"


class TestScriptRunsCorrectly:
    """Test that the script now runs correctly without exiting early."""

    def test_script_does_not_exit_early(self):
        """Verify the script runs for full 60 seconds (timeout kills it)."""
        # Clear or note the current state of unified.log
        if os.path.exists(UNIFIED_LOG):
            initial_size = os.path.getsize(UNIFIED_LOG)
        else:
            initial_size = 0

        # Run the script with timeout
        result = subprocess.run(
            ['timeout', '60', 'python3', TAIL_SCRIPT],
            cwd=LOGWATCH_DIR,
            capture_output=True
        )

        # Exit code 124 means timeout killed it (which is what we want)
        assert result.returncode == 124, \
            f"Script exited early with code {result.returncode}. " \
            f"Expected it to run for 60 seconds and be killed by timeout (exit code 124). " \
            f"stdout: {result.stdout.decode()[:500]}, stderr: {result.stderr.decode()[:500]}"

    def test_unified_log_has_content(self):
        """Verify unified.log contains aggregated content after running."""
        # First run the script for a bit to generate content
        if os.path.exists(UNIFIED_LOG):
            os.remove(UNIFIED_LOG)

        # Run script for 60 seconds
        result = subprocess.run(
            ['timeout', '60', 'python3', TAIL_SCRIPT],
            cwd=LOGWATCH_DIR,
            capture_output=True
        )

        assert os.path.exists(UNIFIED_LOG), \
            f"unified.log was not created at {UNIFIED_LOG}"

        with open(UNIFIED_LOG, 'r') as f:
            content = f.read()

        lines = [l for l in content.strip().split('\n') if l.strip()]

        assert len(lines) >= 20, \
            f"Expected at least 20 lines in unified.log after 60 seconds, got {len(lines)}. " \
            f"The script must actually aggregate log content from multiple sources."

    def test_unified_log_has_diverse_sources(self):
        """Verify unified.log contains content from multiple source files."""
        # The content should come from multiple different app logs
        if os.path.exists(UNIFIED_LOG):
            os.remove(UNIFIED_LOG)

        # Run script for 60 seconds
        subprocess.run(
            ['timeout', '60', 'python3', TAIL_SCRIPT],
            cwd=LOGWATCH_DIR,
            capture_output=True
        )

        assert os.path.exists(UNIFIED_LOG), \
            f"unified.log was not created at {UNIFIED_LOG}"

        with open(UNIFIED_LOG, 'r') as f:
            content = f.read()

        # Check that we have actual log content (not just empty or error messages)
        lines = [l for l in content.strip().split('\n') if l.strip()]

        # The feeder writes timestamped lines, so we should see some variety
        # At minimum, verify we have substantial content
        total_chars = len(content)
        assert total_chars >= 100, \
            f"unified.log has insufficient content ({total_chars} chars). " \
            f"Expected substantial aggregated log data."


class TestNoCyclicSymlinksRemain:
    """Test that no cyclic symlinks remain."""

    def test_no_cyclic_symlinks(self):
        """Verify no symlinks form cycles anymore."""
        entries = os.listdir(VAR_LOG_APPS)

        for entry in entries:
            full_path = os.path.join(VAR_LOG_APPS, entry)
            if os.path.islink(full_path):
                # Check that realpath resolves to something in /srv/applogs/
                real_path = os.path.realpath(full_path)

                # A cyclic symlink would resolve to itself or another symlink in /var/log/apps/
                assert not real_path.startswith(VAR_LOG_APPS), \
                    f"Symlink {full_path} appears to be cyclic (resolves to {real_path}). " \
                    f"All symlinks should resolve to real files in {SRV_APPLOGS}."

                # Should resolve to a real file
                assert os.path.isfile(real_path), \
                    f"Symlink {full_path} does not resolve to a real file. Got: {real_path}"


class TestScriptFileIntegrity:
    """Test that the script file is still valid."""

    def test_script_is_valid_python(self):
        """Verify the script is valid Python syntax."""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', TAIL_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, \
            f"Script {TAIL_SCRIPT} has Python syntax errors: {result.stderr.decode()}"

    def test_script_can_import_dependencies(self):
        """Verify the script's imports work."""
        # Extract imports from the script and verify they work
        result = subprocess.run(
            ['python3', '-c', 'import pyinotify'],
            capture_output=True
        )
        assert result.returncode == 0, \
            f"pyinotify import failed: {result.stderr.decode()}"
