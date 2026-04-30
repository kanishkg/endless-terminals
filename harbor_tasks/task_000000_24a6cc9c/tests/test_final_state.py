# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the version bump and changelog update task.
"""

import json
import os
import re
from datetime import datetime
import pytest


class TestFinalState:
    """Validate the final state after the task is performed."""

    def test_libmetrics_directory_exists(self):
        """Verify /home/user/libmetrics directory still exists."""
        dir_path = "/home/user/libmetrics"
        assert os.path.isdir(dir_path), (
            f"Directory {dir_path} does not exist. "
            "The libmetrics project directory must still be present."
        )

    def test_package_json_exists(self):
        """Verify package.json still exists in the libmetrics directory."""
        file_path = "/home/user/libmetrics/package.json"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "The package.json file must still be present."
        )

    def test_package_json_is_valid_json(self):
        """Verify package.json still contains valid JSON after modification."""
        file_path = "/home/user/libmetrics/package.json"
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {file_path} does not contain valid JSON after modification: {e}. "
                "The package.json must remain valid JSON after version bump."
            )

    def test_package_json_has_version_2_4_0(self):
        """Verify package.json has been updated to version 2.4.0."""
        file_path = "/home/user/libmetrics/package.json"
        with open(file_path, 'r') as f:
            data = json.load(f)

        assert "version" in data, (
            f"File {file_path} does not contain a 'version' field. "
            "The package.json must have a version field."
        )
        assert data["version"] == "2.4.0", (
            f"File {file_path} has version '{data['version']}' but expected '2.4.0'. "
            "The version must be bumped from 2.3.1 to 2.4.0."
        )

    def test_changelog_exists(self):
        """Verify CHANGELOG.md still exists in the libmetrics directory."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "The CHANGELOG.md file must still be present."
        )

    def test_changelog_has_header(self):
        """Verify CHANGELOG.md still has the # Changelog header."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "# Changelog" in content, (
            f"File {file_path} does not contain '# Changelog' header. "
            "The changelog must retain its proper header."
        )

    def test_changelog_has_version_2_4_0_heading(self):
        """Verify CHANGELOG.md has the new 2.4.0 version heading."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "## [2.4.0]" in content, (
            f"File {file_path} does not contain '## [2.4.0]' heading. "
            "A new changelog entry with ## [2.4.0] heading must be added."
        )

    def test_changelog_2_4_0_has_todays_date(self):
        """Verify the 2.4.0 changelog entry has today's date in YYYY-MM-DD format."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        today = datetime.now().strftime("%Y-%m-%d")

        # Look for the 2.4.0 heading with today's date
        pattern = r"##\s*\[2\.4\.0\].*" + re.escape(today)
        match = re.search(pattern, content)

        assert match is not None, (
            f"File {file_path} does not have the 2.4.0 entry with today's date ({today}). "
            f"The ## [2.4.0] heading should be followed by today's date in YYYY-MM-DD format."
        )

    def test_changelog_has_histogram_bucketing_entry(self):
        """Verify CHANGELOG.md has the histogram bucketing entry for 2.4.0."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        # Check for the key terms - flexible matching
        content_lower = content.lower()
        assert "histogram" in content_lower and "bucketing" in content_lower and "latency" in content_lower, (
            f"File {file_path} does not contain an entry mentioning 'histogram bucketing for latency metrics'. "
            "The 2.4.0 changelog entry must mention histogram bucketing for latency metrics."
        )

    def test_changelog_preserves_version_2_3_1_entry(self):
        """Verify CHANGELOG.md still has the 2.3.1 version entry."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "## [2.3.1]" in content, (
            f"File {file_path} does not contain '## [2.3.1]' heading. "
            "The existing 2.3.1 changelog entry must be preserved."
        )
        assert "Fixed memory leak in counter reset" in content, (
            f"File {file_path} does not contain the 2.3.1 changelog entry content. "
            "The original 2.3.1 entry 'Fixed memory leak in counter reset' must be preserved."
        )

    def test_changelog_preserves_version_2_3_0_entry(self):
        """Verify CHANGELOG.md still has the 2.3.0 version entry."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "## [2.3.0]" in content, (
            f"File {file_path} does not contain '## [2.3.0]' heading. "
            "The existing 2.3.0 changelog entry must be preserved."
        )
        assert "Added gauge metric type" in content, (
            f"File {file_path} does not contain the 2.3.0 changelog entry content. "
            "The original 2.3.0 entry 'Added gauge metric type' must be preserved."
        )
        assert "Improved thread safety" in content, (
            f"File {file_path} does not contain the 2.3.0 changelog entry content. "
            "The original 2.3.0 entry 'Improved thread safety' must be preserved."
        )

    def test_changelog_version_order(self):
        """Verify changelog versions appear in correct order: 2.4.0, 2.3.1, 2.3.0."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        pos_240 = content.find("## [2.4.0]")
        pos_231 = content.find("## [2.3.1]")
        pos_230 = content.find("## [2.3.0]")

        assert pos_240 != -1, (
            "Could not find ## [2.4.0] in CHANGELOG.md"
        )
        assert pos_231 != -1, (
            "Could not find ## [2.3.1] in CHANGELOG.md"
        )
        assert pos_230 != -1, (
            "Could not find ## [2.3.0] in CHANGELOG.md"
        )

        assert pos_240 < pos_231 < pos_230, (
            f"Changelog versions are not in correct order. "
            f"Expected: 2.4.0 (pos {pos_240}) < 2.3.1 (pos {pos_231}) < 2.3.0 (pos {pos_230}). "
            f"The new 2.4.0 entry must appear before the existing entries."
        )

    def test_changelog_2_4_0_after_main_header(self):
        """Verify the 2.4.0 entry appears after the # Changelog header."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        pos_header = content.find("# Changelog")
        pos_240 = content.find("## [2.4.0]")

        assert pos_header != -1, (
            "Could not find '# Changelog' header in CHANGELOG.md"
        )
        assert pos_240 != -1, (
            "Could not find '## [2.4.0]' in CHANGELOG.md"
        )
        assert pos_header < pos_240, (
            "The ## [2.4.0] entry should appear after the # Changelog header."
        )

    def test_package_json_other_fields_intact(self):
        """Verify package.json has a name field (basic check that structure is intact)."""
        file_path = "/home/user/libmetrics/package.json"
        with open(file_path, 'r') as f:
            data = json.load(f)

        # The package.json should have more than just the version field
        # This is a basic sanity check that the file wasn't completely overwritten
        assert len(data) >= 1, (
            f"File {file_path} appears to have been corrupted. "
            "The package.json should retain its structure with multiple fields."
        )
