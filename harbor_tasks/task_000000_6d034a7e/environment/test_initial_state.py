# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the checksum verification fix task.
"""

import os
import subprocess
import pytest

INGEST_DIR = "/home/user/ingest"
PACKAGES_DIR = "/home/user/ingest/packages"
CHECKSUMS_FILE = "/home/user/ingest/checksums.sha256"
VERIFY_SCRIPT = "/home/user/ingest/verify.sh"

EXPECTED_PACKAGES = [
    "alpha-1.2.tar.gz",
    "beta-3.0.tar.gz",
    "gamma-2.1.tar.gz",
    "delta-0.9.tar.gz",
    "epsilon-1.0.tar.gz",
]

# These are the filenames that should appear in checksums.sha256 with wrong case
WRONG_CASE_FILENAMES = ["Beta-3.0.tar.gz", "Delta-0.9.tar.gz", "Epsilon-1.0.tar.gz"]
CORRECT_CASE_FILENAMES = ["alpha-1.2.tar.gz", "gamma-2.1.tar.gz"]


class TestIngestDirectoryStructure:
    """Test that the ingest directory structure exists."""

    def test_ingest_directory_exists(self):
        """The /home/user/ingest directory must exist."""
        assert os.path.isdir(INGEST_DIR), f"Directory {INGEST_DIR} does not exist"

    def test_packages_directory_exists(self):
        """The /home/user/ingest/packages directory must exist."""
        assert os.path.isdir(PACKAGES_DIR), f"Directory {PACKAGES_DIR} does not exist"

    def test_checksums_file_exists(self):
        """The checksums.sha256 file must exist."""
        assert os.path.isfile(CHECKSUMS_FILE), f"File {CHECKSUMS_FILE} does not exist"

    def test_verify_script_exists(self):
        """The verify.sh script must exist."""
        assert os.path.isfile(VERIFY_SCRIPT), f"File {VERIFY_SCRIPT} does not exist"

    def test_verify_script_is_executable_or_readable(self):
        """The verify.sh script must be readable (can be run with bash)."""
        assert os.access(VERIFY_SCRIPT, os.R_OK), f"File {VERIFY_SCRIPT} is not readable"


class TestPackageFiles:
    """Test that all expected package files exist."""

    def test_all_five_packages_exist(self):
        """All five .tar.gz package files must exist in packages directory."""
        for pkg in EXPECTED_PACKAGES:
            pkg_path = os.path.join(PACKAGES_DIR, pkg)
            assert os.path.isfile(pkg_path), f"Package file {pkg_path} does not exist"

    def test_exactly_five_tar_gz_files(self):
        """There should be exactly 5 .tar.gz files in packages directory."""
        files = [f for f in os.listdir(PACKAGES_DIR) if f.endswith(".tar.gz")]
        assert len(files) == 5, f"Expected 5 .tar.gz files, found {len(files)}: {files}"

    def test_package_files_are_lowercase(self):
        """All package files should have lowercase names."""
        for pkg in EXPECTED_PACKAGES:
            pkg_path = os.path.join(PACKAGES_DIR, pkg)
            assert os.path.isfile(pkg_path), f"Lowercase package file {pkg_path} does not exist"


class TestChecksumsFile:
    """Test the checksums.sha256 file format and content."""

    def test_checksums_file_has_five_lines(self):
        """The checksums file should have exactly 5 lines (one per package)."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        assert len(lines) == 5, f"Expected 5 lines in checksums file, found {len(lines)}"

    def test_checksums_file_format(self):
        """Each line should have format: <64-char-hash>  <filename> (two spaces)."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        for line in lines:
            # sha256sum format: 64 hex chars, two spaces, filename
            parts = line.split("  ")  # two spaces
            assert len(parts) == 2, f"Line does not have two-space separator: {line}"
            hash_part, filename = parts
            assert len(hash_part) == 64, f"Hash is not 64 characters: {hash_part}"
            assert all(c in "0123456789abcdef" for c in hash_part.lower()), \
                f"Hash contains non-hex characters: {hash_part}"
            assert filename.endswith(".tar.gz"), f"Filename doesn't end with .tar.gz: {filename}"

    def test_checksums_file_contains_case_mismatches(self):
        """The checksums file should contain some uppercase filenames (the bug)."""
        with open(CHECKSUMS_FILE, "r") as f:
            content = f.read()

        # Check that at least some of the wrong-case filenames are present
        found_wrong_case = []
        for wrong_name in WRONG_CASE_FILENAMES:
            if wrong_name in content:
                found_wrong_case.append(wrong_name)

        assert len(found_wrong_case) > 0, \
            f"Expected to find uppercase filenames in checksums.sha256, but found none. " \
            f"The initial state should have case mismatches for: {WRONG_CASE_FILENAMES}"

    def test_checksums_file_has_correct_lowercase_entries(self):
        """Some entries should already be correct (lowercase)."""
        with open(CHECKSUMS_FILE, "r") as f:
            content = f.read()

        found_correct = []
        for correct_name in CORRECT_CASE_FILENAMES:
            if correct_name in content:
                found_correct.append(correct_name)

        assert len(found_correct) > 0, \
            f"Expected some correct lowercase entries in checksums.sha256"


class TestVerifyScript:
    """Test the verify.sh script content and behavior."""

    def test_verify_script_uses_sha256sum(self):
        """The verify script should use sha256sum for verification."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "sha256sum" in content, "verify.sh should use sha256sum command"

    def test_verify_script_references_checksums_file(self):
        """The verify script should reference the checksums file."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "checksums.sha256" in content, "verify.sh should reference checksums.sha256"

    def test_verify_script_currently_fails(self):
        """Running verify.sh should currently fail (exit 1) due to the case mismatch bug."""
        result = subprocess.run(
            ["bash", VERIFY_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, \
            f"verify.sh should fail (exit 1) in initial state, but got exit code {result.returncode}. " \
            f"stdout: {result.stdout}, stderr: {result.stderr}"

    def test_verify_script_outputs_mismatch_message(self):
        """The verify script should output 'checksum mismatch' on failure."""
        result = subprocess.run(
            ["bash", VERIFY_SCRIPT],
            capture_output=True,
            text=True
        )
        assert "checksum mismatch" in result.stdout or "checksum mismatch" in result.stderr, \
            f"verify.sh should output 'checksum mismatch', got stdout: {result.stdout}, stderr: {result.stderr}"


class TestSystemTools:
    """Test that required system tools are available."""

    def test_sha256sum_available(self):
        """sha256sum command must be available."""
        result = subprocess.run(["which", "sha256sum"], capture_output=True)
        assert result.returncode == 0, "sha256sum command is not available"

    def test_bash_available(self):
        """bash must be available."""
        result = subprocess.run(["which", "bash"], capture_output=True)
        assert result.returncode == 0, "bash is not available"


class TestDirectoryPermissions:
    """Test that the ingest directory and contents are writable."""

    def test_ingest_directory_writable(self):
        """The ingest directory should be writable."""
        assert os.access(INGEST_DIR, os.W_OK), f"{INGEST_DIR} is not writable"

    def test_checksums_file_writable(self):
        """The checksums.sha256 file should be writable."""
        assert os.access(CHECKSUMS_FILE, os.W_OK), f"{CHECKSUMS_FILE} is not writable"

    def test_packages_directory_writable(self):
        """The packages directory should be writable."""
        assert os.access(PACKAGES_DIR, os.W_OK), f"{PACKAGES_DIR} is not writable"
