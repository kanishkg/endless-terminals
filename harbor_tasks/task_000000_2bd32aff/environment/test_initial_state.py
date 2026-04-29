# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the GPG decryption and signature verification task.
"""

import os
import subprocess
import pytest


HOME = "/home/user"
EVIDENCE_DIR = f"{HOME}/evidence"
ENCRYPTED_FILE = f"{EVIDENCE_DIR}/packet_dump.tar.gz.gpg"
SIGNATURE_FILE = f"{EVIDENCE_DIR}/packet_dump.tar.gz.sig"
EXTRACTED_DIR = f"{EVIDENCE_DIR}/extracted"
GNUPG_DIR = f"{HOME}/.gnupg"


class TestEvidenceDirectory:
    """Tests for the evidence directory structure."""

    def test_evidence_directory_exists(self):
        """The /home/user/evidence/ directory must exist."""
        assert os.path.isdir(EVIDENCE_DIR), (
            f"Evidence directory {EVIDENCE_DIR} does not exist"
        )

    def test_evidence_directory_is_writable(self):
        """The /home/user/evidence/ directory must be writable."""
        assert os.access(EVIDENCE_DIR, os.W_OK), (
            f"Evidence directory {EVIDENCE_DIR} is not writable"
        )

    def test_extracted_directory_does_not_exist(self):
        """The /home/user/evidence/extracted/ directory must NOT exist initially."""
        assert not os.path.exists(EXTRACTED_DIR), (
            f"Extracted directory {EXTRACTED_DIR} should not exist initially"
        )


class TestEncryptedFile:
    """Tests for the encrypted tarball."""

    def test_encrypted_file_exists(self):
        """The encrypted file packet_dump.tar.gz.gpg must exist."""
        assert os.path.isfile(ENCRYPTED_FILE), (
            f"Encrypted file {ENCRYPTED_FILE} does not exist"
        )

    def test_encrypted_file_is_readable(self):
        """The encrypted file must be readable."""
        assert os.access(ENCRYPTED_FILE, os.R_OK), (
            f"Encrypted file {ENCRYPTED_FILE} is not readable"
        )

    def test_encrypted_file_has_content(self):
        """The encrypted file must have non-zero size."""
        size = os.path.getsize(ENCRYPTED_FILE)
        assert size > 0, (
            f"Encrypted file {ENCRYPTED_FILE} is empty (size: {size})"
        )

    def test_encrypted_file_is_gpg_encrypted(self):
        """The encrypted file must be a valid GPG encrypted file."""
        result = subprocess.run(
            ["gpg", "--list-packets", ENCRYPTED_FILE],
            capture_output=True,
            text=True
        )
        # GPG list-packets should show encryption info
        output = result.stdout + result.stderr
        assert "encrypted" in output.lower() or ":pubkey enc packet:" in output or ":symkey enc packet:" in output, (
            f"File {ENCRYPTED_FILE} does not appear to be GPG encrypted. "
            f"gpg --list-packets output: {output}"
        )


class TestSignatureFile:
    """Tests for the detached signature file."""

    def test_signature_file_exists(self):
        """The signature file packet_dump.tar.gz.sig must exist."""
        assert os.path.isfile(SIGNATURE_FILE), (
            f"Signature file {SIGNATURE_FILE} does not exist"
        )

    def test_signature_file_is_readable(self):
        """The signature file must be readable."""
        assert os.access(SIGNATURE_FILE, os.R_OK), (
            f"Signature file {SIGNATURE_FILE} is not readable"
        )

    def test_signature_file_has_content(self):
        """The signature file must have non-zero size."""
        size = os.path.getsize(SIGNATURE_FILE)
        assert size > 0, (
            f"Signature file {SIGNATURE_FILE} is empty (size: {size})"
        )

    def test_signature_file_is_gpg_signature(self):
        """The signature file must be a valid GPG signature file."""
        result = subprocess.run(
            ["gpg", "--list-packets", SIGNATURE_FILE],
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        assert "signature" in output.lower() or ":signature packet:" in output, (
            f"File {SIGNATURE_FILE} does not appear to be a GPG signature. "
            f"gpg --list-packets output: {output}"
        )


class TestGPGKeyring:
    """Tests for the GPG keyring configuration."""

    def test_gnupg_directory_exists(self):
        """The .gnupg directory must exist."""
        assert os.path.isdir(GNUPG_DIR), (
            f"GPG directory {GNUPG_DIR} does not exist"
        )

    def test_user_has_secret_key(self):
        """The user must have at least one secret key for decryption."""
        result = subprocess.run(
            ["gpg", "--list-secret-keys"],
            capture_output=True,
            text=True,
            env={**os.environ, "GNUPGHOME": GNUPG_DIR}
        )
        assert result.returncode == 0, (
            f"Failed to list secret keys: {result.stderr}"
        )
        # Check that there's at least one secret key
        assert "sec" in result.stdout or result.stdout.strip(), (
            f"No secret keys found in keyring. User needs a private key for decryption. "
            f"Output: {result.stdout}"
        )

    def test_has_public_keys_for_verification(self):
        """The keyring must have public keys (including field team's signing key)."""
        result = subprocess.run(
            ["gpg", "--list-keys"],
            capture_output=True,
            text=True,
            env={**os.environ, "GNUPGHOME": GNUPG_DIR}
        )
        assert result.returncode == 0, (
            f"Failed to list public keys: {result.stderr}"
        )
        # Check that there's at least one public key
        assert "pub" in result.stdout or result.stdout.strip(), (
            f"No public keys found in keyring. Field team's signing key should be imported. "
            f"Output: {result.stdout}"
        )


class TestRequiredTools:
    """Tests for required command-line tools."""

    def test_gpg_is_installed(self):
        """GPG must be installed and accessible."""
        result = subprocess.run(
            ["which", "gpg"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "gpg is not installed or not in PATH"
        )

    def test_gpg_is_functional(self):
        """GPG must be functional."""
        result = subprocess.run(
            ["gpg", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"gpg --version failed: {result.stderr}"
        )
        assert "gpg" in result.stdout.lower(), (
            f"Unexpected gpg --version output: {result.stdout}"
        )

    def test_tar_is_installed(self):
        """tar must be installed and accessible."""
        result = subprocess.run(
            ["which", "tar"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "tar is not installed or not in PATH"
        )

    def test_tar_is_functional(self):
        """tar must be functional."""
        result = subprocess.run(
            ["tar", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"tar --version failed: {result.stderr}"
        )


class TestDecryptedTarballDoesNotExist:
    """Ensure the decrypted tarball doesn't already exist."""

    def test_decrypted_tarball_does_not_exist(self):
        """The decrypted tarball should not exist initially."""
        decrypted_path = f"{EVIDENCE_DIR}/packet_dump.tar.gz"
        assert not os.path.exists(decrypted_path), (
            f"Decrypted tarball {decrypted_path} should not exist initially - "
            "student needs to decrypt it"
        )
