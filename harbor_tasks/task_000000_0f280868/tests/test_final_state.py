# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the patch debugging task.
"""

import os
import pytest
import subprocess


BASE_DIR = "/home/user/mldata"
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCRIPT_PATH = os.path.join(BASE_DIR, "apply_patches.py")
EXPECTED_PATH = os.path.join(BASE_DIR, "expected.txt")


# Expected output content for each sample (with trailing newline)
EXPECTED_OUTPUTS = {
    "sample_001.txt": "Hello world\n",
    "sample_002.txt": "Goodbye world\n",
    "sample_003.txt": "The quick brown fox jumps over the lazy dog\n",
    "sample_004.txt": "Machine learning is transforming industries\n",
    "sample_005.txt": "Data quality matters more than model size\n",
}


class TestScriptExecution:
    """Test that the script runs successfully."""

    def test_script_exits_zero(self):
        """Running the script should exit with code 0."""
        result = subprocess.run(
            ['python3', SCRIPT_PATH],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        assert result.returncode == 0, \
            f"Script exited with code {result.returncode}. stderr: {result.stderr}, stdout: {result.stdout}"


class TestOutputFiles:
    """Test that all output files exist and have correct content."""

    @pytest.mark.parametrize("filename,expected_content", list(EXPECTED_OUTPUTS.items()))
    def test_output_file_exists(self, filename, expected_content):
        """Each output file should exist."""
        output_path = os.path.join(OUTPUT_DIR, filename)
        assert os.path.isfile(output_path), \
            f"Output file {output_path} does not exist"

    @pytest.mark.parametrize("filename,expected_content", list(EXPECTED_OUTPUTS.items()))
    def test_output_file_content(self, filename, expected_content):
        """Each output file should have the exact expected content."""
        output_path = os.path.join(OUTPUT_DIR, filename)

        # First ensure file exists
        if not os.path.isfile(output_path):
            pytest.fail(f"Output file {output_path} does not exist")

        with open(output_path, 'r') as f:
            actual_content = f.read()

        assert actual_content == expected_content, \
            f"Content mismatch for {filename}.\n" \
            f"Expected: {repr(expected_content)}\n" \
            f"Actual: {repr(actual_content)}"

    def test_sample_001_output(self):
        """Specific test for sample_001 output."""
        output_path = os.path.join(OUTPUT_DIR, "sample_001.txt")
        with open(output_path, 'r') as f:
            content = f.read()
        assert content == "Hello world\n", \
            f"sample_001.txt should contain 'Hello world\\n', got: {repr(content)}"

    def test_sample_002_output(self):
        """Specific test for sample_002 output."""
        output_path = os.path.join(OUTPUT_DIR, "sample_002.txt")
        with open(output_path, 'r') as f:
            content = f.read()
        assert content == "Goodbye world\n", \
            f"sample_002.txt should contain 'Goodbye world\\n', got: {repr(content)}"

    def test_sample_003_output(self):
        """Specific test for sample_003 output - the main problematic case."""
        output_path = os.path.join(OUTPUT_DIR, "sample_003.txt")
        with open(output_path, 'r') as f:
            content = f.read()
        assert content == "The quick brown fox jumps over the lazy dog\n", \
            f"sample_003.txt should contain 'The quick brown fox jumps over the lazy dog\\n', got: {repr(content)}"

    def test_sample_004_output(self):
        """Specific test for sample_004 output."""
        output_path = os.path.join(OUTPUT_DIR, "sample_004.txt")
        with open(output_path, 'r') as f:
            content = f.read()
        assert content == "Machine learning is transforming industries\n", \
            f"sample_004.txt should contain 'Machine learning is transforming industries\\n', got: {repr(content)}"

    def test_sample_005_output(self):
        """Specific test for sample_005 output."""
        output_path = os.path.join(OUTPUT_DIR, "sample_005.txt")
        with open(output_path, 'r') as f:
            content = f.read()
        assert content == "Data quality matters more than model size\n", \
            f"sample_005.txt should contain 'Data quality matters more than model size\\n', got: {repr(content)}"


class TestAntiShortcutGuards:
    """Tests to ensure the solution isn't a shortcut/hardcoded approach."""

    def test_script_still_references_samples_directory(self):
        """Script must still read from samples/ directory."""
        result = subprocess.run(
            ['grep', '-c', 'samples/', SCRIPT_PATH],
            capture_output=True,
            text=True
        )
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert count >= 1, \
            f"Script must reference 'samples/' directory (found {count} references). " \
            "The script should still perform patching logic, not bypass it."

    def test_script_does_not_hardcode_expected_outputs(self):
        """Script must not simply hardcode the expected outputs."""
        result = subprocess.run(
            ['grep', '-E', 'quick brown fox|transforming industries|quality matters', SCRIPT_PATH],
            capture_output=True,
            text=True
        )
        # grep returns 0 if matches found, 1 if no matches
        assert result.returncode != 0, \
            f"Script appears to hardcode expected outputs. Found: {result.stdout}. " \
            "The script should perform actual patching, not hardcode results."

    def test_failing_samples_still_exist_in_samples_dir(self):
        """sample_003.txt, sample_004.txt, sample_005.txt must still exist in samples/."""
        for sample_num in ["003", "004", "005"]:
            txt_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.txt")
            assert os.path.isfile(txt_path), \
                f"Sample file {txt_path} must still exist. Cannot delete failing cases as a workaround."


class TestInvariants:
    """Tests to ensure certain files remain unchanged."""

    def test_expected_txt_unchanged(self):
        """expected.txt should remain unchanged (contains manifest)."""
        with open(EXPECTED_PATH, 'r') as f:
            content = f.read()

        # Check that it still contains the expected manifest entries
        assert "sample_001: Hello world" in content, \
            "expected.txt should still contain 'sample_001: Hello world'"
        assert "sample_002: Goodbye world" in content, \
            "expected.txt should still contain 'sample_002: Goodbye world'"
        assert "sample_003: The quick brown fox jumps over the lazy dog" in content, \
            "expected.txt should still contain 'sample_003: The quick brown fox jumps over the lazy dog'"
        assert "sample_004: Machine learning is transforming industries" in content, \
            "expected.txt should still contain 'sample_004: Machine learning is transforming industries'"
        assert "sample_005: Data quality matters more than model size" in content, \
            "expected.txt should still contain 'sample_005: Data quality matters more than model size'"

    def test_samples_directory_still_has_all_files(self):
        """All sample files should still exist."""
        for sample_num in ["001", "002", "003", "004", "005"]:
            txt_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.txt")
            patch_path = os.path.join(SAMPLES_DIR, f"sample_{sample_num}.patch")
            assert os.path.isfile(txt_path), f"Sample file {txt_path} should still exist"
            assert os.path.isfile(patch_path), f"Patch file {patch_path} should still exist"


class TestScriptIntegrity:
    """Tests to ensure the script is still valid Python."""

    def test_script_has_valid_syntax(self):
        """Script should still have valid Python syntax."""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', SCRIPT_PATH],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"Script has syntax errors: {result.stderr}"

    def test_script_is_python_file(self):
        """Script should still be a Python file."""
        with open(SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'def ' in content or 'import ' in content, \
            f"Script {SCRIPT_PATH} does not appear to be a Python file"


class TestRerunProducesConsistentResults:
    """Test that running the script again produces the same results."""

    def test_rerun_produces_same_output(self):
        """Running the script twice should produce identical output."""
        # Run the script
        result = subprocess.run(
            ['python3', SCRIPT_PATH],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        assert result.returncode == 0, \
            f"Script failed on rerun with code {result.returncode}"

        # Check all outputs are still correct
        for filename, expected_content in EXPECTED_OUTPUTS.items():
            output_path = os.path.join(OUTPUT_DIR, filename)
            with open(output_path, 'r') as f:
                actual_content = f.read()
            assert actual_content == expected_content, \
                f"Content mismatch after rerun for {filename}. " \
                f"Expected: {repr(expected_content)}, Actual: {repr(actual_content)}"
