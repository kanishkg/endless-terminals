# test_initial_state.py
"""
Tests to validate the initial state of the archive_pipeline before the student fixes the bug.
"""

import os
import pytest
import subprocess
import stat


PIPELINE_DIR = "/home/user/archive_pipeline"


class TestPipelineDirectoryExists:
    """Verify the archive_pipeline directory exists and is accessible."""

    def test_pipeline_directory_exists(self):
        assert os.path.isdir(PIPELINE_DIR), \
            f"Directory {PIPELINE_DIR} does not exist"

    def test_pipeline_directory_is_readable(self):
        assert os.access(PIPELINE_DIR, os.R_OK), \
            f"Directory {PIPELINE_DIR} is not readable"

    def test_pipeline_directory_is_writable(self):
        assert os.access(PIPELINE_DIR, os.W_OK), \
            f"Directory {PIPELINE_DIR} is not writable"


class TestRequiredFilesExist:
    """Verify all required files exist in the pipeline directory."""

    def test_create_py_exists(self):
        filepath = os.path.join(PIPELINE_DIR, "create.py")
        assert os.path.isfile(filepath), \
            f"create.py not found at {filepath}"

    def test_extract_py_exists(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        assert os.path.isfile(filepath), \
            f"extract.py not found at {filepath}"

    def test_run_test_sh_exists(self):
        filepath = os.path.join(PIPELINE_DIR, "run_test.sh")
        assert os.path.isfile(filepath), \
            f"run_test.sh not found at {filepath}"

    def test_carch_format_md_exists(self):
        filepath = os.path.join(PIPELINE_DIR, "carch_format.md")
        assert os.path.isfile(filepath), \
            f"carch_format.md not found at {filepath}"


class TestFilePermissions:
    """Verify files have appropriate permissions."""

    def test_create_py_is_readable(self):
        filepath = os.path.join(PIPELINE_DIR, "create.py")
        assert os.access(filepath, os.R_OK), \
            f"create.py is not readable"

    def test_extract_py_is_readable(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        assert os.access(filepath, os.R_OK), \
            f"extract.py is not readable"

    def test_extract_py_is_writable(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        assert os.access(filepath, os.W_OK), \
            f"extract.py is not writable - student needs to be able to fix it"

    def test_run_test_sh_is_executable(self):
        filepath = os.path.join(PIPELINE_DIR, "run_test.sh")
        assert os.access(filepath, os.X_OK), \
            f"run_test.sh is not executable"


class TestRequiredTools:
    """Verify required command-line tools are available."""

    def test_python3_available(self):
        result = subprocess.run(["which", "python3"], capture_output=True)
        assert result.returncode == 0, \
            "python3 is not available in PATH"

    def test_tar_available(self):
        result = subprocess.run(["which", "tar"], capture_output=True)
        assert result.returncode == 0, \
            "tar is not available in PATH"

    def test_zstd_available(self):
        result = subprocess.run(["which", "zstd"], capture_output=True)
        assert result.returncode == 0, \
            "zstd is not available in PATH"

    def test_sha256sum_available(self):
        result = subprocess.run(["which", "sha256sum"], capture_output=True)
        assert result.returncode == 0, \
            "sha256sum is not available in PATH"


class TestExtractPyContainsBug:
    """Verify extract.py contains the expected bug pattern."""

    def test_extract_py_has_struct_import(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'struct' in content, \
            "extract.py should use struct module for binary parsing"

    def test_extract_py_has_header_len_variable(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'header_len' in content, \
            "extract.py should have header_len variable for parsing header"

    def test_extract_py_reads_magic(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'CARC' in content or 'magic' in content.lower(), \
            "extract.py should check for CARC magic bytes"

    def test_extract_py_has_seek_or_offset_logic(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        with open(filepath, 'r') as f:
            content = f.read()
        # The bug is in offset calculation, so there should be seek or offset logic
        has_seek = 'seek' in content
        has_offset = 'offset' in content.lower()
        assert has_seek or has_offset, \
            "extract.py should have seek or offset logic for reading payload"


class TestCreatePyIsValid:
    """Verify create.py appears to be a valid Python script."""

    def test_create_py_is_valid_python(self):
        filepath = os.path.join(PIPELINE_DIR, "create.py")
        result = subprocess.run(
            ["python3", "-m", "py_compile", filepath],
            capture_output=True
        )
        assert result.returncode == 0, \
            f"create.py has syntax errors: {result.stderr.decode()}"

    def test_create_py_has_struct_import(self):
        filepath = os.path.join(PIPELINE_DIR, "create.py")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'struct' in content, \
            "create.py should use struct module for binary packing"


class TestExtractPyIsValidPython:
    """Verify extract.py is syntactically valid Python (even if buggy)."""

    def test_extract_py_is_valid_python(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        result = subprocess.run(
            ["python3", "-m", "py_compile", filepath],
            capture_output=True
        )
        assert result.returncode == 0, \
            f"extract.py has syntax errors: {result.stderr.decode()}"


class TestRunTestShContent:
    """Verify run_test.sh has expected structure."""

    def test_run_test_sh_creates_test_src(self):
        filepath = os.path.join(PIPELINE_DIR, "run_test.sh")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'test_src' in content or '/tmp/' in content, \
            "run_test.sh should reference test source directory"

    def test_run_test_sh_uses_sha256(self):
        filepath = os.path.join(PIPELINE_DIR, "run_test.sh")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'sha256' in content.lower(), \
            "run_test.sh should use sha256 for checksum verification"

    def test_run_test_sh_calls_create_and_extract(self):
        filepath = os.path.join(PIPELINE_DIR, "run_test.sh")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'create' in content.lower() and 'extract' in content.lower(), \
            "run_test.sh should call both create and extract scripts"


class TestCarchFormatDoc:
    """Verify the format documentation exists and describes the format."""

    def test_format_doc_describes_magic(self):
        filepath = os.path.join(PIPELINE_DIR, "carch_format.md")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'CARC' in content or 'magic' in content.lower(), \
            "carch_format.md should document the magic bytes"

    def test_format_doc_describes_header_len(self):
        filepath = os.path.join(PIPELINE_DIR, "carch_format.md")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'header' in content.lower() and ('len' in content.lower() or 'length' in content.lower()), \
            "carch_format.md should document the header length field"

    def test_format_doc_mentions_json(self):
        filepath = os.path.join(PIPELINE_DIR, "carch_format.md")
        with open(filepath, 'r') as f:
            content = f.read()
        assert 'json' in content.lower() or 'JSON' in content, \
            "carch_format.md should document JSON metadata"


class TestTmpDirectoryWritable:
    """Verify /tmp is writable for test execution."""

    def test_tmp_exists(self):
        assert os.path.isdir("/tmp"), \
            "/tmp directory does not exist"

    def test_tmp_is_writable(self):
        assert os.access("/tmp", os.W_OK), \
            "/tmp is not writable - needed for test execution"


class TestBugPresence:
    """Verify the bug is actually present in extract.py."""

    def test_extract_py_has_incorrect_offset_calculation(self):
        """
        The bug is that payload_offset = header_len instead of 8 + header_len.
        We check that the code does NOT correctly add 8 to the offset.
        """
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        with open(filepath, 'r') as f:
            content = f.read()

        # Look for patterns that would indicate the bug is present
        # The buggy code likely has: payload_offset = header_len
        # or: f.seek(header_len)
        # The correct code would have: 8 + header_len or similar

        lines = content.split('\n')
        has_buggy_pattern = False
        has_correct_pattern = False

        for line in lines:
            # Skip comments
            if line.strip().startswith('#'):
                continue

            # Check for correct patterns (8 + header_len, header_len + 8, etc.)
            if '8 + header_len' in line or 'header_len + 8' in line:
                has_correct_pattern = True
            if '4 + 4 + header_len' in line or 'header_len + 4 + 4' in line:
                has_correct_pattern = True

            # Check for buggy patterns
            if 'offset = header_len' in line and '+ 8' not in line and '+ 4' not in line:
                has_buggy_pattern = True
            if 'seek(header_len)' in line:
                has_buggy_pattern = True

        # The bug should be present (buggy pattern found OR correct pattern not found)
        assert has_buggy_pattern or not has_correct_pattern, \
            "extract.py appears to already have the correct offset calculation - bug may already be fixed"
