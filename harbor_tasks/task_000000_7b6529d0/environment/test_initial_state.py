# test_initial_state.py
"""
Tests to validate the initial state before the student performs the task.
Verifies the buggy state of the log aggregator system with cyclic symlinks.
"""

import os
import subprocess
import pytest
import stat
import time


# Constants
HOME = "/home/user"
LOGWATCH_DIR = os.path.join(HOME, "logwatch")
TAIL_SCRIPT = os.path.join(LOGWATCH_DIR, "tail_all.py")
UNIFIED_LOG = os.path.join(LOGWATCH_DIR, "unified.log")
VAR_LOG_APPS = "/var/log/apps"
SRV_APPLOGS = "/srv/applogs"
FEEDER_SCRIPT = os.path.join(LOGWATCH_DIR, "feeder.sh")

# The cyclic symlinks as described
CYCLIC_SYMLINKS = [
    "app089.log", "app112.log", "app134.log", "app156.log",
    "app178.log", "app189.log", "app201.log", "app212.log",
    "app223.log", "app231.log", "app238.log", "app245.log"
]

TOTAL_SYMLINKS = 247


class TestDirectoryStructure:
    """Test that required directories exist."""

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

    def test_logwatch_directory_writable(self):
        """Verify /home/user/logwatch/ is writable."""
        assert os.access(LOGWATCH_DIR, os.W_OK), \
            f"Directory {LOGWATCH_DIR} is not writable"

    def test_var_log_apps_writable(self):
        """Verify /var/log/apps/ is writable (user can fix symlinks)."""
        assert os.access(VAR_LOG_APPS, os.W_OK), \
            f"Directory {VAR_LOG_APPS} is not writable"

    def test_srv_applogs_readable(self):
        """Verify /srv/applogs/ is readable."""
        assert os.access(SRV_APPLOGS, os.R_OK), \
            f"Directory {SRV_APPLOGS} is not readable"


class TestTailScript:
    """Test the tail_all.py script exists and has expected properties."""

    def test_tail_script_exists(self):
        """Verify tail_all.py script exists."""
        assert os.path.isfile(TAIL_SCRIPT), \
            f"Script {TAIL_SCRIPT} does not exist"

    def test_tail_script_readable(self):
        """Verify tail_all.py is readable."""
        assert os.access(TAIL_SCRIPT, os.R_OK), \
            f"Script {TAIL_SCRIPT} is not readable"

    def test_tail_script_uses_inotify(self):
        """Verify tail_all.py uses pyinotify for watching."""
        with open(TAIL_SCRIPT, 'r') as f:
            content = f.read()
        assert 'pyinotify' in content or 'inotify' in content, \
            f"Script {TAIL_SCRIPT} does not appear to use inotify/pyinotify"

    def test_tail_script_is_python(self):
        """Verify tail_all.py is a Python script."""
        with open(TAIL_SCRIPT, 'r') as f:
            first_line = f.readline()
        # Check shebang or just that it's valid Python-ish content
        with open(TAIL_SCRIPT, 'r') as f:
            content = f.read()
        assert 'import' in content or 'def ' in content or 'class ' in content, \
            f"Script {TAIL_SCRIPT} does not appear to be a Python script"


class TestPythonAndPyinotify:
    """Test that required Python packages are installed."""

    def test_python3_installed(self):
        """Verify python3 is installed."""
        result = subprocess.run(['which', 'python3'], capture_output=True)
        assert result.returncode == 0, "python3 is not installed"

    def test_pyinotify_installed(self):
        """Verify pyinotify module is installed."""
        result = subprocess.run(
            ['python3', '-c', 'import pyinotify'],
            capture_output=True
        )
        assert result.returncode == 0, \
            f"pyinotify module is not installed: {result.stderr.decode()}"


class TestSymlinksInVarLogApps:
    """Test the symlinks in /var/log/apps/."""

    def test_correct_number_of_symlinks(self):
        """Verify there are 247 symlinks in /var/log/apps/."""
        entries = os.listdir(VAR_LOG_APPS)
        symlinks = [e for e in entries if os.path.islink(os.path.join(VAR_LOG_APPS, e))]
        assert len(symlinks) == TOTAL_SYMLINKS, \
            f"Expected {TOTAL_SYMLINKS} symlinks in {VAR_LOG_APPS}, found {len(symlinks)}"

    def test_symlinks_named_correctly(self):
        """Verify symlinks are named app001.log through app247.log."""
        expected_names = {f"app{i:03d}.log" for i in range(1, TOTAL_SYMLINKS + 1)}
        actual_names = set(os.listdir(VAR_LOG_APPS))
        assert expected_names == actual_names, \
            f"Symlink names don't match expected pattern. Missing: {expected_names - actual_names}, Extra: {actual_names - expected_names}"

    def test_all_entries_are_symlinks(self):
        """Verify all entries in /var/log/apps/ are symlinks."""
        for entry in os.listdir(VAR_LOG_APPS):
            full_path = os.path.join(VAR_LOG_APPS, entry)
            assert os.path.islink(full_path), \
                f"{full_path} is not a symlink"


class TestActualLogFiles:
    """Test the actual log files in /srv/applogs/."""

    def test_correct_number_of_log_files(self):
        """Verify there are 247 log files in /srv/applogs/."""
        entries = os.listdir(SRV_APPLOGS)
        log_files = [e for e in entries if e.endswith('.log')]
        assert len(log_files) == TOTAL_SYMLINKS, \
            f"Expected {TOTAL_SYMLINKS} log files in {SRV_APPLOGS}, found {len(log_files)}"

    def test_log_files_are_regular_files(self):
        """Verify log files in /srv/applogs/ are regular files."""
        for i in range(1, TOTAL_SYMLINKS + 1):
            filename = f"app{i:03d}.log"
            full_path = os.path.join(SRV_APPLOGS, filename)
            assert os.path.isfile(full_path), \
                f"{full_path} does not exist or is not a regular file"
            assert not os.path.islink(full_path), \
                f"{full_path} should be a regular file, not a symlink"


class TestCyclicSymlinks:
    """Test that the cyclic symlinks exist as described."""

    def test_cyclic_symlinks_exist(self):
        """Verify the 12 cyclic symlinks exist."""
        for name in CYCLIC_SYMLINKS:
            full_path = os.path.join(VAR_LOG_APPS, name)
            assert os.path.islink(full_path), \
                f"Expected cyclic symlink {full_path} does not exist"

    def test_cyclic_symlinks_form_cycle(self):
        """Verify the cyclic symlinks point to each other in a cycle."""
        # The cycle: app089 -> app112 -> app134 -> ... -> app245 -> app089
        cycle_order = CYCLIC_SYMLINKS

        for i, name in enumerate(cycle_order):
            full_path = os.path.join(VAR_LOG_APPS, name)
            target = os.readlink(full_path)
            next_name = cycle_order[(i + 1) % len(cycle_order)]

            # The target should be the next symlink in the cycle
            # It could be absolute or relative path
            expected_targets = [
                os.path.join(VAR_LOG_APPS, next_name),
                next_name,
                f"./{next_name}"
            ]

            # Normalize target path
            if not os.path.isabs(target):
                target_full = os.path.normpath(os.path.join(VAR_LOG_APPS, target))
            else:
                target_full = target

            expected_full = os.path.join(VAR_LOG_APPS, next_name)

            assert target_full == expected_full or target == next_name, \
                f"Cyclic symlink {name} should point to {next_name}, but points to {target}"

    def test_cyclic_symlinks_do_not_resolve_to_real_files(self):
        """Verify cyclic symlinks don't resolve to real files in /srv/applogs/."""
        for name in CYCLIC_SYMLINKS:
            full_path = os.path.join(VAR_LOG_APPS, name)
            # os.path.realpath will resolve the symlink
            # For cyclic symlinks, it should not resolve to a file in /srv/applogs/
            try:
                real_path = os.path.realpath(full_path)
                # If it resolves, check it's not in /srv/applogs/
                # For cyclic symlinks, realpath returns the symlink itself or loops
                assert not real_path.startswith(SRV_APPLOGS), \
                    f"Cyclic symlink {name} unexpectedly resolves to {real_path}"
            except OSError:
                # This is expected for cyclic symlinks in some cases
                pass


class TestNonCyclicSymlinks:
    """Test that non-cyclic symlinks resolve correctly."""

    def test_non_cyclic_symlinks_resolve_to_srv_applogs(self):
        """Verify non-cyclic symlinks resolve to files in /srv/applogs/."""
        cyclic_set = set(CYCLIC_SYMLINKS)

        for i in range(1, TOTAL_SYMLINKS + 1):
            name = f"app{i:03d}.log"
            if name in cyclic_set:
                continue

            full_path = os.path.join(VAR_LOG_APPS, name)
            real_path = os.path.realpath(full_path)
            expected_target = os.path.join(SRV_APPLOGS, name)

            assert real_path == expected_target, \
                f"Non-cyclic symlink {name} should resolve to {expected_target}, got {real_path}"


class TestFeederProcess:
    """Test that the feeder process is running."""

    def test_feeder_script_exists(self):
        """Verify feeder.sh exists."""
        assert os.path.isfile(FEEDER_SCRIPT), \
            f"Feeder script {FEEDER_SCRIPT} does not exist"

    def test_feeder_process_running(self):
        """Verify feeder.sh is running (via nohup or similar)."""
        # Check for the feeder process
        result = subprocess.run(
            ['pgrep', '-f', 'feeder.sh'],
            capture_output=True
        )
        assert result.returncode == 0, \
            "feeder.sh process is not running. Expected it to be running via nohup."

    def test_logs_are_being_written(self):
        """Verify that log files are being written to (feeder is active)."""
        # Pick a non-cyclic log file and check it's growing
        test_file = os.path.join(SRV_APPLOGS, "app001.log")

        # Get initial size/mtime
        initial_stat = os.stat(test_file)
        initial_mtime = initial_stat.st_mtime

        # Wait a bit for feeder to write
        time.sleep(3)

        # Check if any file in /srv/applogs/ has been modified
        any_modified = False
        for name in os.listdir(SRV_APPLOGS):
            full_path = os.path.join(SRV_APPLOGS, name)
            if os.path.isfile(full_path):
                current_mtime = os.stat(full_path).st_mtime
                if current_mtime > initial_mtime - 3:  # Modified in last 6 seconds
                    any_modified = True
                    break

        assert any_modified, \
            "No log files appear to be modified. Is feeder.sh actually writing?"


class TestScriptBehavior:
    """Test that the script exhibits the buggy behavior (exits early)."""

    def test_script_exits_early(self):
        """Verify the script exits before 60 seconds (the bug)."""
        # Run the script with a timeout
        result = subprocess.run(
            ['timeout', '35', 'python3', TAIL_SCRIPT],
            cwd=LOGWATCH_DIR,
            capture_output=True
        )

        # If the script exits before timeout (30 seconds as described),
        # the return code will be 0 (clean exit) not 124 (timeout)
        assert result.returncode != 124, \
            f"Script did not exit early as expected (bug not present). Return code: {result.returncode}"

        # The script should exit cleanly (return code 0) due to the bug
        assert result.returncode == 0, \
            f"Script exited with unexpected code {result.returncode}. Expected 0 (clean exit due to bug). stderr: {result.stderr.decode()}"


class TestSymlinkInodes:
    """Record symlink inodes for anti-shortcut verification."""

    def test_symlinks_have_inodes(self):
        """Verify we can get inodes for symlinks (for later comparison)."""
        # This test just verifies the symlinks exist and have inodes
        # The actual inode comparison will be done in the final state tests
        cyclic_set = set(CYCLIC_SYMLINKS)
        inode_count = 0

        for name in os.listdir(VAR_LOG_APPS):
            full_path = os.path.join(VAR_LOG_APPS, name)
            if os.path.islink(full_path):
                # Get the inode of the symlink itself (not the target)
                stat_result = os.lstat(full_path)
                assert stat_result.st_ino > 0, \
                    f"Could not get inode for symlink {full_path}"
                inode_count += 1

        assert inode_count == TOTAL_SYMLINKS, \
            f"Expected {TOTAL_SYMLINKS} symlinks with inodes, found {inode_count}"
