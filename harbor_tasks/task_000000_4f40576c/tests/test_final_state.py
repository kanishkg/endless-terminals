# test_final_state.py
"""
Tests to validate the final state of the archive_pipeline after the student fixes the bug.
The main requirement is that ./run_test.sh exits 0, meaning all files round-trip correctly.
"""

import os
import pytest
import subprocess
import stat
import tempfile
import hashlib


PIPELINE_DIR = "/home/user/archive_pipeline"


class TestPipelineDirectoryIntact:
    """Verify the archive_pipeline directory still exists and is accessible."""

    def test_pipeline_directory_exists(self):
        assert os.path.isdir(PIPELINE_DIR), \
            f"Directory {PIPELINE_DIR} does not exist"

    def test_pipeline_directory_is_readable(self):
        assert os.access(PIPELINE_DIR, os.R_OK), \
            f"Directory {PIPELINE_DIR} is not readable"


class TestRequiredFilesStillExist:
    """Verify all required files still exist in the pipeline directory."""

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


class TestExtractPyIsValidPython:
    """Verify extract.py is still syntactically valid Python after the fix."""

    def test_extract_py_is_valid_python(self):
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        result = subprocess.run(
            ["python3", "-m", "py_compile", filepath],
            capture_output=True
        )
        assert result.returncode == 0, \
            f"extract.py has syntax errors: {result.stderr.decode()}"


class TestExtractPyHasCorrectOffsetCalculation:
    """Verify extract.py now has the correct offset calculation."""

    def test_extract_py_accounts_for_magic_and_header_len_bytes(self):
        """
        The fix should account for the 8 bytes before the JSON metadata:
        - 4 bytes for magic ("CARC")
        - 4 bytes for header_len (uint32)

        So payload starts at offset 8 + header_len, not just header_len.
        """
        filepath = os.path.join(PIPELINE_DIR, "extract.py")
        with open(filepath, 'r') as f:
            content = f.read()

        # Look for patterns indicating correct offset calculation
        # The fix could be implemented in various ways:
        # 1. payload_offset = 8 + header_len
        # 2. payload_offset = header_len + 8
        # 3. payload_offset = 4 + 4 + header_len
        # 4. f.seek(8 + header_len)
        # 5. Not seeking at all after reading (file position is already correct)
        # 6. Using f.tell() to get current position

        lines = content.split('\n')

        # Check for explicit 8 + header_len patterns
        has_explicit_8_offset = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            # Various ways to express 8 + header_len
            if '8 + header_len' in line or 'header_len + 8' in line:
                has_explicit_8_offset = True
            if '4 + 4 + header_len' in line or 'header_len + 4 + 4' in line:
                has_explicit_8_offset = True
            # Could also use HEADER_SIZE constant or similar
            if 'HEADER_SIZE' in line or 'MAGIC_SIZE' in line:
                has_explicit_8_offset = True

        # Alternative: check that the buggy pattern is NOT present
        has_buggy_seek = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            # Buggy pattern: seek(header_len) without adding 8
            if 'seek(header_len)' in line:
                has_buggy_seek = True
            # Buggy pattern: offset = header_len (without adding 8)
            if 'offset = header_len' in line and '8' not in line and '4' not in line:
                # Check if this line doesn't have the fix
                if '+ 8' not in line and '+ 4' not in line:
                    has_buggy_seek = True

        # The fix is correct if we have explicit 8 offset OR the buggy pattern is gone
        # We'll check both conditions - at minimum the buggy pattern should be fixed
        assert not has_buggy_seek or has_explicit_8_offset, \
            "extract.py still appears to have incorrect offset calculation. " \
            "The payload offset should be 8 + header_len (4 bytes magic + 4 bytes header_len field + header_len bytes of JSON)"


class TestRunTestShPasses:
    """The main test: verify run_test.sh exits 0, meaning the round-trip works."""

    def test_run_test_sh_exits_zero(self):
        """
        This is the definitive test. run_test.sh:
        1. Creates a test tree with ~50 files of varying sizes
        2. Creates a .carch archive using create.py
        3. Extracts it using extract.py
        4. Compares sha256sums of all files
        5. Exits 0 only if all checksums match
        """
        result = subprocess.run(
            ["./run_test.sh"],
            cwd=PIPELINE_DIR,
            capture_output=True,
            timeout=120  # Allow up to 2 minutes for large file operations
        )

        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')

        assert result.returncode == 0, \
            f"run_test.sh failed with exit code {result.returncode}.\n" \
            f"STDOUT:\n{stdout}\n" \
            f"STDERR:\n{stderr}\n" \
            "This means the archive round-trip is still corrupting files. " \
            "Check that extract.py correctly calculates the payload offset as 8 + header_len."


class TestRoundTripManually:
    """Additional manual verification of the round-trip process."""

    def test_manual_round_trip_small_files(self):
        """Create a small test case and verify round-trip works."""
        import shutil

        # Create temporary directories
        src_dir = tempfile.mkdtemp(prefix="carch_test_src_")
        dst_dir = tempfile.mkdtemp(prefix="carch_test_dst_")
        archive_path = tempfile.mktemp(suffix=".carch")

        try:
            # Create some test files with known content
            test_files = {
                "file1.txt": b"Hello, World!",
                "file2.bin": bytes(range(256)),
                "subdir/file3.txt": b"Nested file content",
                "empty.txt": b"",
            }

            for relpath, content in test_files.items():
                filepath = os.path.join(src_dir, relpath)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as f:
                    f.write(content)

            # Run create.py
            create_result = subprocess.run(
                ["python3", os.path.join(PIPELINE_DIR, "create.py"), src_dir, archive_path],
                capture_output=True,
                timeout=30
            )
            assert create_result.returncode == 0, \
                f"create.py failed: {create_result.stderr.decode()}"

            # Run extract.py
            extract_result = subprocess.run(
                ["python3", os.path.join(PIPELINE_DIR, "extract.py"), archive_path, dst_dir],
                capture_output=True,
                timeout=30
            )
            assert extract_result.returncode == 0, \
                f"extract.py failed: {extract_result.stderr.decode()}"

            # Verify all files match
            for relpath, expected_content in test_files.items():
                # Find the extracted file (may be nested under src_dir basename)
                possible_paths = [
                    os.path.join(dst_dir, relpath),
                    os.path.join(dst_dir, os.path.basename(src_dir), relpath),
                ]

                extracted_path = None
                for p in possible_paths:
                    if os.path.isfile(p):
                        extracted_path = p
                        break

                # Also search recursively
                if extracted_path is None:
                    for root, dirs, files in os.walk(dst_dir):
                        if os.path.basename(relpath) in files:
                            candidate = os.path.join(root, os.path.basename(relpath))
                            # Verify it's the right file by checking parent dirs
                            if relpath in candidate or os.path.basename(relpath) == relpath:
                                extracted_path = candidate
                                break

                assert extracted_path is not None and os.path.isfile(extracted_path), \
                    f"Extracted file not found for {relpath}"

                with open(extracted_path, 'rb') as f:
                    actual_content = f.read()

                assert actual_content == expected_content, \
                    f"Content mismatch for {relpath}. " \
                    f"Expected {len(expected_content)} bytes, got {len(actual_content)} bytes. " \
                    f"Expected hash: {hashlib.sha256(expected_content).hexdigest()}, " \
                    f"Actual hash: {hashlib.sha256(actual_content).hexdigest()}"

        finally:
            # Cleanup
            shutil.rmtree(src_dir, ignore_errors=True)
            shutil.rmtree(dst_dir, ignore_errors=True)
            if os.path.exists(archive_path):
                os.unlink(archive_path)

    def test_manual_round_trip_larger_file(self):
        """Test with a larger file to ensure no truncation issues."""
        import shutil

        src_dir = tempfile.mkdtemp(prefix="carch_large_src_")
        dst_dir = tempfile.mkdtemp(prefix="carch_large_dst_")
        archive_path = tempfile.mktemp(suffix=".carch")

        try:
            # Create a larger file (1MB of random-ish data)
            large_content = bytes([i % 256 for i in range(1024 * 1024)])
            large_file_path = os.path.join(src_dir, "large_file.bin")
            with open(large_file_path, 'wb') as f:
                f.write(large_content)

            expected_hash = hashlib.sha256(large_content).hexdigest()

            # Run create.py
            create_result = subprocess.run(
                ["python3", os.path.join(PIPELINE_DIR, "create.py"), src_dir, archive_path],
                capture_output=True,
                timeout=60
            )
            assert create_result.returncode == 0, \
                f"create.py failed: {create_result.stderr.decode()}"

            # Run extract.py
            extract_result = subprocess.run(
                ["python3", os.path.join(PIPELINE_DIR, "extract.py"), archive_path, dst_dir],
                capture_output=True,
                timeout=60
            )
            assert extract_result.returncode == 0, \
                f"extract.py failed: {extract_result.stderr.decode()}"

            # Find and verify the large file
            extracted_path = None
            for root, dirs, files in os.walk(dst_dir):
                if "large_file.bin" in files:
                    extracted_path = os.path.join(root, "large_file.bin")
                    break

            assert extracted_path is not None, \
                "large_file.bin not found in extracted output"

            with open(extracted_path, 'rb') as f:
                actual_content = f.read()

            actual_hash = hashlib.sha256(actual_content).hexdigest()

            assert len(actual_content) == len(large_content), \
                f"Size mismatch: expected {len(large_content)}, got {len(actual_content)}"

            assert actual_hash == expected_hash, \
                f"Hash mismatch for large file. Expected {expected_hash}, got {actual_hash}"

        finally:
            shutil.rmtree(src_dir, ignore_errors=True)
            shutil.rmtree(dst_dir, ignore_errors=True)
            if os.path.exists(archive_path):
                os.unlink(archive_path)
