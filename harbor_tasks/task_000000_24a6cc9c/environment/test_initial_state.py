# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the version bump and changelog update task.
"""

import json
import os
import pytest
import subprocess


class TestInitialState:
    """Validate the initial state before the task is performed."""

    def test_libmetrics_directory_exists(self):
        """Verify /home/user/libmetrics directory exists."""
        dir_path = "/home/user/libmetrics"
        assert os.path.isdir(dir_path), (
            f"Directory {dir_path} does not exist. "
            "The libmetrics project directory must be present."
        )

    def test_package_json_exists(self):
        """Verify package.json exists in the libmetrics directory."""
        file_path = "/home/user/libmetrics/package.json"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "The package.json file must be present for version bumping."
        )

    def test_package_json_is_valid_json(self):
        """Verify package.json contains valid JSON."""
        file_path = "/home/user/libmetrics/package.json"
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {file_path} does not contain valid JSON: {e}"
            )

    def test_package_json_has_version_2_3_1(self):
        """Verify package.json has version 2.3.1."""
        file_path = "/home/user/libmetrics/package.json"
        with open(file_path, 'r') as f:
            data = json.load(f)

        assert "version" in data, (
            f"File {file_path} does not contain a 'version' field. "
            "The package.json must have a version field to bump."
        )
        assert data["version"] == "2.3.1", (
            f"File {file_path} has version '{data['version']}' but expected '2.3.1'. "
            "The initial version must be 2.3.1 before bumping to 2.4.0."
        )

    def test_changelog_exists(self):
        """Verify CHANGELOG.md exists in the libmetrics directory."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "The CHANGELOG.md file must be present for adding changelog entries."
        )

    def test_changelog_has_header(self):
        """Verify CHANGELOG.md has the # Changelog header."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "# Changelog" in content, (
            f"File {file_path} does not contain '# Changelog' header. "
            "The changelog must have a proper header."
        )

    def test_changelog_has_version_2_3_1_entry(self):
        """Verify CHANGELOG.md has the 2.3.1 version entry."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "## [2.3.1]" in content, (
            f"File {file_path} does not contain '## [2.3.1]' heading. "
            "The changelog must have the 2.3.1 version entry."
        )
        assert "Fixed memory leak in counter reset" in content, (
            f"File {file_path} does not contain the 2.3.1 changelog entry. "
            "Expected 'Fixed memory leak in counter reset'."
        )

    def test_changelog_has_version_2_3_0_entry(self):
        """Verify CHANGELOG.md has the 2.3.0 version entry."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "## [2.3.0]" in content, (
            f"File {file_path} does not contain '## [2.3.0]' heading. "
            "The changelog must have the 2.3.0 version entry."
        )
        assert "Added gauge metric type" in content, (
            f"File {file_path} does not contain the 2.3.0 changelog entry. "
            "Expected 'Added gauge metric type'."
        )

    def test_changelog_does_not_have_version_2_4_0(self):
        """Verify CHANGELOG.md does NOT yet have a 2.4.0 entry."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        with open(file_path, 'r') as f:
            content = f.read()

        assert "## [2.4.0]" not in content, (
            f"File {file_path} already contains '## [2.4.0]' heading. "
            "The 2.4.0 entry should not exist in the initial state."
        )

    def test_package_json_is_writable(self):
        """Verify package.json is writable by the user."""
        file_path = "/home/user/libmetrics/package.json"
        assert os.access(file_path, os.W_OK), (
            f"File {file_path} is not writable. "
            "The user must have write permissions to modify package.json."
        )

    def test_changelog_is_writable(self):
        """Verify CHANGELOG.md is writable by the user."""
        file_path = "/home/user/libmetrics/CHANGELOG.md"
        assert os.access(file_path, os.W_OK), (
            f"File {file_path} is not writable. "
            "The user must have write permissions to modify CHANGELOG.md."
        )

    def test_jq_is_available(self):
        """Verify jq tool is available."""
        result = subprocess.run(
            ["which", "jq"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "jq is not available on the system. "
            "The jq tool should be installed for JSON manipulation."
        )

    def test_sed_is_available(self):
        """Verify sed tool is available."""
        result = subprocess.run(
            ["which", "sed"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "sed is not available on the system. "
            "The sed tool should be installed for text manipulation."
        )

    def test_python3_is_available(self):
        """Verify python3 is available."""
        result = subprocess.run(
            ["which", "python3"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "python3 is not available on the system. "
            "Python 3 should be installed as an alternative tool."
        )
