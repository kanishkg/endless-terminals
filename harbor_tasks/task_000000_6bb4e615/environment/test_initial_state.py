# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the integrity audit debugging task.
"""

import os
import subprocess
import hashlib
import pytest

AUDIT_DIR = "/home/user/audit"
MANIFEST_FILE = os.path.join(AUDIT_DIR, "manifest.sha256")
CHECKER_SCRIPT = os.path.join(AUDIT_DIR, "check_integrity.py")
DATA_DIR = os.path.join(AUDIT_DIR, "data")

# The three files that should be "failing" due to CRLF line endings
CRLF_FILES = [
    "data/report_2024q1.csv",
    "data/config.json",
    "data/notes.txt",
]


class TestAuditDirectoryStructure:
    """Test that the audit directory structure exists as expected."""

    def test_audit_directory_exists(self):
        """The /home/user/audit directory must exist."""
        assert os.path.isdir(AUDIT_DIR), f"Audit directory {AUDIT_DIR} does not exist"

    def test_manifest_file_exists(self):
        """The manifest.sha256 file must exist."""
        assert os.path.isfile(MANIFEST_FILE), f"Manifest file {MANIFEST_FILE} does not exist"

    def test_checker_script_exists(self):
        """The check_integrity.py script must exist."""
        assert os.path.isfile(CHECKER_SCRIPT), f"Checker script {CHECKER_SCRIPT} does not exist"

    def test_data_directory_exists(self):
        """The data/ subdirectory must exist."""
        assert os.path.isdir(DATA_DIR), f"Data directory {DATA_DIR} does not exist"


class TestDataDirectoryContents:
    """Test that the data directory contains the expected files."""

    def test_data_directory_has_files(self):
        """The data/ directory should contain approximately 40 files."""
        files = [f for f in os.listdir(DATA_DIR) if os.path.isfile(os.path.join(DATA_DIR, f))]
        assert len(files) >= 35, f"Expected ~40 files in data/, found {len(files)}"

    def test_data_directory_has_various_types(self):
        """The data/ directory should contain files of various types."""
        files = os.listdir(DATA_DIR)
        extensions = set()
        for f in files:
            if '.' in f:
                ext = f.rsplit('.', 1)[-1]
                extensions.add(ext)

        expected_types = {'txt', 'bin', 'csv', 'json'}
        found_types = extensions & expected_types
        assert len(found_types) >= 3, f"Expected various file types (.txt, .bin, .csv, .json), found extensions: {extensions}"

    def test_crlf_files_exist(self):
        """The three CRLF files that should fail must exist."""
        for rel_path in CRLF_FILES:
            full_path = os.path.join(AUDIT_DIR, rel_path)
            assert os.path.isfile(full_path), f"Expected CRLF file {full_path} does not exist"


class TestManifestFormat:
    """Test that the manifest file has the correct format."""

    def test_manifest_has_content(self):
        """The manifest file should have content."""
        with open(MANIFEST_FILE, 'r') as f:
            content = f.read()
        assert len(content) > 0, "Manifest file is empty"

    def test_manifest_format_is_sha256sum_compatible(self):
        """The manifest should follow sha256sum -c format: <hash>  <path>"""
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()

        assert len(lines) >= 35, f"Expected ~40 lines in manifest, found {len(lines)}"

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            # Format should be: 64 hex chars, two spaces, then a path
            parts = line.split('  ', 1)  # Split on double space
            assert len(parts) == 2, f"Line {i+1} does not have correct format (hash  path): {line}"
            hash_part, path_part = parts
            assert len(hash_part) == 64, f"Line {i+1} hash is not 64 characters: {hash_part}"
            assert all(c in '0123456789abcdef' for c in hash_part.lower()), f"Line {i+1} hash contains non-hex characters: {hash_part}"

    def test_manifest_references_existing_files(self):
        """All files referenced in the manifest should exist."""
        with open(MANIFEST_FILE, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            parts = line.split('  ', 1)
            if len(parts) == 2:
                rel_path = parts[1]
                full_path = os.path.join(AUDIT_DIR, rel_path)
                assert os.path.isfile(full_path), f"Manifest references non-existent file: {rel_path}"


class TestManifestCorrectness:
    """Test that the manifest hashes are correct (using sha256sum)."""

    def test_sha256sum_verifies_all_files(self):
        """Running sha256sum -c on the manifest should pass for all files."""
        result = subprocess.run(
            ['sha256sum', '-c', 'manifest.sha256'],
            cwd=AUDIT_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"sha256sum -c failed. This means the manifest is incorrect or files are corrupted.\nstdout: {result.stdout}\nstderr: {result.stderr}"


class TestCRLFFiles:
    """Test that the three problematic files contain CRLF line endings."""

    def test_crlf_files_have_carriage_returns(self):
        """The three 'failing' files must contain CRLF (\\r\\n) line endings."""
        for rel_path in CRLF_FILES:
            full_path = os.path.join(AUDIT_DIR, rel_path)
            with open(full_path, 'rb') as f:
                content = f.read()

            assert b'\r\n' in content, f"File {rel_path} does not contain CRLF line endings - it should have Windows-style line endings"


class TestCheckerScript:
    """Test the checker script properties."""

    def test_checker_is_python_script(self):
        """The checker script should be a Python file."""
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        # Should contain Python-like content
        assert 'def ' in content or 'import ' in content or 'open(' in content, \
            "check_integrity.py does not appear to be a Python script"

    def test_checker_reads_manifest(self):
        """The checker script should reference the manifest file."""
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        assert 'manifest' in content.lower(), \
            "check_integrity.py does not appear to reference the manifest"

    def test_checker_uses_sha256(self):
        """The checker script should use SHA256 hashing."""
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        assert 'sha256' in content.lower() or 'hashlib' in content, \
            "check_integrity.py does not appear to use SHA256 hashing"

    def test_checker_has_text_mode_bug(self):
        """The checker script should have the text mode bug (opens files without 'rb')."""
        with open(CHECKER_SCRIPT, 'r') as f:
            content = f.read()

        # Look for evidence of text mode file opening for hashing
        # The bug is using open(path, 'r') instead of open(path, 'rb')
        # We check that there's an open() call that doesn't use 'rb' for reading file content
        has_text_mode_open = ("open(" in content and 
                             ("'r'" in content or '"r"' in content or 
                              "open(path)" in content or "open(filepath)" in content or
                              "open(file)" in content))

        # Also check it's not already using binary mode everywhere
        uses_binary_for_all = content.count("'rb'") + content.count('"rb"')
        uses_text_mode = content.count("'r'") + content.count('"r"') + content.count("open(") - uses_binary_for_all

        # The script should have some indication of text mode usage
        assert has_text_mode_open or uses_text_mode > uses_binary_for_all, \
            "check_integrity.py appears to already use binary mode correctly - the bug may have been pre-fixed"

    def test_checker_is_executable_as_python(self):
        """The checker script should be runnable with Python."""
        result = subprocess.run(
            ['python3', '-m', 'py_compile', CHECKER_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"check_integrity.py has syntax errors: {result.stderr}"


class TestCheckerBehavior:
    """Test that the checker script exhibits the expected buggy behavior."""

    def test_checker_reports_failures(self):
        """The checker script should currently report failures (exit non-zero or show failures)."""
        result = subprocess.run(
            ['python3', CHECKER_SCRIPT],
            cwd=AUDIT_DIR,
            capture_output=True,
            text=True
        )

        # The script should either exit non-zero OR print failure messages
        has_failures = (result.returncode != 0 or 
                       'fail' in result.stdout.lower() or 
                       'fail' in result.stderr.lower() or
                       'error' in result.stdout.lower() or
                       'mismatch' in result.stdout.lower())

        assert has_failures, f"check_integrity.py should report failures but appears to pass.\nreturncode: {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"

    def test_checker_reports_approximately_3_failures(self):
        """The checker should report approximately 3 failures (the CRLF files)."""
        result = subprocess.run(
            ['python3', CHECKER_SCRIPT],
            cwd=AUDIT_DIR,
            capture_output=True,
            text=True
        )

        output = result.stdout + result.stderr
        output_lower = output.lower()

        # Count failure indicators
        fail_count = output_lower.count('fail')

        # Also check if the specific files are mentioned
        mentions_crlf_files = sum(1 for f in CRLF_FILES if os.path.basename(f) in output or f in output)

        # We expect around 3 failures
        assert fail_count >= 2 or mentions_crlf_files >= 2, \
            f"Expected ~3 failures to be reported. Output: {output}"


class TestToolsAvailable:
    """Test that required tools are available."""

    def test_sha256sum_available(self):
        """sha256sum command must be available."""
        result = subprocess.run(['which', 'sha256sum'], capture_output=True)
        assert result.returncode == 0, "sha256sum command is not available"

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(['python3', '--version'], capture_output=True)
        assert result.returncode == 0, "python3 is not available"

    def test_xxd_available(self):
        """xxd command must be available."""
        result = subprocess.run(['which', 'xxd'], capture_output=True)
        assert result.returncode == 0, "xxd command is not available"

    def test_file_command_available(self):
        """file command must be available."""
        result = subprocess.run(['which', 'file'], capture_output=True)
        assert result.returncode == 0, "file command is not available"

    def test_od_available(self):
        """od command must be available."""
        result = subprocess.run(['which', 'od'], capture_output=True)
        assert result.returncode == 0, "od command is not available"


class TestDirectoryWritable:
    """Test that the audit directory is writable."""

    def test_audit_directory_writable(self):
        """The audit directory must be writable."""
        assert os.access(AUDIT_DIR, os.W_OK), f"{AUDIT_DIR} is not writable"

    def test_checker_script_writable(self):
        """The checker script must be writable (so it can be fixed)."""
        assert os.access(CHECKER_SCRIPT, os.W_OK), f"{CHECKER_SCRIPT} is not writable"
