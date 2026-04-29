# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of recreating a Python virtual environment.
"""

import os
import subprocess
import sys

import pytest


class TestWebappDirectoryExists:
    """Verify /home/user/webapp/ exists and is writable."""

    def test_webapp_directory_exists(self):
        webapp_path = "/home/user/webapp"
        assert os.path.exists(webapp_path), (
            f"Directory {webapp_path} does not exist. "
            "The webapp directory must exist before creating the venv."
        )

    def test_webapp_is_directory(self):
        webapp_path = "/home/user/webapp"
        assert os.path.isdir(webapp_path), (
            f"{webapp_path} exists but is not a directory. "
            "Expected a directory for the webapp."
        )

    def test_webapp_is_writable(self):
        webapp_path = "/home/user/webapp"
        assert os.access(webapp_path, os.W_OK), (
            f"Directory {webapp_path} is not writable. "
            "The webapp directory must be writable to create a venv."
        )


class TestRequirementsFile:
    """Verify requirements.txt exists with correct contents."""

    def test_requirements_file_exists(self):
        req_path = "/home/user/webapp/requirements.txt"
        assert os.path.exists(req_path), (
            f"File {req_path} does not exist. "
            "The requirements.txt file must exist with flask and gunicorn versions."
        )

    def test_requirements_file_is_file(self):
        req_path = "/home/user/webapp/requirements.txt"
        assert os.path.isfile(req_path), (
            f"{req_path} exists but is not a regular file."
        )

    def test_requirements_contains_flask_version(self):
        req_path = "/home/user/webapp/requirements.txt"
        with open(req_path, "r") as f:
            contents = f.read()
        assert "flask==2.3.3" in contents.lower(), (
            f"requirements.txt does not contain 'flask==2.3.3'. "
            f"Contents: {contents}"
        )

    def test_requirements_contains_gunicorn_version(self):
        req_path = "/home/user/webapp/requirements.txt"
        with open(req_path, "r") as f:
            contents = f.read()
        assert "gunicorn==21.2.0" in contents.lower(), (
            f"requirements.txt does not contain 'gunicorn==21.2.0'. "
            f"Contents: {contents}"
        )


class TestVenvDoesNotExist:
    """Verify the old venv does NOT exist (was deleted)."""

    def test_venv_directory_does_not_exist(self):
        venv_path = "/home/user/webapp/venv"
        assert not os.path.exists(venv_path), (
            f"Directory {venv_path} already exists. "
            "The initial state requires the venv to be deleted/missing."
        )


class TestPythonAvailable:
    """Verify Python 3.10+ is available with venv module."""

    def test_python3_available(self):
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "python3 is not available or not working. "
            f"Error: {result.stderr}"
        )

    def test_python3_version_sufficient(self):
        result = subprocess.run(
            ["python3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to get Python version: {result.stderr}"
        version_str = result.stdout.strip()
        major, minor = map(int, version_str.split("."))
        assert (major, minor) >= (3, 10), (
            f"Python version {version_str} is less than required 3.10. "
            "Python 3.10+ is required."
        )

    def test_venv_module_available(self):
        result = subprocess.run(
            ["python3", "-c", "import venv"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Python venv module is not available. "
            "python3-venv package must be installed. "
            f"Error: {result.stderr}"
        )


class TestPipAvailable:
    """Verify pip is available."""

    def test_pip_available(self):
        # Try pip3 first, then pip
        result = subprocess.run(
            ["python3", "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "pip is not available via 'python3 -m pip'. "
            "pip must be installed to install requirements. "
            f"Error: {result.stderr}"
        )
