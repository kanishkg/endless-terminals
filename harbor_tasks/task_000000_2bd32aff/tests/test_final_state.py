# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the GPG decryption, signature verification, and extraction task.
"""

import os
import subprocess
import pytest


HOME = "/home/user"
EVIDENCE_DIR = f"{HOME}/evidence"
ENCRYPTED_FILE = f"{EVIDENCE_DIR}/packet_dump.tar.gz.gpg"
SIGNATURE_FILE = f"{EVIDENCE_DIR}/packet_dump.tar.gz.sig"
DECRYPTED_TARBALL = f"{EVIDENCE_DIR}/packet_dump.tar.gz"
EXTRACTED_DIR = f"{EVIDENCE_DIR}/extracted"
GNUPG_DIR = f"{HOME}/.gnupg"


class TestDecryptedTarball:
    """Tests for the decrypted tarball."""

    def test_decrypted_tarball_exists(self):
        """The decrypted tarball packet_dump.tar.gz must exist."""
        assert os.path.isfile(DECRYPTED_TARBALL), (
            f"Decrypted tarball {DECRYPTED_TARBALL} does not exist. "
            "You need to decrypt the .gpg file."
        )

    def test_decrypted_tarball_has_content(self):
        """The decrypted tarball must have non-zero size."""
        assert os.path.isfile(DECRYPTED_TARBALL), (
            f"Decrypted tarball {DECRYPTED_TARBALL} does not exist."
        )
        size = os.path.getsize(DECRYPTED_TARBALL)
        assert size > 0, (
            f"Decrypted tarball {DECRYPTED_TARBALL} is empty (size: {size})"
        )

    def test_decrypted_tarball_is_valid_gzip(self):
        """The decrypted tarball must be a valid gzip file."""
        assert os.path.isfile(DECRYPTED_TARBALL), (
            f"Decrypted tarball {DECRYPTED_TARBALL} does not exist."
        )
        result = subprocess.run(
            ["gzip", "-t", DECRYPTED_TARBALL],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Decrypted file {DECRYPTED_TARBALL} is not a valid gzip file. "
            f"Error: {result.stderr}"
        )


class TestSignatureVerification:
    """Tests for GPG signature verification."""

    def test_signature_verifies_successfully(self):
        """The signature must verify successfully against the decrypted tarball."""
        assert os.path.isfile(DECRYPTED_TARBALL), (
            f"Decrypted tarball {DECRYPTED_TARBALL} does not exist. "
            "Cannot verify signature without the decrypted file."
        )
        assert os.path.isfile(SIGNATURE_FILE), (
            f"Signature file {SIGNATURE_FILE} does not exist."
        )

        result = subprocess.run(
            ["gpg", "--verify", SIGNATURE_FILE, DECRYPTED_TARBALL],
            capture_output=True,
            text=True,
            env={**os.environ, "GNUPGHOME": GNUPG_DIR}
        )

        # GPG outputs verification info to stderr
        combined_output = result.stdout + result.stderr

        assert result.returncode == 0, (
            f"GPG signature verification failed with exit code {result.returncode}. "
            f"Output: {combined_output}"
        )

        # Check for "Good signature" in output (case-insensitive)
        assert "good signature" in combined_output.lower(), (
            f"Signature verification did not report 'Good signature'. "
            f"Output: {combined_output}"
        )


class TestExtractedDirectory:
    """Tests for the extracted directory."""

    def test_extracted_directory_exists(self):
        """The extracted directory must exist."""
        assert os.path.isdir(EXTRACTED_DIR), (
            f"Extracted directory {EXTRACTED_DIR} does not exist. "
            "You need to extract the tarball contents."
        )

    def test_extracted_directory_has_contents(self):
        """The extracted directory must have contents."""
        assert os.path.isdir(EXTRACTED_DIR), (
            f"Extracted directory {EXTRACTED_DIR} does not exist."
        )
        contents = os.listdir(EXTRACTED_DIR)
        assert len(contents) > 0, (
            f"Extracted directory {EXTRACTED_DIR} is empty. "
            "The tarball should have been extracted here."
        )


class TestPcapFiles:
    """Tests for the .pcap files in the extracted directory."""

    def _find_pcap_files(self, directory):
        """Recursively find all .pcap files under a directory."""
        pcap_files = []
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if filename.endswith('.pcap'):
                    pcap_files.append(os.path.join(root, filename))
        return pcap_files

    def test_pcap_files_exist(self):
        """At least one .pcap file must exist under the extracted directory."""
        assert os.path.isdir(EXTRACTED_DIR), (
            f"Extracted directory {EXTRACTED_DIR} does not exist."
        )

        pcap_files = self._find_pcap_files(EXTRACTED_DIR)
        assert len(pcap_files) > 0, (
            f"No .pcap files found under {EXTRACTED_DIR}. "
            "The tarball should contain at least one .pcap file."
        )

    def test_pcap_files_have_content(self):
        """All .pcap files must have non-zero size (not empty stubs)."""
        assert os.path.isdir(EXTRACTED_DIR), (
            f"Extracted directory {EXTRACTED_DIR} does not exist."
        )

        pcap_files = self._find_pcap_files(EXTRACTED_DIR)
        assert len(pcap_files) > 0, (
            f"No .pcap files found under {EXTRACTED_DIR}."
        )

        for pcap_file in pcap_files:
            size = os.path.getsize(pcap_file)
            assert size > 0, (
                f"PCAP file {pcap_file} is empty (size: {size}). "
                "This appears to be an empty stub, not a real pcap file."
            )


class TestInvariants:
    """Tests to ensure original files are unchanged."""

    def test_encrypted_file_still_exists(self):
        """The original encrypted file must still exist (unchanged)."""
        assert os.path.isfile(ENCRYPTED_FILE), (
            f"Original encrypted file {ENCRYPTED_FILE} no longer exists. "
            "It should not have been deleted."
        )

    def test_encrypted_file_still_encrypted(self):
        """The original encrypted file must still be GPG encrypted."""
        assert os.path.isfile(ENCRYPTED_FILE), (
            f"Original encrypted file {ENCRYPTED_FILE} does not exist."
        )

        result = subprocess.run(
            ["gpg", "--list-packets", ENCRYPTED_FILE],
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        is_encrypted = (
            "encrypted" in output.lower() or 
            ":pubkey enc packet:" in output or 
            ":symkey enc packet:" in output
        )
        assert is_encrypted, (
            f"Original file {ENCRYPTED_FILE} no longer appears to be GPG encrypted. "
            "It should not have been modified."
        )

    def test_signature_file_still_exists(self):
        """The original signature file must still exist (unchanged)."""
        assert os.path.isfile(SIGNATURE_FILE), (
            f"Original signature file {SIGNATURE_FILE} no longer exists. "
            "It should not have been deleted."
        )

    def test_signature_file_still_valid(self):
        """The original signature file must still be a valid GPG signature."""
        assert os.path.isfile(SIGNATURE_FILE), (
            f"Original signature file {SIGNATURE_FILE} does not exist."
        )

        result = subprocess.run(
            ["gpg", "--list-packets", SIGNATURE_FILE],
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        is_signature = "signature" in output.lower() or ":signature packet:" in output
        assert is_signature, (
            f"Original file {SIGNATURE_FILE} no longer appears to be a GPG signature. "
            "It should not have been modified."
        )

    def test_gnupg_directory_still_exists(self):
        """The GPG keyring directory must still exist."""
        assert os.path.isdir(GNUPG_DIR), (
            f"GPG directory {GNUPG_DIR} no longer exists. "
            "The keyring should not have been deleted."
        )

    def test_secret_keys_still_present(self):
        """The user's secret keys must still be present."""
        result = subprocess.run(
            ["gpg", "--list-secret-keys"],
            capture_output=True,
            text=True,
            env={**os.environ, "GNUPGHOME": GNUPG_DIR}
        )
        assert result.returncode == 0, (
            f"Failed to list secret keys: {result.stderr}"
        )
        assert "sec" in result.stdout or result.stdout.strip(), (
            f"Secret keys appear to be missing from keyring. "
            f"Output: {result.stdout}"
        )


class TestContentIntegrity:
    """Tests to verify the extracted content matches the tarball."""

    def test_extracted_matches_tarball_listing(self):
        """The extracted files should match what's in the tarball."""
        assert os.path.isfile(DECRYPTED_TARBALL), (
            f"Decrypted tarball {DECRYPTED_TARBALL} does not exist."
        )
        assert os.path.isdir(EXTRACTED_DIR), (
            f"Extracted directory {EXTRACTED_DIR} does not exist."
        )

        # List contents of tarball
        result = subprocess.run(
            ["tar", "-tzf", DECRYPTED_TARBALL],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Failed to list tarball contents: {result.stderr}"
        )

        tarball_entries = set()
        for line in result.stdout.strip().split('\n'):
            if line:
                # Normalize: remove trailing slashes for directories
                entry = line.rstrip('/')
                if entry:
                    tarball_entries.add(entry)

        # Check that key files from tarball exist in extracted dir
        # We check for .pcap files specifically as they're mentioned in the task
        pcap_in_tarball = [e for e in tarball_entries if e.endswith('.pcap')]
        assert len(pcap_in_tarball) > 0, (
            "No .pcap files found in tarball listing"
        )

        # Verify at least one pcap from tarball exists in extracted
        found_match = False
        for pcap_entry in pcap_in_tarball:
            # The entry might be a path like "data/capture.pcap"
            # Check if it exists under extracted dir
            potential_path = os.path.join(EXTRACTED_DIR, pcap_entry)
            if os.path.isfile(potential_path):
                found_match = True
                break

        # Also do a recursive search in case extraction flattened structure
        if not found_match:
            for root, dirs, files in os.walk(EXTRACTED_DIR):
                for f in files:
                    if f.endswith('.pcap'):
                        found_match = True
                        break
                if found_match:
                    break

        assert found_match, (
            f"Could not find expected .pcap files from tarball in {EXTRACTED_DIR}. "
            f"Tarball contains: {pcap_in_tarball}"
        )
