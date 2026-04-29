# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the unzip task for Spanish translation files.
"""

import os
import subprocess
import zipfile
import pytest


class TestInitialState:
    """Validate the initial state before the unzip operation."""

    def test_translations_directory_exists(self):
        """The /home/user/translations/ directory must exist."""
        translations_dir = "/home/user/translations"
        assert os.path.isdir(translations_dir), (
            f"Directory {translations_dir} does not exist. "
            "The translations directory must be present."
        )

    def test_translations_directory_is_writable(self):
        """The /home/user/translations/ directory must be writable."""
        translations_dir = "/home/user/translations"
        assert os.access(translations_dir, os.W_OK), (
            f"Directory {translations_dir} is not writable. "
            "The user must have write permissions to extract files."
        )

    def test_zip_file_exists(self):
        """The es_MX.zip file must exist."""
        zip_path = "/home/user/translations/es_MX.zip"
        assert os.path.isfile(zip_path), (
            f"Zip file {zip_path} does not exist. "
            "The vendor zip file must be present for extraction."
        )

    def test_zip_file_is_valid(self):
        """The es_MX.zip file must be a valid zip archive."""
        zip_path = "/home/user/translations/es_MX.zip"
        assert zipfile.is_zipfile(zip_path), (
            f"{zip_path} is not a valid zip archive. "
            "The file must be a proper zip file."
        )

    def test_zip_contains_messages_properties(self):
        """The zip must contain messages.properties."""
        zip_path = "/home/user/translations/es_MX.zip"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "messages.properties" in names, (
                "messages.properties not found in zip archive. "
                f"Found files: {names}"
            )

    def test_zip_contains_errors_properties(self):
        """The zip must contain errors.properties."""
        zip_path = "/home/user/translations/es_MX.zip"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "errors.properties" in names, (
                "errors.properties not found in zip archive. "
                f"Found files: {names}"
            )

    def test_zip_contains_ui_labels_properties(self):
        """The zip must contain ui_labels.properties."""
        zip_path = "/home/user/translations/es_MX.zip"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            names = zf.namelist()
            assert "ui_labels.properties" in names, (
                "ui_labels.properties not found in zip archive. "
                f"Found files: {names}"
            )

    def test_messages_properties_has_content(self):
        """messages.properties in zip should have ~50 lines with property format."""
        zip_path = "/home/user/translations/es_MX.zip"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            content = zf.read("messages.properties").decode('utf-8')
            lines = content.strip().split('\n')
            # Check it has substantial content (around 50 lines)
            assert len(lines) >= 40, (
                f"messages.properties has only {len(lines)} lines, expected ~50. "
                "The file should contain Spanish translations."
            )
            # Check it has property format (lines with =)
            property_lines = [l for l in lines if '=' in l and not l.strip().startswith('#')]
            assert len(property_lines) > 0, (
                "messages.properties doesn't appear to be in property file format. "
                "Expected lines with '=' character."
            )

    def test_errors_properties_has_content(self):
        """errors.properties in zip should have ~20 lines with property format."""
        zip_path = "/home/user/translations/es_MX.zip"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            content = zf.read("errors.properties").decode('utf-8')
            lines = content.strip().split('\n')
            # Check it has substantial content (around 20 lines)
            assert len(lines) >= 15, (
                f"errors.properties has only {len(lines)} lines, expected ~20. "
                "The file should contain error messages."
            )
            # Check it has property format (lines with =)
            property_lines = [l for l in lines if '=' in l and not l.strip().startswith('#')]
            assert len(property_lines) > 0, (
                "errors.properties doesn't appear to be in property file format. "
                "Expected lines with '=' character."
            )

    def test_ui_labels_properties_has_content(self):
        """ui_labels.properties in zip should have ~30 lines with property format."""
        zip_path = "/home/user/translations/es_MX.zip"
        with zipfile.ZipFile(zip_path, 'r') as zf:
            content = zf.read("ui_labels.properties").decode('utf-8')
            lines = content.strip().split('\n')
            # Check it has substantial content (around 30 lines)
            assert len(lines) >= 25, (
                f"ui_labels.properties has only {len(lines)} lines, expected ~30. "
                "The file should contain UI strings."
            )
            # Check it has property format (lines with =)
            property_lines = [l for l in lines if '=' in l and not l.strip().startswith('#')]
            assert len(property_lines) > 0, (
                "ui_labels.properties doesn't appear to be in property file format. "
                "Expected lines with '=' character."
            )

    def test_es_mx_directory_does_not_exist(self):
        """The /home/user/translations/es_MX/ directory must NOT exist initially."""
        es_mx_dir = "/home/user/translations/es_MX"
        assert not os.path.exists(es_mx_dir), (
            f"Directory {es_mx_dir} already exists. "
            "The target directory should not exist before the student performs the extraction."
        )

    def test_unzip_is_installed(self):
        """The unzip command must be available."""
        result = subprocess.run(
            ["which", "unzip"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "unzip command is not installed or not in PATH. "
            "The unzip utility must be available for extraction."
        )

    def test_unzip_is_functional(self):
        """The unzip command must be functional."""
        result = subprocess.run(
            ["unzip", "-v"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "unzip command is not functional. "
            f"Error: {result.stderr}"
        )
