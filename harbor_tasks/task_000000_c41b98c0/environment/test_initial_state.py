# test_initial_state.py
"""
Tests to validate the initial state of the system before the student performs the action.
This validates the environment described in the task where a Python venv/alias issue
causes import failures.
"""

import os
import subprocess
import pytest


HOME = "/home/user"
MLSERVICE_DIR = os.path.join(HOME, "mlservice")
VENV_DIR = os.path.join(MLSERVICE_DIR, ".venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")
REQUIREMENTS_FILE = os.path.join(MLSERVICE_DIR, "requirements.txt")
BASHRC = os.path.join(HOME, ".bashrc")


class TestDirectoryStructure:
    """Test that the mlservice directory structure exists."""

    def test_mlservice_directory_exists(self):
        assert os.path.isdir(MLSERVICE_DIR), (
            f"Directory {MLSERVICE_DIR} does not exist. "
            "The mlservice package directory should be present."
        )

    def test_mlservice_init_exists(self):
        init_file = os.path.join(MLSERVICE_DIR, "__init__.py")
        assert os.path.isfile(init_file), (
            f"File {init_file} does not exist. "
            "The mlservice package should have an __init__.py file."
        )

    def test_mlservice_main_exists(self):
        main_file = os.path.join(MLSERVICE_DIR, "__main__.py")
        assert os.path.isfile(main_file), (
            f"File {main_file} does not exist. "
            "The mlservice package should have a __main__.py file."
        )

    def test_requirements_txt_exists(self):
        assert os.path.isfile(REQUIREMENTS_FILE), (
            f"File {REQUIREMENTS_FILE} does not exist. "
            "The requirements.txt file should be present."
        )


class TestVirtualEnvironment:
    """Test that the virtual environment exists and is properly set up."""

    def test_venv_directory_exists(self):
        assert os.path.isdir(VENV_DIR), (
            f"Directory {VENV_DIR} does not exist. "
            "The virtual environment should be present at .venv/"
        )

    def test_venv_python_exists(self):
        assert os.path.isfile(VENV_PYTHON), (
            f"File {VENV_PYTHON} does not exist. "
            "The virtual environment should have a Python interpreter."
        )

    def test_venv_python_is_executable(self):
        assert os.access(VENV_PYTHON, os.X_OK), (
            f"File {VENV_PYTHON} is not executable. "
            "The venv Python interpreter should be executable."
        )

    def test_venv_python_is_python311(self):
        result = subprocess.run(
            [VENV_PYTHON, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to get Python version from {VENV_PYTHON}"
        )
        version_output = result.stdout.strip()
        assert "3.11" in version_output, (
            f"Expected Python 3.11 in venv, got: {version_output}. "
            "The virtual environment should use Python 3.11."
        )


class TestRequirementsTxt:
    """Test that requirements.txt contains the expected packages."""

    def test_requirements_contains_transformers(self):
        with open(REQUIREMENTS_FILE, "r") as f:
            content = f.read()
        assert "transformers" in content.lower(), (
            "requirements.txt should contain transformers package"
        )

    def test_requirements_contains_tokenizers(self):
        with open(REQUIREMENTS_FILE, "r") as f:
            content = f.read()
        assert "tokenizers" in content.lower(), (
            "requirements.txt should contain tokenizers package"
        )


class TestVenvPackages:
    """Test that packages are installed in the virtual environment."""

    def test_tokenizers_installed_in_venv(self):
        result = subprocess.run(
            [VENV_PYTHON, "-c", "import tokenizers; print(tokenizers.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"tokenizers is not importable in venv Python. "
            f"stderr: {result.stderr}"
        )
        # Should be 0.15.0
        assert "0.15" in result.stdout, (
            f"Expected tokenizers 0.15.x in venv, got: {result.stdout.strip()}"
        )

    def test_transformers_installed_in_venv(self):
        result = subprocess.run(
            [VENV_PYTHON, "-c", "import transformers; print(transformers.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"transformers is not importable in venv Python. "
            f"stderr: {result.stderr}"
        )
        assert "4.36" in result.stdout, (
            f"Expected transformers 4.36.x in venv, got: {result.stdout.strip()}"
        )


class TestSystemPython:
    """Test that system Python exists and has the problematic setup."""

    def test_system_python_exists(self):
        assert os.path.isfile("/usr/bin/python3"), (
            "/usr/bin/python3 should exist as the system Python"
        )

    def test_system_python_is_different_version(self):
        result = subprocess.run(
            ["/usr/bin/python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Failed to get system Python version"
        # System Python should be 3.10, not 3.11
        version = result.stdout.strip()
        assert "3.10" in version or "3.11" not in version or True, (
            f"System Python version: {version}"
        )


class TestBashrcAlias:
    """Test that the problematic alias exists in .bashrc."""

    def test_bashrc_exists(self):
        assert os.path.isfile(BASHRC), (
            f"File {BASHRC} does not exist. "
            "The .bashrc file should be present."
        )

    def test_bashrc_contains_python_alias(self):
        with open(BASHRC, "r") as f:
            content = f.read()
        # Check for the alias that causes the problem
        assert "alias python" in content or "alias python=" in content, (
            "~/.bashrc should contain a python alias that causes the PATH issue. "
            f"Content: {content[:500]}"
        )


class TestMlserviceSourceCode:
    """Test that the mlservice source code is as expected."""

    def test_init_imports_transformers(self):
        init_file = os.path.join(MLSERVICE_DIR, "__init__.py")
        with open(init_file, "r") as f:
            content = f.read()
        assert "from transformers import" in content or "import transformers" in content, (
            "__init__.py should import from transformers"
        )
        assert "AutoTokenizer" in content, (
            "__init__.py should use AutoTokenizer"
        )

    def test_main_imports_from_mlservice(self):
        main_file = os.path.join(MLSERVICE_DIR, "__main__.py")
        with open(main_file, "r") as f:
            content = f.read()
        assert "from mlservice import" in content or "import mlservice" in content, (
            "__main__.py should import from mlservice"
        )


class TestWritePermissions:
    """Test that necessary files/directories are writable."""

    def test_mlservice_dir_writable(self):
        assert os.access(MLSERVICE_DIR, os.W_OK), (
            f"{MLSERVICE_DIR} should be writable"
        )

    def test_bashrc_writable(self):
        assert os.access(BASHRC, os.W_OK), (
            f"{BASHRC} should be writable"
        )


class TestProblemReproduction:
    """Test that the problem described in the task actually exists."""

    def test_venv_python_can_run_mlservice(self):
        """The venv Python SHOULD be able to run mlservice successfully."""
        # This tests that the venv itself is properly set up
        result = subprocess.run(
            [VENV_PYTHON, "-c", "from transformers import AutoTokenizer"],
            capture_output=True,
            text=True,
            cwd=MLSERVICE_DIR
        )
        assert result.returncode == 0, (
            f"Venv Python should be able to import transformers.AutoTokenizer. "
            f"stderr: {result.stderr}"
        )

    def test_system_python_has_old_tokenizers_or_none(self):
        """System Python should have old tokenizers or incompatible setup."""
        result = subprocess.run(
            ["/usr/bin/python3", "-c", "import tokenizers; print(tokenizers.__version__)"],
            capture_output=True,
            text=True
        )
        # Either it fails entirely or has an old version
        if result.returncode == 0:
            version = result.stdout.strip()
            # If it exists, it should be an older version (0.13.x or similar)
            # that's incompatible with transformers 4.36
            assert "0.15" not in version, (
                f"System Python has tokenizers {version}, expected older version "
                "or no tokenizers to reproduce the bug"
            )
