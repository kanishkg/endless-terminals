# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the deployment archive creation task.
"""

import os
import pytest


class TestSourceDirectoryStructure:
    """Test that the source directory structure exists correctly."""

    def test_app_release_directory_exists(self):
        """The main app release directory must exist."""
        app_dir = "/home/user/app_release_v2.3.1"
        assert os.path.isdir(app_dir), (
            f"Source directory '{app_dir}' does not exist. "
            "This directory should contain the application files to be archived."
        )

    def test_lib_subdirectory_exists(self):
        """The lib subdirectory must exist within the app release directory."""
        lib_dir = "/home/user/app_release_v2.3.1/lib"
        assert os.path.isdir(lib_dir), (
            f"Subdirectory '{lib_dir}' does not exist. "
            "This directory should contain helper modules (utils.py, database.py)."
        )

    def test_deployments_directory_exists(self):
        """The deployments directory must exist for output files."""
        deployments_dir = "/home/user/deployments"
        assert os.path.isdir(deployments_dir), (
            f"Deployments directory '{deployments_dir}' does not exist. "
            "This directory is needed to store the output archive and log file."
        )


class TestApplicationFilesExist:
    """Test that all required application files exist in the source directory."""

    def test_main_py_exists(self):
        """main.py must exist in the app release directory."""
        filepath = "/home/user/app_release_v2.3.1/main.py"
        assert os.path.isfile(filepath), (
            f"File '{filepath}' does not exist. "
            "This is the main application script that needs to be packaged."
        )

    def test_config_json_exists(self):
        """config.json must exist in the app release directory."""
        filepath = "/home/user/app_release_v2.3.1/config.json"
        assert os.path.isfile(filepath), (
            f"File '{filepath}' does not exist. "
            "This is the configuration file that needs to be packaged."
        )

    def test_requirements_txt_exists(self):
        """requirements.txt must exist in the app release directory."""
        filepath = "/home/user/app_release_v2.3.1/requirements.txt"
        assert os.path.isfile(filepath), (
            f"File '{filepath}' does not exist. "
            "This is the Python dependencies file that needs to be packaged."
        )

    def test_readme_md_exists(self):
        """README.md must exist in the app release directory."""
        filepath = "/home/user/app_release_v2.3.1/README.md"
        assert os.path.isfile(filepath), (
            f"File '{filepath}' does not exist. "
            "This is the documentation file that needs to be packaged."
        )

    def test_utils_py_exists(self):
        """utils.py must exist in the lib subdirectory."""
        filepath = "/home/user/app_release_v2.3.1/lib/utils.py"
        assert os.path.isfile(filepath), (
            f"File '{filepath}' does not exist. "
            "This is a helper module that needs to be packaged."
        )

    def test_database_py_exists(self):
        """database.py must exist in the lib subdirectory."""
        filepath = "/home/user/app_release_v2.3.1/lib/database.py"
        assert os.path.isfile(filepath), (
            f"File '{filepath}' does not exist. "
            "This is the database module that needs to be packaged."
        )


class TestFileContents:
    """Test that application files have content (are not empty)."""

    def test_main_py_has_content(self):
        """main.py should have content."""
        filepath = "/home/user/app_release_v2.3.1/main.py"
        if os.path.isfile(filepath):
            assert os.path.getsize(filepath) > 0, (
                f"File '{filepath}' exists but is empty. "
                "It should contain the main application script."
            )

    def test_config_json_has_content(self):
        """config.json should have content."""
        filepath = "/home/user/app_release_v2.3.1/config.json"
        if os.path.isfile(filepath):
            assert os.path.getsize(filepath) > 0, (
                f"File '{filepath}' exists but is empty. "
                "It should contain configuration settings."
            )

    def test_requirements_txt_has_content(self):
        """requirements.txt should have content."""
        filepath = "/home/user/app_release_v2.3.1/requirements.txt"
        if os.path.isfile(filepath):
            assert os.path.getsize(filepath) > 0, (
                f"File '{filepath}' exists but is empty. "
                "It should contain Python dependencies."
            )

    def test_readme_md_has_content(self):
        """README.md should have content."""
        filepath = "/home/user/app_release_v2.3.1/README.md"
        if os.path.isfile(filepath):
            assert os.path.getsize(filepath) > 0, (
                f"File '{filepath}' exists but is empty. "
                "It should contain documentation."
            )

    def test_utils_py_has_content(self):
        """utils.py should have content."""
        filepath = "/home/user/app_release_v2.3.1/lib/utils.py"
        if os.path.isfile(filepath):
            assert os.path.getsize(filepath) > 0, (
                f"File '{filepath}' exists but is empty. "
                "It should contain utility functions."
            )

    def test_database_py_has_content(self):
        """database.py should have content."""
        filepath = "/home/user/app_release_v2.3.1/lib/database.py"
        if os.path.isfile(filepath):
            assert os.path.getsize(filepath) > 0, (
                f"File '{filepath}' exists but is empty. "
                "It should contain database connection code."
            )


class TestPermissions:
    """Test that necessary directories have write permissions."""

    def test_deployments_directory_is_writable(self):
        """The deployments directory must be writable to create output files."""
        deployments_dir = "/home/user/deployments"
        if os.path.isdir(deployments_dir):
            assert os.access(deployments_dir, os.W_OK), (
                f"Directory '{deployments_dir}' is not writable. "
                "Write permission is needed to create the archive and log file."
            )

    def test_source_directory_is_readable(self):
        """The source directory must be readable to create the archive."""
        app_dir = "/home/user/app_release_v2.3.1"
        if os.path.isdir(app_dir):
            assert os.access(app_dir, os.R_OK), (
                f"Directory '{app_dir}' is not readable. "
                "Read permission is needed to archive the application files."
            )


class TestFileCount:
    """Test that the correct number of files exist."""

    def test_correct_number_of_files_in_app_dir(self):
        """The app release directory should contain exactly 4 files."""
        app_dir = "/home/user/app_release_v2.3.1"
        if os.path.isdir(app_dir):
            files = [f for f in os.listdir(app_dir) 
                     if os.path.isfile(os.path.join(app_dir, f))]
            expected_files = {"main.py", "config.json", "requirements.txt", "README.md"}
            assert set(files) == expected_files, (
                f"Expected files {expected_files} in '{app_dir}', "
                f"but found {set(files)}."
            )

    def test_correct_number_of_files_in_lib_dir(self):
        """The lib subdirectory should contain exactly 2 files."""
        lib_dir = "/home/user/app_release_v2.3.1/lib"
        if os.path.isdir(lib_dir):
            files = [f for f in os.listdir(lib_dir) 
                     if os.path.isfile(os.path.join(lib_dir, f))]
            expected_files = {"utils.py", "database.py"}
            assert set(files) == expected_files, (
                f"Expected files {expected_files} in '{lib_dir}', "
                f"but found {set(files)}."
            )
