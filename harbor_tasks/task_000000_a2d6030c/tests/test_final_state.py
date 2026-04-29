# test_final_state.py
"""
Tests to validate the final state after the student has fixed the changelog
generator bug at /home/user/releaser. The fix should make release.py correctly
output 3.0.0 when there's a breaking change after 2.9.x.
"""

import os
import subprocess
import pytest
import yaml
import tempfile
import shutil


BASE_DIR = "/home/user/releaser"
PROJECT_DIR = os.path.join(BASE_DIR, "project")


class TestReleaseOutputsCorrectVersion:
    """Verify that release.py now correctly outputs 3.0.0 for breaking changes."""

    def test_release_outputs_3_0_0(self):
        """Running release.py should output 3.0.0 (not 2.10.0) for breaking change."""
        result = subprocess.run(
            ["python3", "release.py"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        output = result.stdout + result.stderr

        # Must contain 3.0.0
        assert "3.0.0" in output, \
            f"release.py should output '3.0.0' for breaking change after 2.9.x. Got: {output}"

        # Must NOT contain 2.10.0 (the buggy output)
        assert "2.10.0" not in output, \
            f"release.py still outputs buggy '2.10.0' instead of '3.0.0'. Got: {output}"

    def test_release_exits_successfully(self):
        """release.py should exit with code 0."""
        result = subprocess.run(
            ["python3", "release.py"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        assert result.returncode == 0, \
            f"release.py exited with code {result.returncode}. stderr: {result.stderr}"


class TestChangelogUpdated:
    """If CHANGELOG.md is updated, verify it contains 3.0.0 section."""

    def test_changelog_contains_3_0_0_if_exists(self):
        """If CHANGELOG.md exists and was updated, it should have 3.0.0 section."""
        changelog_path = os.path.join(PROJECT_DIR, "CHANGELOG.md")
        if os.path.isfile(changelog_path):
            with open(changelog_path, 'r') as f:
                content = f.read()
            # If changelog has any version headers, 3.0.0 should be present
            if "## " in content or "# " in content:
                assert "3.0.0" in content, \
                    "CHANGELOG.md exists but doesn't contain 3.0.0 section"


class TestGitHistoryUnchanged:
    """Verify git history in /home/user/releaser/project remains unchanged."""

    def test_v2_9_3_tag_still_exists(self):
        """The v2.9.3 tag must still exist."""
        result = subprocess.run(
            ["git", "tag", "-l", "v2.9.3"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        assert result.returncode == 0, "Failed to list git tags"
        assert "v2.9.3" in result.stdout, \
            "Tag v2.9.3 was deleted - git history should remain unchanged"

    def test_breaking_change_commit_still_exists(self):
        """The breaking change commit must still exist."""
        result = subprocess.run(
            ["git", "log", "v2.9.3..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        assert result.returncode == 0, "Failed to get git log"
        commit_messages = result.stdout.strip()
        has_breaking = "!" in commit_messages or "BREAKING" in commit_messages.upper()
        assert has_breaking, \
            "Breaking change commit was removed - git history should remain unchanged"

    def test_commit_count_unchanged(self):
        """Number of commits since v2.9.3 should be approximately the same (3)."""
        result = subprocess.run(
            ["git", "rev-list", "--count", "v2.9.3..HEAD"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        assert result.returncode == 0, "Failed to count commits"
        count = int(result.stdout.strip())
        # Should be 3 commits, allow small variance
        assert count >= 3, \
            f"Expected at least 3 commits since v2.9.3, got {count}. Git history may have been modified."


class TestParseCommitsStillWorks:
    """Verify parse_commits.py still correctly identifies breaking changes."""

    def test_parse_commits_exists(self):
        """parse_commits.py must still exist."""
        filepath = os.path.join(BASE_DIR, "parse_commits.py")
        assert os.path.isfile(filepath), f"parse_commits.py was deleted or moved"

    def test_parse_commits_identifies_breaking(self):
        """parse_commits.py should still identify breaking changes."""
        # Import and test the module
        result = subprocess.run(
            ["python3", "-c", """
import sys
sys.path.insert(0, '/home/user/releaser')
from parse_commits import parse_commits
commits = parse_commits('/home/user/releaser/project', 'v2.9.3')
# Check if any commit is marked as breaking/major
has_breaking = any(
    c.get('breaking', False) or 
    c.get('bump_type') == 'major' or
    c.get('type', '').endswith('!')
    for c in commits
) if isinstance(commits, list) else 'major' in str(commits).lower()
print('BREAKING_FOUND' if has_breaking else 'NO_BREAKING')
"""],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        # Even if the exact API differs, the module should work
        assert result.returncode == 0 or "BREAKING_FOUND" in result.stdout, \
            f"parse_commits.py may not be working correctly: {result.stderr}"


class TestAntiShortcutHardcodedVersion:
    """Ensure version is computed, not hardcoded."""

    def test_no_hardcoded_3_0_0_in_release(self):
        """release.py must not have hardcoded 3.0.0."""
        release_path = os.path.join(BASE_DIR, "release.py")
        result = subprocess.run(
            ["grep", "-E", r'bump_type.*=.*major|return.*3\.0\.0|"3\.0\.0"'],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            input=open(release_path).read()
        )
        # grep returns 0 if match found, 1 if no match
        with open(release_path, 'r') as f:
            content = f.read()

        # Check for hardcoded version
        hardcoded_patterns = [
            '"3.0.0"',
            "'3.0.0'",
            'return "3.0.0"',
            "return '3.0.0'",
        ]
        for pattern in hardcoded_patterns:
            assert pattern not in content, \
                f"release.py contains hardcoded version '{pattern}' - version must be computed"


class TestPolicyStillFunctions:
    """Verify the max_minor_before_major policy still works correctly."""

    def test_policy_blocks_at_lower_minor(self):
        """Setting max_minor_before_major to 5 should block major bumps at 2.4.x."""
        # Create a temporary modified config and test
        config_path = os.path.join(BASE_DIR, "releaser.yaml")

        # Read original config
        with open(config_path, 'r') as f:
            original_config = f.read()

        try:
            # Modify config to set max_minor_before_major to 5
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            config['max_minor_before_major'] = 5
            with open(config_path, 'w') as f:
                yaml.dump(config, f)

            # We need to simulate v2.4.0 scenario
            # Create a test script that checks the policy logic
            test_script = """
import sys
sys.path.insert(0, '/home/user/releaser')
import yaml

# Load config
with open('/home/user/releaser/releaser.yaml', 'r') as f:
    config = yaml.safe_load(f)

from semver import Version

# Create a version 2.4.0 and check if major bump is allowed
v = Version('2.4.0', config)
can_bump = v.can_bump_major()
print(f'CAN_BUMP_MAJOR_AT_2_4_0: {can_bump}')

# Also test 2.5.0 - should allow major bump
v2 = Version('2.5.0', config)
can_bump2 = v2.can_bump_major()
print(f'CAN_BUMP_MAJOR_AT_2_5_0: {can_bump2}')

# Test 2.6.0 - should allow major bump (6 > 5)
v3 = Version('2.6.0', config)
can_bump3 = v3.can_bump_major()
print(f'CAN_BUMP_MAJOR_AT_2_6_0: {can_bump3}')
"""
            result = subprocess.run(
                ["python3", "-c", test_script],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )

            output = result.stdout + result.stderr

            # At 2.4.0 with max=5, should NOT allow major bump (4 < 5)
            if "CAN_BUMP_MAJOR_AT_2_4_0: False" in output:
                pass  # Correct behavior
            elif "CAN_BUMP_MAJOR_AT_2_4_0: True" in output:
                pytest.fail("Policy broken: major bump allowed at 2.4.0 when max_minor_before_major=5")

            # At 2.5.0 or 2.6.0 with max=5, SHOULD allow major bump (5 >= 5, 6 > 5)
            if "CAN_BUMP_MAJOR_AT_2_5_0: True" in output or "CAN_BUMP_MAJOR_AT_2_6_0: True" in output:
                pass  # Correct - policy allows bump at or after threshold

        finally:
            # Restore original config
            with open(config_path, 'w') as f:
                f.write(original_config)


class TestSemverUnitTestsPass:
    """Verify test_semver.py still passes after the fix."""

    def test_semver_unit_tests_pass(self):
        """test_semver.py unit tests must still pass."""
        test_path = os.path.join(BASE_DIR, "test_semver.py")
        if os.path.isfile(test_path):
            result = subprocess.run(
                ["python3", "-m", "pytest", test_path, "-v"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            # Allow for pytest not being installed - try unittest
            if result.returncode != 0 and "No module named pytest" in result.stderr:
                result = subprocess.run(
                    ["python3", "-m", "unittest", "test_semver", "-v"],
                    capture_output=True,
                    text=True,
                    cwd=BASE_DIR
                )

            assert result.returncode == 0, \
                f"test_semver.py tests failed after fix: {result.stdout}\n{result.stderr}"


class TestPolicyCheckNotRemoved:
    """Verify the policy check wasn't simply deleted."""

    def test_can_bump_major_still_exists(self):
        """The can_bump_major method must still exist in semver.py."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        with open(semver_path, 'r') as f:
            content = f.read()
        assert "can_bump_major" in content, \
            "can_bump_major was removed from semver.py - fix should correct the logic, not delete it"

    def test_max_minor_before_major_still_referenced(self):
        """The max_minor_before_major config should still be used."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        with open(semver_path, 'r') as f:
            content = f.read()
        assert "max_minor_before_major" in content, \
            "max_minor_before_major config is no longer used - policy check may have been improperly removed"

    def test_release_still_checks_can_bump_major(self):
        """release.py must still call can_bump_major."""
        release_path = os.path.join(BASE_DIR, "release.py")
        with open(release_path, 'r') as f:
            content = f.read()
        assert "can_bump_major" in content, \
            "release.py no longer calls can_bump_major - policy check should not be bypassed"


class TestFixIsInVersionBumpLogic:
    """Verify the fix is in the version/bump logic, not elsewhere."""

    def test_semver_was_modified_or_config_fixed(self):
        """Either semver.py comparison was fixed or config uses integer."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        config_path = os.path.join(BASE_DIR, "releaser.yaml")

        with open(semver_path, 'r') as f:
            semver_content = f.read()

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # The fix should be one of:
        # 1. Convert to int in comparison (int(self.minor) or int(config.get(...)))
        # 2. Config value is now an integer

        config_value = config.get('max_minor_before_major')
        config_is_int = isinstance(config_value, int)

        # Check if semver has int conversion
        has_int_conversion = (
            "int(" in semver_content and "max_minor_before_major" in semver_content
        ) or (
            "int(self.minor)" in semver_content
        ) or (
            # Check for proper integer comparison
            "self.minor >=" in semver_content or
            "self.minor <" in semver_content
        )

        # At least one fix approach should be present
        assert config_is_int or has_int_conversion or "int(" in semver_content, \
            "Fix not found: semver.py should use integer comparison or config should be integer"


class TestAllRequiredFilesExist:
    """Verify all required files still exist after the fix."""

    @pytest.mark.parametrize("filename", [
        "release.py",
        "parse_commits.py", 
        "semver.py",
        "changelog.py",
        "releaser.yaml",
    ])
    def test_required_file_exists(self, filename):
        """Each required file must still exist."""
        filepath = os.path.join(BASE_DIR, filename)
        assert os.path.isfile(filepath), \
            f"Required file {filepath} was deleted during fix"


class TestConfigStillValid:
    """Verify releaser.yaml is still valid after any modifications."""

    def test_config_is_valid_yaml(self):
        """releaser.yaml must still be valid YAML."""
        config_path = os.path.join(BASE_DIR, "releaser.yaml")
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"releaser.yaml is no longer valid YAML: {e}")
        assert config is not None, "releaser.yaml is empty"

    def test_config_has_required_keys(self):
        """Config must still have required keys."""
        config_path = os.path.join(BASE_DIR, "releaser.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        assert 'max_minor_before_major' in config, \
            "releaser.yaml missing 'max_minor_before_major' after fix"
