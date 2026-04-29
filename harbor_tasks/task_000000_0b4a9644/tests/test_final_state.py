# test_final_state.py
"""
Tests to validate the final state of the release tooling at /home/user/releaser
after the student has fixed the bugs.

These tests verify:
1. release.py runs successfully
2. SECURITY commits result in patch bumps (2.3.1 -> 2.3.2)
3. SECURITY entries appear under "Security" section in CHANGELOG.md
4. The fix is general (works for other commit types too)
5. Config is actually being used (not hardcoded)
"""

import os
import json
import subprocess
import sys
import shutil
import tempfile

import pytest

RELEASER_DIR = "/home/user/releaser"


def run_release_py(cwd=RELEASER_DIR):
    """Helper to run release.py and return the result."""
    result = subprocess.run(
        [sys.executable, "release.py"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result


def read_version():
    """Read the current VERSION file content."""
    filepath = os.path.join(RELEASER_DIR, "VERSION")
    with open(filepath, "r") as f:
        return f.read().strip()


def read_changelog():
    """Read the current CHANGELOG.md content."""
    filepath = os.path.join(RELEASER_DIR, "CHANGELOG.md")
    with open(filepath, "r") as f:
        return f.read()


def write_version(version):
    """Write a version to the VERSION file."""
    filepath = os.path.join(RELEASER_DIR, "VERSION")
    with open(filepath, "w") as f:
        f.write(version)


def write_commits(commits):
    """Write commits to commits.json."""
    filepath = os.path.join(RELEASER_DIR, "commits.json")
    with open(filepath, "w") as f:
        json.dump(commits, f)


def backup_files():
    """Backup VERSION, CHANGELOG.md, and commits.json."""
    backups = {}
    for filename in ["VERSION", "CHANGELOG.md", "commits.json"]:
        filepath = os.path.join(RELEASER_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                backups[filename] = f.read()
    return backups


def restore_files(backups):
    """Restore backed up files."""
    for filename, content in backups.items():
        filepath = os.path.join(RELEASER_DIR, filename)
        with open(filepath, "w") as f:
            f.write(content)


class TestBasicFunctionality:
    """Test that release.py runs and produces correct output for SECURITY commit."""

    def test_release_py_exits_zero(self):
        """release.py must exit with code 0."""
        result = run_release_py()
        assert result.returncode == 0, (
            f"release.py exited with code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_version_is_2_3_2(self):
        """After running release.py with SECURITY commit, VERSION must be 2.3.2."""
        # First ensure we're starting from expected state
        backups = backup_files()
        try:
            write_version("2.3.1")
            write_commits([{
                "hash": "abc123",
                "message": "SECURITY: Fix auth bypass vulnerability",
                "tag": "SECURITY"
            }])

            result = run_release_py()
            assert result.returncode == 0, (
                f"release.py failed: {result.stderr}"
            )

            version = read_version()
            assert version == "2.3.2", (
                f"VERSION is '{version}' but should be '2.3.2'. "
                "SECURITY commits should trigger a patch bump (2.3.1 -> 2.3.2), "
                "not a minor bump (2.4.0)."
            )
        finally:
            restore_files(backups)

    def test_changelog_has_security_section(self):
        """CHANGELOG.md must have a 'Security' section header."""
        backups = backup_files()
        try:
            write_version("2.3.1")
            write_commits([{
                "hash": "abc123",
                "message": "SECURITY: Fix auth bypass vulnerability",
                "tag": "SECURITY"
            }])

            run_release_py()
            changelog = read_changelog()

            # Check for Security section - could be ## Security or # Security or just Security:
            has_security_section = (
                "## Security" in changelog or
                "# Security" in changelog or
                "\nSecurity\n" in changelog or
                "Security:" in changelog
            )
            assert has_security_section, (
                "CHANGELOG.md does not have a 'Security' section. "
                "Security fixes should appear under a 'Security' header, not 'Features'."
            )
        finally:
            restore_files(backups)

    def test_security_entry_under_security_section(self):
        """The auth bypass entry must be under Security section, not Features."""
        backups = backup_files()
        try:
            write_version("2.3.1")
            write_commits([{
                "hash": "abc123",
                "message": "SECURITY: Fix auth bypass vulnerability",
                "tag": "SECURITY"
            }])

            run_release_py()
            changelog = read_changelog()

            # Find the security entry
            assert "auth bypass" in changelog.lower() or "Fix auth bypass" in changelog, (
                "CHANGELOG.md does not contain the auth bypass entry"
            )

            # Check that it's NOT under Features
            # Find positions of sections and the entry
            changelog_lower = changelog.lower()

            # Find Security section position
            security_pos = -1
            for marker in ["## security", "# security", "\nsecurity\n", "security:"]:
                pos = changelog_lower.find(marker)
                if pos != -1:
                    security_pos = pos
                    break

            # Find Features section position
            features_pos = -1
            for marker in ["## features", "# features", "\nfeatures\n", "features:"]:
                pos = changelog_lower.find(marker)
                if pos != -1:
                    features_pos = pos
                    break

            # Find the auth bypass entry position
            entry_pos = changelog_lower.find("auth bypass")
            if entry_pos == -1:
                entry_pos = changelog.find("Fix auth bypass")

            # If both sections exist, verify entry is closer to Security than Features
            if security_pos != -1 and features_pos != -1 and entry_pos != -1:
                # Entry should come after Security section
                assert entry_pos > security_pos, (
                    "The auth bypass entry should appear AFTER the Security section header"
                )

                # If Features comes before Security, entry should not be between them
                if features_pos < security_pos:
                    assert not (features_pos < entry_pos < security_pos), (
                        "The auth bypass entry appears under Features section instead of Security"
                    )
        finally:
            restore_files(backups)


class TestGeneralFix:
    """Test that the fix is general, not just hardcoded for SECURITY."""

    def test_bugfix_commit_patch_bump(self):
        """BUGFIX commits should also trigger patch bumps."""
        backups = backup_files()
        try:
            write_version("2.3.2")
            write_commits([{
                "hash": "def456",
                "message": "BUGFIX: Fix null pointer exception",
                "tag": "BUGFIX"
            }])

            result = run_release_py()
            assert result.returncode == 0, (
                f"release.py failed with BUGFIX commit: {result.stderr}"
            )

            version = read_version()
            assert version == "2.3.3", (
                f"VERSION is '{version}' but should be '2.3.3'. "
                "BUGFIX commits should trigger a patch bump."
            )
        finally:
            restore_files(backups)

    def test_bugfix_under_bug_fixes_section(self):
        """BUGFIX entries should appear under 'Bug Fixes' section."""
        backups = backup_files()
        try:
            write_version("2.3.2")
            write_commits([{
                "hash": "def456",
                "message": "BUGFIX: Fix null pointer exception",
                "tag": "BUGFIX"
            }])

            run_release_py()
            changelog = read_changelog()

            # Check for Bug Fixes section
            has_bug_fixes_section = (
                "## Bug Fixes" in changelog or
                "# Bug Fixes" in changelog or
                "Bug Fixes:" in changelog or
                "\nBug Fixes\n" in changelog
            )
            assert has_bug_fixes_section, (
                "CHANGELOG.md should have a 'Bug Fixes' section for BUGFIX commits"
            )
        finally:
            restore_files(backups)

    def test_feature_commit_minor_bump(self):
        """FEATURE commits should trigger minor bumps."""
        backups = backup_files()
        try:
            write_version("2.3.1")
            write_commits([{
                "hash": "ghi789",
                "message": "FEATURE: Add new dashboard widget",
                "tag": "FEATURE"
            }])

            result = run_release_py()
            assert result.returncode == 0, (
                f"release.py failed with FEATURE commit: {result.stderr}"
            )

            version = read_version()
            assert version == "2.4.0", (
                f"VERSION is '{version}' but should be '2.4.0'. "
                "FEATURE commits should trigger a minor bump (2.3.1 -> 2.4.0)."
            )
        finally:
            restore_files(backups)

    def test_feature_under_features_section(self):
        """FEATURE entries should appear under 'Features' section."""
        backups = backup_files()
        try:
            write_version("2.3.1")
            write_commits([{
                "hash": "ghi789",
                "message": "FEATURE: Add new dashboard widget",
                "tag": "FEATURE"
            }])

            run_release_py()
            changelog = read_changelog()

            # Check for Features section
            has_features_section = (
                "## Features" in changelog or
                "# Features" in changelog or
                "Features:" in changelog or
                "\nFeatures\n" in changelog
            )
            assert has_features_section, (
                "CHANGELOG.md should have a 'Features' section for FEATURE commits"
            )
        finally:
            restore_files(backups)


class TestConfigIsUsed:
    """Test that config.yaml is actually being used, not hardcoded logic."""

    def test_config_yaml_still_exists(self):
        """config.yaml must still exist and be used."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        assert os.path.isfile(filepath), (
            "config.yaml has been deleted. The fix should preserve config-driven behavior."
        )

    def test_config_structure_preserved(self):
        """config.yaml structure should be preserved."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        try:
            import yaml
            with open(filepath, "r") as f:
                config = yaml.safe_load(f)

            assert "version_rules" in config, (
                "config.yaml missing 'version_rules' section"
            )
            assert "changelog_sections" in config, (
                "config.yaml missing 'changelog_sections' section"
            )
        except ImportError:
            # Fallback to text check
            with open(filepath, "r") as f:
                content = f.read()
            assert "version_rules" in content
            assert "changelog_sections" in content

    def test_config_patch_triggers_unchanged(self):
        """patch_triggers should still contain SECURITY, BUGFIX, DOCS."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        with open(filepath, "r") as f:
            content = f.read()

        # These should all still be in config
        for trigger in ["SECURITY", "BUGFIX", "DOCS"]:
            assert trigger in content, (
                f"config.yaml should still contain '{trigger}' in patch_triggers"
            )


class TestCommitsJsonUnchanged:
    """Test that commits.json structure is still valid."""

    def test_commits_json_exists(self):
        """commits.json must still exist."""
        filepath = os.path.join(RELEASER_DIR, "commits.json")
        assert os.path.isfile(filepath), (
            "commits.json has been deleted."
        )

    def test_commits_json_is_valid(self):
        """commits.json must be valid JSON."""
        filepath = os.path.join(RELEASER_DIR, "commits.json")
        with open(filepath, "r") as f:
            content = f.read()
        try:
            data = json.loads(content)
            assert isinstance(data, list), "commits.json must be a JSON array"
        except json.JSONDecodeError as e:
            pytest.fail(f"commits.json is not valid JSON: {e}")


class TestAllModulesValid:
    """Test that all Python modules are still valid after fixes."""

    def test_release_py_valid_syntax(self):
        """release.py must have valid Python syntax."""
        filepath = os.path.join(RELEASER_DIR, "release.py")
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"release.py has syntax errors: {result.stderr}"
        )

    def test_semver_py_valid_syntax(self):
        """semver.py must have valid Python syntax."""
        filepath = os.path.join(RELEASER_DIR, "semver.py")
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"semver.py has syntax errors: {result.stderr}"
        )

    def test_changelog_py_valid_syntax(self):
        """changelog.py must have valid Python syntax."""
        filepath = os.path.join(RELEASER_DIR, "changelog.py")
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"changelog.py has syntax errors: {result.stderr}"
        )

    def test_utils_py_valid_syntax(self):
        """utils.py must have valid Python syntax if it exists."""
        filepath = os.path.join(RELEASER_DIR, "utils.py")
        if os.path.exists(filepath):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", filepath],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, (
                f"utils.py has syntax errors: {result.stderr}"
            )


class TestVersionComputedByTooling:
    """Test that VERSION is computed by the tooling, not manually set."""

    def test_version_computed_not_hardcoded(self):
        """
        Reset VERSION to 2.3.1, use FEATURE commit, verify it becomes 2.4.0.
        This proves the tooling computes the version, not just hardcoded.
        """
        backups = backup_files()
        try:
            # Reset to 2.3.1
            write_version("2.3.1")

            # Use a FEATURE commit
            write_commits([{
                "hash": "xyz999",
                "message": "FEATURE: Add export functionality",
                "tag": "FEATURE"
            }])

            result = run_release_py()
            assert result.returncode == 0, (
                f"release.py failed: {result.stderr}"
            )

            version = read_version()
            assert version == "2.4.0", (
                f"VERSION is '{version}' but should be '2.4.0' after FEATURE commit. "
                "This suggests the version is hardcoded rather than computed."
            )
        finally:
            restore_files(backups)

    def test_different_starting_version(self):
        """Test with a different starting version to ensure computation works."""
        backups = backup_files()
        try:
            # Start from a different version
            write_version("1.0.0")

            # Use a SECURITY commit
            write_commits([{
                "hash": "test123",
                "message": "SECURITY: Fix XSS vulnerability",
                "tag": "SECURITY"
            }])

            result = run_release_py()
            assert result.returncode == 0, (
                f"release.py failed: {result.stderr}"
            )

            version = read_version()
            assert version == "1.0.1", (
                f"VERSION is '{version}' but should be '1.0.1'. "
                "Starting from 1.0.0, a SECURITY patch bump should give 1.0.1."
            )
        finally:
            restore_files(backups)
