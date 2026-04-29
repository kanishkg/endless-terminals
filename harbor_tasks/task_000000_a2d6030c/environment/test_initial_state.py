# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the debugging task for the changelog generator at /home/user/releaser.
"""

import os
import subprocess
import pytest
import yaml


BASE_DIR = "/home/user/releaser"
PROJECT_DIR = os.path.join(BASE_DIR, "project")


class TestDirectoryStructure:
    """Verify the expected directory structure exists."""

    def test_releaser_directory_exists(self):
        """The /home/user/releaser directory must exist."""
        assert os.path.isdir(BASE_DIR), f"Directory {BASE_DIR} does not exist"

    def test_project_directory_exists(self):
        """The /home/user/releaser/project directory must exist."""
        assert os.path.isdir(PROJECT_DIR), f"Directory {PROJECT_DIR} does not exist"


class TestRequiredFiles:
    """Verify all required Python files and config exist."""

    @pytest.mark.parametrize("filename", [
        "release.py",
        "parse_commits.py",
        "semver.py",
        "changelog.py",
        "releaser.yaml",
    ])
    def test_required_file_exists(self, filename):
        """Each required file must exist in the releaser directory."""
        filepath = os.path.join(BASE_DIR, filename)
        assert os.path.isfile(filepath), f"Required file {filepath} does not exist"

    def test_test_semver_exists(self):
        """test_semver.py should exist for unit tests."""
        filepath = os.path.join(BASE_DIR, "test_semver.py")
        assert os.path.isfile(filepath), f"Test file {filepath} does not exist"


class TestGitRepository:
    """Verify the project is a valid git repository with expected state."""

    def test_project_is_git_repo(self):
        """The project directory must be a git repository."""
        git_dir = os.path.join(PROJECT_DIR, ".git")
        assert os.path.isdir(git_dir), f"{PROJECT_DIR} is not a git repository (no .git directory)"

    def test_git_available(self):
        """Git must be available on the system."""
        result = subprocess.run(
            ["which", "git"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Git is not installed or not in PATH"

    def test_v2_9_3_tag_exists(self):
        """The v2.9.3 tag must exist in the project repository."""
        result = subprocess.run(
            ["git", "tag", "-l", "v2.9.3"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        assert result.returncode == 0, "Failed to list git tags"
        assert "v2.9.3" in result.stdout, "Tag v2.9.3 does not exist in the repository"

    def test_commits_since_v2_9_3_exist(self):
        """There should be commits after the v2.9.3 tag."""
        result = subprocess.run(
            ["git", "log", "v2.9.3..HEAD", "--oneline"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        assert result.returncode == 0, "Failed to get git log"
        commits = result.stdout.strip().split('\n')
        commits = [c for c in commits if c]  # Filter empty lines
        assert len(commits) >= 1, "No commits found after v2.9.3 tag"

    def test_breaking_change_commit_exists(self):
        """At least one commit with breaking change indicator (feat!:) must exist."""
        result = subprocess.run(
            ["git", "log", "v2.9.3..HEAD", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            cwd=PROJECT_DIR
        )
        assert result.returncode == 0, "Failed to get git log"
        commit_messages = result.stdout.strip()
        # Check for breaking change indicators
        has_breaking = "!" in commit_messages or "BREAKING" in commit_messages.upper()
        assert has_breaking, "No breaking change commit found (expected feat!: or similar)"


class TestConfigFile:
    """Verify the releaser.yaml configuration file has expected content."""

    def test_config_is_valid_yaml(self):
        """releaser.yaml must be valid YAML."""
        config_path = os.path.join(BASE_DIR, "releaser.yaml")
        with open(config_path, 'r') as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as e:
                pytest.fail(f"releaser.yaml is not valid YAML: {e}")
        assert config is not None, "releaser.yaml is empty"

    def test_config_has_max_minor_before_major(self):
        """Config must have max_minor_before_major setting."""
        config_path = os.path.join(BASE_DIR, "releaser.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        assert 'max_minor_before_major' in config, \
            "releaser.yaml missing 'max_minor_before_major' setting"

    def test_max_minor_before_major_is_9(self):
        """max_minor_before_major should be set to '9' (as string, the bug source)."""
        config_path = os.path.join(BASE_DIR, "releaser.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        value = config.get('max_minor_before_major')
        # The bug involves string comparison, so value should be "9" as string
        assert str(value) == "9", \
            f"max_minor_before_major should be '9', got '{value}'"


class TestSemverModule:
    """Verify semver.py has the expected buggy behavior."""

    def test_semver_has_version_class(self):
        """semver.py should define a Version class."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        with open(semver_path, 'r') as f:
            content = f.read()
        assert "class Version" in content, "semver.py should contain a Version class"

    def test_semver_has_can_bump_major(self):
        """semver.py should have a can_bump_major method."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        with open(semver_path, 'r') as f:
            content = f.read()
        assert "can_bump_major" in content, \
            "semver.py should contain can_bump_major method"

    def test_semver_has_string_comparison_bug(self):
        """The bug should be present - string comparison in can_bump_major."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        with open(semver_path, 'r') as f:
            content = f.read()
        # Look for indicators of the string comparison bug
        # The bug is comparing minor (int) with config value (string) without conversion
        # or comparing as strings
        has_potential_bug = (
            "max_minor_before_major" in content and
            "can_bump_major" in content
        )
        assert has_potential_bug, \
            "semver.py should reference max_minor_before_major in can_bump_major"


class TestReleaseModule:
    """Verify release.py has the expected structure."""

    def test_release_has_bump_type_check(self):
        """release.py should check can_bump_major before major bumps."""
        release_path = os.path.join(BASE_DIR, "release.py")
        with open(release_path, 'r') as f:
            content = f.read()
        assert "can_bump_major" in content, \
            "release.py should call can_bump_major"

    def test_release_has_fallback_to_minor(self):
        """release.py should fall back to minor when major is blocked."""
        release_path = os.path.join(BASE_DIR, "release.py")
        with open(release_path, 'r') as f:
            content = f.read()
        # Check for the fallback logic
        has_fallback = "minor" in content.lower() and "major" in content.lower()
        assert has_fallback, \
            "release.py should have logic to fall back from major to minor bump"


class TestParseCommitsModule:
    """Verify parse_commits.py exists and handles breaking changes."""

    def test_parse_commits_handles_breaking(self):
        """parse_commits.py should be able to identify breaking changes."""
        parse_path = os.path.join(BASE_DIR, "parse_commits.py")
        with open(parse_path, 'r') as f:
            content = f.read()
        # Should handle breaking change detection
        handles_breaking = (
            "breaking" in content.lower() or
            "major" in content.lower() or
            "!" in content
        )
        assert handles_breaking, \
            "parse_commits.py should handle breaking change detection"


class TestPythonEnvironment:
    """Verify Python environment is properly set up."""

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python 3 is not available"

    def test_python_version_3_11_or_higher(self):
        """Python version should be 3.11 or compatible."""
        result = subprocess.run(
            ["python3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Failed to get Python version"
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        assert major >= 3 and minor >= 8, f"Python version {version} may be too old (expected 3.11+)"


class TestCurrentBuggyBehavior:
    """Verify the bug is present - release.py outputs 2.10.0 instead of 3.0.0."""

    def test_release_produces_wrong_version(self):
        """Running release.py should currently produce 2.10.0 (the bug)."""
        result = subprocess.run(
            ["python3", "release.py"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        # The script should run without crashing
        # It should output 2.10.0 (the buggy behavior) not 3.0.0
        output = result.stdout + result.stderr

        # Verify the bug exists - it should NOT output 3.0.0 yet
        assert "3.0.0" not in output, \
            "Bug not present: release.py already outputs 3.0.0 (expected 2.10.0)"

        # Should output 2.10.0 (the buggy minor bump instead of major)
        assert "2.10.0" in output or result.returncode == 0, \
            f"release.py did not produce expected buggy output. Got: {output}"


class TestDirectoryWritable:
    """Verify the releaser directory is writable."""

    def test_releaser_dir_writable(self):
        """The /home/user/releaser directory must be writable."""
        assert os.access(BASE_DIR, os.W_OK), \
            f"Directory {BASE_DIR} is not writable"

    def test_semver_file_writable(self):
        """semver.py must be writable (for fixing the bug)."""
        semver_path = os.path.join(BASE_DIR, "semver.py")
        assert os.access(semver_path, os.W_OK), \
            f"File {semver_path} is not writable"
