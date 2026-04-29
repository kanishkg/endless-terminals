# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the unzip task for Spanish translation files.
"""

import os
import zipfile
import pytest


class TestFinalState:
    """Validate the final state after the unzip operation."""

    def test_es_mx_directory_exists(self):
        """The /home/user/translations/es_MX/ directory must exist after extraction."""
        es_mx_dir = "/home/user/translations/es_MX"
        assert os.path.isdir(es_mx_dir), (
            f"Directory {es_mx_dir} does not exist. "
            "You need to extract the zip file to this directory."
        )

    def test_zip_file_still_exists(self):
        """The original es_MX.zip file must still exist (not deleted)."""
        zip_path = "/home/user/translations/es_MX.zip"
        assert os.path.isfile(zip_path), (
            f"Zip file {zip_path} no longer exists. "
            "The original zip file should remain intact after extraction."
        )

    def test_zip_file_still_valid(self):
        """The original es_MX.zip file must still be a valid zip archive."""
        zip_path = "/home/user/translations/es_MX.zip"
        assert zipfile.is_zipfile(zip_path), (
            f"{zip_path} is no longer a valid zip archive. "
            "The original zip file should not be modified."
        )

    def test_messages_properties_exists(self):
        """messages.properties must exist in the extracted directory."""
        file_path = "/home/user/translations/es_MX/messages.properties"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "This file should be extracted from the zip archive."
        )

    def test_errors_properties_exists(self):
        """errors.properties must exist in the extracted directory."""
        file_path = "/home/user/translations/es_MX/errors.properties"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "This file should be extracted from the zip archive."
        )

    def test_ui_labels_properties_exists(self):
        """ui_labels.properties must exist in the extracted directory."""
        file_path = "/home/user/translations/es_MX/ui_labels.properties"
        assert os.path.isfile(file_path), (
            f"File {file_path} does not exist. "
            "This file should be extracted from the zip archive."
        )

    def test_messages_properties_readable(self):
        """messages.properties must be readable by the user."""
        file_path = "/home/user/translations/es_MX/messages.properties"
        assert os.access(file_path, os.R_OK), (
            f"File {file_path} is not readable. "
            "The extracted file must have read permissions."
        )

    def test_errors_properties_readable(self):
        """errors.properties must be readable by the user."""
        file_path = "/home/user/translations/es_MX/errors.properties"
        assert os.access(file_path, os.R_OK), (
            f"File {file_path} is not readable. "
            "The extracted file must have read permissions."
        )

    def test_ui_labels_properties_readable(self):
        """ui_labels.properties must be readable by the user."""
        file_path = "/home/user/translations/es_MX/ui_labels.properties"
        assert os.access(file_path, os.R_OK), (
            f"File {file_path} is not readable. "
            "The extracted file must have read permissions."
        )

    def test_messages_properties_not_empty(self):
        """messages.properties must have content (size > 0)."""
        file_path = "/home/user/translations/es_MX/messages.properties"
        size = os.path.getsize(file_path)
        assert size > 0, (
            f"File {file_path} is empty (size=0). "
            "The file must be properly extracted with content."
        )

    def test_errors_properties_not_empty(self):
        """errors.properties must have content (size > 0)."""
        file_path = "/home/user/translations/es_MX/errors.properties"
        size = os.path.getsize(file_path)
        assert size > 0, (
            f"File {file_path} is empty (size=0). "
            "The file must be properly extracted with content."
        )

    def test_ui_labels_properties_not_empty(self):
        """ui_labels.properties must have content (size > 0)."""
        file_path = "/home/user/translations/es_MX/ui_labels.properties"
        size = os.path.getsize(file_path)
        assert size > 0, (
            f"File {file_path} is empty (size=0). "
            "The file must be properly extracted with content."
        )

    def test_messages_properties_is_property_format(self):
        """messages.properties must contain at least one line with '=' (property format)."""
        file_path = "/home/user/translations/es_MX/messages.properties"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        has_property_line = any('=' in line for line in content.split('\n') 
                                if line.strip() and not line.strip().startswith('#'))
        assert has_property_line, (
            f"File {file_path} does not appear to be in property file format. "
            "Expected at least one line with '=' character (key=value format)."
        )

    def test_errors_properties_is_property_format(self):
        """errors.properties must contain at least one line with '=' (property format)."""
        file_path = "/home/user/translations/es_MX/errors.properties"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        has_property_line = any('=' in line for line in content.split('\n') 
                                if line.strip() and not line.strip().startswith('#'))
        assert has_property_line, (
            f"File {file_path} does not appear to be in property file format. "
            "Expected at least one line with '=' character (key=value format)."
        )

    def test_ui_labels_properties_is_property_format(self):
        """ui_labels.properties must contain at least one line with '=' (property format)."""
        file_path = "/home/user/translations/es_MX/ui_labels.properties"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        has_property_line = any('=' in line for line in content.split('\n') 
                                if line.strip() and not line.strip().startswith('#'))
        assert has_property_line, (
            f"File {file_path} does not appear to be in property file format. "
            "Expected at least one line with '=' character (key=value format)."
        )

    def test_messages_properties_matches_zip_content(self):
        """messages.properties content must match what's in the zip archive."""
        zip_path = "/home/user/translations/es_MX.zip"
        file_path = "/home/user/translations/es_MX/messages.properties"

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zip_content = zf.read("messages.properties")

        with open(file_path, 'rb') as f:
            extracted_content = f.read()

        assert extracted_content == zip_content, (
            f"Content of {file_path} does not match the content in the zip archive. "
            "The file must be properly extracted from the zip."
        )

    def test_errors_properties_matches_zip_content(self):
        """errors.properties content must match what's in the zip archive."""
        zip_path = "/home/user/translations/es_MX.zip"
        file_path = "/home/user/translations/es_MX/errors.properties"

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zip_content = zf.read("errors.properties")

        with open(file_path, 'rb') as f:
            extracted_content = f.read()

        assert extracted_content == zip_content, (
            f"Content of {file_path} does not match the content in the zip archive. "
            "The file must be properly extracted from the zip."
        )

    def test_ui_labels_properties_matches_zip_content(self):
        """ui_labels.properties content must match what's in the zip archive."""
        zip_path = "/home/user/translations/es_MX.zip"
        file_path = "/home/user/translations/es_MX/ui_labels.properties"

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zip_content = zf.read("ui_labels.properties")

        with open(file_path, 'rb') as f:
            extracted_content = f.read()

        assert extracted_content == zip_content, (
            f"Content of {file_path} does not match the content in the zip archive. "
            "The file must be properly extracted from the zip."
        )
