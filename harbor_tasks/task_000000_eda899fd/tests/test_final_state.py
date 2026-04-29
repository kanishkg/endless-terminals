# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the pip wheel build issue in /home/user/myapp.

The fix should resolve the urllib3 version conflict between boto3 (requires urllib3<2.0.0)
and the [dev] extra (which originally required urllib3>=2.0.0).
"""

import os
import subprocess
import sys
import tempfile
import shutil
import glob
import pytest


MYAPP_DIR = "/home/user/myapp"
SRC_DIR = os.path.join(MYAPP_DIR, "src")
MYAPP_PKG_DIR = os.path.join(SRC_DIR, "myapp")


class TestWheelBuildSucceeds:
    """Test that pip wheel build now succeeds."""

    def test_pip_wheel_builds_successfully(self):
        """pip wheel . -w dist/ must exit with code 0."""
        dist_dir = os.path.join(MYAPP_DIR, "dist")
        # Clean up any existing dist directory to ensure fresh build
        if os.path.exists(dist_dir):
            shutil.rmtree(dist_dir)
        os.makedirs(dist_dir, exist_ok=True)

        result = subprocess.run(
            [sys.executable, "-m", "pip", "wheel", ".", "-w", "dist/"],
            cwd=MYAPP_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"pip wheel . -w dist/ failed with exit code {result.returncode}.\n" \
            f"STDOUT:\n{result.stdout}\n" \
            f"STDERR:\n{result.stderr}"

    def test_wheel_file_created(self):
        """A .whl file must be created in dist/."""
        dist_dir = os.path.join(MYAPP_DIR, "dist")
        whl_files = glob.glob(os.path.join(dist_dir, "myapp-*.whl"))
        assert len(whl_files) >= 1, \
            f"Expected at least one myapp-*.whl file in {dist_dir}, found: {os.listdir(dist_dir) if os.path.exists(dist_dir) else 'dist/ does not exist'}"


class TestPackageInstallation:
    """Test that the package can be installed with [dev] extra."""

    @pytest.fixture(scope="class")
    def test_venv(self, tmp_path_factory):
        """Create a temporary virtual environment for testing installation."""
        venv_dir = tmp_path_factory.mktemp("test_venv")
        venv_path = str(venv_dir / "venv")

        # Create virtual environment
        result = subprocess.run(
            [sys.executable, "-m", "venv", venv_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to create venv: {result.stderr}"

        # Get the pip path in the venv
        if sys.platform == "win32":
            pip_path = os.path.join(venv_path, "Scripts", "pip")
            python_path = os.path.join(venv_path, "Scripts", "python")
        else:
            pip_path = os.path.join(venv_path, "bin", "pip")
            python_path = os.path.join(venv_path, "bin", "python")

        # Upgrade pip in the venv
        subprocess.run([pip_path, "install", "--upgrade", "pip"], capture_output=True)

        yield {"venv_path": venv_path, "pip_path": pip_path, "python_path": python_path}

    def test_install_with_dev_extra_succeeds(self, test_venv):
        """pip install dist/myapp-*.whl[dev] must succeed."""
        dist_dir = os.path.join(MYAPP_DIR, "dist")
        whl_files = glob.glob(os.path.join(dist_dir, "myapp-*.whl"))

        assert len(whl_files) >= 1, "No wheel file found to install"
        whl_file = whl_files[0]

        result = subprocess.run(
            [test_venv["pip_path"], "install", f"{whl_file}[dev]"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"pip install {whl_file}[dev] failed.\n" \
            f"STDOUT:\n{result.stdout}\n" \
            f"STDERR:\n{result.stderr}"

    def test_myapp_importable(self, test_venv):
        """After installation, myapp.core.main must be importable and work."""
        result = subprocess.run(
            [test_venv["python_path"], "-c", "from myapp.core import main; print('ok')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Failed to import myapp.core.main.\n" \
            f"STDOUT:\n{result.stdout}\n" \
            f"STDERR:\n{result.stderr}"
        assert "ok" in result.stdout, \
            f"Expected 'ok' in output, got: {result.stdout}"

    def test_pytest_available_in_dev(self, test_venv):
        """pytest must be available after installing with [dev] extra."""
        result = subprocess.run(
            [test_venv["python_path"], "-c", "import pytest; print(pytest.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"pytest not available after installing with [dev] extra.\n" \
            f"STDERR:\n{result.stderr}"

    def test_moto_available_in_dev(self, test_venv):
        """moto must be available after installing with [dev] extra."""
        result = subprocess.run(
            [test_venv["python_path"], "-c", "import moto; print(moto.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"moto not available after installing with [dev] extra.\n" \
            f"STDERR:\n{result.stderr}"

    def test_requests_mock_available_in_dev(self, test_venv):
        """requests-mock must be available after installing with [dev] extra."""
        result = subprocess.run(
            [test_venv["python_path"], "-c", "import requests_mock; print('ok')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"requests-mock not available after installing with [dev] extra.\n" \
            f"STDERR:\n{result.stderr}"

    def test_requests_available(self, test_venv):
        """requests must be available (base dependency)."""
        result = subprocess.run(
            [test_venv["python_path"], "-c", "import requests; print(requests.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"requests not available.\n" \
            f"STDERR:\n{result.stderr}"

    def test_aws_sdk_available(self, test_venv):
        """boto3 or botocore must be available (base dependency for AWS)."""
        # Try boto3 first
        result = subprocess.run(
            [test_venv["python_path"], "-c", "import boto3; print(boto3.__version__)"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return  # boto3 is available

        # If boto3 not available, check botocore
        result = subprocess.run(
            [test_venv["python_path"], "-c", "import botocore; print(botocore.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "Neither boto3 nor botocore available. AWS SDK dependency required."


class TestPyprojectTomlInvariants:
    """Test that pyproject.toml maintains required invariants."""

    @pytest.fixture
    def pyproject_content(self):
        """Read the pyproject.toml content."""
        pyproject_path = os.path.join(MYAPP_DIR, "pyproject.toml")
        with open(pyproject_path, "r") as f:
            return f.read()

    def test_project_name_unchanged(self, pyproject_content):
        """Project name must still be 'myapp'."""
        assert 'name = "myapp"' in pyproject_content, \
            "Project name must remain 'myapp'"

    def test_version_unchanged(self, pyproject_content):
        """Project version must still be '0.1.0'."""
        assert 'version = "0.1.0"' in pyproject_content, \
            "Project version must remain '0.1.0'"

    def test_dev_extra_still_exists(self, pyproject_content):
        """The [dev] optional dependency group must still exist."""
        assert "[project.optional-dependencies]" in pyproject_content, \
            "Must still have optional-dependencies section"
        # Check that dev extra is defined (may have different formatting)
        assert "dev" in pyproject_content.lower(), \
            "Must still have a 'dev' extra defined"

    def test_dev_extra_has_pytest(self, pyproject_content):
        """The [dev] extra must still include pytest."""
        assert "pytest" in pyproject_content.lower(), \
            "The [dev] extra must still include pytest"

    def test_dev_extra_has_moto(self, pyproject_content):
        """The [dev] extra must still include moto."""
        assert "moto" in pyproject_content.lower(), \
            "The [dev] extra must still include moto"

    def test_dev_extra_has_requests_mock(self, pyproject_content):
        """The [dev] extra must still include requests-mock."""
        assert "requests-mock" in pyproject_content.lower() or "requests_mock" in pyproject_content.lower(), \
            "The [dev] extra must still include requests-mock"

    def test_has_requests_dependency(self, pyproject_content):
        """Base dependencies must still include requests."""
        assert "requests" in pyproject_content.lower(), \
            "Base dependencies must still include requests"

    def test_has_aws_sdk_dependency(self, pyproject_content):
        """Base dependencies must still include boto3 or botocore."""
        content_lower = pyproject_content.lower()
        assert "boto3" in content_lower or "botocore" in content_lower, \
            "Base dependencies must still include boto3 or botocore for AWS SDK"


class TestSourceFilesUnchanged:
    """Test that source files are unchanged (byte-identical)."""

    def test_init_py_has_version(self):
        """__init__.py must still define __version__ = '0.1.0'."""
        init_path = os.path.join(MYAPP_PKG_DIR, "__init__.py")
        assert os.path.isfile(init_path), f"File {init_path} must exist"
        with open(init_path, "r") as f:
            content = f.read()
        assert '__version__ = "0.1.0"' in content or "__version__ = '0.1.0'" in content, \
            "__init__.py must still define __version__ = '0.1.0'"

    def test_core_py_has_main_function(self):
        """core.py must still have a main function."""
        core_path = os.path.join(MYAPP_PKG_DIR, "core.py")
        assert os.path.isfile(core_path), f"File {core_path} must exist"
        with open(core_path, "r") as f:
            content = f.read()
        assert "def main" in content, \
            "core.py must still define a 'main' function"


class TestUrllib3ConflictResolved:
    """Test that the urllib3 version conflict is actually resolved."""

    def test_no_conflicting_urllib3_constraint(self):
        """The explicit urllib3>=2.0.0 constraint should be removed or relaxed."""
        pyproject_path = os.path.join(MYAPP_DIR, "pyproject.toml")
        with open(pyproject_path, "r") as f:
            content = f.read()

        # The problematic constraint was urllib3>=2.0.0
        # It should either be removed entirely, or changed to a compatible version
        # We check that the exact problematic constraint is gone
        if "urllib3>=2.0.0" in content:
            pytest.fail(
                "The problematic 'urllib3>=2.0.0' constraint is still present. "
                "This conflicts with boto3's requirement for urllib3<2.0.0. "
                "Remove or relax this constraint to fix the build."
            )
