# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the credential rotation optimization task.

The script must:
1. Complete in under 60 seconds
2. Produce correctly formatted output with all 80,000 entries re-encrypted
3. Pass verification against the original data
4. Not have excessive file open operations in the code
"""

import os
import struct
import subprocess
import hashlib
import time
import pytest


HOME = "/home/user"
ROTATE_DIR = os.path.join(HOME, "rotate")
REENCRYPT_SCRIPT = os.path.join(ROTATE_DIR, "reencrypt.py")
VAULT_DUMP = os.path.join(ROTATE_DIR, "vault_dump.enc")
OUTPUT_FILE = os.path.join(ROTATE_DIR, "vault_dump.new.enc")
OLD_KEY = os.path.join(ROTATE_DIR, "old.key")
NEW_KEY = os.path.join(ROTATE_DIR, "new.key")
VERIFY_SCRIPT = os.path.join(ROTATE_DIR, "verify.py")

EXPECTED_ENTRY_COUNT = 80000
HEADER_SIZE = 42  # 6 (magic) + 4 (entry_count) + 32 (key_id)
TIMEOUT_SECONDS = 60


class TestScriptCompletion:
    """Test that the reencrypt script completes within the time limit."""

    def test_script_completes_under_60_seconds(self):
        """The optimized script must complete in under 60 seconds."""
        # Remove output file if it exists from previous runs
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

        start_time = time.time()
        result = subprocess.run(
            ["timeout", str(TIMEOUT_SECONDS), "python3", REENCRYPT_SCRIPT],
            capture_output=True,
            text=True,
            cwd=ROTATE_DIR
        )
        elapsed_time = time.time() - start_time

        assert result.returncode == 0, (
            f"Script failed or timed out (exit code {result.returncode}). "
            f"Elapsed time: {elapsed_time:.2f}s. "
            f"Stdout: {result.stdout[:500]}... "
            f"Stderr: {result.stderr[:500]}..."
        )

        assert elapsed_time < TIMEOUT_SECONDS, (
            f"Script took {elapsed_time:.2f} seconds, must complete in under {TIMEOUT_SECONDS} seconds"
        )


class TestOutputFileExists:
    """Test that the output file was created."""

    def test_output_file_exists(self):
        """The output file must exist after running the script."""
        assert os.path.isfile(OUTPUT_FILE), (
            f"Output file {OUTPUT_FILE} does not exist. "
            "The reencrypt script should create vault_dump.new.enc"
        )

    def test_output_file_is_readable(self):
        """The output file must be readable."""
        assert os.access(OUTPUT_FILE, os.R_OK), (
            f"Output file {OUTPUT_FILE} is not readable"
        )


class TestOutputFileFormat:
    """Test that the output file has the correct format."""

    def test_output_has_correct_magic(self):
        """Output file must have VAULT1 magic header."""
        with open(OUTPUT_FILE, "rb") as f:
            magic = f.read(6)
        assert magic == b"VAULT1", (
            f"Output file has incorrect magic: {magic!r}, expected b'VAULT1'"
        )

    def test_output_has_correct_entry_count(self):
        """Output file must have 80,000 entries in header."""
        with open(OUTPUT_FILE, "rb") as f:
            f.read(6)  # skip magic
            entry_count_bytes = f.read(4)
        entry_count = struct.unpack("<I", entry_count_bytes)[0]
        assert entry_count == EXPECTED_ENTRY_COUNT, (
            f"Output file has {entry_count} entries in header, expected {EXPECTED_ENTRY_COUNT}"
        )

    def test_output_has_new_key_id(self):
        """Output file key_id should be SHA-256 of new.key (first 32 bytes)."""
        with open(NEW_KEY, "rb") as f:
            new_key = f.read()
        expected_key_id = hashlib.sha256(new_key).digest()[:32]

        with open(OUTPUT_FILE, "rb") as f:
            f.read(6)  # skip magic
            f.read(4)  # skip entry_count
            key_id = f.read(32)

        assert key_id == expected_key_id, (
            f"Output file key_id does not match SHA-256 of new.key. "
            f"Got: {key_id.hex()}, Expected: {expected_key_id.hex()}"
        )

    def test_output_header_complete(self):
        """Output file must have complete 42-byte header."""
        with open(OUTPUT_FILE, "rb") as f:
            header = f.read(HEADER_SIZE)
        assert len(header) == HEADER_SIZE, (
            f"Output file header is {len(header)} bytes, expected {HEADER_SIZE}"
        )


class TestOutputFileSize:
    """Test that output file size is reasonable."""

    def test_output_size_within_tolerance(self):
        """Output file size must be within 1% of input file size."""
        input_size = os.path.getsize(VAULT_DUMP)
        output_size = os.path.getsize(OUTPUT_FILE)

        tolerance = 0.01  # 1%
        min_size = input_size * (1 - tolerance)
        max_size = input_size * (1 + tolerance)

        assert min_size <= output_size <= max_size, (
            f"Output file size {output_size} is not within 1% of input size {input_size}. "
            f"Expected between {min_size:.0f} and {max_size:.0f} bytes. "
            "This may indicate dropped entries or corrupted data."
        )


class TestOriginalFileUnchanged:
    """Test that the original vault dump was not modified."""

    def test_original_file_still_exists(self):
        """Original vault_dump.enc must still exist."""
        assert os.path.isfile(VAULT_DUMP), (
            f"Original vault dump {VAULT_DUMP} no longer exists!"
        )

    def test_original_file_has_correct_magic(self):
        """Original file must still have VAULT1 magic."""
        with open(VAULT_DUMP, "rb") as f:
            magic = f.read(6)
        assert magic == b"VAULT1", (
            f"Original vault dump magic was corrupted: {magic!r}"
        )

    def test_original_file_has_correct_entry_count(self):
        """Original file must still have 80,000 entries."""
        with open(VAULT_DUMP, "rb") as f:
            f.read(6)
            entry_count_bytes = f.read(4)
        entry_count = struct.unpack("<I", entry_count_bytes)[0]
        assert entry_count == EXPECTED_ENTRY_COUNT, (
            f"Original vault dump was corrupted: entry count is {entry_count}"
        )


class TestVerificationScript:
    """Test that the verification script passes."""

    def test_verification_passes(self):
        """The verify.py script must exit 0, confirming correct re-encryption."""
        result = subprocess.run(
            ["python3", VERIFY_SCRIPT],
            capture_output=True,
            text=True,
            cwd=ROTATE_DIR
        )
        assert result.returncode == 0, (
            f"Verification script failed with exit code {result.returncode}. "
            f"This means the re-encrypted data does not match the original. "
            f"Stdout: {result.stdout[:1000]}... "
            f"Stderr: {result.stderr[:1000]}..."
        )


class TestCodeQuality:
    """Test that the code doesn't use excessive file operations."""

    def test_not_excessive_file_opens(self):
        """
        The script should not open vault_dump.enc in a loop.
        grep for 'open.*vault_dump.enc' should return 1 or 2 matches, not many.
        """
        result = subprocess.run(
            ["grep", "-c", "open.*vault_dump.enc", REENCRYPT_SCRIPT],
            capture_output=True,
            text=True
        )

        # grep returns 1 if no matches, 0 if matches found
        if result.returncode == 1:
            # No matches found - that's actually fine, maybe they renamed the variable
            count = 0
        else:
            try:
                count = int(result.stdout.strip())
            except ValueError:
                count = 0

        # We allow 0-3 occurrences (could be comments, could be one open statement)
        # The anti-pattern would be opening inside a loop, which would show up
        # as the loop body, not as multiple literal opens in the source
        # This is a heuristic check
        assert count <= 5, (
            f"Found {count} occurrences of opening vault_dump.enc in the script. "
            "This suggests the file may still be opened multiple times in a loop."
        )


class TestOutputEntryStructure:
    """Test that output entries have valid structure."""

    def test_first_entry_valid_structure(self):
        """First entry in output should have valid structure."""
        with open(OUTPUT_FILE, "rb") as f:
            f.read(HEADER_SIZE)  # skip header

            # Read nonce
            nonce = f.read(12)
            assert len(nonce) == 12, f"First entry nonce is {len(nonce)} bytes, expected 12"

            # Read ciphertext length
            ct_len_bytes = f.read(4)
            assert len(ct_len_bytes) == 4, "Could not read ciphertext length"
            ct_len = struct.unpack("<I", ct_len_bytes)[0]

            assert ct_len >= 16, f"Ciphertext too small: {ct_len} bytes (min 16 for GCM tag)"
            assert ct_len < 1000000, f"Ciphertext suspiciously large: {ct_len} bytes"

            # Read ciphertext
            ciphertext = f.read(ct_len)
            assert len(ciphertext) == ct_len, "Could not read full ciphertext"

            # Read metadata length
            meta_len_bytes = f.read(2)
            assert len(meta_len_bytes) == 2, "Could not read metadata length"
            meta_len = struct.unpack("<H", meta_len_bytes)[0]

            # Read metadata
            metadata = f.read(meta_len)
            assert len(metadata) == meta_len, "Could not read full metadata"

    def test_can_parse_multiple_entries(self):
        """Should be able to parse several entries without errors."""
        entries_to_check = 100

        with open(OUTPUT_FILE, "rb") as f:
            f.read(HEADER_SIZE)  # skip header

            for i in range(entries_to_check):
                # Read nonce
                nonce = f.read(12)
                if len(nonce) != 12:
                    pytest.fail(f"Entry {i}: nonce is {len(nonce)} bytes, expected 12")

                # Read ciphertext length
                ct_len_bytes = f.read(4)
                if len(ct_len_bytes) != 4:
                    pytest.fail(f"Entry {i}: could not read ciphertext length")
                ct_len = struct.unpack("<I", ct_len_bytes)[0]

                # Read ciphertext
                ciphertext = f.read(ct_len)
                if len(ciphertext) != ct_len:
                    pytest.fail(f"Entry {i}: ciphertext truncated")

                # Read metadata length
                meta_len_bytes = f.read(2)
                if len(meta_len_bytes) != 2:
                    pytest.fail(f"Entry {i}: could not read metadata length")
                meta_len = struct.unpack("<H", meta_len_bytes)[0]

                # Read metadata
                metadata = f.read(meta_len)
                if len(metadata) != meta_len:
                    pytest.fail(f"Entry {i}: metadata truncated")


class TestDecryptionWithNewKey:
    """Test that entries can actually be decrypted with the new key."""

    def test_first_entry_decryptable(self):
        """First entry should be decryptable with new key."""
        from Crypto.Cipher import AES

        with open(NEW_KEY, "rb") as f:
            new_key = f.read()

        with open(OUTPUT_FILE, "rb") as f:
            f.read(HEADER_SIZE)  # skip header

            # Read first entry
            nonce = f.read(12)
            ct_len = struct.unpack("<I", f.read(4))[0]
            ciphertext = f.read(ct_len)

        # Ciphertext includes 16-byte GCM tag at the end
        tag = ciphertext[-16:]
        actual_ciphertext = ciphertext[:-16]

        cipher = AES.new(new_key, AES.MODE_GCM, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(actual_ciphertext, tag)
            # If we get here, decryption succeeded
            assert len(plaintext) > 0, "Decrypted plaintext is empty"
        except Exception as e:
            pytest.fail(f"Failed to decrypt first entry with new key: {e}")


class TestAllEntriesPresent:
    """Test that all 80,000 entries are present in output."""

    def test_can_seek_to_end_of_all_entries(self):
        """
        Verify we can read through all entries without running out of data.
        This confirms all 80,000 entries are present.
        """
        entries_parsed = 0

        with open(OUTPUT_FILE, "rb") as f:
            f.read(HEADER_SIZE)  # skip header

            for i in range(EXPECTED_ENTRY_COUNT):
                # Read nonce
                nonce = f.read(12)
                if len(nonce) != 12:
                    pytest.fail(
                        f"Ran out of data at entry {i}. "
                        f"Only {entries_parsed} entries present, expected {EXPECTED_ENTRY_COUNT}"
                    )

                # Read ciphertext length
                ct_len_bytes = f.read(4)
                if len(ct_len_bytes) != 4:
                    pytest.fail(f"Truncated at entry {i} ciphertext length")
                ct_len = struct.unpack("<I", ct_len_bytes)[0]

                # Skip ciphertext
                ciphertext = f.read(ct_len)
                if len(ciphertext) != ct_len:
                    pytest.fail(f"Truncated at entry {i} ciphertext")

                # Read metadata length
                meta_len_bytes = f.read(2)
                if len(meta_len_bytes) != 2:
                    pytest.fail(f"Truncated at entry {i} metadata length")
                meta_len = struct.unpack("<H", meta_len_bytes)[0]

                # Skip metadata
                metadata = f.read(meta_len)
                if len(metadata) != meta_len:
                    pytest.fail(f"Truncated at entry {i} metadata")

                entries_parsed += 1

        assert entries_parsed == EXPECTED_ENTRY_COUNT, (
            f"Parsed {entries_parsed} entries, expected {EXPECTED_ENTRY_COUNT}"
        )
