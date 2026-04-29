# test_final_state.py
"""
Tests to validate the final state after the student has fixed the alerter pipeline.
The alerter should now correctly read the threshold from config.yaml and generate alerts
for hours where error_rate > 0.05.
"""

import os
import json
import subprocess
import re
import pytest
from pathlib import Path


class TestInvariantsPreserved:
    """Test that invariants are preserved - files that should not change."""

    def test_ingest_log_files_unchanged(self):
        """Verify /var/log/ingest/ still has 72 log files."""
        ingest_dir = Path("/var/log/ingest")
        log_files = list(ingest_dir.glob("ingest_*.log"))
        assert len(log_files) == 72, \
            f"Expected 72 ingest log files (unchanged), found {len(log_files)}"

    def test_summary_files_unchanged(self):
        """Verify /home/user/monitoring/summaries/ still has 72 summary files."""
        summaries_dir = Path("/home/user/monitoring/summaries")
        summary_files = list(summaries_dir.glob("summary_*.json"))
        assert len(summary_files) == 72, \
            f"Expected 72 summary files (unchanged), found {len(summary_files)}"

    def test_config_threshold_unchanged(self):
        """Verify config.yaml still has threshold: 0.05."""
        result = subprocess.run(
            ["grep", "threshold", "/home/user/monitoring/config.yaml"],
            capture_output=True, text=True
        )
        assert result.returncode == 0, \
            "config.yaml should still contain 'threshold'"
        assert "0.05" in result.stdout, \
            f"config.yaml threshold should still be 0.05, got: {result.stdout.strip()}"


class TestAntiShortcutGuards:
    """Test that the solution doesn't use shortcuts/hardcoding."""

    def test_threshold_not_hardcoded_in_alerter(self):
        """Verify threshold is not hardcoded as 0.05 in alerter.py."""
        result = subprocess.run(
            ["grep", "-E", r"threshold.*=.*0\.05|THRESHOLD.*=.*0\.05",
             "/home/user/monitoring/alerter.py"],
            capture_output=True, text=True
        )
        # grep returns 0 if match found, 1 if no match
        assert result.returncode != 0, \
            "alerter.py should NOT have threshold hardcoded as 0.05 - it must read from config.yaml"

    def test_alerter_reads_threshold_from_config(self):
        """Verify alerter.py reads 'threshold' (correctly spelled) from config."""
        alerter_path = Path("/home/user/monitoring/alerter.py")
        content = alerter_path.read_text()

        # Should reference 'threshold' with correct spelling when reading from config
        # Look for patterns like config['threshold'] or config.get('threshold' or similar
        has_correct_threshold_access = (
            "['threshold']" in content or
            '["threshold"]' in content or
            ".get('threshold'" in content or
            '.get("threshold"' in content or
            "['threshold'" in content or
            '["threshold"' in content
        )
        assert has_correct_threshold_access, \
            "alerter.py must read 'threshold' (correctly spelled) from config"


class TestAlerterExecution:
    """Test that alerter.py executes correctly."""

    def test_alerter_exits_zero(self):
        """Verify alerter.py exits with code 0."""
        result = subprocess.run(
            ["python3", "/home/user/monitoring/alerter.py"],
            capture_output=True, text=True,
            cwd="/home/user/monitoring"
        )
        assert result.returncode == 0, \
            f"alerter.py should exit 0, got {result.returncode}. stderr: {result.stderr}"


class TestAlertsLogContent:
    """Test the alerts.log file has proper content."""

    def test_alerts_log_exists(self):
        """Verify alerts.log exists."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        assert alerts_path.exists(), \
            "alerts.log does not exist"

    def test_alerts_log_not_empty(self):
        """Verify alerts.log is not empty."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        size = alerts_path.stat().st_size
        assert size > 0, \
            "alerts.log should not be empty - alerts should have been generated"

    def test_alerts_log_has_at_least_two_lines(self):
        """Verify alerts.log contains at least 2 alert lines."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        content = alerts_path.read_text().strip()
        lines = [line for line in content.split('\n') if line.strip()]
        assert len(lines) >= 2, \
            f"alerts.log should have at least 2 alert lines, found {len(lines)}"

    def test_alerts_log_contains_20250610_14(self):
        """Verify alerts.log contains an alert for the 20250610_14 hour (~12% error rate)."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        content = alerts_path.read_text()
        # Check for the hour identifier in various possible formats
        has_alert = (
            "20250610_14" in content or
            "2025061014" in content or
            "2025-06-10 14" in content or
            "2025-06-10T14" in content or
            "20250610 14" in content
        )
        assert has_alert, \
            "alerts.log should contain an alert for hour 20250610_14 (had ~12% error rate)"

    def test_alerts_log_contains_20250611_09(self):
        """Verify alerts.log contains an alert for the 20250611_09 hour (~8% error rate)."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        content = alerts_path.read_text()
        # Check for the hour identifier in various possible formats
        has_alert = (
            "20250611_09" in content or
            "2025061109" in content or
            "2025-06-11 09" in content or
            "2025-06-11T09" in content or
            "20250611 09" in content
        )
        assert has_alert, \
            "alerts.log should contain an alert for hour 20250611_09 (had ~8% error rate)"

    def test_alerts_reference_real_hours(self):
        """Verify alerts reference hours that actually exist in summaries."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        summaries_dir = Path("/home/user/monitoring/summaries")

        alerts_content = alerts_path.read_text()

        # Extract all YYYYMMDD_HH patterns from alerts
        alert_hours = set(re.findall(r'(\d{8}_\d{2})', alerts_content))

        # Also try other common date formats and convert them
        alt_patterns = re.findall(r'(\d{8})[\s_T]?(\d{2})', alerts_content)
        for date_part, hour_part in alt_patterns:
            alert_hours.add(f"{date_part}_{hour_part}")

        # Get all valid hours from summaries
        summary_files = list(summaries_dir.glob("summary_*.json"))
        valid_hours = set()
        for sf in summary_files:
            match = re.search(r'summary_(\d{8}_\d{2})\.json', sf.name)
            if match:
                valid_hours.add(match.group(1))

        # At least some alert hours should match valid summary hours
        matching_hours = alert_hours & valid_hours
        assert len(matching_hours) >= 2, \
            f"Alerts should reference real hours from summaries. Found hours in alerts: {alert_hours}, valid hours: {valid_hours}"


class TestAlertsAreForHighErrorRates:
    """Test that alerts are generated for actual high error rate hours."""

    def test_alerts_correspond_to_threshold_breaches(self):
        """Verify alerts are for hours where error_rate > 0.05."""
        alerts_path = Path("/home/user/monitoring/alerts.log")
        summaries_dir = Path("/home/user/monitoring/summaries")

        alerts_content = alerts_path.read_text()

        # Find hours mentioned in alerts
        alert_hours = set(re.findall(r'(\d{8}_\d{2})', alerts_content))

        # For each alerted hour, verify it had error_rate > 0.05
        verified_breaches = 0
        for hour in alert_hours:
            summary_path = summaries_dir / f"summary_{hour}.json"
            if summary_path.exists():
                with open(summary_path, 'r') as f:
                    data = json.load(f)
                    error_rate = float(data['error_rate'])
                    if error_rate > 0.05:
                        verified_breaches += 1

        assert verified_breaches >= 2, \
            f"Expected at least 2 alerts for hours with error_rate > 0.05, verified {verified_breaches}"


class TestBugIsFixed:
    """Test that the typo bug has been fixed."""

    def test_treshold_typo_fixed_or_not_used(self):
        """Verify the 'treshold' typo is either fixed or not causing the default to 0.5."""
        alerter_path = Path("/home/user/monitoring/alerter.py")
        content = alerter_path.read_text()

        # The bug was: config.get('treshold', 0.5) which defaulted to 0.5
        # Either the typo is fixed to 'threshold', or if 'treshold' still exists,
        # it should not be the one used for the actual threshold comparison

        # If treshold typo still exists with 0.5 default, that's the unfixed bug
        if "treshold" in content and "0.5" in content:
            # Check if it's still being used as the threshold
            # The fix could be: changing 'treshold' to 'threshold'
            # We already verified alerts are generated, so the bug is functionally fixed
            pass

        # The real test is that alerts are generated (tested elsewhere)
        # This test just documents that we expect the typo to be addressed

        # Check that 'threshold' (correct spelling) is now used
        has_correct_spelling = (
            "['threshold']" in content or
            '["threshold"]' in content or
            ".get('threshold'" in content or
            '.get("threshold"' in content
        )

        # Either the typo is completely removed, or correct spelling is now used
        typo_removed = "treshold" not in content

        assert has_correct_spelling or typo_removed, \
            "The 'treshold' typo should be fixed to 'threshold' in alerter.py"


class TestEndToEndFunctionality:
    """Test the complete pipeline works end-to-end."""

    def test_running_alerter_produces_alerts(self):
        """Run alerter and verify it produces alerts for high error rate hours."""
        # Clear alerts.log first to test fresh run
        alerts_path = Path("/home/user/monitoring/alerts.log")
        original_content = alerts_path.read_text() if alerts_path.exists() else ""

        # Run the alerter
        result = subprocess.run(
            ["python3", "/home/user/monitoring/alerter.py"],
            capture_output=True, text=True,
            cwd="/home/user/monitoring"
        )

        assert result.returncode == 0, \
            f"alerter.py should run successfully, got exit code {result.returncode}"

        # Check alerts.log has content (either original or new)
        new_content = alerts_path.read_text()
        assert len(new_content.strip()) > 0, \
            "alerts.log should have content after running alerter"

    def test_alerter_uses_config_threshold(self):
        """Verify the alerter actually uses the threshold from config (not hardcoded)."""
        # This is a semantic test - if threshold was hardcoded to something other than 0.05,
        # we might see different alerts. Since we verified alerts exist for 0.05+ error rates,
        # and we verified threshold isn't hardcoded, the alerter must be reading from config.

        # Read config to confirm threshold value
        import yaml
        config_path = Path("/home/user/monitoring/config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        assert 'threshold' in config, "config.yaml must have 'threshold' key"
        assert abs(float(config['threshold']) - 0.05) < 0.001, \
            f"config.yaml threshold should be 0.05, got {config['threshold']}"

        # Verify alerts exist (meaning threshold is being used correctly)
        alerts_path = Path("/home/user/monitoring/alerts.log")
        content = alerts_path.read_text()
        lines = [l for l in content.strip().split('\n') if l.strip()]
        assert len(lines) >= 2, \
            "With threshold=0.05, at least 2 hours should trigger alerts"
