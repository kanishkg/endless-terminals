# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the patch debugging task.
"""

import os
import pytest
import subprocess
import stat


BASE_DIR = "/home/user/mldata"
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCRIPT_PATH = os.path.join(BASE_DIR, "apply_patches.py")
EXPECTED_PATH = os.path.join(BASE_DIR, "expected.txt")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_base_directory_exists(self):
        assert os.path.isdir(BASE_DIR), f"Base directory {BASE_DIR} does not exist"

    def test_samples_directory_exists(self):
        assert os.path.isdir(SAMPLES_DIR), f"Samples directory {SAMPLES_DIR} does not exist"

    def test_output_directory_exists(self):
        assert os.path.isdir(OUTPUT_DIR), f"Output directory {OUTPUT_DIR} does not exist"

    def test_output_directory_is_empty(self):
        contents = os.listdir(OUTPUT_DIR)
        assert len(contents) == 0, f"Output directory should be empty initially, but contains: {contents}"


class TestScriptFile:
    """Test that the main script exists and is properly configured."""

    def test_script_exists(self):
        assert os.path.isfile(SCRIPT_PATH), f"Script {SCRIPT_PATH} does not exist"

    def test_script_is_readable(self):
        assert os.access(SCRIPT_PATH, os.R_OK), f"Script {SCRIPT_PATH} is not readable"

    def test_script_is_executable(self):
        # Check if file has executable permission or can be run with python3
        mode = os.stat(SCRIPT_PATH).st_mode
        is_executable = bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
        # Also acceptable if it's a Python script that can be run with python3
        assert is_executable or SCRIPT_PATH.endswith('.py'), \
            f"Script {SCRIPT_PATH} should be executable or a .py file"

    def test_script_is_python_file(self):
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        # Should contain Python code indicators
        assert 'def ' in content or 'import ' in content, \
            f"Script {SCRIPT_PATH} does not appear to be a Python file"

    def test_script_references_samples_directory(self):
        """Script must read from samples/ directory."""
        result = subprocess.run(
            ['grep', '-c', 'samples/', SCRIPT_PATH],
            capture_output=True,
            text=True
        )
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert count >= 1, \
            f"Script must reference 'samples/' directory (found {count} references)"


class TestExpectedFile:
    """Test that the expected.txt manifest exists with proper content."""

    def test_expected_file_exists(self):
        assert os.path.isfile(EXPECTED_PATH), f"Expected file {EXPECTED_PATH} does not exist"

    def test_expected_file_is_readable(self):
        assert os.access(EXPECTED_PATH, os.R_OK), f"Expected file {EXPECTED_PATH} is not readable"

    def test_expected_file_has_content(self):
        with open(EXPECTED_PATH, 'r') as f:
            content = f.read()
        assert len(content) > 0, f"Expected file {EXPECTED_PATH} is empty"

    def test_expected_file_contains_all_samples(self):
        with open(EXPECTED_PATH, 'r') as f:
            content = f.read()
        for i in range(1, 6):
            sample_name = f"sample_00{i}"
            assert sample_name in content, \
                f"Expected file should contain reference to {sample_name}"

    def test_expected_file_contains_sample_003_expected_text(self):
        with open(EXPECTED_PATH, 'r') as f:
            content = f.read()
        assert "The quick brown fox jumps over the lazy dog" in content, \
            "Expected file should contain the expected text for sample_003"


class TestSampleFiles:
    """Test that all sample files exist."""

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_sample_txt_exists(self, sample_num):
        txt_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.txt")
        assert os.path.isfile(txt_path), f"Sample file {txt_path} does not exist"

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_sample_patch_exists(self, sample_num):
        patch_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.patch")
        assert os.path.isfile(patch_path), f"Patch file {patch_path} does not exist"

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_sample_txt_is_readable(self, sample_num):
        txt_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.txt")
        assert os.access(txt_path, os.R_OK), f"Sample file {txt_path} is not readable"

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_sample_patch_is_readable(self, sample_num):
        patch_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.patch")
        assert os.access(patch_path, os.R_OK), f"Patch file {patch_path} is not readable"

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_sample_txt_has_content(self, sample_num):
        txt_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.txt")
        with open(txt_path, 'r') as f:
            content = f.read()
        assert len(content) > 0, f"Sample file {txt_path} is empty"

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_sample_patch_has_content(self, sample_num):
        patch_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.patch")
        with open(patch_path, 'r') as f:
            content = f.read()
        assert len(content) > 0, f"Patch file {patch_path} is empty"

    @pytest.mark.parametrize("sample_num", ["001", "002", "003", "004", "005"])
    def test_patch_has_unified_diff_format(self, sample_num):
        """Patches should be in unified diff format (contain @@ markers)."""
        patch_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.patch")
        with open(patch_path, 'r') as f:
            content = f.read()
        assert '@@' in content, \
            f"Patch file {patch_path} does not appear to be in unified diff format (no @@ markers)"


class TestFilePermissions:
    """Test that files are writable for the task."""

    def test_script_is_writable(self):
        assert os.access(SCRIPT_PATH, os.W_OK), \
            f"Script {SCRIPT_PATH} is not writable"

    def test_output_directory_is_writable(self):
        assert os.access(OUTPUT_DIR, os.W_OK), \
            f"Output directory {OUTPUT_DIR} is not writable"

    @pytest.mark.parametrize("sample_num", ["003", "004", "005"])
    def test_failing_sample_txt_is_writable(self, sample_num):
        """The failing samples should be writable in case patches need fixing."""
        txt_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.txt")
        assert os.access(txt_path, os.W_OK), \
            f"Sample file {txt_path} is not writable"

    @pytest.mark.parametrize("sample_num", ["003", "004", "005"])
    def test_failing_sample_patch_is_writable(self, sample_num):
        """The failing patches should be writable in case they need fixing."""
        patch_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.patch")
        assert os.access(patch_path, os.W_OK), \
            f"Patch file {patch_path} is not writable"


class TestSystemTools:
    """Test that required system tools are available."""

    def test_python3_available(self):
        result = subprocess.run(['which', 'python3'], capture_output=True)
        assert result.returncode == 0, "python3 is not available in PATH"

    def test_patch_utility_available(self):
        assert os.path.isfile('/usr/bin/patch'), \
            "Standard patch utility not found at /usr/bin/patch"

    def test_diff_utility_available(self):
        result = subprocess.run(['which', 'diff'], capture_output=True)
        assert result.returncode == 0, "diff utility is not available in PATH"


class TestScriptSyntax:
    """Test that the script has valid Python syntax."""

    def test_script_has_valid_syntax(self):
        result = subprocess.run(
            ['python3', '-m', 'py_compile', SCRIPT_PATH],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Script has syntax errors: {result.stderr}"
