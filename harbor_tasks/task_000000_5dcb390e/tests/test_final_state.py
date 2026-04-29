# test_final_state.py
"""
Tests to validate the final state after the student has fixed the standard-version release script issue.
The release should complete successfully, bumping version from 2.4.0 to 2.5.0.
"""

import json
import os
import re
import subprocess
import pytest


class TestReleaseScriptSuccess:
    """Test that the release script now runs successfully."""

    def test_release_script_exits_zero(self):
        """Verify ./scripts/release.sh exits with code 0."""
        # First, we need to check if 2.5.0 already exists (task was completed)
        # If so, we'll run a patch release to verify the fix is permanent
        result = subprocess.run(
            ["git", "tag", "-l", "v2.5.0"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )

        if "v2.5.0" in result.stdout:
            # Version 2.5.0 already exists, the task was completed
            # We just verify the state is correct
            pass
        else:
            # Run the release script - it should succeed now
            result = subprocess.run(
                ["./scripts/release.sh"],
                cwd="/home/user/project",
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"Release script failed with exit code {result.returncode}.\nStdout: {result.stdout}\nStderr: {result.stderr}"


class TestVersionBump:
    """Test that version was bumped correctly to 2.5.0."""

    def test_package_json_version_is_2_5_0(self):
        """Verify package.json version is 2.5.0."""
        with open("/home/user/project/package.json", "r") as f:
            package_json = json.load(f)
        assert package_json.get("version") == "2.5.0", \
            f"package.json version should be '2.5.0', but is '{package_json.get('version')}'"

    def test_version_file_is_valid_and_updated(self):
        """Verify VERSION file contains valid content that was bumped."""
        with open("/home/user/project/VERSION", "r") as f:
            content = f.read().strip()

        # The VERSION file should contain 2.5.0 in some valid format
        # It could be "2.5.0" (plain) or configured differently
        # The key is that it should NOT have the problematic "v" prefix for plain-text type
        # OR the config should have been changed to handle the prefix
        assert "2.5.0" in content, \
            f"VERSION file should contain '2.5.0' after bump, but contains '{content}'"


class TestChangelogUpdated:
    """Test that CHANGELOG.md was updated with new release."""

    def test_changelog_contains_2_5_0_section(self):
        """Verify CHANGELOG.md contains a section for version 2.5.0."""
        with open("/home/user/project/CHANGELOG.md", "r") as f:
            content = f.read()

        # Check for 2.5.0 version header (various formats standard-version might use)
        assert "2.5.0" in content, \
            "CHANGELOG.md does not contain version 2.5.0"

    def test_changelog_contains_feat_entry(self):
        """Verify CHANGELOG.md contains the feat commit entry."""
        with open("/home/user/project/CHANGELOG.md", "r") as f:
            content = f.read().lower()

        # Check for the feature about backup rotation policy
        assert "backup" in content or "rotation" in content or "features" in content, \
            "CHANGELOG.md does not appear to contain the feat commit about backup rotation policy"

    def test_changelog_contains_fix_entry(self):
        """Verify CHANGELOG.md contains the fix commit entry."""
        with open("/home/user/project/CHANGELOG.md", "r") as f:
            content = f.read().lower()

        # Check for the fix about archive timestamp
        assert "archive" in content or "timestamp" in content or "bug fixes" in content or "fix" in content, \
            "CHANGELOG.md does not appear to contain the fix commit about archive timestamp format"


class TestGitState:
    """Test git repository state after release."""

    def test_git_tag_v2_5_0_exists(self):
        """Verify git tag v2.5.0 exists."""
        result = subprocess.run(
            ["git", "tag", "-l", "v2.5.0"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert "v2.5.0" in result.stdout, \
            "Git tag 'v2.5.0' does not exist - release did not create the tag"

    def test_version_bump_commit_exists(self):
        """Verify a version bump commit exists."""
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Failed to get git log"
        latest_commit = result.stdout.strip().lower()
        # standard-version creates commits like "chore(release): 2.5.0"
        assert "2.5.0" in latest_commit or "release" in latest_commit, \
            f"Latest commit doesn't appear to be a version bump commit: {latest_commit}"

    def test_original_tag_v2_4_0_still_exists(self):
        """Verify original git tag v2.4.0 still exists (history preserved)."""
        result = subprocess.run(
            ["git", "tag", "-l", "v2.4.0"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert "v2.4.0" in result.stdout, \
            "Git tag 'v2.4.0' no longer exists - git history was not preserved"


class TestConfigurationIntegrity:
    """Test that configuration integrity is maintained."""

    def test_tag_prefix_is_still_v(self):
        """Verify tagPrefix is still 'v' in configuration."""
        with open("/home/user/project/.versionrc.json", "r") as f:
            versionrc = json.load(f)
        assert versionrc.get("tagPrefix") == "v", \
            f"tagPrefix should still be 'v', but is '{versionrc.get('tagPrefix')}'"

    def test_standard_version_still_used(self):
        """Verify standard-version is still the tool being used."""
        with open("/home/user/project/scripts/release.sh", "r") as f:
            content = f.read()
        assert "standard-version" in content, \
            "release.sh no longer uses standard-version - tool was replaced"

    def test_both_bump_files_still_configured(self):
        """Verify both package.json and VERSION are still in bumpFiles."""
        with open("/home/user/project/.versionrc.json", "r") as f:
            versionrc = json.load(f)

        bump_files = versionrc.get("bumpFiles", [])
        filenames = [bf.get("filename") for bf in bump_files]

        assert "package.json" in filenames, \
            "package.json was removed from bumpFiles configuration"
        assert "VERSION" in filenames, \
            "VERSION was removed from bumpFiles configuration - this is not a valid fix"

    def test_version_file_still_exists(self):
        """Verify VERSION file still exists (wasn't deleted as a shortcut)."""
        assert os.path.isfile("/home/user/project/VERSION"), \
            "VERSION file was deleted - this is not a valid fix"


class TestSubsequentReleaseWorks:
    """Test that a subsequent release also works (proving the fix is permanent)."""

    def test_patch_release_succeeds(self):
        """Verify running another release (patch) also succeeds."""
        # Check current state
        with open("/home/user/project/package.json", "r") as f:
            package_json = json.load(f)

        current_version = package_json.get("version")

        # Only run this test if we're at 2.5.0 (task was completed)
        if current_version != "2.5.0":
            pytest.skip("Version is not 2.5.0 yet, skipping subsequent release test")

        # Check if 2.5.1 already exists (test was run before)
        result = subprocess.run(
            ["git", "tag", "-l", "v2.5.1"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )

        if "v2.5.1" in result.stdout:
            # Already tested, just verify state
            with open("/home/user/project/package.json", "r") as f:
                package_json = json.load(f)
            assert package_json.get("version") == "2.5.1", \
                "Subsequent release to 2.5.1 did not update package.json correctly"
            return

        # Run a patch release
        result = subprocess.run(
            ["npx", "standard-version", "--release-as", "patch"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, \
            f"Subsequent patch release failed with exit code {result.returncode}.\n" \
            f"This indicates the fix was a one-time workaround, not a proper solution.\n" \
            f"Stdout: {result.stdout}\nStderr: {result.stderr}"

        # Verify the patch release created 2.5.1
        with open("/home/user/project/package.json", "r") as f:
            package_json = json.load(f)

        assert package_json.get("version") == "2.5.1", \
            f"Patch release should have bumped to 2.5.1, but version is {package_json.get('version')}"

        # Verify VERSION file was also updated
        with open("/home/user/project/VERSION", "r") as f:
            version_content = f.read().strip()

        assert "2.5.1" in version_content, \
            f"VERSION file should contain 2.5.1 after patch release, but contains '{version_content}'"


class TestStandardVersionStillInstalled:
    """Test that standard-version is still properly installed."""

    def test_standard_version_in_dev_dependencies(self):
        """Verify standard-version is still in devDependencies."""
        with open("/home/user/project/package.json", "r") as f:
            package_json = json.load(f)

        dev_deps = package_json.get("devDependencies", {})
        assert "standard-version" in dev_deps, \
            "standard-version is no longer in devDependencies"

    def test_standard_version_node_module_exists(self):
        """Verify standard-version is still installed in node_modules."""
        assert os.path.isdir("/home/user/project/node_modules/standard-version"), \
            "standard-version is not installed in node_modules"
