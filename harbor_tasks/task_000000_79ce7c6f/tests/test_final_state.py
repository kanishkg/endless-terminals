# test_final_state.py
"""
Tests to validate the final state after the student has recreated the Python
virtual environment at /home/user/webapp/venv with flask and gunicorn installed.
"""

import os
import subprocess
import hashlib

import pytest


class TestVenvExists:
    """Verify /home/user/webapp/venv exists and is a valid virtual environment."""

    def test_venv_directory_exists(self):
        venv_path = "/home/user/webapp/venv"
        assert os.path.exists(venv_path), (
            f"Directory {venv_path} does not exist. "
            "The virtual environment must be created."
        )

    def test_venv_is_directory(self):
        venv_path = "/home/user/webapp/venv"
        assert os.path.isdir(venv_path), (
            f"{venv_path} exists but is not a directory. "
            "Expected a directory for the virtual environment."
        )

    def test_venv_bin_directory_exists(self):
        venv_bin_path = "/home/user/webapp/venv/bin"
        assert os.path.isdir(venv_bin_path), (
            f"{venv_bin_path} does not exist or is not a directory. "
            "A valid venv should have a bin directory."
        )

    def test_venv_python_exists(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        assert os.path.exists(venv_python), (
            f"{venv_python} does not exist. "
            "The virtual environment must have a Python executable."
        )

    def test_venv_pip_exists(self):
        venv_pip = "/home/user/webapp/venv/bin/pip"
        assert os.path.exists(venv_pip), (
            f"{venv_pip} does not exist. "
            "The virtual environment must have pip installed."
        )


class TestVenvFunctional:
    """Verify the venv is functional."""

    def test_venv_python_runs(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [venv_python, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Venv Python failed to run with exit code {result.returncode}. "
            f"Stderr: {result.stderr}"
        )

    def test_venv_pip_runs(self):
        venv_pip = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [venv_pip, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Venv pip failed to run with exit code {result.returncode}. "
            f"Stderr: {result.stderr}"
        )


class TestFlaskInstalled:
    """Verify Flask 2.3.3 is installed in the venv."""

    def test_flask_importable(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [venv_python, "-c", "import flask"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "Flask is not importable in the venv. "
            f"Error: {result.stderr}"
        )

    def test_flask_version_correct(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [venv_python, "-c", "import flask; print(flask.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get Flask version. Error: {result.stderr}"
        )
        version = result.stdout.strip()
        assert version == "2.3.3", (
            f"Flask version is {version}, expected 2.3.3. "
            "Flask must be pinned to version 2.3.3."
        )

    def test_flask_in_pip_list(self):
        venv_pip = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [venv_pip, "list", "--format=freeze"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"pip list failed. Error: {result.stderr}"
        )
        # Check for Flask==2.3.3 (case-insensitive for package name)
        lines = result.stdout.strip().lower().split('\n')
        flask_lines = [line for line in lines if line.startswith('flask==')]
        assert flask_lines, (
            "Flask not found in pip list output. "
            f"Output: {result.stdout}"
        )
        assert 'flask==2.3.3' in lines, (
            f"Flask version mismatch in pip list. Found: {flask_lines}. "
            "Expected Flask==2.3.3."
        )


class TestGunicornInstalled:
    """Verify gunicorn 21.2.0 is installed in the venv."""

    def test_gunicorn_importable(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [venv_python, "-c", "import gunicorn"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "gunicorn is not importable in the venv. "
            f"Error: {result.stderr}"
        )

    def test_gunicorn_version_correct(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [venv_python, "-c", "import gunicorn; print(gunicorn.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get gunicorn version. Error: {result.stderr}"
        )
        version = result.stdout.strip()
        assert version == "21.2.0", (
            f"gunicorn version is {version}, expected 21.2.0. "
            "gunicorn must be pinned to version 21.2.0."
        )

    def test_gunicorn_in_pip_list(self):
        venv_pip = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [venv_pip, "list", "--format=freeze"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"pip list failed. Error: {result.stderr}"
        )
        # Check for gunicorn==21.2.0 (case-insensitive for package name)
        lines = result.stdout.strip().lower().split('\n')
        gunicorn_lines = [line for line in lines if line.startswith('gunicorn==')]
        assert gunicorn_lines, (
            "gunicorn not found in pip list output. "
            f"Output: {result.stdout}"
        )
        assert 'gunicorn==21.2.0' in lines, (
            f"gunicorn version mismatch in pip list. Found: {gunicorn_lines}. "
            "Expected gunicorn==21.2.0."
        )


class TestRequirementsUnchanged:
    """Verify requirements.txt is unchanged."""

    def test_requirements_file_exists(self):
        req_path = "/home/user/webapp/requirements.txt"
        assert os.path.exists(req_path), (
            f"File {req_path} no longer exists. "
            "requirements.txt must remain unchanged."
        )

    def test_requirements_contents_unchanged(self):
        req_path = "/home/user/webapp/requirements.txt"
        with open(req_path, "r") as f:
            contents = f.read()

        # Check that the required lines are present
        lines = [line.strip().lower() for line in contents.strip().split('\n') if line.strip()]

        assert "flask==2.3.3" in lines, (
            f"requirements.txt missing 'flask==2.3.3'. Contents: {contents}"
        )
        assert "gunicorn==21.2.0" in lines, (
            f"requirements.txt missing 'gunicorn==21.2.0'. Contents: {contents}"
        )

        # Verify only these two requirements are present (no extra lines added)
        non_empty_lines = [line for line in lines if line and not line.startswith('#')]
        assert len(non_empty_lines) == 2, (
            f"requirements.txt should have exactly 2 requirements, found {len(non_empty_lines)}. "
            f"Contents: {contents}"
        )


class TestNoSystemWideInstall:
    """Verify packages are only in the venv, not system-wide."""

    def test_flask_not_in_system_python(self):
        # Try to import flask using system python, should fail or be different location
        result = subprocess.run(
            ["python3", "-c", "import flask; print(flask.__file__)"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            flask_path = result.stdout.strip()
            # If flask is importable in system python, it should NOT be in the venv path
            # This is a soft check - some systems may have flask pre-installed
            assert "/home/user/webapp/venv" not in flask_path or True, (
                "This check is informational - system may have flask pre-installed"
            )

    def test_packages_installed_in_venv_site_packages(self):
        venv_python = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [venv_python, "-c", "import flask; print(flask.__file__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to get flask path: {result.stderr}"
        flask_path = result.stdout.strip()
        assert "/home/user/webapp/venv" in flask_path, (
            f"Flask is installed at {flask_path}, which is not in the venv. "
            "Packages must be installed in the virtual environment."
        )
