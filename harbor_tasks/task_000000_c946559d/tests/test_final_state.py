# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the bump.sh script's "invalid version format" error and successfully
bumped the version to 2.4.0.
"""

import os
import re
import subprocess
import pytest
from datetime import datetime


RELEASE_DIR = "/home/user/release"
BUMP_SCRIPT = os.path.join(RELEASE_DIR, "bump.sh")
VERSION_FILE = os.path.join(RELEASE_DIR, "VERSION")
CHANGELOG_FILE = os.path.join(RELEASE_DIR, "CHANGELOG.md")


class TestBumpScriptSucceeded:
    """Verify that bump.sh can now run successfully."""

    def test_bump_script_still_exists_and_executable(self):
        """bump.sh must still exist and be executable."""
        assert os.path.isfile(BUMP_SCRIPT), (
            f"Script {BUMP_SCRIPT} no longer exists. "
            "The fix should be in CHANGELOG.md, not by removing the script."
        )
        assert os.access(BUMP_SCRIPT, os.X_OK), (
            f"Script {BUMP_SCRIPT} is no longer executable."
        )

    def test_bump_script_validation_logic_intact(self):
        """bump.sh should still contain its validation logic (not gutted)."""
        with open(BUMP_SCRIPT, 'r') as f:
            content = f.read()

        assert 'invalid version format' in content, (
            "bump.sh no longer contains 'invalid version format' error message. "
            "The script's validation logic should not be removed - the fix should be in CHANGELOG.md."
        )

        assert 'PREV_FROM_CHANGELOG' in content, (
            "bump.sh no longer extracts version from changelog. "
            "The script logic should remain intact."
        )

        # Check that the semver regex validation is still present
        assert re.search(r'\[0-9\]+\\\.\[0-9\]+\\\.\[0-9\]+', content) or \
               re.search(r'\[0-9\]\+\.\[0-9\]\+\.\[0-9\]\+', content.replace('\\', '')) or \
               '[0-9]+.[0-9]+.[0-9]+' in content.replace('\\', ''), (
            "bump.sh no longer contains semver validation regex. "
            "The script's validation should not be weakened."
        )


class TestVersionFileUpdated:
    """Verify VERSION file was updated to 2.4.0."""

    def test_version_file_exists(self):
        """VERSION file must still exist."""
        assert os.path.isfile(VERSION_FILE), (
            f"File {VERSION_FILE} no longer exists."
        )

    def test_version_file_contains_2_4_0(self):
        """VERSION file should now contain 2.4.0."""
        with open(VERSION_FILE, 'r') as f:
            content = f.read().strip()

        assert content == "2.4.0", (
            f"VERSION file contains '{content}' but should contain '2.4.0'. "
            "The bump.sh script should have updated VERSION to the new version."
        )


class TestChangelogUpdated:
    """Verify CHANGELOG.md was properly updated."""

    def test_changelog_file_exists(self):
        """CHANGELOG.md must still exist."""
        assert os.path.isfile(CHANGELOG_FILE), (
            f"File {CHANGELOG_FILE} no longer exists."
        )

    def test_changelog_has_new_unreleased_section(self):
        """CHANGELOG.md should have a new empty Unreleased section at the top."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '[Unreleased]' in content, (
            "CHANGELOG.md does not contain a new '[Unreleased]' section. "
            "After bumping, a new empty Unreleased section should be created."
        )

        # Unreleased should appear before 2.4.0
        unreleased_pos = content.find('[Unreleased]')
        version_240_pos = content.find('[2.4.0]')

        assert unreleased_pos < version_240_pos, (
            "The [Unreleased] section should appear before the [2.4.0] section in the changelog."
        )

    def test_changelog_has_2_4_0_section(self):
        """CHANGELOG.md should have a 2.4.0 section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '[2.4.0]' in content, (
            "CHANGELOG.md does not contain a '[2.4.0]' section. "
            "The bump should have created this section from the Unreleased content."
        )

    def test_changelog_2_4_0_has_date(self):
        """The 2.4.0 section should have a date."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        # Look for pattern like [2.4.0] - YYYY-MM-DD or similar date format
        pattern_with_date = re.search(r'\[2\.4\.0\]\s*-\s*\d{4}-\d{2}-\d{2}', content)

        assert pattern_with_date, (
            "CHANGELOG.md [2.4.0] section does not have a date in expected format. "
            "Expected format like '[2.4.0] - 2024-01-15'."
        )

    def test_changelog_2_4_0_contains_new_features(self):
        """The 2.4.0 section should contain the features that were under Unreleased."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        # Find the 2.4.0 section content
        content_lower = content.lower()

        # The new features should be in the changelog
        assert 'monitoring dashboard' in content_lower, (
            "CHANGELOG.md does not contain 'monitoring dashboard'. "
            "This feature should have been moved from Unreleased to 2.4.0."
        )

        assert 'rate limiting' in content_lower, (
            "CHANGELOG.md does not contain 'rate limiting'. "
            "This feature should have been moved from Unreleased to 2.4.0."
        )

    def test_changelog_preserves_2_3_0_section(self):
        """CHANGELOG.md should still have the 2.3.0 section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        # Should have 2.3.0 section (properly formatted now, without trailing space)
        assert '2.3.0' in content, (
            "CHANGELOG.md no longer contains '2.3.0' version. "
            "Historical versions should be preserved."
        )

        assert 'memory leak' in content.lower() or 'worker pool' in content.lower(), (
            "CHANGELOG.md no longer contains the 2.3.0 fix notes. "
            "Historical changelog content should be preserved."
        )

    def test_changelog_preserves_2_2_0_section(self):
        """CHANGELOG.md should still have the 2.2.0 section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '2.2.0' in content, (
            "CHANGELOG.md no longer contains '2.2.0' version. "
            "Historical versions should be preserved."
        )

        assert 'metrics endpoint' in content.lower(), (
            "CHANGELOG.md no longer contains the 2.2.0 feature notes. "
            "Historical changelog content should be preserved."
        )

    def test_changelog_no_longer_has_trailing_space_bug(self):
        """The [2.3.0 ] trailing space bug should be fixed."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        # The problematic pattern should no longer exist
        assert '[2.3.0 ]' not in content, (
            "CHANGELOG.md still contains '[2.3.0 ]' with trailing space. "
            "This formatting bug should have been fixed."
        )


class TestBumpScriptStillFunctional:
    """Verify bump.sh remains functional for future releases."""

    def test_bump_script_can_run_2_5_0(self):
        """
        Running bump.sh 2.5.0 should work (script remains functional).
        This verifies the fix wasn't a one-time hack.
        """
        result = subprocess.run(
            ["./bump.sh", "2.5.0"],
            cwd=RELEASE_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"bump.sh 2.5.0 failed with exit code {result.returncode}. "
            f"Stderr: {result.stderr}. "
            "The script should remain functional for future version bumps."
        )

        assert 'Bumped to 2.5.0' in result.stdout or 'bumped' in result.stdout.lower(), (
            f"bump.sh did not output expected success message. "
            f"Stdout: {result.stdout}"
        )

    def test_version_file_after_2_5_0_bump(self):
        """After running 2.5.0 bump, VERSION should be 2.5.0."""
        # First run the bump (in case previous test didn't run)
        subprocess.run(
            ["./bump.sh", "2.5.0"],
            cwd=RELEASE_DIR,
            capture_output=True,
            text=True
        )

        with open(VERSION_FILE, 'r') as f:
            content = f.read().strip()

        assert content == "2.5.0", (
            f"VERSION file contains '{content}' but should contain '2.5.0' "
            "after running bump.sh 2.5.0."
        )

    def test_changelog_has_2_5_0_after_bump(self):
        """After running 2.5.0 bump, CHANGELOG should have 2.5.0 section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '[2.5.0]' in content, (
            "CHANGELOG.md does not contain '[2.5.0]' section after running bump.sh 2.5.0."
        )


class TestBumpScriptOutputCorrect:
    """
    Test that re-running bump.sh on a clean state would work.
    Since we've already bumped to 2.5.0, we test the script's basic validation.
    """

    def test_bump_script_rejects_invalid_version(self):
        """bump.sh should reject invalid version formats."""
        result = subprocess.run(
            ["./bump.sh", "invalid"],
            cwd=RELEASE_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0, (
            "bump.sh should reject 'invalid' as a version argument."
        )

    def test_bump_script_rejects_version_without_patch(self):
        """bump.sh should reject versions without all three components."""
        result = subprocess.run(
            ["./bump.sh", "2.4"],
            cwd=RELEASE_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0, (
            "bump.sh should reject '2.4' (missing patch version) as a version argument."
        )
