# test_final_state.py
"""
Tests to validate the final state after the student has completed the
integrity audit debugging task. The fix should make check_integrity.py
work correctly without modifying the manifest or data files.
"""

import os
import subprocess
import hashlib
import tempfile
import shutil
import pytest

AUDIT_DIR = "/home/user/audit"
MANIFEST_FILE = os.path.join(AUDIT_DIR, "manifest.sha256")
CHECKER_SCRIPT = os.path.join(AUDIT_DIR, "check_integrity.py")
DATA_DIR = os.path.join(AUDIT_DIR, "data")

# The three files that had CRLF line endings
CRLF_FILES = [
    "data/report_2024q1.csv",
    "data/config.json",
    "data/notes.txt",
]


class TestCheckerScriptPasses:
    """Test that the checker script now passes."""

    def test_checker_exits_zero(self):
        """The check_integrity.py script must exit with code 0."""
        result = subprocess.run(
            ['python3', CHECKER_SCRIPT],
            cwd=AUDIT_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"check_integrity.py should exit 0 but exited {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_checker_indicates_success(self):
        """The checker script output should indicate all files pass."""
        result = subprocess.run(
            ['python3', CHECKER_SCRIPT],
            cwd=AUDIT_DIR,
            capture_output=True,
            text=True
        )
        output = (result.stdout + result.stderr).lower()

        # Should not contain failure indicators
        assert 'fail' not in output or 'failed: 0' in output or '0 failed' in output, (
            f"Checker output suggests failures still exist.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


class TestManifestUnchanged:
    """Test that the manifest file was not modified."""

    def test_sha256sum_still_verifies_all_files(self):
        """sha256sum -c manifest.sha256 must still pass for all files."""
        result = subprocess.run(
            ['sha256sum', '-c', 'manifest.sha256'],
            cwd=AUDIT_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"sha256sum -c manifest.sha256 failed. The manifest or data files may have been incorrectly modified.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    def test_manifest_still_has_correct_format(self):
        """The manifest should still have the correct sha256sum format."""
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 35, f"Manifest appears truncated, only {len(lines)} lines"

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            parts = line.split('  ', 1)
            assert len(parts) == 2, f"Line {i+1} format corrupted: {line}"
            hash_part, path_part = parts
            assert len(hash_part) == 64, f"Line {i+1} hash length wrong: {len(hash_part)}"


class TestDataFilesUnchanged:
    """Test that data files were not modified."""

    def test_crlf_files_still_have_crlf(self):
        """The three CRLF files must still contain CRLF line endings."""
        for rel_path in CRLF_FILES:
            full_path = os.path.join(AUDIT_DIR, rel_path)

            # Use grep -c to count lines with carriage return
            result = subprocess.run(
                ['grep', '-c', '\r'],
                stdin=open(full_path, 'rb'),
                capture_output=True
            )

            # Also check directly with Python
            with open(full_path, 'rb') as f:
                content = f.read()

            assert b'\r\n' in content, (
                f"File {rel_path} no longer contains CRLF line endings. "
                f"The fix should modify the script, not convert the files to Unix line endings."
            )

    def test_all_data_files_verify_against_manifest(self):
        """All data files should still match their manifest hashes."""
        # This is a more thorough check than just running sha256sum -c
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split('  ', 1)
            if len(parts) != 2:
                continue
            expected_hash, rel_path = parts
            full_path = os.path.join(AUDIT_DIR, rel_path)

            with open(full_path, 'rb') as f:
                actual_hash = hashlib.sha256(f.read()).hexdigest()

            assert actual_hash == expected_hash.lower(), (
                f"File {rel_path} hash mismatch. File may have been modified.\n"
                f"Expected: {expected_hash}\n"
                f"Actual: {actual_hash}"
            )


class TestCheckerScriptIntegrity:
    """Test that the checker script still exists and functions properly."""

    def test_checker_script_exists(self):
        """check_integrity.py must still exist."""
        assert os.path.isfile(CHECKER_SCRIPT), (
            f"check_integrity.py no longer exists at {CHECKER_SCRIPT}"
        )

    def test_checker_is_valid_python(self):
        """check_integrity.py must be valid Python syntax."""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', CHECKER_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"check_integrity.py has syntax errors: {result.stderr}"
        )

    def test_checker_actually_reads_and_hashes_files(self):
        """
        The checker must actually read and hash file contents.
        Test by temporarily corrupting a file and verifying the checker detects it.
        """
        # Find a file from the manifest to test with
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()

        # Get the first data file
        test_file_rel = None
        for line in lines:
            line = line.strip()
            if line and '  ' in line:
                _, rel_path = line.split('  ', 1)
                if rel_path.startswith('data/'):
                    test_file_rel = rel_path
                    break

        assert test_file_rel is not None, "Could not find a data file to test with"

        test_file_full = os.path.join(AUDIT_DIR, test_file_rel)

        # Backup the file
        with open(test_file_full, 'rb') as f:
            original_content = f.read()

        try:
            # Corrupt the file by truncating it
            with open(test_file_full, 'wb') as f:
                f.write(b'CORRUPTED')

            # Run the checker - it should now fail
            result = subprocess.run(
                ['python3', CHECKER_SCRIPT],
                cwd=AUDIT_DIR,
                capture_output=True,
                text=True
            )

            # The checker should detect the corruption
            detected_corruption = (
                result.returncode != 0 or
                'fail' in result.stdout.lower() or
                'fail' in result.stderr.lower() or
                'error' in result.stdout.lower() or
                'mismatch' in result.stdout.lower()
            )

            assert detected_corruption, (
                "check_integrity.py did not detect file corruption. "
                "The script may be hardcoding results or not actually hashing files.\n"
                f"returncode: {result.returncode}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
        finally:
            # Restore the original file
            with open(test_file_full, 'wb') as f:
                f.write(original_content)

    def test_checker_does_not_just_shell_out_to_sha256sum(self):
        """
        The checker should use Python's hashlib, not just shell out to sha256sum.
        We check that the script contains hashlib usage.
        """
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        # The script should use hashlib for hashing
        uses_hashlib = 'hashlib' in content and 'sha256' in content.lower()

        # Check it's not just calling sha256sum via subprocess
        shells_out = (
            'subprocess' in content and 'sha256sum' in content
        ) or (
            'os.system' in content and 'sha256sum' in content
        ) or (
            'os.popen' in content and 'sha256sum' in content
        )

        # It should use hashlib and not primarily shell out
        assert uses_hashlib, (
            "check_integrity.py should use Python's hashlib for hashing, "
            "not shell out to external commands."
        )


class TestAllFilesInManifestExist:
    """Verify all files referenced in manifest still exist."""

    def test_all_manifest_files_exist(self):
        """Every file in the manifest must exist."""
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()

        missing = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split('  ', 1)
            if len(parts) == 2:
                rel_path = parts[1]
                full_path = os.path.join(AUDIT_DIR, rel_path)
                if not os.path.isfile(full_path):
                    missing.append(rel_path)

        assert not missing, f"Files missing from manifest: {missing}"


class TestDataDirectoryIntact:
    """Verify the data directory structure is intact."""

    def test_data_directory_exists(self):
        """The data/ subdirectory must still exist."""
        assert os.path.isdir(DATA_DIR), f"Data directory {DATA_DIR} no longer exists"

    def test_data_directory_file_count(self):
        """The data directory should still have approximately 40 files."""
        files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
        assert len(files) >= 35, (
            f"Data directory should have ~40 files but only has {len(files)}. "
            f"Files may have been deleted."
        )


class TestNoHardcodedResults:
    """Ensure the fix doesn't involve hardcoding or bypassing verification."""

    def test_checker_still_reads_manifest(self):
        """The checker should still read from manifest.sha256."""
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        assert 'manifest' in content.lower(), (
            "check_integrity.py no longer references the manifest file. "
            "The fix should not bypass manifest verification."
        )

    def test_checker_opens_files_for_reading(self):
        """The checker should still open files to read their contents."""
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        # Should have open() calls for reading files
        assert 'open(' in content, (
            "check_integrity.py no longer appears to open files. "
            "The fix should not bypass file reading."
        )
