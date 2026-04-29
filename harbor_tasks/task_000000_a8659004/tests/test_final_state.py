# test_final_state.py
"""
Tests to validate the final state after the student has fixed the log aggregation script.
The script should now correctly read from access.log.1 and produce the top 10 paths report.
"""

import os
import re
import subprocess
import pytest


class TestScriptExecution:
    """Verify the script runs successfully and produces output."""

    def test_script_exists(self):
        """The script file must still exist."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        assert os.path.exists(script_path), f"Script not found at {script_path}"

    def test_script_is_executable(self):
        """The script must still be executable."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        assert os.access(script_path, os.X_OK), f"{script_path} is not executable"

    def test_script_exits_zero(self):
        """Running the script should exit with code 0."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Script exited with code {result.returncode}. stderr: {result.stderr}"


class TestOutputFile:
    """Verify the output file has correct content."""

    def test_output_file_exists(self):
        """The output file must exist."""
        output_file = "/var/log/reports/top_paths.txt"
        assert os.path.exists(output_file), f"Output file not found at {output_file}"

    def test_output_file_not_empty(self):
        """The output file must not be empty."""
        output_file = "/var/log/reports/top_paths.txt"
        size = os.path.getsize(output_file)
        assert size > 0, f"{output_file} is empty (0 bytes)"

    def test_output_has_exactly_10_lines(self):
        """The output file must contain exactly 10 lines."""
        output_file = "/var/log/reports/top_paths.txt"
        with open(output_file, 'r') as f:
            lines = [line for line in f.readlines() if line.strip()]
        assert len(lines) == 10, \
            f"Output has {len(lines)} non-empty lines, expected exactly 10"

    def test_output_lines_have_correct_format(self):
        """Each line should have format: count followed by path."""
        output_file = "/var/log/reports/top_paths.txt"
        pattern = re.compile(r'^\s*(\d+)\s+(/\S*)$')
        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        for i, line in enumerate(lines, 1):
            match = pattern.match(line)
            assert match, \
                f"Line {i} doesn't match expected format (count path): '{line}'"

    def test_output_sorted_descending(self):
        """Lines must be sorted by count in descending order."""
        output_file = "/var/log/reports/top_paths.txt"
        pattern = re.compile(r'^\s*(\d+)\s+(/\S*)$')
        with open(output_file, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip()]

        counts = []
        for line in lines:
            match = pattern.match(line)
            if match:
                counts.append(int(match.group(1)))

        assert counts == sorted(counts, reverse=True), \
            f"Counts are not in descending order: {counts}"


class TestOutputContent:
    """Verify the output contains the expected top paths from access.log.1."""

    def test_first_line_is_api_health(self):
        """First line should be /api/health with 203 hits."""
        output_file = "/var/log/reports/top_paths.txt"
        with open(output_file, 'r') as f:
            first_line = f.readline().strip()

        assert '203' in first_line, \
            f"First line should contain count 203, got: '{first_line}'"
        assert '/api/health' in first_line, \
            f"First line should contain /api/health, got: '{first_line}'"

    def test_second_line_is_api_users(self):
        """Second line should be /api/users with 156 hits."""
        output_file = "/var/log/reports/top_paths.txt"
        with open(output_file, 'r') as f:
            lines = f.readlines()

        if len(lines) >= 2:
            second_line = lines[1].strip()
            assert '156' in second_line, \
                f"Second line should contain count 156, got: '{second_line}'"
            assert '/api/users' in second_line, \
                f"Second line should contain /api/users, got: '{second_line}'"
        else:
            pytest.fail("Output file has fewer than 2 lines")

    def test_tenth_line_is_favicon(self):
        """Tenth line should be /favicon.ico with 28 hits."""
        output_file = "/var/log/reports/top_paths.txt"
        with open(output_file, 'r') as f:
            lines = [line for line in f.readlines() if line.strip()]

        if len(lines) >= 10:
            tenth_line = lines[9].strip()
            assert '28' in tenth_line, \
                f"Tenth line should contain count 28, got: '{tenth_line}'"
            assert '/favicon.ico' in tenth_line, \
                f"Tenth line should contain /favicon.ico, got: '{tenth_line}'"
        else:
            pytest.fail(f"Output file has only {len(lines)} lines, expected 10")

    def test_expected_paths_present(self):
        """All expected top 10 paths should be present in output."""
        expected_paths = [
            '/api/health',
            '/api/users',
            '/static/app.js',
            '/api/orders',
            '/',
            '/static/style.css',
            '/api/products',
            '/login',
            '/api/auth',
            '/favicon.ico'
        ]

        output_file = "/var/log/reports/top_paths.txt"
        with open(output_file, 'r') as f:
            content = f.read()

        for path in expected_paths:
            assert path in content, \
                f"Expected path '{path}' not found in output"


class TestSourceDataPreserved:
    """Verify source log files are unchanged."""

    def test_access_log_1_exists(self):
        """Yesterday's log file must still exist."""
        log_file = "/var/log/nginx/access.log.1"
        assert os.path.exists(log_file), f"Source log file missing: {log_file}"

    def test_access_log_1_has_847_lines(self):
        """Yesterday's log should still have 847 lines (unchanged)."""
        log_file = "/var/log/nginx/access.log.1"
        with open(log_file, 'r') as f:
            lines = f.readlines()
        assert len(lines) == 847, \
            f"Source log has {len(lines)} lines, expected 847 (should be unchanged)"

    def test_access_log_exists(self):
        """Today's access.log must still exist."""
        log_file = "/var/log/nginx/access.log"
        assert os.path.exists(log_file), f"Today's log file missing: {log_file}"


class TestAntiShortcut:
    """Verify the script actually processes the log file and doesn't have hardcoded output."""

    def test_script_does_not_contain_hardcoded_counts(self):
        """Script should not contain hardcoded count values."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Check that specific counts from the expected output are not in the script
        # Using grep-like check for patterns like "203.*health" or "156.*users"
        hardcoded_patterns = [
            (r'203.*health', '203 with health'),
            (r'156.*users', '156 with users'),
            (r'health.*203', 'health with 203'),
            (r'users.*156', 'users with 156'),
        ]

        for pattern, description in hardcoded_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            assert match is None, \
                f"Script appears to have hardcoded output ({description}). Script must process actual log data."

    def test_script_uses_core_pipeline_tools(self):
        """Script should still use sort, uniq, and head (core pipeline pattern)."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert 'sort' in content, "Script should use 'sort' command"
        assert 'uniq' in content, "Script should use 'uniq' command"
        assert 'head' in content, "Script should use 'head' command"

    def test_output_derives_from_log_content(self):
        """Verify output matches what we'd get from processing access.log.1."""
        # Run a reference pipeline on access.log.1 and compare key results
        log_file = "/var/log/nginx/access.log.1"

        # Extract paths and count them
        result = subprocess.run(
            f"cat {log_file} | awk '{{print $7}}' | sort | uniq -c | sort -rn | head -10",
            shell=True,
            capture_output=True,
            text=True
        )

        reference_output = result.stdout.strip()

        output_file = "/var/log/reports/top_paths.txt"
        with open(output_file, 'r') as f:
            actual_output = f.read().strip()

        # Extract counts and paths from both
        ref_pattern = re.compile(r'^\s*(\d+)\s+(/\S*)$', re.MULTILINE)
        ref_matches = ref_pattern.findall(reference_output)
        actual_matches = ref_pattern.findall(actual_output)

        # Compare the top entry at minimum
        if ref_matches and actual_matches:
            ref_top_count, ref_top_path = ref_matches[0]
            actual_top_count, actual_top_path = actual_matches[0]

            assert ref_top_path == actual_top_path, \
                f"Top path mismatch: expected {ref_top_path}, got {actual_top_path}"
            assert ref_top_count == actual_top_count, \
                f"Top count mismatch: expected {ref_top_count}, got {actual_top_count}"


class TestScriptReproducibility:
    """Verify running the script again produces the same output."""

    def test_script_produces_consistent_output(self):
        """Running the script twice should produce identical output."""
        script_path = "/home/user/scripts/aggregate_logs.sh"
        output_file = "/var/log/reports/top_paths.txt"

        # Run once
        subprocess.run([script_path], capture_output=True)
        with open(output_file, 'r') as f:
            first_output = f.read()

        # Run again
        subprocess.run([script_path], capture_output=True)
        with open(output_file, 'r') as f:
            second_output = f.read()

        assert first_output == second_output, \
            "Script produces inconsistent output on repeated runs"
