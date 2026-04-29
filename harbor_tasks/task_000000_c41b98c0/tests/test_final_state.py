# test_final_state.py
"""
Tests to validate the final state of the system after the student has fixed
the Python venv/alias issue that was causing import failures.
"""

import os
import subprocess
import hashlib
import pytest


HOME = "/home/user"
MLSERVICE_DIR = os.path.join(HOME, "mlservice")
VENV_DIR = os.path.join(MLSERVICE_DIR, ".venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python")
REQUIREMENTS_FILE = os.path.join(MLSERVICE_DIR, "requirements.txt")
BASHRC = os.path.join(HOME, ".bashrc")


class TestMlserviceRunsSuccessfully:
    """Test that mlservice can be run successfully after the fix."""

    def test_mlservice_runs_with_explicit_venv_python(self):
        """
        Running mlservice with explicit venv Python should succeed.
        This is the primary success criterion.
        """
        result = subprocess.run(
            [VENV_PYTHON, "-m", "mlservice"],
            capture_output=True,
            text=True,
            cwd=MLSERVICE_DIR,
            timeout=120
        )
        assert result.returncode == 0, (
            f"Running '{VENV_PYTHON} -m mlservice' should exit 0.\n"
            f"Exit code: {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Tokenizer loaded:" in result.stdout, (
            f"Expected 'Tokenizer loaded:' in output.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_mlservice_runs_with_activated_venv_and_python_command(self):
        """
        After activating the venv, 'python -m mlservice' should work.
        This tests that the alias/PATH issue is resolved for normal usage.
        """
        # Use bash to source the activate script and then run python
        script = f"""
        cd {MLSERVICE_DIR}
        source .venv/bin/activate
        python -m mlservice
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            timeout=120,
            env={**os.environ, "HOME": HOME}  # Ensure HOME is set correctly
        )
        assert result.returncode == 0, (
            f"Running 'source .venv/bin/activate && python -m mlservice' should exit 0.\n"
            f"Exit code: {result.returncode}\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        assert "Tokenizer loaded:" in result.stdout, (
            f"Expected 'Tokenizer loaded:' in output after venv activation.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_mlservice_output_contains_tokenizer_class(self):
        """
        The output should contain a tokenizer class name like BertTokenizerFast.
        """
        result = subprocess.run(
            [VENV_PYTHON, "-m", "mlservice"],
            capture_output=True,
            text=True,
            cwd=MLSERVICE_DIR,
            timeout=120
        )
        assert result.returncode == 0, (
            f"mlservice should run successfully. stderr: {result.stderr}"
        )
        # Check that the output contains a tokenizer class name
        output = result.stdout
        assert "Tokenizer loaded:" in output, (
            f"Output should contain 'Tokenizer loaded:'. Got: {output}"
        )
        # The class name should follow "Tokenizer loaded: "
        # Common names: BertTokenizerFast, BertTokenizer, PreTrainedTokenizerFast
        assert any(name in output for name in ["Tokenizer", "tokenizer"]), (
            f"Output should mention a tokenizer class. Got: {output}"
        )


class TestSourceCodeUnchanged:
    """Test that the mlservice source code was not modified (invariant)."""

    def test_init_py_unchanged(self):
        """__init__.py should not have been modified."""
        init_file = os.path.join(MLSERVICE_DIR, "__init__.py")
        with open(init_file, "r") as f:
            content = f.read()

        # Check for the expected content structure
        assert "from transformers import AutoTokenizer" in content, (
            "__init__.py should still contain 'from transformers import AutoTokenizer'. "
            "The source code should not have been modified."
        )
        assert "def run():" in content, (
            "__init__.py should still contain 'def run():'. "
            "The source code should not have been modified."
        )
        assert 'AutoTokenizer.from_pretrained' in content, (
            "__init__.py should still use AutoTokenizer.from_pretrained. "
            "The source code should not have been modified."
        )
        assert 'print(' in content and 'Tokenizer loaded' in content, (
            "__init__.py should still print 'Tokenizer loaded'. "
            "The source code should not have been modified."
        )

    def test_main_py_unchanged(self):
        """__main__.py should not have been modified."""
        main_file = os.path.join(MLSERVICE_DIR, "__main__.py")
        with open(main_file, "r") as f:
            content = f.read()

        # Check for the expected content
        assert "from mlservice import run" in content, (
            "__main__.py should still contain 'from mlservice import run'. "
            "The source code should not have been modified."
        )
        assert "run()" in content, (
            "__main__.py should still call 'run()'. "
            "The source code should not have been modified."
        )


class TestRequirementsUnchanged:
    """Test that requirements.txt was not modified (invariant)."""

    def test_requirements_contains_original_packages(self):
        """requirements.txt should still contain the original packages."""
        with open(REQUIREMENTS_FILE, "r") as f:
            content = f.read().lower()

        assert "transformers" in content, (
            "requirements.txt should still contain transformers"
        )
        assert "tokenizers" in content, (
            "requirements.txt should still contain tokenizers"
        )
        assert "torch" in content, (
            "requirements.txt should still contain torch"
        )
        assert "numpy" in content, (
            "requirements.txt should still contain numpy"
        )

    def test_transformers_version_unchanged(self):
        """transformers version should still be 4.36.0."""
        with open(REQUIREMENTS_FILE, "r") as f:
            content = f.read()

        assert "4.36" in content, (
            "requirements.txt should still specify transformers 4.36.x. "
            "The requirements should not have been downgraded."
        )


class TestVenvPackagesIntact:
    """Test that the venv packages remain as originally installed."""

    def test_tokenizers_version_in_venv(self):
        """tokenizers 0.15.0 should still be in the venv."""
        result = subprocess.run(
            [VENV_PYTHON, "-c", "import tokenizers; print(tokenizers.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"tokenizers should be importable in venv. stderr: {result.stderr}"
        )
        assert "0.15" in result.stdout, (
            f"Expected tokenizers 0.15.x in venv, got: {result.stdout.strip()}. "
            "The venv packages should not have been modified."
        )

    def test_transformers_version_in_venv(self):
        """transformers 4.36.0 should still be in the venv."""
        result = subprocess.run(
            [VENV_PYTHON, "-c", "import transformers; print(transformers.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"transformers should be importable in venv. stderr: {result.stderr}"
        )
        assert "4.36" in result.stdout, (
            f"Expected transformers 4.36.x in venv, got: {result.stdout.strip()}. "
            "The venv packages should not have been modified."
        )


class TestVenvPythonIsUsed:
    """Test that the fix ensures venv Python is used, not system Python."""

    def test_venv_python_resolves_correctly_after_activation(self):
        """
        After activating the venv, 'which python' should point to venv Python.
        """
        script = f"""
        cd {MLSERVICE_DIR}
        source .venv/bin/activate
        which python
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": HOME}
        )
        # The python command should resolve to the venv
        python_path = result.stdout.strip()
        assert ".venv" in python_path or "mlservice" in python_path, (
            f"After venv activation, 'which python' should point to venv Python. "
            f"Got: {python_path}. "
            "The alias/PATH issue may not be fully resolved."
        )

    def test_python_version_after_activation_is_311(self):
        """
        After activating the venv, 'python --version' should show 3.11.
        """
        script = f"""
        cd {MLSERVICE_DIR}
        source .venv/bin/activate
        python --version
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            env={**os.environ, "HOME": HOME}
        )
        version_output = result.stdout.strip() + result.stderr.strip()
        assert "3.11" in version_output, (
            f"After venv activation, Python should be 3.11. Got: {version_output}. "
            "The venv Python may not be correctly activated."
        )


class TestImportWorksCorrectly:
    """Test that imports work correctly with the venv Python."""

    def test_transformers_autotokenizer_import(self):
        """AutoTokenizer should be importable."""
        result = subprocess.run(
            [VENV_PYTHON, "-c", "from transformers import AutoTokenizer; print('OK')"],
            capture_output=True,
            text=True,
            cwd=MLSERVICE_DIR
        )
        assert result.returncode == 0, (
            f"AutoTokenizer should be importable. stderr: {result.stderr}"
        )
        assert "OK" in result.stdout, (
            f"Import test should print 'OK'. stdout: {result.stdout}"
        )

    def test_tokenizers_import_with_correct_version(self):
        """tokenizers should import with version 0.15.x."""
        result = subprocess.run(
            [VENV_PYTHON, "-c", 
             "import tokenizers; "
             "v = tokenizers.__version__; "
             "assert v.startswith('0.15'), f'Wrong version: {v}'; "
             "print('OK')"],
            capture_output=True,
            text=True,
            cwd=MLSERVICE_DIR
        )
        assert result.returncode == 0, (
            f"tokenizers should import with version 0.15.x. stderr: {result.stderr}"
        )


class TestNoSystemPackageModification:
    """Test that system Python packages were not modified (no root access)."""

    def test_system_python_still_exists(self):
        """System Python should still exist."""
        assert os.path.isfile("/usr/bin/python3"), (
            "/usr/bin/python3 should still exist"
        )

    def test_venv_is_still_separate(self):
        """The venv should still be a separate environment."""
        # Check that venv Python and system Python are different
        venv_result = subprocess.run(
            [VENV_PYTHON, "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True
        )
        system_result = subprocess.run(
            ["/usr/bin/python3", "-c", "import sys; print(sys.executable)"],
            capture_output=True,
            text=True
        )

        venv_exec = venv_result.stdout.strip()
        system_exec = system_result.stdout.strip()

        assert venv_exec != system_exec, (
            f"Venv Python ({venv_exec}) should be different from "
            f"system Python ({system_exec})"
        )
