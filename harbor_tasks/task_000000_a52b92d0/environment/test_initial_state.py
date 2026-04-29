# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of generating requirements-lock.txt for /home/user/webapp.
"""

import os
import subprocess
import sys
import pytest


class TestWebappDirectoryExists:
    """Verify /home/user/webapp directory exists and is writable."""

    def test_webapp_directory_exists(self):
        webapp_path = "/home/user/webapp"
        assert os.path.exists(webapp_path), f"Directory {webapp_path} does not exist"
        assert os.path.isdir(webapp_path), f"{webapp_path} is not a directory"

    def test_webapp_directory_is_writable(self):
        webapp_path = "/home/user/webapp"
        assert os.access(webapp_path, os.W_OK), f"Directory {webapp_path} is not writable"


class TestRequirementsTxtExists:
    """Verify requirements.txt exists with unpinned packages."""

    def test_requirements_txt_exists(self):
        req_path = "/home/user/webapp/requirements.txt"
        assert os.path.exists(req_path), f"File {req_path} does not exist"
        assert os.path.isfile(req_path), f"{req_path} is not a file"

    def test_requirements_txt_contains_unpinned_packages(self):
        req_path = "/home/user/webapp/requirements.txt"
        with open(req_path, "r") as f:
            content = f.read()

        lines = [line.strip().lower() for line in content.splitlines() if line.strip()]

        # Check that flask, requests, click are present (unpinned)
        assert "flask" in lines, "requirements.txt should contain 'flask' (unpinned)"
        assert "requests" in lines, "requirements.txt should contain 'requests' (unpinned)"
        assert "click" in lines, "requirements.txt should contain 'click' (unpinned)"

        # Verify they are unpinned (no == in the lines)
        for line in lines:
            if line in ["flask", "requests", "click"]:
                # These should be unpinned
                assert "==" not in line, f"Package '{line}' should be unpinned in requirements.txt"


class TestVirtualenvExists:
    """Verify the virtualenv at /home/user/webapp/venv exists and is functional."""

    def test_venv_directory_exists(self):
        venv_path = "/home/user/webapp/venv"
        assert os.path.exists(venv_path), f"Virtualenv directory {venv_path} does not exist"
        assert os.path.isdir(venv_path), f"{venv_path} is not a directory"

    def test_venv_python_exists(self):
        python_path = "/home/user/webapp/venv/bin/python"
        assert os.path.exists(python_path), f"Python executable {python_path} does not exist"
        assert os.access(python_path, os.X_OK), f"{python_path} is not executable"

    def test_venv_pip_exists(self):
        pip_path = "/home/user/webapp/venv/bin/pip"
        assert os.path.exists(pip_path), f"pip executable {pip_path} does not exist"
        assert os.access(pip_path, os.X_OK), f"{pip_path} is not executable"

    def test_venv_is_functional(self):
        """Test that the venv python can be invoked."""
        python_path = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Virtualenv python failed to run: {result.stderr}"


class TestPackagesInstalled:
    """Verify the required packages are installed in the virtualenv with correct versions."""

    def test_flask_installed_with_correct_version(self):
        pip_path = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [pip_path, "show", "flask"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "flask is not installed in the virtualenv"
        assert "Version: 2.3.2" in result.stdout, f"flask should be version 2.3.2, got: {result.stdout}"

    def test_requests_installed_with_correct_version(self):
        pip_path = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [pip_path, "show", "requests"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "requests is not installed in the virtualenv"
        assert "Version: 2.31.0" in result.stdout, f"requests should be version 2.31.0, got: {result.stdout}"

    def test_click_installed_with_correct_version(self):
        pip_path = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [pip_path, "show", "click"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "click is not installed in the virtualenv"
        assert "Version: 8.1.3" in result.stdout, f"click should be version 8.1.3, got: {result.stdout}"

    def test_dependencies_installed(self):
        """Verify that transitive dependencies are also installed."""
        pip_path = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [pip_path, "freeze"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"pip freeze failed: {result.stderr}"

        installed = result.stdout.lower()

        # Check for common dependencies
        expected_deps = ["werkzeug", "jinja2", "markupsafe", "itsdangerous", "certifi", "urllib3"]
        for dep in expected_deps:
            assert dep in installed, f"Expected dependency '{dep}' not found in virtualenv"


class TestPythonAvailable:
    """Verify Python 3.10+ is available."""

    def test_python_version(self):
        python_path = "/home/user/webapp/venv/bin/python"
        result = subprocess.run(
            [python_path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to get Python version: {result.stderr}"

        version = result.stdout.strip()
        major, minor = map(int, version.split("."))
        assert major >= 3 and minor >= 10, f"Python version should be 3.10+, got {version}"


class TestRequirementsLockDoesNotExist:
    """Verify that requirements-lock.txt does NOT exist yet (student needs to create it)."""

    def test_requirements_lock_does_not_exist(self):
        lock_path = "/home/user/webapp/requirements-lock.txt"
        assert not os.path.exists(lock_path), (
            f"File {lock_path} already exists - it should not exist before the task is performed"
        )
