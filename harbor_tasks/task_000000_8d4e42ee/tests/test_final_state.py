# test_final_state.py
"""
Tests to validate the final state of the operating system/filesystem
after the student has completed the GPG encryption/signing task.
"""

import pytest
import os
import re
import hashlib
import subprocess
import json


class TestFinalState:
    """Test the final state after the task is performed."""

    def test_signature_file_exists(self):
        """Verify the detached signature file was created."""
        sig_file = "/home/user/api_payload.json.sig"
        assert os.path.isfile(sig_file), (
            f"Signature file {sig_file} does not exist. "
            "The task requires creating a detached signature for api_payload.json."
        )

    def test_signature_file_not_empty(self):
        """Verify the signature file is not empty."""
        sig_file = "/home/user/api_payload.json.sig"
        assert os.path.getsize(sig_file) > 0, (
            f"Signature file {sig_file} exists but is empty. "
            "A valid GPG signature should have content."
        )

    def test_encrypted_file_exists(self):
        """Verify the encrypted file was created."""
        gpg_file = "/home/user/api_payload.json.gpg"
        assert os.path.isfile(gpg_file), (
            f"Encrypted file {gpg_file} does not exist. "
            "The task requires encrypting api_payload.json."
        )

    def test_encrypted_file_not_empty(self):
        """Verify the encrypted file is not empty."""
        gpg_file = "/home/user/api_payload.json.gpg"
        assert os.path.getsize(gpg_file) > 0, (
            f"Encrypted file {gpg_file} exists but is empty. "
            "A valid GPG encrypted file should have content."
        )

    def test_log_file_exists(self):
        """Verify the verification log file was created."""
        log_file = "/home/user/gpg_test_results.log"
        assert os.path.isfile(log_file), (
            f"Log file {log_file} does not exist. "
            "The task requires creating a verification log file."
        )

    def test_log_file_not_empty(self):
        """Verify the log file is not empty."""
        log_file = "/home/user/gpg_test_results.log"
        assert os.path.getsize(log_file) > 0, (
            f"Log file {log_file} exists but is empty. "
            "The log file should contain verification results."
        )

    def test_log_file_contains_key_fingerprint(self):
        """Verify the log file contains KEY_FINGERPRINT line."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert "KEY_FINGERPRINT=" in content, (
            f"Log file {log_file} does not contain KEY_FINGERPRINT line. "
            "Expected format: KEY_FINGERPRINT=<40-character fingerprint>"
        )

    def test_log_file_key_fingerprint_format(self):
        """Verify the KEY_FINGERPRINT has exactly 40 hexadecimal characters."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        # Find the KEY_FINGERPRINT line
        match = re.search(r'^KEY_FINGERPRINT=([A-Fa-f0-9]+)$', content, re.MULTILINE)
        assert match is not None, (
            f"Log file {log_file} does not have a properly formatted KEY_FINGERPRINT line. "
            "Expected format: KEY_FINGERPRINT=<40-character hex fingerprint>"
        )

        fingerprint = match.group(1)
        assert len(fingerprint) == 40, (
            f"KEY_FINGERPRINT should be exactly 40 characters, got {len(fingerprint)}. "
            f"Fingerprint value: {fingerprint}"
        )

    def test_log_file_contains_signature_valid_yes(self):
        """Verify the log file contains SIGNATURE_VALID=YES."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert "SIGNATURE_VALID=YES" in content, (
            f"Log file {log_file} does not contain 'SIGNATURE_VALID=YES'. "
            "The signature verification should have succeeded."
        )

    def test_log_file_contains_decryption_successful_yes(self):
        """Verify the log file contains DECRYPTION_SUCCESSFUL=YES."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert "DECRYPTION_SUCCESSFUL=YES" in content, (
            f"Log file {log_file} does not contain 'DECRYPTION_SUCCESSFUL=YES'. "
            "The decryption should have succeeded."
        )

    def test_log_file_contains_original_hash(self):
        """Verify the log file contains ORIGINAL_HASH line."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert "ORIGINAL_HASH=" in content, (
            f"Log file {log_file} does not contain ORIGINAL_HASH line. "
            "Expected format: ORIGINAL_HASH=<sha256sum>"
        )

    def test_log_file_contains_decrypted_hash(self):
        """Verify the log file contains DECRYPTED_HASH line."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        assert "DECRYPTED_HASH=" in content, (
            f"Log file {log_file} does not contain DECRYPTED_HASH line. "
            "Expected format: DECRYPTED_HASH=<sha256sum>"
        )

    def test_log_file_hashes_match(self):
        """Verify that ORIGINAL_HASH and DECRYPTED_HASH match."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        # Extract ORIGINAL_HASH
        original_match = re.search(r'^ORIGINAL_HASH=([a-fA-F0-9]+)$', content, re.MULTILINE)
        assert original_match is not None, (
            "Could not parse ORIGINAL_HASH from log file. "
            "Expected format: ORIGINAL_HASH=<sha256sum>"
        )
        original_hash = original_match.group(1).lower()

        # Extract DECRYPTED_HASH
        decrypted_match = re.search(r'^DECRYPTED_HASH=([a-fA-F0-9]+)$', content, re.MULTILINE)
        assert decrypted_match is not None, (
            "Could not parse DECRYPTED_HASH from log file. "
            "Expected format: DECRYPTED_HASH=<sha256sum>"
        )
        decrypted_hash = decrypted_match.group(1).lower()

        assert original_hash == decrypted_hash, (
            f"ORIGINAL_HASH and DECRYPTED_HASH do not match. "
            f"ORIGINAL_HASH={original_hash}, DECRYPTED_HASH={decrypted_hash}. "
            "If encryption/decryption worked correctly, these should be identical."
        )

    def test_log_file_hash_format(self):
        """Verify that hashes are valid SHA256 format (64 hex characters)."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        original_match = re.search(r'^ORIGINAL_HASH=([a-fA-F0-9]+)$', content, re.MULTILINE)
        if original_match:
            original_hash = original_match.group(1)
            assert len(original_hash) == 64, (
                f"ORIGINAL_HASH should be 64 characters (SHA256), got {len(original_hash)}"
            )

        decrypted_match = re.search(r'^DECRYPTED_HASH=([a-fA-F0-9]+)$', content, re.MULTILINE)
        if decrypted_match:
            decrypted_hash = decrypted_match.group(1)
            assert len(decrypted_hash) == 64, (
                f"DECRYPTED_HASH should be 64 characters (SHA256), got {len(decrypted_hash)}"
            )

    def test_log_file_original_hash_matches_actual_file(self):
        """Verify that ORIGINAL_HASH matches the actual sha256sum of api_payload.json."""
        log_file = "/home/user/gpg_test_results.log"
        payload_file = "/home/user/api_payload.json"

        # Calculate actual hash
        with open(payload_file, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest().lower()

        # Get hash from log file
        with open(log_file, 'r') as f:
            content = f.read()

        original_match = re.search(r'^ORIGINAL_HASH=([a-fA-F0-9]+)$', content, re.MULTILINE)
        assert original_match is not None, (
            "Could not parse ORIGINAL_HASH from log file."
        )
        logged_hash = original_match.group(1).lower()

        assert logged_hash == actual_hash, (
            f"ORIGINAL_HASH in log file does not match actual sha256sum of api_payload.json. "
            f"Logged: {logged_hash}, Actual: {actual_hash}"
        )

    def test_gpg_key_exists_for_apitest_email(self):
        """Verify that a GPG key exists for apitest@example.com."""
        try:
            result = subprocess.run(
                ['gpg', '--list-keys', 'apitest@example.com'],
                capture_output=True,
                text=True,
                timeout=30
            )
            assert result.returncode == 0, (
                f"No GPG key found for 'apitest@example.com'. "
                f"The task requires creating a GPG key for this email address. "
                f"GPG output: {result.stderr}"
            )
        except subprocess.TimeoutExpired:
            pytest.fail("GPG command timed out while checking for key")
        except FileNotFoundError:
            pytest.fail("GPG is not installed or not in PATH")

    def test_gpg_key_has_correct_name(self):
        """Verify that the GPG key has the correct name 'API Test User'."""
        try:
            result = subprocess.run(
                ['gpg', '--list-keys', 'apitest@example.com'],
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout + result.stderr
            assert "API Test User" in output, (
                f"GPG key for apitest@example.com does not have name 'API Test User'. "
                f"GPG output: {output}"
            )
        except subprocess.TimeoutExpired:
            pytest.fail("GPG command timed out")
        except FileNotFoundError:
            pytest.fail("GPG is not installed or not in PATH")

    def test_log_file_format_no_extra_spaces(self):
        """Verify the log file has no extra spaces around equals signs."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if '=' in line:
                # Check for spaces around the equals sign
                assert ' =' not in line and '= ' not in line, (
                    f"Log file line has extra spaces around '=': '{line}'. "
                    "Format should be KEY=VALUE with no spaces around '='."
                )

    def test_log_file_has_all_required_lines(self):
        """Verify the log file has all 5 required lines."""
        log_file = "/home/user/gpg_test_results.log"
        with open(log_file, 'r') as f:
            content = f.read()

        required_prefixes = [
            "KEY_FINGERPRINT=",
            "SIGNATURE_VALID=",
            "DECRYPTION_SUCCESSFUL=",
            "ORIGINAL_HASH=",
            "DECRYPTED_HASH="
        ]

        for prefix in required_prefixes:
            assert prefix in content, (
                f"Log file is missing required line starting with '{prefix}'"
            )

    def test_original_payload_file_still_exists(self):
        """Verify the original api_payload.json file still exists."""
        payload_file = "/home/user/api_payload.json"
        assert os.path.isfile(payload_file), (
            f"Original file {payload_file} no longer exists. "
            "The original file should be preserved."
        )

    def test_original_payload_file_unchanged(self):
        """Verify the original api_payload.json file content is unchanged."""
        payload_file = "/home/user/api_payload.json"

        expected_content = {
            "api_version": "2.1",
            "endpoint": "/v2/transactions",
            "method": "POST",
            "test_id": "TX-20240115-001",
            "payload": {
                "amount": 150.00,
                "currency": "USD",
                "merchant_id": "MERCH-9876"
            }
        }

        with open(payload_file, 'r') as f:
            actual_content = json.load(f)

        assert actual_content == expected_content, (
            f"Original file {payload_file} content has been modified. "
            f"Expected: {expected_content}, Got: {actual_content}"
        )
