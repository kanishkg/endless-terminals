# test_final_state.py
"""
Tests to validate the final state after the student has fixed the top_ips.sh script.
The script should correctly parse both old-format and X-Forwarded-For format log lines
to extract real client IPs and produce accurate counts.
"""

import os
import subprocess
import re
import pytest


class TestScriptExists:
    """Tests for the monitoring script existence and properties."""

    def test_script_file_exists(self):
        """Verify /home/user/scripts/top_ips.sh still exists."""
        script_path = "/home/user/scripts/top_ips.sh"
        assert os.path.isfile(script_path), \
            f"Script file {script_path} does not exist"

    def test_script_is_executable(self):
        """Verify the script is still executable."""
        script_path = "/home/user/scripts/top_ips.sh"
        assert os.access(script_path, os.X_OK), \
            f"Script {script_path} is not executable"

    def test_script_is_bash_script(self):
        """Verify the script is still a bash script."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            first_line = f.readline().strip()
        assert first_line.startswith("#!") and "bash" in first_line, \
            f"Script should be a bash script (shebang with bash), got: {first_line}"


class TestScriptUsesDateLogic:
    """Tests to ensure the script still uses date-based log selection."""

    def test_script_references_yesterday(self):
        """Verify the script still calculates yesterday's date."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Script should still reference yesterday somehow
        assert "yesterday" in content.lower() or "date" in content.lower(), \
            "Script should still use date logic to determine which log file to read"

    def test_script_references_log_directory(self):
        """Verify the script still targets /var/log/httpd/."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        assert "/var/log/httpd" in content, \
            "Script should still reference /var/log/httpd/ log directory"


class TestLogFilesUnchanged:
    """Tests to verify log files were not modified."""

    def test_log_files_still_exist(self):
        """Verify all expected log files still exist."""
        log_dir = "/var/log/httpd"
        expected_dates = ["20250120", "20250121", "20250122", "20250123", "20250124", "20250125"]

        for date in expected_dates:
            log_file = os.path.join(log_dir, f"access_{date}.log")
            assert os.path.isfile(log_file), \
                f"Log file {log_file} should still exist (invariant)"

    def test_log_file_20250125_line_count_unchanged(self):
        """Verify access_20250125.log still has ~8847 lines."""
        log_file = "/var/log/httpd/access_20250125.log"
        result = subprocess.run(['wc', '-l', log_file], capture_output=True, text=True)
        line_count = int(result.stdout.split()[0])
        assert 8800 <= line_count <= 8900, \
            f"Log file {log_file} should still have ~8847 lines (unchanged), got {line_count}"

    def test_log_file_still_contains_x_forwarded_for(self):
        """Verify the log file still contains X-Forwarded-For lines (wasn't modified)."""
        log_file = "/var/log/httpd/access_20250125.log"
        result = subprocess.run(
            ['grep', '-c', 'X-Forwarded-For:', log_file],
            capture_output=True, text=True
        )
        xff_count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert xff_count > 5000, \
            f"Log file should still contain X-Forwarded-For lines (invariant), found only {xff_count}"


class TestScriptOutput:
    """Tests for the corrected script output."""

    def _run_script_against_log(self, log_file):
        """Helper to run the script logic against a specific log file."""
        # We need to simulate running the script but targeting a specific log
        # Read the script and modify it to use the specific log file
        script_path = "/home/user/scripts/top_ips.sh"

        with open(script_path, 'r') as f:
            script_content = f.read()

        # Create a modified version that uses the specific log file
        # Replace the YESTERDAY calculation with a hardcoded date
        modified_script = script_content

        # Try to run the script with a modified date command
        # We'll use a wrapper that sets the date to make "yesterday" = 20250125
        result = subprocess.run(
            ['bash', '-c', f'''
                # Override date to return 20250126 so yesterday = 20250125
                date() {{
                    if [[ "$*" == *"yesterday"* ]]; then
                        echo "20250125"
                    else
                        command date "$@"
                    fi
                }}
                export -f date
                bash {script_path}
            '''],
            capture_output=True, text=True,
            env={**os.environ, 'PATH': os.environ.get('PATH', '/usr/bin:/bin')}
        )
        return result

    def test_script_outputs_exactly_10_lines(self):
        """Verify the script outputs exactly 10 lines."""
        result = self._run_script_against_log("/var/log/httpd/access_20250125.log")

        # Filter out empty lines
        output_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]

        assert len(output_lines) == 10, \
            f"Script should output exactly 10 lines, got {len(output_lines)}:\n{result.stdout}"

    def test_output_format_is_count_ip(self):
        """Verify output format is 'count IP' (whitespace-separated)."""
        result = self._run_script_against_log("/var/log/httpd/access_20250125.log")
        output_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]

        ip_pattern = re.compile(r'^\s*(\d+)\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*$')

        for i, line in enumerate(output_lines):
            match = ip_pattern.match(line)
            assert match is not None, \
                f"Line {i+1} should be 'count IP' format, got: '{line}'"

    def test_no_x_forwarded_for_in_output(self):
        """Verify no line contains 'X-Forwarded-For' or 'Forwarded'."""
        result = self._run_script_against_log("/var/log/httpd/access_20250125.log")
        output = result.stdout.lower()

        assert "x-forwarded-for" not in output, \
            f"Output should not contain 'X-Forwarded-For':\n{result.stdout}"
        assert "forwarded" not in output, \
            f"Output should not contain 'Forwarded':\n{result.stdout}"

    def test_total_count_is_substantial(self):
        """Verify the sum of counts is >= 5000 (proving bulk traffic is counted)."""
        result = self._run_script_against_log("/var/log/httpd/access_20250125.log")
        output_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]

        total_count = 0
        for line in output_lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    total_count += int(parts[0])
                except ValueError:
                    pass

        assert total_count >= 5000, \
            f"Sum of top 10 counts should be >= 5000 (proving bulk traffic counted), got {total_count}"

    def test_top_ip_is_correct(self):
        """Verify the top IP is 192.168.44.12 with count ~847."""
        result = self._run_script_against_log("/var/log/httpd/access_20250125.log")
        output_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]

        assert len(output_lines) > 0, "Script should produce output"

        first_line = output_lines[0].strip()
        parts = first_line.split()

        assert len(parts) >= 2, f"First line should have count and IP, got: '{first_line}'"

        count = int(parts[0])
        ip = parts[1]

        assert ip == "192.168.44.12", \
            f"Top IP should be 192.168.44.12, got {ip}"

        # Allow ±5 tolerance as mentioned in truth
        assert 840 <= count <= 855, \
            f"Top IP count should be 847 (±5), got {count}"

    def test_output_is_sorted_descending(self):
        """Verify output is sorted by count in descending order."""
        result = self._run_script_against_log("/var/log/httpd/access_20250125.log")
        output_lines = [line for line in result.stdout.strip().split('\n') if line.strip()]

        counts = []
        for line in output_lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    counts.append(int(parts[0]))
                except ValueError:
                    pass

        assert len(counts) == 10, f"Should have 10 counts, got {len(counts)}"

        for i in range(len(counts) - 1):
            assert counts[i] >= counts[i+1], \
                f"Output should be sorted descending, but count at position {i} ({counts[i]}) < count at position {i+1} ({counts[i+1]})"


class TestScriptNotHardcoded:
    """Tests to ensure the script isn't just hardcoding expected output."""

    def test_script_actually_reads_log_file(self):
        """Verify the script references log file reading operations."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Script should have some form of file reading
        reads_file = any(keyword in content for keyword in ['cat', 'awk', '<', 'while read', 'grep'])
        assert reads_file, \
            "Script should contain file reading operations (cat, awk, etc.)"

    def test_script_has_processing_logic(self):
        """Verify the script has IP extraction and counting logic."""
        script_path = "/home/user/scripts/top_ips.sh"
        with open(script_path, 'r') as f:
            content = f.read()

        # Should have some form of counting/sorting
        has_counting = any(keyword in content for keyword in ['uniq', 'sort', 'awk', 'count', 'wc'])
        assert has_counting, \
            "Script should contain counting/aggregation logic"

    def test_expected_ips_appear_in_output(self):
        """Verify multiple expected IPs appear in output (not just top one)."""
        result = subprocess.run(
            ['bash', '-c', f'''
                date() {{
                    if [[ "$*" == *"yesterday"* ]]; then
                        echo "20250125"
                    else
                        command date "$@"
                    fi
                }}
                export -f date
                bash /home/user/scripts/top_ips.sh
            '''],
            capture_output=True, text=True
        )
        output = result.stdout

        # Check for several expected IPs from the truth
        expected_ips = ["192.168.44.12", "10.0.0.55", "172.16.8.99"]
        found_count = sum(1 for ip in expected_ips if ip in output)

        assert found_count >= 2, \
            f"Expected to find at least 2 of the known top IPs in output, found {found_count}"


class TestScriptExecution:
    """Tests for script execution behavior."""

    def test_script_runs_without_error(self):
        """Verify the script runs without errors."""
        result = subprocess.run(
            ['bash', '-c', f'''
                date() {{
                    if [[ "$*" == *"yesterday"* ]]; then
                        echo "20250125"
                    else
                        command date "$@"
                    fi
                }}
                export -f date
                bash /home/user/scripts/top_ips.sh
            '''],
            capture_output=True, text=True
        )

        # Script should complete successfully
        assert result.returncode == 0, \
            f"Script should exit with code 0, got {result.returncode}. Stderr: {result.stderr}"

    def test_script_produces_output(self):
        """Verify the script produces non-empty output."""
        result = subprocess.run(
            ['bash', '-c', f'''
                date() {{
                    if [[ "$*" == *"yesterday"* ]]; then
                        echo "20250125"
                    else
                        command date "$@"
                    fi
                }}
                export -f date
                bash /home/user/scripts/top_ips.sh
            '''],
            capture_output=True, text=True
        )

        assert result.stdout.strip(), \
            f"Script should produce output. Stderr: {result.stderr}"
