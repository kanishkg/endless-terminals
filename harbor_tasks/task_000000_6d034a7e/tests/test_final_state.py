# test_final_state.py
"""
Tests to validate the final state after the student has fixed the checksum
verification issue. The fix should correct the filename case mismatches in
checksums.sha256 so that verify.sh passes.
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


class TestVerifyScriptPasses:
    """Test that the verify.sh script now passes."""

    def test_verify_script_exits_zero(self):
        """Running verify.sh should now exit 0 (success)."""
        result = subprocess.run(
            ["bash", VERIFY_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"verify.sh should pass (exit 0) after fix, but got exit code {result.returncode}. " \
            f"stdout: {result.stdout}, stderr: {result.stderr}"

    def test_verify_script_outputs_success_message(self):
        """The verify script should output 'all checksums valid' on success."""
        result = subprocess.run(
            ["bash", VERIFY_SCRIPT],
            capture_output=True,
            text=True
        )
        assert "all checksums valid" in result.stdout, \
            f"verify.sh should output 'all checksums valid', got stdout: {result.stdout}"


class TestPackageFilesIntact:
    """Test that all package files still exist with original names."""

    def test_all_five_packages_exist(self):
        """All five .tar.gz package files must still exist."""
        for pkg in EXPECTED_PACKAGES:
            pkg_path = os.path.join(PACKAGES_DIR, pkg)
            assert os.path.isfile(pkg_path), \
                f"Package file {pkg_path} does not exist - files should not be renamed or deleted"

    def test_exactly_five_tar_gz_files(self):
        """There should still be exactly 5 .tar.gz files."""
        files = [f for f in os.listdir(PACKAGES_DIR) if f.endswith(".tar.gz")]
        assert len(files) == 5, f"Expected 5 .tar.gz files, found {len(files)}: {files}"

    def test_all_packages_are_lowercase(self):
        """All package files should have lowercase names (not renamed to uppercase)."""
        files = os.listdir(PACKAGES_DIR)
        tar_gz_files = [f for f in files if f.endswith(".tar.gz")]

        for f in tar_gz_files:
            # Check that filename matches expected lowercase pattern
            assert f == f.lower(), \
                f"Package file {f} should be lowercase - files should not be renamed"

    def test_package_names_match_expected_pattern(self):
        """Package files should match the expected naming pattern."""
        files = os.listdir(PACKAGES_DIR)
        tar_gz_files = sorted([f for f in files if f.endswith(".tar.gz")])

        import re
        pattern = re.compile(r'^(alpha|beta|gamma|delta|epsilon)-[0-9.]+\.tar\.gz$')

        matching = [f for f in tar_gz_files if pattern.match(f)]
        assert len(matching) == 5, \
            f"Expected 5 files matching pattern, found {len(matching)}: {matching}"


class TestChecksumsFileValid:
    """Test that checksums.sha256 still exists and contains valid hashes."""

    def test_checksums_file_exists(self):
        """The checksums.sha256 file must still exist."""
        assert os.path.isfile(CHECKSUMS_FILE), \
            f"File {CHECKSUMS_FILE} does not exist - should not be deleted"

    def test_checksums_file_has_five_lines(self):
        """The checksums file should still have 5 lines."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
        assert len(lines) == 5, \
            f"Expected 5 lines in checksums file, found {len(lines)}"

    def test_checksums_file_format_valid(self):
        """Each line should have valid sha256sum format."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        for line in lines:
            # sha256sum format: 64 hex chars, two spaces, filename
            parts = line.split("  ")  # two spaces
            assert len(parts) == 2, \
                f"Line does not have two-space separator: {line}"
            hash_part, filename = parts
            assert len(hash_part) == 64, \
                f"Hash is not 64 characters: {hash_part}"
            assert all(c in "0123456789abcdef" for c in hash_part.lower()), \
                f"Hash contains non-hex characters: {hash_part}"
            assert filename.endswith(".tar.gz"), \
                f"Filename doesn't end with .tar.gz: {filename}"

    def test_checksums_file_contains_real_hashes(self):
        """Checksums should be real sha256 hashes, not dummy values."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        hashes = set()
        for line in lines:
            parts = line.split("  ")
            if len(parts) == 2:
                hashes.add(parts[0].lower())

        # All hashes should be unique (not all the same dummy value)
        assert len(hashes) == 5, \
            f"Expected 5 unique hashes, found {len(hashes)} - checksums may be dummy values"

        # Hashes should not be obvious dummy values
        dummy_patterns = ["0" * 64, "a" * 64, "f" * 64, "1234567890" * 6 + "1234"]
        for h in hashes:
            assert h not in dummy_patterns, \
                f"Hash {h} appears to be a dummy value"


class TestSha256sumDirectVerification:
    """Test that sha256sum -c directly verifies the checksums (anti-shortcut)."""

    def test_sha256sum_check_passes(self):
        """Running sha256sum -c directly from packages dir should pass."""
        result = subprocess.run(
            ["sha256sum", "-c", CHECKSUMS_FILE],
            capture_output=True,
            text=True,
            cwd=PACKAGES_DIR
        )
        assert result.returncode == 0, \
            f"sha256sum -c should pass, but got exit code {result.returncode}. " \
            f"This means checksums.sha256 is not correctly fixed. " \
            f"stdout: {result.stdout}, stderr: {result.stderr}"

    def test_all_files_report_ok(self):
        """sha256sum -c should report OK for all 5 files."""
        result = subprocess.run(
            ["sha256sum", "-c", CHECKSUMS_FILE],
            capture_output=True,
            text=True,
            cwd=PACKAGES_DIR
        )

        ok_count = result.stdout.count(": OK")
        assert ok_count == 5, \
            f"Expected 5 files to report OK, found {ok_count}. Output: {result.stdout}"


class TestHashesMatchActualFiles:
    """Test that the hashes in checksums.sha256 match the actual file contents."""

    def test_computed_hashes_match_checksums_file(self):
        """Compute sha256 of each file and verify it matches checksums.sha256."""
        # Read the checksums file
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        checksum_dict = {}
        for line in lines:
            parts = line.split("  ")
            if len(parts) == 2:
                hash_val, filename = parts
                checksum_dict[filename] = hash_val.lower()

        # Compute actual hashes
        for pkg in EXPECTED_PACKAGES:
            pkg_path = os.path.join(PACKAGES_DIR, pkg)
            result = subprocess.run(
                ["sha256sum", pkg_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"Failed to compute hash for {pkg}"

            computed_hash = result.stdout.split()[0].lower()

            # The file should be in the checksums dict
            assert pkg in checksum_dict, \
                f"File {pkg} not found in checksums.sha256 - filenames may still have wrong case"

            assert checksum_dict[pkg] == computed_hash, \
                f"Hash mismatch for {pkg}: checksums.sha256 has {checksum_dict[pkg]}, " \
                f"but computed hash is {computed_hash}"


class TestVerifyScriptNotNeutered:
    """Test that verify.sh still performs real verification."""

    def test_verify_script_still_uses_sha256sum(self):
        """verify.sh should still use sha256sum command."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "sha256sum" in content, \
            "verify.sh should still use sha256sum - script should not be neutered"

    def test_verify_script_still_references_checksums(self):
        """verify.sh should still reference checksums.sha256."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "checksums.sha256" in content, \
            "verify.sh should still reference checksums.sha256"

    def test_verify_script_not_hardcoded_to_pass(self):
        """verify.sh should not be hardcoded to always exit 0."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()

        # Check that the script still has conditional logic
        assert "if" in content or "&&" in content or "||" in content, \
            "verify.sh should have conditional logic, not be hardcoded to pass"

        # Check it's not just "exit 0" at the start
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
        if len(lines) >= 2:
            # Second non-comment line shouldn't be just "exit 0"
            assert lines[1] != "exit 0", \
                "verify.sh appears to be hardcoded to exit 0"


class TestFilenamesInChecksumsAreLowercase:
    """Test that the filenames in checksums.sha256 are now lowercase."""

    def test_all_filenames_lowercase(self):
        """All filenames in checksums.sha256 should be lowercase."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        for line in lines:
            parts = line.split("  ")
            if len(parts) == 2:
                filename = parts[1]
                assert filename == filename.lower(), \
                    f"Filename {filename} in checksums.sha256 should be lowercase"

    def test_filenames_match_actual_files(self):
        """Filenames in checksums.sha256 should match actual file names exactly."""
        with open(CHECKSUMS_FILE, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        checksums_filenames = set()
        for line in lines:
            parts = line.split("  ")
            if len(parts) == 2:
                checksums_filenames.add(parts[1])

        actual_files = set(EXPECTED_PACKAGES)

        assert checksums_filenames == actual_files, \
            f"Filenames in checksums.sha256 don't match actual files. " \
            f"In checksums: {checksums_filenames}, Actual: {actual_files}"
