# test_initial_state.py
"""
Tests to validate the initial state of the release tooling at /home/user/releaser
before the student fixes the bugs.
"""

import os
import json
import pytest
import subprocess
import sys

RELEASER_DIR = "/home/user/releaser"


class TestDirectoryStructure:
    """Test that the releaser directory and required files exist."""

    def test_releaser_directory_exists(self):
        """The /home/user/releaser directory must exist."""
        assert os.path.isdir(RELEASER_DIR), (
            f"Directory {RELEASER_DIR} does not exist. "
            "The release tooling directory is required."
        )

    def test_release_py_exists(self):
        """The main entry point release.py must exist."""
        filepath = os.path.join(RELEASER_DIR, "release.py")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The main release.py script is required."
        )

    def test_semver_py_exists(self):
        """The version bumping logic semver.py must exist."""
        filepath = os.path.join(RELEASER_DIR, "semver.py")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The semver.py module is required for version bumping logic."
        )

    def test_changelog_py_exists(self):
        """The changelog generation module changelog.py must exist."""
        filepath = os.path.join(RELEASER_DIR, "changelog.py")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The changelog.py module is required for changelog generation."
        )

    def test_config_yaml_exists(self):
        """The configuration file config.yaml must exist."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The config.yaml configuration file is required."
        )

    def test_version_file_exists(self):
        """The VERSION file must exist."""
        filepath = os.path.join(RELEASER_DIR, "VERSION")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The VERSION file is required."
        )

    def test_changelog_md_exists(self):
        """The CHANGELOG.md file must exist."""
        filepath = os.path.join(RELEASER_DIR, "CHANGELOG.md")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The CHANGELOG.md file is required."
        )

    def test_commits_json_exists(self):
        """The commits.json file must exist for simulated commit data."""
        filepath = os.path.join(RELEASER_DIR, "commits.json")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The commits.json file is required for simulated commit data."
        )


class TestVersionFile:
    """Test the VERSION file content."""

    def test_version_file_contains_2_3_1(self):
        """The VERSION file must contain exactly '2.3.1'."""
        filepath = os.path.join(RELEASER_DIR, "VERSION")
        with open(filepath, "r") as f:
            content = f.read().strip()
        assert content == "2.3.1", (
            f"VERSION file contains '{content}' but should contain '2.3.1'. "
            "The initial version must be 2.3.1 for this task."
        )


class TestConfigYaml:
    """Test the config.yaml structure and content."""

    def test_config_yaml_is_valid_yaml(self):
        """The config.yaml must be valid YAML."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        try:
            import yaml
            with open(filepath, "r") as f:
                config = yaml.safe_load(f)
            assert config is not None, "config.yaml is empty or invalid"
        except ImportError:
            # If PyYAML not available, just check file is readable
            with open(filepath, "r") as f:
                content = f.read()
            assert len(content) > 0, "config.yaml is empty"

    def test_config_has_version_rules(self):
        """The config.yaml must have version_rules section."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        try:
            import yaml
            with open(filepath, "r") as f:
                config = yaml.safe_load(f)
            assert "version_rules" in config, (
                "config.yaml missing 'version_rules' section"
            )
        except ImportError:
            with open(filepath, "r") as f:
                content = f.read()
            assert "version_rules" in content, (
                "config.yaml missing 'version_rules' section"
            )

    def test_config_has_changelog_sections(self):
        """The config.yaml must have changelog_sections section."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        try:
            import yaml
            with open(filepath, "r") as f:
                config = yaml.safe_load(f)
            assert "changelog_sections" in config, (
                "config.yaml missing 'changelog_sections' section"
            )
        except ImportError:
            with open(filepath, "r") as f:
                content = f.read()
            assert "changelog_sections" in content, (
                "config.yaml missing 'changelog_sections' section"
            )

    def test_config_has_patch_triggers_with_security(self):
        """The config.yaml must have SECURITY in patch_triggers."""
        filepath = os.path.join(RELEASER_DIR, "config.yaml")
        with open(filepath, "r") as f:
            content = f.read()
        # Check that SECURITY appears in the patch_triggers context
        assert "patch_triggers" in content, (
            "config.yaml missing 'patch_triggers' in version_rules"
        )
        assert "SECURITY" in content, (
            "config.yaml missing 'SECURITY' - it should be in patch_triggers"
        )


class TestCommitsJson:
    """Test the commits.json content."""

    def test_commits_json_is_valid_json(self):
        """The commits.json must be valid JSON."""
        filepath = os.path.join(RELEASER_DIR, "commits.json")
        with open(filepath, "r") as f:
            content = f.read()
        try:
            data = json.loads(content)
            assert isinstance(data, list), "commits.json must contain a JSON array"
        except json.JSONDecodeError as e:
            pytest.fail(f"commits.json is not valid JSON: {e}")

    def test_commits_json_has_security_commit(self):
        """The commits.json must have a SECURITY tagged commit."""
        filepath = os.path.join(RELEASER_DIR, "commits.json")
        with open(filepath, "r") as f:
            data = json.load(f)

        security_commits = [c for c in data if c.get("tag") == "SECURITY"]
        assert len(security_commits) > 0, (
            "commits.json must contain at least one commit with tag 'SECURITY'"
        )

    def test_commits_json_has_auth_bypass_commit(self):
        """The commits.json must have the auth bypass security commit."""
        filepath = os.path.join(RELEASER_DIR, "commits.json")
        with open(filepath, "r") as f:
            data = json.load(f)

        auth_bypass_commits = [
            c for c in data 
            if "auth bypass" in c.get("message", "").lower() or 
               "auth bypass" in c.get("message", "")
        ]
        assert len(auth_bypass_commits) > 0, (
            "commits.json must contain the auth bypass vulnerability commit"
        )


class TestUtilsModule:
    """Test for the utils.py module that contains the buggy YAML loader."""

    def test_utils_py_exists(self):
        """The utils.py module should exist (contains the buggy YAML loader)."""
        filepath = os.path.join(RELEASER_DIR, "utils.py")
        assert os.path.isfile(filepath), (
            f"File {filepath} does not exist. "
            "The utils.py module is expected to contain the custom YAML loader."
        )

    def test_utils_has_yaml_loader_or_config_loader(self):
        """The utils.py should have some form of config/YAML loading function."""
        filepath = os.path.join(RELEASER_DIR, "utils.py")
        with open(filepath, "r") as f:
            content = f.read()

        # Check for indicators of a config loader
        has_loader = (
            "yaml" in content.lower() or 
            "load" in content.lower() or
            "config" in content.lower()
        )
        assert has_loader, (
            "utils.py should contain YAML/config loading functionality"
        )


class TestPythonEnvironment:
    """Test that Python environment is properly set up."""

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python is not available"
        assert "Python 3" in result.stdout or "Python 3" in result.stderr, (
            "Python 3 is required"
        )

    def test_pyyaml_installed(self):
        """PyYAML must be installed."""
        result = subprocess.run(
            [sys.executable, "-c", "import yaml; print(yaml.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"PyYAML is not installed. Error: {result.stderr}"
        )


class TestDirectoryWritable:
    """Test that the releaser directory is writable."""

    def test_releaser_directory_writable(self):
        """The /home/user/releaser directory must be writable."""
        assert os.access(RELEASER_DIR, os.W_OK), (
            f"Directory {RELEASER_DIR} is not writable. "
            "The student needs write access to fix the bugs."
        )

    def test_version_file_writable(self):
        """The VERSION file must be writable."""
        filepath = os.path.join(RELEASER_DIR, "VERSION")
        assert os.access(filepath, os.W_OK), (
            f"File {filepath} is not writable."
        )

    def test_changelog_file_writable(self):
        """The CHANGELOG.md file must be writable."""
        filepath = os.path.join(RELEASER_DIR, "CHANGELOG.md")
        assert os.access(filepath, os.W_OK), (
            f"File {filepath} is not writable."
        )


class TestReleasePyStructure:
    """Test that release.py has expected structure."""

    def test_release_py_is_python(self):
        """release.py must be valid Python syntax."""
        filepath = os.path.join(RELEASER_DIR, "release.py")
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"release.py has syntax errors: {result.stderr}"
        )

    def test_semver_py_is_python(self):
        """semver.py must be valid Python syntax."""
        filepath = os.path.join(RELEASER_DIR, "semver.py")
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"semver.py has syntax errors: {result.stderr}"
        )

    def test_changelog_py_is_python(self):
        """changelog.py must be valid Python syntax."""
        filepath = os.path.join(RELEASER_DIR, "changelog.py")
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"changelog.py has syntax errors: {result.stderr}"
        )

    def test_utils_py_is_python(self):
        """utils.py must be valid Python syntax."""
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
