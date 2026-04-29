# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the credential rotation optimization task.
"""

import os
import struct
import subprocess
import pytest


HOME = "/home/user"
ROTATE_DIR = os.path.join(HOME, "rotate")
REENCRYPT_SCRIPT = os.path.join(ROTATE_DIR, "reencrypt.py")
VAULT_DUMP = os.path.join(ROTATE_DIR, "vault_dump.enc")
OLD_KEY = os.path.join(ROTATE_DIR, "old.key")
NEW_KEY = os.path.join(ROTATE_DIR, "new.key")
VERIFY_SCRIPT = os.path.join(ROTATE_DIR, "verify.py")

# Output files that should NOT exist initially
OUTPUT_FILE = os.path.join(ROTATE_DIR, "vault_dump.new.enc")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_home_directory_exists(self):
        assert os.path.isdir(HOME), f"Home directory {HOME} does not exist"

    def test_rotate_directory_exists(self):
        assert os.path.isdir(ROTATE_DIR), f"Rotate directory {ROTATE_DIR} does not exist"

    def test_rotate_directory_is_writable(self):
        assert os.access(ROTATE_DIR, os.W_OK), f"Rotate directory {ROTATE_DIR} is not writable"


class TestReencryptScript:
    """Test that the reencrypt.py script exists and is valid."""

    def test_reencrypt_script_exists(self):
        assert os.path.isfile(REENCRYPT_SCRIPT), f"Reencrypt script {REENCRYPT_SCRIPT} does not exist"

    def test_reencrypt_script_is_readable(self):
        assert os.access(REENCRYPT_SCRIPT, os.R_OK), f"Reencrypt script {REENCRYPT_SCRIPT} is not readable"

    def test_reencrypt_script_is_valid_python(self):
        """Verify the script can be parsed by Python."""
        result = subprocess.run(
            ["python3", "-m", "py_compile", REENCRYPT_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Reencrypt script has syntax errors: {result.stderr}"


class TestVaultDumpFile:
    """Test that the vault dump file exists and has correct format."""

    def test_vault_dump_exists(self):
        assert os.path.isfile(VAULT_DUMP), f"Vault dump file {VAULT_DUMP} does not exist"

    def test_vault_dump_is_readable(self):
        assert os.access(VAULT_DUMP, os.R_OK), f"Vault dump file {VAULT_DUMP} is not readable"

    def test_vault_dump_has_correct_magic(self):
        """Verify the vault dump has the correct VAULT1 magic header."""
        with open(VAULT_DUMP, "rb") as f:
            magic = f.read(6)
        assert magic == b"VAULT1", f"Vault dump has incorrect magic: {magic!r}, expected b'VAULT1'"

    def test_vault_dump_has_80000_entries(self):
        """Verify the vault dump header indicates 80,000 entries."""
        with open(VAULT_DUMP, "rb") as f:
            f.read(6)  # skip magic
            entry_count_bytes = f.read(4)
        entry_count = struct.unpack("<I", entry_count_bytes)[0]
        assert entry_count == 80000, f"Vault dump has {entry_count} entries, expected 80000"

    def test_vault_dump_has_key_id(self):
        """Verify the vault dump has a 32-byte key_id in header."""
        with open(VAULT_DUMP, "rb") as f:
            f.read(6)  # skip magic
            f.read(4)  # skip entry_count
            key_id = f.read(32)
        assert len(key_id) == 32, f"Vault dump key_id is {len(key_id)} bytes, expected 32"

    def test_vault_dump_header_size(self):
        """Verify the complete header is 42 bytes (6 + 4 + 32)."""
        expected_header_size = 6 + 4 + 32  # magic + entry_count + key_id
        assert expected_header_size == 42, "Header size calculation error"

        with open(VAULT_DUMP, "rb") as f:
            header = f.read(42)
        assert len(header) == 42, f"Could not read full 42-byte header from vault dump"

    def test_vault_dump_has_reasonable_size(self):
        """Verify the vault dump is large enough for 80k entries."""
        file_size = os.path.getsize(VAULT_DUMP)
        # Header is 42 bytes, each entry has at minimum:
        # nonce (12) + ciphertext_len (4) + min ciphertext (16 for tag) + metadata_len (2) = 34 bytes
        min_expected_size = 42 + (80000 * 34)
        assert file_size >= min_expected_size, (
            f"Vault dump is {file_size} bytes, expected at least {min_expected_size} bytes for 80k entries"
        )


class TestKeyFiles:
    """Test that the key files exist and are correct size."""

    def test_old_key_exists(self):
        assert os.path.isfile(OLD_KEY), f"Old key file {OLD_KEY} does not exist"

    def test_old_key_is_32_bytes(self):
        """AES-256 requires a 32-byte key."""
        size = os.path.getsize(OLD_KEY)
        assert size == 32, f"Old key is {size} bytes, expected 32 bytes for AES-256"

    def test_old_key_is_readable(self):
        assert os.access(OLD_KEY, os.R_OK), f"Old key file {OLD_KEY} is not readable"

    def test_new_key_exists(self):
        assert os.path.isfile(NEW_KEY), f"New key file {NEW_KEY} does not exist"

    def test_new_key_is_32_bytes(self):
        """AES-256 requires a 32-byte key."""
        size = os.path.getsize(NEW_KEY)
        assert size == 32, f"New key is {size} bytes, expected 32 bytes for AES-256"

    def test_new_key_is_readable(self):
        assert os.access(NEW_KEY, os.R_OK), f"New key file {NEW_KEY} is not readable"

    def test_keys_are_different(self):
        """Old and new keys should be different."""
        with open(OLD_KEY, "rb") as f:
            old = f.read()
        with open(NEW_KEY, "rb") as f:
            new = f.read()
        assert old != new, "Old key and new key are identical - they should be different"


class TestVerifyScript:
    """Test that the verification script exists."""

    def test_verify_script_exists(self):
        assert os.path.isfile(VERIFY_SCRIPT), f"Verify script {VERIFY_SCRIPT} does not exist"

    def test_verify_script_is_readable(self):
        assert os.access(VERIFY_SCRIPT, os.R_OK), f"Verify script {VERIFY_SCRIPT} is not readable"

    def test_verify_script_is_valid_python(self):
        """Verify the script can be parsed by Python."""
        result = subprocess.run(
            ["python3", "-m", "py_compile", VERIFY_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Verify script has syntax errors: {result.stderr}"


class TestPythonEnvironment:
    """Test that the required Python environment is available."""

    def test_python3_available(self):
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "python3 is not available"

    def test_python_version_is_311_or_higher(self):
        result = subprocess.run(
            ["python3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Could not determine Python version"
        version = result.stdout.strip()
        major, minor = map(int, version.split("."))
        assert (major, minor) >= (3, 11), f"Python version is {version}, expected 3.11 or higher"

    def test_pycryptodome_installed(self):
        """Verify pycryptodome is installed."""
        result = subprocess.run(
            ["python3", "-c", "from Crypto.Cipher import AES; print('OK')"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"pycryptodome is not installed or not importable: {result.stderr}"
        )
        assert "OK" in result.stdout, "pycryptodome import did not succeed"


class TestOutputFileNotExists:
    """Test that output files do not exist yet (clean initial state)."""

    def test_output_file_does_not_exist(self):
        """The output file should not exist before running the script."""
        # This is a soft check - if it exists, it might be from a previous run
        # but we note it as the expected initial state
        if os.path.exists(OUTPUT_FILE):
            pytest.skip(f"Output file {OUTPUT_FILE} already exists - may be from previous run")


class TestVaultDumpFirstEntry:
    """Test that we can read at least the first entry structure."""

    def test_first_entry_has_valid_structure(self):
        """Verify the first entry after header has valid structure."""
        with open(VAULT_DUMP, "rb") as f:
            # Skip header
            f.read(42)

            # Read first entry's nonce (12 bytes)
            nonce = f.read(12)
            assert len(nonce) == 12, f"First entry nonce is {len(nonce)} bytes, expected 12"

            # Read ciphertext length (4 bytes, uint32 LE)
            ct_len_bytes = f.read(4)
            assert len(ct_len_bytes) == 4, "Could not read ciphertext length"
            ct_len = struct.unpack("<I", ct_len_bytes)[0]

            # Ciphertext should be at least 16 bytes (GCM tag)
            assert ct_len >= 16, f"Ciphertext length {ct_len} is too small (min 16 for GCM tag)"
            # And not absurdly large
            assert ct_len < 1000000, f"Ciphertext length {ct_len} seems too large"

            # Read ciphertext
            ciphertext = f.read(ct_len)
            assert len(ciphertext) == ct_len, f"Could not read full ciphertext"

            # Read metadata length (2 bytes, uint16 LE)
            meta_len_bytes = f.read(2)
            assert len(meta_len_bytes) == 2, "Could not read metadata length"
            meta_len = struct.unpack("<H", meta_len_bytes)[0]

            # Metadata length should be reasonable
            assert meta_len < 65535, f"Metadata length {meta_len} is at maximum uint16"

            # Read metadata
            metadata = f.read(meta_len)
            assert len(metadata) == meta_len, f"Could not read full metadata"
