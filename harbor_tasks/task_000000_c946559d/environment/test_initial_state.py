# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the bump.sh script's "invalid version format" error.
"""

import os
import stat
import subprocess
import pytest


RELEASE_DIR = "/home/user/release"
BUMP_SCRIPT = os.path.join(RELEASE_DIR, "bump.sh")
VERSION_FILE = os.path.join(RELEASE_DIR, "VERSION")
CHANGELOG_FILE = os.path.join(RELEASE_DIR, "CHANGELOG.md")


class TestReleaseDirectoryExists:
    """Verify the release directory structure exists."""

    def test_release_directory_exists(self):
        """The /home/user/release directory must exist."""
        assert os.path.isdir(RELEASE_DIR), (
            f"Release directory {RELEASE_DIR} does not exist. "
            "This directory should contain bump.sh, VERSION, and CHANGELOG.md"
        )

    def test_release_directory_is_writable(self):
        """The release directory must be writable."""
        assert os.access(RELEASE_DIR, os.W_OK), (
            f"Release directory {RELEASE_DIR} is not writable. "
            "The user needs write access to modify files."
        )


class TestBumpScriptExists:
    """Verify bump.sh exists and is executable."""

    def test_bump_script_exists(self):
        """bump.sh must exist in the release directory."""
        assert os.path.isfile(BUMP_SCRIPT), (
            f"Script {BUMP_SCRIPT} does not exist. "
            "The bump.sh script is required for the release process."
        )

    def test_bump_script_is_executable(self):
        """bump.sh must be executable."""
        assert os.access(BUMP_SCRIPT, os.X_OK), (
            f"Script {BUMP_SCRIPT} is not executable. "
            "The script needs execute permissions."
        )

    def test_bump_script_is_bash_script(self):
        """bump.sh should be a bash script."""
        with open(BUMP_SCRIPT, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('#!') and 'bash' in first_line, (
            f"Script {BUMP_SCRIPT} does not appear to be a bash script. "
            f"First line: {first_line.strip()}"
        )

    def test_bump_script_contains_validation_logic(self):
        """bump.sh should contain the version validation logic."""
        with open(BUMP_SCRIPT, 'r') as f:
            content = f.read()

        assert 'invalid version format' in content, (
            "bump.sh does not contain the expected 'invalid version format' error message. "
            "The script's validation logic appears to be missing."
        )

        assert 'PREV_FROM_CHANGELOG' in content or 'grep' in content, (
            "bump.sh does not appear to extract version from CHANGELOG.md. "
            "The script should parse the changelog to validate versions."
        )


class TestVersionFileExists:
    """Verify VERSION file exists with correct content."""

    def test_version_file_exists(self):
        """VERSION file must exist in the release directory."""
        assert os.path.isfile(VERSION_FILE), (
            f"File {VERSION_FILE} does not exist. "
            "The VERSION file tracks the current release version."
        )

    def test_version_file_contains_2_3_0(self):
        """VERSION file should contain 2.3.0 (the current version)."""
        with open(VERSION_FILE, 'r') as f:
            content = f.read().strip()

        assert content == "2.3.0", (
            f"VERSION file contains '{content}' but should contain '2.3.0'. "
            "The current version should be 2.3.0 before bumping to 2.4.0."
        )


class TestChangelogFileExists:
    """Verify CHANGELOG.md exists with expected structure."""

    def test_changelog_file_exists(self):
        """CHANGELOG.md must exist in the release directory."""
        assert os.path.isfile(CHANGELOG_FILE), (
            f"File {CHANGELOG_FILE} does not exist. "
            "The CHANGELOG.md file is required for the release process."
        )

    def test_changelog_has_unreleased_section(self):
        """CHANGELOG.md should have an Unreleased section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '[Unreleased]' in content, (
            "CHANGELOG.md does not contain an '[Unreleased]' section. "
            "This section is required for the bump process."
        )

    def test_changelog_has_2_3_0_section(self):
        """CHANGELOG.md should have a 2.3.0 section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '2.3.0' in content, (
            "CHANGELOG.md does not contain a '2.3.0' version entry. "
            "The previous release version should be documented."
        )

    def test_changelog_has_new_features_in_unreleased(self):
        """CHANGELOG.md should have new features listed under Unreleased."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert 'monitoring dashboard' in content.lower() or 'rate limiting' in content.lower(), (
            "CHANGELOG.md does not contain the expected new features "
            "(monitoring dashboard, API rate limiting) in the Unreleased section."
        )

    def test_changelog_has_2_2_0_section(self):
        """CHANGELOG.md should have a 2.2.0 section."""
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        assert '2.2.0' in content, (
            "CHANGELOG.md does not contain a '2.2.0' version entry. "
            "Historical versions should be preserved."
        )


class TestBumpScriptFailsCurrently:
    """Verify that bump.sh currently fails with the expected error."""

    def test_bump_script_fails_with_invalid_version_format(self):
        """Running bump.sh 2.4.0 should currently fail with 'invalid version format'."""
        result = subprocess.run(
            ["./bump.sh", "2.4.0"],
            cwd=RELEASE_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0, (
            "bump.sh 2.4.0 succeeded but should have failed. "
            "The script should currently be broken due to a changelog formatting issue."
        )

        assert 'invalid version format' in result.stderr.lower(), (
            f"bump.sh failed but not with 'invalid version format' error. "
            f"Actual stderr: {result.stderr}. "
            "The script should fail with the specific version format validation error."
        )


class TestNoGitRepository:
    """Verify there is no git repository (as per the truth value)."""

    def test_no_git_directory(self):
        """There should be no .git directory in the release folder."""
        git_dir = os.path.join(RELEASE_DIR, ".git")
        assert not os.path.exists(git_dir), (
            f"Found .git directory at {git_dir} but there should be none. "
            "The task description mentions git tagging but the script just updates files."
        )


class TestChangelogHasFormattingIssue:
    """Verify the changelog has the specific formatting issue that causes the bug."""

    def test_changelog_2_3_0_line_has_trailing_space_in_brackets(self):
        """
        The 2.3.0 entry should have a trailing space inside brackets: [2.3.0 ]
        This is the bug that causes the 'invalid version format' error.
        """
        with open(CHANGELOG_FILE, 'r') as f:
            content = f.read()

        # Look for the problematic pattern: [2.3.0 ] with space before ]
        # This breaks the regex that expects [x.y.z] immediately followed by ]
        has_trailing_space = '[2.3.0 ]' in content

        assert has_trailing_space, (
            "CHANGELOG.md does not contain '[2.3.0 ]' (with trailing space inside brackets). "
            "This formatting issue is the root cause of the 'invalid version format' error. "
            "The initial state should have this bug present for the student to fix."
        )
