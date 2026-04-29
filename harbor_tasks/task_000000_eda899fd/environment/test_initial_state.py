# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the task of fixing the pip wheel build issue in /home/user/myapp.
"""

import os
import subprocess
import sys
import pytest


MYAPP_DIR = "/home/user/myapp"
SRC_DIR = os.path.join(MYAPP_DIR, "src")
MYAPP_PKG_DIR = os.path.join(SRC_DIR, "myapp")


class TestDirectoryStructure:
    """Test that the required directory structure exists."""

    def test_myapp_directory_exists(self):
        """The /home/user/myapp directory must exist."""
        assert os.path.isdir(MYAPP_DIR), f"Directory {MYAPP_DIR} does not exist"

    def test_src_directory_exists(self):
        """The src directory must exist inside myapp."""
        assert os.path.isdir(SRC_DIR), f"Directory {SRC_DIR} does not exist"

    def test_myapp_package_directory_exists(self):
        """The src/myapp package directory must exist."""
        assert os.path.isdir(MYAPP_PKG_DIR), f"Directory {MYAPP_PKG_DIR} does not exist"

    def test_myapp_directory_is_writable(self):
        """The /home/user/myapp directory must be writable."""
        assert os.access(MYAPP_DIR, os.W_OK), f"Directory {MYAPP_DIR} is not writable"


class TestRequiredFiles:
    """Test that required files exist."""

    def test_pyproject_toml_exists(self):
        """pyproject.toml must exist in the project root."""
        pyproject_path = os.path.join(MYAPP_DIR, "pyproject.toml")
        assert os.path.isfile(pyproject_path), f"File {pyproject_path} does not exist"

    def test_init_py_exists(self):
        """src/myapp/__init__.py must exist."""
        init_path = os.path.join(MYAPP_PKG_DIR, "__init__.py")
        assert os.path.isfile(init_path), f"File {init_path} does not exist"

    def test_core_py_exists(self):
        """src/myapp/core.py must exist."""
        core_path = os.path.join(MYAPP_PKG_DIR, "core.py")
        assert os.path.isfile(core_path), f"File {core_path} does not exist"

    def test_constraints_txt_exists(self):
        """constraints.txt must exist (even if empty)."""
        constraints_path = os.path.join(MYAPP_DIR, "constraints.txt")
        assert os.path.isfile(constraints_path), f"File {constraints_path} does not exist"

    def test_requirements_dev_txt_exists(self):
        """requirements-dev.txt must exist."""
        req_dev_path = os.path.join(MYAPP_DIR, "requirements-dev.txt")
        assert os.path.isfile(req_dev_path), f"File {req_dev_path} does not exist"


class TestPyprojectTomlContent:
    """Test the content of pyproject.toml matches expected initial state."""

    @pytest.fixture
    def pyproject_content(self):
        """Read the pyproject.toml content."""
        pyproject_path = os.path.join(MYAPP_DIR, "pyproject.toml")
        with open(pyproject_path, "r") as f:
            return f.read()

    def test_uses_setuptools_backend(self, pyproject_content):
        """pyproject.toml must use setuptools as build backend."""
        assert "setuptools.build_meta" in pyproject_content, \
            "pyproject.toml must use setuptools.build_meta as build backend"

    def test_project_name_is_myapp(self, pyproject_content):
        """Project name must be 'myapp'."""
        assert 'name = "myapp"' in pyproject_content, \
            "Project name must be 'myapp'"

    def test_version_is_0_1_0(self, pyproject_content):
        """Project version must be '0.1.0'."""
        assert 'version = "0.1.0"' in pyproject_content, \
            "Project version must be '0.1.0'"

    def test_has_requests_dependency(self, pyproject_content):
        """Base dependencies must include requests."""
        assert "requests>=" in pyproject_content, \
            "Base dependencies must include requests"

    def test_has_boto3_dependency(self, pyproject_content):
        """Base dependencies must include boto3."""
        assert "boto3>=" in pyproject_content, \
            "Base dependencies must include boto3"

    def test_has_dev_extra(self, pyproject_content):
        """Must have a [dev] optional dependency group."""
        assert "[project.optional-dependencies]" in pyproject_content, \
            "Must have optional-dependencies section"
        assert "dev = [" in pyproject_content, \
            "Must have a 'dev' extra defined"

    def test_dev_extra_has_pytest(self, pyproject_content):
        """The [dev] extra must include pytest."""
        assert "pytest>=" in pyproject_content, \
            "The [dev] extra must include pytest"

    def test_dev_extra_has_moto(self, pyproject_content):
        """The [dev] extra must include moto."""
        assert "moto>=" in pyproject_content, \
            "The [dev] extra must include moto"

    def test_dev_extra_has_requests_mock(self, pyproject_content):
        """The [dev] extra must include requests-mock."""
        assert "requests-mock>=" in pyproject_content, \
            "The [dev] extra must include requests-mock"

    def test_dev_extra_has_urllib3_constraint(self, pyproject_content):
        """The [dev] extra must have the problematic urllib3>=2.0.0 constraint."""
        assert "urllib3>=2.0.0" in pyproject_content, \
            "The [dev] extra must have urllib3>=2.0.0 (this is the bug to fix)"


class TestInitPyContent:
    """Test the content of __init__.py."""

    def test_has_version(self):
        """__init__.py must define __version__ = '0.1.0'."""
        init_path = os.path.join(MYAPP_PKG_DIR, "__init__.py")
        with open(init_path, "r") as f:
            content = f.read()
        assert '__version__ = "0.1.0"' in content or "__version__ = '0.1.0'" in content, \
            "__init__.py must define __version__ = '0.1.0'"


class TestCorePyContent:
    """Test the content of core.py."""

    def test_has_main_function(self):
        """core.py must have a main function."""
        core_path = os.path.join(MYAPP_PKG_DIR, "core.py")
        with open(core_path, "r") as f:
            content = f.read()
        assert "def main" in content, \
            "core.py must define a 'main' function"


class TestPythonEnvironment:
    """Test that the Python environment is properly configured."""

    def test_python_version(self):
        """Python 3.10.x must be available."""
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True
        )
        version_output = result.stdout.strip()
        assert "3.10" in version_output or "3.11" in version_output or "3.12" in version_output, \
            f"Python 3.10+ required, got: {version_output}"

    def test_pip_available(self):
        """pip must be available."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "pip must be available"

    def test_setuptools_available(self):
        """setuptools must be available."""
        result = subprocess.run(
            [sys.executable, "-c", "import setuptools; print(setuptools.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "setuptools must be available"

    def test_wheel_available(self):
        """wheel package must be available."""
        result = subprocess.run(
            [sys.executable, "-c", "import wheel; print(wheel.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "wheel package must be available"


class TestDistDirectoryDoesNotExist:
    """Verify that dist/ directory doesn't exist yet (or is empty)."""

    def test_dist_directory_state(self):
        """dist/ directory should not contain wheel files initially."""
        dist_dir = os.path.join(MYAPP_DIR, "dist")
        if os.path.exists(dist_dir):
            whl_files = [f for f in os.listdir(dist_dir) if f.endswith('.whl')]
            # It's okay if dist exists but has no wheels
            assert len(whl_files) == 0, \
                f"dist/ directory should not contain wheel files initially, found: {whl_files}"
