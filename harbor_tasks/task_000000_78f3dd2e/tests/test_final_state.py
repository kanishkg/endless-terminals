# test_final_state.py
"""
Tests to validate the final state after the student has fixed the backup verification issue.
The fix should handle the CRLF line ending issue in manifest.txt so that verify.sh exits 0.
"""

import os
import subprocess
import pytest
import hashlib

BASE_DIR = "/home/user/backup-check"
DATA_DIR = os.path.join(BASE_DIR, "data")
MANIFEST_FILE = os.path.join(BASE_DIR, "manifest.txt")
VERIFY_SCRIPT = os.path.join(BASE_DIR, "verify.sh")

# Expected files in the manifest
EXPECTED_DATA_FILES = [
    "data/config.json",
    "data/database.sql",
    "data/logs/app.log",
    "data/logs/error.log",
    "data/assets/logo.png",
    "data/assets/style.css",
    "data/readme.txt",
    "data/backup_meta.xml",
]


class TestVerifyScriptSucceeds:
    """Test that verify.sh now succeeds after the fix."""

    def test_verify_script_exits_zero(self):
        """Running verify.sh should now exit 0 (success)."""
        result = subprocess.run(
            ["./verify.sh"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"verify.sh should exit 0 after fix, but exited {result.returncode}.\n" \
            f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_verify_script_no_mismatch_output(self):
        """Running verify.sh should not report any mismatches."""
        result = subprocess.run(
            ["./verify.sh"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        output = (result.stdout + result.stderr).lower()
        # Should not contain mismatch indicators
        assert "mismatch" not in output, \
            f"verify.sh output should not contain 'mismatch' after fix.\nOutput: {result.stdout + result.stderr}"


class TestDataFilesUnchanged:
    """Test that the data files remain byte-identical (invariant)."""

    def test_all_data_files_exist(self):
        """All 8 data files must still exist."""
        for relative_path in EXPECTED_DATA_FILES:
            full_path = os.path.join(BASE_DIR, relative_path)
            assert os.path.isfile(full_path), f"Data file {full_path} must still exist"

    def test_data_files_hashes_match_manifest(self):
        """Data file hashes must still match the hash values in the manifest."""
        # Read manifest and extract hash values (stripping any \r)
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()

        lines = [line.rstrip(b"\r") for line in content.split(b"\n") if line.strip(b"\r").strip()]

        for line in lines:
            line_str = line.decode("utf-8")
            parts = line_str.split("  ", 1)
            if len(parts) != 2:
                # Try single space as fallback
                parts = line_str.split(" ", 1)
            if len(parts) != 2:
                continue

            expected_hash, relative_path = parts
            expected_hash = expected_hash.strip()
            relative_path = relative_path.strip()
            full_path = os.path.join(BASE_DIR, relative_path)

            if not os.path.isfile(full_path):
                continue

            # Compute actual hash
            result = subprocess.run(
                ["sha256sum", full_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"sha256sum failed for {full_path}"

            computed_hash = result.stdout.split()[0]
            assert computed_hash.lower() == expected_hash.lower(), \
                f"Data file {relative_path} has been modified! " \
                f"Expected hash {expected_hash}, got {computed_hash}. " \
                f"Data files must remain byte-identical."


class TestManifestHashesUnchanged:
    """Test that the hash values in manifest.txt are unchanged (invariant)."""

    def test_manifest_has_8_entries(self):
        """The manifest must still contain exactly 8 entries."""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        # Count non-empty lines (accounting for possible CRLF or LF)
        lines = [line for line in content.replace(b"\r\n", b"\n").split(b"\n") if line.strip()]
        assert len(lines) == 8, f"Manifest should still have 8 entries, found {len(lines)}"

    def test_manifest_hash_values_are_valid_sha256(self):
        """All hash values in manifest must be valid 64-character hex strings."""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()

        lines = [line.rstrip(b"\r") for line in content.split(b"\n") if line.strip(b"\r").strip()]

        for line in lines:
            line_str = line.decode("utf-8")
            parts = line_str.split("  ", 1)
            if len(parts) != 2:
                parts = line_str.split(" ", 1)

            assert len(parts) >= 1, f"Could not parse manifest line: {line_str}"
            hash_part = parts[0].strip()

            assert len(hash_part) == 64, \
                f"Hash should be 64 characters, got {len(hash_part)}: {hash_part}"
            assert all(c in "0123456789abcdefABCDEF" for c in hash_part), \
                f"Hash should be hex: {hash_part}"


class TestScriptStillPerformsVerification:
    """Test that verify.sh still performs actual SHA256 verification (anti-shortcut)."""

    def test_script_still_uses_sha256sum(self):
        """The verify.sh script must still use sha256sum."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "sha256sum" in content, \
            "verify.sh must still use sha256sum for hash computation"

    def test_script_not_unconditionally_exiting_zero(self):
        """The script should not be gutted to unconditionally exit 0."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()

        lines = content.split("\n")

        # Check for suspicious patterns that bypass verification
        suspicious_patterns = [
            # Script that just exits 0 without doing anything
            (content.strip().endswith("exit 0") and "sha256sum" not in content),
            # Script starts with exit 0
            any(line.strip() == "exit 0" for line in lines[:5] if not line.strip().startswith("#")),
        ]

        assert not any(suspicious_patterns), \
            "verify.sh appears to be gutted to unconditionally exit 0"

    def test_script_still_reads_manifest(self):
        """The verify.sh script must still reference the manifest."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "manifest" in content.lower(), \
            "verify.sh must still reference the manifest file"

    def test_script_detects_modified_file(self):
        """If a data file is modified, verify.sh must exit non-zero."""
        test_file = os.path.join(BASE_DIR, "data/readme.txt")

        # Read original content
        with open(test_file, "rb") as f:
            original_content = f.read()

        try:
            # Modify the file
            with open(test_file, "ab") as f:
                f.write(b"x")

            # Run verify.sh - should now fail
            result = subprocess.run(
                ["./verify.sh"],
                cwd=BASE_DIR,
                capture_output=True,
                text=True
            )

            assert result.returncode != 0, \
                f"verify.sh should exit non-zero when a file is modified, " \
                f"but it exited {result.returncode}. " \
                f"This suggests the script is not actually verifying hashes."
        finally:
            # Restore original content
            with open(test_file, "wb") as f:
                f.write(original_content)

    def test_script_succeeds_after_restore(self):
        """After restoring the modified file, verify.sh should succeed again."""
        # This runs after the previous test restored the file
        result = subprocess.run(
            ["./verify.sh"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"verify.sh should succeed after file is restored. " \
            f"Exit code: {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"


class TestVerifyScriptStructure:
    """Test that verify.sh maintains proper structure."""

    def test_script_is_executable(self):
        """The verify.sh script must be executable."""
        assert os.access(VERIFY_SCRIPT, os.X_OK), \
            f"Script {VERIFY_SCRIPT} must be executable"

    def test_script_has_shebang(self):
        """The verify.sh script should have a shell shebang."""
        with open(VERIFY_SCRIPT, "r") as f:
            first_line = f.readline()
        assert first_line.startswith("#!"), \
            "verify.sh should have a shebang line"
        assert "sh" in first_line or "bash" in first_line, \
            "verify.sh should be a shell script"


class TestAllFilesVerified:
    """Test that all 8 files are being verified."""

    def test_verify_processes_all_files(self):
        """The verification should process all 8 files."""
        # We can infer this by checking the script runs without error
        # and the manifest still has 8 entries
        result = subprocess.run(
            ["./verify.sh"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, \
            f"verify.sh should process all files successfully. " \
            f"Exit code: {result.returncode}"

        # Verify manifest still has all entries
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        lines = [line for line in content.replace(b"\r\n", b"\n").split(b"\n") if line.strip()]
        assert len(lines) == 8, \
            f"Manifest should still have 8 entries for verification"
