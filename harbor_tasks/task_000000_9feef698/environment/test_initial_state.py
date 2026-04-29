# test_initial_state.py
"""
Tests to validate the initial state of the operating system before the student
performs the OOMKilled event extraction task.
"""

import os
import pytest


class TestInitialState:
    """Test suite to validate initial state before task execution."""

    def test_source_log_file_exists(self):
        """Verify that the source log file exists."""
        log_path = "/var/log/pods/kube-system.log"
        assert os.path.exists(log_path), (
            f"Source log file does not exist: {log_path}. "
            "This file must be present for the task."
        )

    def test_source_log_file_is_readable(self):
        """Verify that the source log file is readable."""
        log_path = "/var/log/pods/kube-system.log"
        assert os.access(log_path, os.R_OK), (
            f"Source log file is not readable: {log_path}. "
            "The file must be readable to extract OOMKilled events."
        )

    def test_source_log_file_is_regular_file(self):
        """Verify that the source log file is a regular file."""
        log_path = "/var/log/pods/kube-system.log"
        assert os.path.isfile(log_path), (
            f"{log_path} exists but is not a regular file. "
            "Expected a regular file for the log."
        )

    def test_source_log_has_content(self):
        """Verify that the source log file has approximately 200 lines."""
        log_path = "/var/log/pods/kube-system.log"
        with open(log_path, 'r') as f:
            lines = f.readlines()

        # Should have approximately 200 lines (allow some tolerance)
        assert len(lines) >= 50, (
            f"Source log file has too few lines ({len(lines)}). "
            "Expected approximately 200 lines of mixed pod events."
        )
        assert len(lines) <= 500, (
            f"Source log file has too many lines ({len(lines)}). "
            "Expected approximately 200 lines of mixed pod events."
        )

    def test_source_log_contains_oomkilled_events(self):
        """Verify that the source log contains exactly 7 OOMKilled events."""
        log_path = "/var/log/pods/kube-system.log"
        with open(log_path, 'r') as f:
            content = f.read()

        oomkilled_count = content.count("OOMKilled")
        assert oomkilled_count == 7, (
            f"Source log file contains {oomkilled_count} OOMKilled events, "
            "but expected exactly 7 OOMKilled events."
        )

    def test_source_log_format_is_correct(self):
        """Verify that log lines follow the expected format."""
        log_path = "/var/log/pods/kube-system.log"
        with open(log_path, 'r') as f:
            lines = f.readlines()

        # Check at least some lines to verify format
        valid_format_count = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 3:
                # Check timestamp format (ISO8601-like)
                timestamp = parts[0]
                if 'T' in timestamp and 'Z' in timestamp:
                    # Check namespace/pod-name format
                    ns_pod = parts[1]
                    if '/' in ns_pod:
                        valid_format_count += 1

        assert valid_format_count > 0, (
            "No lines in the log file match the expected format: "
            "<ISO8601-timestamp> <namespace>/<pod-name> <event-type>"
        )

    def test_source_log_contains_expected_oomkilled_entries(self):
        """Verify that the source log contains the specific expected OOMKilled entries."""
        log_path = "/var/log/pods/kube-system.log"
        with open(log_path, 'r') as f:
            content = f.read()

        expected_entries = [
            "2024-03-15T09:23:41Z kube-system/coredns-5dd5756b68-x7vzq OOMKilled",
            "2024-03-15T11:45:02Z kube-system/metrics-server-6d94bc8694-2plwm OOMKilled",
            "2024-03-15T14:12:58Z kube-system/kube-proxy-7h9xt OOMKilled",
            "2024-03-16T02:33:19Z kube-system/etcd-control-plane-1 OOMKilled",
            "2024-03-16T08:17:44Z kube-system/coredns-5dd5756b68-x7vzq OOMKilled",
            "2024-03-17T16:41:03Z kube-system/kube-dns-autoscaler-5c78bb4d6f-9kzpl OOMKilled",
            "2024-03-18T03:55:27Z kube-system/metrics-server-6d94bc8694-2plwm OOMKilled",
        ]

        for entry in expected_entries:
            assert entry in content, (
                f"Expected OOMKilled entry not found in log file: {entry}"
            )

    def test_home_user_directory_exists(self):
        """Verify that /home/user directory exists."""
        home_path = "/home/user"
        assert os.path.exists(home_path), (
            f"Home directory does not exist: {home_path}. "
            "This directory must exist for the output file."
        )

    def test_home_user_directory_is_writable(self):
        """Verify that /home/user directory is writable."""
        home_path = "/home/user"
        assert os.access(home_path, os.W_OK), (
            f"Home directory is not writable: {home_path}. "
            "The directory must be writable to create the output file."
        )

    def test_output_file_does_not_exist(self):
        """Verify that the output file does not exist initially."""
        output_path = "/home/user/oom-events.txt"
        assert not os.path.exists(output_path), (
            f"Output file already exists: {output_path}. "
            "The output file should not exist before the task is performed."
        )

    def test_source_log_contains_various_event_types(self):
        """Verify that the source log contains various event types, not just OOMKilled."""
        log_path = "/var/log/pods/kube-system.log"
        with open(log_path, 'r') as f:
            content = f.read()

        # Check for presence of other event types to ensure it's a realistic log
        other_events = ["Started", "Running", "CrashLoopBackOff", "Pulled", "Scheduled"]
        found_other_events = sum(1 for event in other_events if event in content)

        assert found_other_events >= 2, (
            "Source log file should contain various event types besides OOMKilled "
            "(e.g., Started, Running, CrashLoopBackOff, Pulled, Scheduled). "
            f"Only found {found_other_events} other event types."
        )
