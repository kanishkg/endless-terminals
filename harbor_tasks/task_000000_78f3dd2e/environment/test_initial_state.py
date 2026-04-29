# test_initial_state.py
"""
Tests to validate the initial state before the student performs the backup verification fix task.
"""

import os
import subprocess
import pytest

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


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_backup_check_directory_exists(self):
        """The /home/user/backup-check directory must exist."""
        assert os.path.isdir(BASE_DIR), f"Directory {BASE_DIR} does not exist"

    def test_data_directory_exists(self):
        """The /home/user/backup-check/data directory must exist."""
        assert os.path.isdir(DATA_DIR), f"Directory {DATA_DIR} does not exist"

    def test_logs_subdirectory_exists(self):
        """The /home/user/backup-check/data/logs directory must exist."""
        logs_dir = os.path.join(DATA_DIR, "logs")
        assert os.path.isdir(logs_dir), f"Directory {logs_dir} does not exist"

    def test_assets_subdirectory_exists(self):
        """The /home/user/backup-check/data/assets directory must exist."""
        assets_dir = os.path.join(DATA_DIR, "assets")
        assert os.path.isdir(assets_dir), f"Directory {assets_dir} does not exist"


class TestRequiredFiles:
    """Test that required files exist."""

    def test_verify_script_exists(self):
        """The verify.sh script must exist."""
        assert os.path.isfile(VERIFY_SCRIPT), f"Script {VERIFY_SCRIPT} does not exist"

    def test_verify_script_is_executable(self):
        """The verify.sh script must be executable."""
        assert os.access(VERIFY_SCRIPT, os.X_OK), f"Script {VERIFY_SCRIPT} is not executable"

    def test_manifest_file_exists(self):
        """The manifest.txt file must exist."""
        assert os.path.isfile(MANIFEST_FILE), f"Manifest file {MANIFEST_FILE} does not exist"

    @pytest.mark.parametrize("relative_path", EXPECTED_DATA_FILES)
    def test_data_file_exists(self, relative_path):
        """Each data file referenced in the manifest must exist."""
        full_path = os.path.join(BASE_DIR, relative_path)
        assert os.path.isfile(full_path), f"Data file {full_path} does not exist"


class TestManifestFormat:
    """Test the manifest file format and content."""

    def test_manifest_has_8_entries(self):
        """The manifest must contain exactly 8 entries."""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        # Count non-empty lines (accounting for possible CRLF)
        lines = [line for line in content.split(b"\n") if line.strip(b"\r").strip()]
        assert len(lines) == 8, f"Manifest should have 8 entries, found {len(lines)}"

    def test_manifest_has_windows_line_endings(self):
        """The manifest must have Windows line endings (CRLF) - this is the bug."""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        assert b"\r\n" in content, "Manifest file should have Windows line endings (CRLF) - this is the expected bug"

    def test_manifest_format_is_hash_space_space_path(self):
        """Each manifest line should be in format: <sha256hash>  <filepath>"""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        lines = [line.rstrip(b"\r") for line in content.split(b"\n") if line.strip(b"\r").strip()]

        for line in lines:
            line_str = line.decode("utf-8")
            parts = line_str.split("  ", 1)  # Split on two spaces
            assert len(parts) == 2, f"Line should have hash and path separated by two spaces: {line_str}"
            hash_part, path_part = parts
            # SHA256 hash is 64 hex characters
            assert len(hash_part) == 64, f"Hash should be 64 characters, got {len(hash_part)}: {hash_part}"
            assert all(c in "0123456789abcdef" for c in hash_part.lower()), f"Hash should be hex: {hash_part}"

    def test_manifest_references_expected_files(self):
        """The manifest should reference all expected data files."""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        lines = [line.rstrip(b"\r").decode("utf-8") for line in content.split(b"\n") if line.strip(b"\r").strip()]

        manifest_paths = []
        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) == 2:
                manifest_paths.append(parts[1])

        for expected_file in EXPECTED_DATA_FILES:
            assert expected_file in manifest_paths, f"Expected file {expected_file} not found in manifest"


class TestVerifyScript:
    """Test the verify.sh script properties."""

    def test_verify_script_is_bash(self):
        """The verify.sh script should be a bash script."""
        with open(VERIFY_SCRIPT, "r") as f:
            first_line = f.readline()
        assert "bash" in first_line or "sh" in first_line, "verify.sh should have a shell shebang"

    def test_verify_script_uses_sha256sum(self):
        """The verify.sh script should use sha256sum for hash computation."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "sha256sum" in content, "verify.sh should use sha256sum for hash computation"

    def test_verify_script_reads_manifest(self):
        """The verify.sh script should read the manifest file."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        assert "manifest" in content.lower(), "verify.sh should reference the manifest file"

    def test_verify_script_has_comparison_logic(self):
        """The verify.sh script should have comparison logic."""
        with open(VERIFY_SCRIPT, "r") as f:
            content = f.read()
        # Should have some form of comparison
        has_comparison = ("!=" in content or "-ne" in content or "diff" in content.lower() 
                         or "compare" in content.lower() or "match" in content.lower())
        assert has_comparison, "verify.sh should have comparison logic"


class TestHashesMatch:
    """Test that the actual file hashes match the manifest (ignoring CRLF issue)."""

    def test_file_hashes_match_manifest_values(self):
        """The actual file hashes should match manifest values (ignoring \\r)."""
        with open(MANIFEST_FILE, "rb") as f:
            content = f.read()
        lines = [line.rstrip(b"\r").decode("utf-8") for line in content.split(b"\n") if line.strip(b"\r").strip()]

        for line in lines:
            parts = line.split("  ", 1)
            if len(parts) != 2:
                continue
            expected_hash, relative_path = parts
            full_path = os.path.join(BASE_DIR, relative_path)

            # Compute actual hash
            result = subprocess.run(
                ["sha256sum", full_path],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"sha256sum failed for {full_path}"

            computed_hash = result.stdout.split()[0]
            assert computed_hash.lower() == expected_hash.lower(), \
                f"Hash mismatch for {relative_path}: expected {expected_hash}, got {computed_hash}"


class TestCurrentBrokenState:
    """Test that the script currently fails (the bug exists)."""

    def test_verify_script_currently_fails(self):
        """Running verify.sh should currently exit with non-zero (the bug)."""
        result = subprocess.run(
            ["./verify.sh"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode != 0, \
            "verify.sh should currently fail (exit non-zero) due to the CRLF bug"

    def test_verify_script_reports_mismatches(self):
        """Running verify.sh should report mismatches for files."""
        result = subprocess.run(
            ["./verify.sh"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        # Should mention mismatch or fail in some way
        has_mismatch_indication = ("mismatch" in output.lower() or "fail" in output.lower() 
                                   or "error" in output.lower() or result.returncode != 0)
        assert has_mismatch_indication, "verify.sh should indicate mismatches in output"


class TestRequiredTools:
    """Test that required tools are available."""

    @pytest.mark.parametrize("tool", ["sha256sum", "dos2unix", "sed", "awk", "tr", "bash"])
    def test_tool_available(self, tool):
        """Required tools must be available in PATH."""
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Tool '{tool}' is not available in PATH"


class TestDirectoryWritable:
    """Test that the working directory is writable."""

    def test_backup_check_directory_is_writable(self):
        """The /home/user/backup-check directory must be writable."""
        assert os.access(BASE_DIR, os.W_OK), f"Directory {BASE_DIR} is not writable"

    def test_manifest_file_is_writable(self):
        """The manifest.txt file must be writable."""
        assert os.access(MANIFEST_FILE, os.W_OK), f"File {MANIFEST_FILE} is not writable"

    def test_verify_script_is_writable(self):
        """The verify.sh script must be writable."""
        assert os.access(VERIFY_SCRIPT, os.W_OK), f"File {VERIFY_SCRIPT} is not writable"
