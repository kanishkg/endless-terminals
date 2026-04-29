# test_final_state.py
"""
Tests to validate the final state of the operating system after the student
has completed the OOMKilled event extraction task.
"""

import os
import pytest


class TestFinalState:
    """Test suite to validate final state after task execution."""

    def test_output_file_exists(self):
        """Verify that the output file exists."""
        output_path = "/home/user/oom-events.txt"
        assert os.path.exists(output_path), (
            f"Output file does not exist: {output_path}. "
            "The task requires creating this file with extracted OOMKilled events."
        )

    def test_output_file_is_regular_file(self):
        """Verify that the output file is a regular file."""
        output_path = "/home/user/oom-events.txt"
        assert os.path.isfile(output_path), (
            f"{output_path} exists but is not a regular file. "
            "Expected a regular file for the output."
        )

    def test_output_file_is_readable(self):
        """Verify that the output file is readable."""
        output_path = "/home/user/oom-events.txt"
        assert os.access(output_path, os.R_OK), (
            f"Output file is not readable: {output_path}."
        )

    def test_output_file_has_exactly_7_lines(self):
        """Verify that the output file contains exactly 7 lines."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        assert len(lines) == 7, (
            f"Output file contains {len(lines)} non-empty lines, but expected exactly 7 lines "
            "(one for each OOMKilled event in the source log)."
        )

    def test_output_line_format(self):
        """Verify that each line has the correct format: <timestamp> <pod-name>."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            parts = line.split()
            assert len(parts) == 2, (
                f"Line {i} has incorrect format. Expected '<timestamp> <pod-name>' "
                f"(2 space-separated fields), but got: '{line}'"
            )

            timestamp, pod_name = parts
            # Verify timestamp looks like ISO8601
            assert 'T' in timestamp and 'Z' in timestamp, (
                f"Line {i} timestamp does not appear to be ISO8601 format: '{timestamp}'"
            )

            # Verify pod_name does not contain namespace (no slash)
            assert '/' not in pod_name, (
                f"Line {i} pod name should not include namespace prefix. "
                f"Expected just pod name, but got: '{pod_name}'"
            )

    def test_output_contains_expected_timestamps(self):
        """Verify that the output contains all expected timestamps."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            content = f.read()

        expected_timestamps = [
            "2024-03-15T09:23:41Z",
            "2024-03-15T11:45:02Z",
            "2024-03-15T14:12:58Z",
            "2024-03-16T02:33:19Z",
            "2024-03-16T08:17:44Z",
            "2024-03-17T16:41:03Z",
            "2024-03-18T03:55:27Z",
        ]

        for timestamp in expected_timestamps:
            assert timestamp in content, (
                f"Expected timestamp not found in output: {timestamp}"
            )

    def test_output_contains_expected_pod_names(self):
        """Verify that the output contains all expected pod names."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            content = f.read()

        expected_pod_names = [
            "coredns-5dd5756b68-x7vzq",
            "metrics-server-6d94bc8694-2plwm",
            "kube-proxy-7h9xt",
            "etcd-control-plane-1",
            "kube-dns-autoscaler-5c78bb4d6f-9kzpl",
        ]

        for pod_name in expected_pod_names:
            assert pod_name in content, (
                f"Expected pod name not found in output: {pod_name}"
            )

    def test_output_exact_content(self):
        """Verify the exact content of each line in the output file."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        expected_lines = [
            "2024-03-15T09:23:41Z coredns-5dd5756b68-x7vzq",
            "2024-03-15T11:45:02Z metrics-server-6d94bc8694-2plwm",
            "2024-03-15T14:12:58Z kube-proxy-7h9xt",
            "2024-03-16T02:33:19Z etcd-control-plane-1",
            "2024-03-16T08:17:44Z coredns-5dd5756b68-x7vzq",
            "2024-03-17T16:41:03Z kube-dns-autoscaler-5c78bb4d6f-9kzpl",
            "2024-03-18T03:55:27Z metrics-server-6d94bc8694-2plwm",
        ]

        assert len(lines) == len(expected_lines), (
            f"Output has {len(lines)} lines but expected {len(expected_lines)} lines."
        )

        for i, (actual, expected) in enumerate(zip(lines, expected_lines), 1):
            assert actual == expected, (
                f"Line {i} mismatch.\n"
                f"Expected: '{expected}'\n"
                f"Actual:   '{actual}'"
            )

    def test_output_lines_in_correct_order(self):
        """Verify that lines are in chronological order (same as source log)."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        timestamps = []
        for line in lines:
            parts = line.split()
            if parts:
                timestamps.append(parts[0])

        # Verify timestamps are in ascending order
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], (
                f"Lines are not in chronological order. "
                f"Timestamp '{timestamps[i]}' should come before '{timestamps[i + 1]}'"
            )

    def test_source_log_unchanged(self):
        """Verify that the source log file still exists and is unchanged."""
        log_path = "/var/log/pods/kube-system.log"

        assert os.path.exists(log_path), (
            f"Source log file no longer exists: {log_path}. "
            "The source file should remain unchanged."
        )

        with open(log_path, 'r') as f:
            content = f.read()

        # Verify it still has 7 OOMKilled events
        oomkilled_count = content.count("OOMKilled")
        assert oomkilled_count == 7, (
            f"Source log file now has {oomkilled_count} OOMKilled events, "
            "but should still have exactly 7. The source file should be unchanged."
        )

    def test_output_derived_from_source(self):
        """
        Anti-shortcut guard: Verify output line count matches OOMKilled count in source.
        This ensures the output was derived from the log file, not hardcoded.
        """
        log_path = "/var/log/pods/kube-system.log"
        output_path = "/home/user/oom-events.txt"

        with open(log_path, 'r') as f:
            source_content = f.read()

        with open(output_path, 'r') as f:
            output_lines = [line.strip() for line in f.readlines() if line.strip()]

        source_oomkilled_count = source_content.count("OOMKilled")

        assert len(output_lines) == source_oomkilled_count, (
            f"Output has {len(output_lines)} lines but source log has "
            f"{source_oomkilled_count} OOMKilled events. "
            "Output must be derived from the source log file."
        )

    def test_no_namespace_prefix_in_output(self):
        """Verify that no line contains 'kube-system/' prefix."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            content = f.read()

        assert "kube-system/" not in content, (
            "Output file contains 'kube-system/' prefix. "
            "Pod names should not include the namespace prefix."
        )

    def test_no_oomkilled_text_in_output(self):
        """Verify that 'OOMKilled' event type is not in the output."""
        output_path = "/home/user/oom-events.txt"
        with open(output_path, 'r') as f:
            content = f.read()

        assert "OOMKilled" not in content, (
            "Output file contains 'OOMKilled' text. "
            "Output should only contain timestamp and pod name, not the event type."
        )
