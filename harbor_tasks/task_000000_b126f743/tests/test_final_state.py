# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the archive/restore scripts to work reliably regardless of locale.
"""

import os
import stat
import subprocess
import shutil
import pytest


HOME = "/home/user"
SCRIPTS_DIR = os.path.join(HOME, "scripts")
TEST_PAYLOAD_DIR = os.path.join(HOME, "test_payload")
ARTIFACTS_DIR = os.path.join(HOME, "artifacts")
RESTORED_DIR = os.path.join(HOME, "restored")
ARCHIVE_SCRIPT = os.path.join(SCRIPTS_DIR, "archive.sh")
RESTORE_SCRIPT = os.path.join(SCRIPTS_DIR, "restore.sh")
BASHRC = os.path.join(HOME, ".bashrc")
COLLATE_SETTING = os.path.join(HOME, ".collate_setting")


class TestScriptsExistAndExecutable:
    """Test that the archive and restore scripts exist and are executable."""

    def test_archive_script_exists(self):
        assert os.path.isfile(ARCHIVE_SCRIPT), f"Archive script {ARCHIVE_SCRIPT} does not exist"

    def test_restore_script_exists(self):
        assert os.path.isfile(RESTORE_SCRIPT), f"Restore script {RESTORE_SCRIPT} does not exist"

    def test_archive_script_executable(self):
        assert os.access(ARCHIVE_SCRIPT, os.X_OK), f"Archive script {ARCHIVE_SCRIPT} is not executable"

    def test_restore_script_executable(self):
        assert os.access(RESTORE_SCRIPT, os.X_OK), f"Restore script {RESTORE_SCRIPT} is not executable"


class TestScriptsUseRequiredTools:
    """Test that scripts still use tar, gzip, and split as required."""

    def test_archive_script_uses_tar(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'tar' in content, "Archive script must still use tar command"

    def test_archive_script_uses_gzip(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'gzip' in content, "Archive script must still use gzip command"

    def test_archive_script_uses_split(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'split' in content, "Archive script must still use split command"

    def test_archive_script_uses_50m_chunks(self):
        with open(ARCHIVE_SCRIPT, 'r') as f:
            content = f.read()
        assert '50M' in content or '50m' in content.lower(), "Archive script must still use 50M chunk size"

    def test_restore_script_uses_gunzip_or_gzip(self):
        with open(RESTORE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'gunzip' in content or 'gzip' in content, "Restore script must still use gunzip/gzip command"

    def test_restore_script_uses_tar(self):
        with open(RESTORE_SCRIPT, 'r') as f:
            content = f.read()
        assert 'tar' in content, "Restore script must still use tar command"


class TestTestPayloadUnchanged:
    """Test that test_payload directory still exists and has content."""

    def test_test_payload_exists(self):
        assert os.path.isdir(TEST_PAYLOAD_DIR), f"Test payload directory {TEST_PAYLOAD_DIR} must still exist"

    def test_test_payload_has_files(self):
        """Check that test_payload contains actual files."""
        has_files = False
        for root, dirs, files in os.walk(TEST_PAYLOAD_DIR):
            if files:
                has_files = True
                break
        assert has_files, f"Test payload directory {TEST_PAYLOAD_DIR} must still contain files"

    def test_test_payload_size_reasonable(self):
        """Check that test_payload is still approximately the right size."""
        total_size = 0
        for root, dirs, files in os.walk(TEST_PAYLOAD_DIR):
            for f in files:
                filepath = os.path.join(root, f)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)

        min_size = 150 * 1024 * 1024  # 150MB
        assert total_size >= min_size, (
            f"Test payload appears to have been modified. "
            f"Size is now {total_size / (1024*1024):.1f}MB, expected at least 150MB."
        )


class TestCollateRotationStillExists:
    """Test that the .collate_setting rotation mechanism was not removed."""

    def test_collate_setting_file_exists(self):
        assert os.path.isfile(COLLATE_SETTING), (
            f"Collate setting file {COLLATE_SETTING} must not be removed. "
            "The fix must work regardless of locale, not by disabling the rotation."
        )

    def test_bashrc_still_has_collate_mechanism(self):
        """Check that .bashrc still has the locale rotation mechanism."""
        assert os.path.isfile(BASHRC), f"Bashrc file {BASHRC} must still exist"
        with open(BASHRC, 'r') as f:
            content = f.read()

        has_locale_ref = any(term in content for term in ['LC_COLLATE', 'collate', 'COLLATE'])
        assert has_locale_ref, (
            ".bashrc must still contain the locale/collate rotation mechanism. "
            "The fix must work regardless of locale, not by removing the rotation."
        )


def run_roundtrip_in_fresh_shell(run_number):
    """
    Run the full archive/restore round-trip in a fresh bash login shell.
    This triggers the locale rotation mechanism.
    Returns (success, error_message).
    """
    # Clean up any previous artifacts and restored directories
    cleanup_script = f"""
    rm -rf {ARTIFACTS_DIR} {RESTORED_DIR}
    """

    # The full round-trip command
    roundtrip_script = f"""
    set -e
    rm -rf {ARTIFACTS_DIR} {RESTORED_DIR}
    {ARCHIVE_SCRIPT} {TEST_PAYLOAD_DIR} {ARTIFACTS_DIR}
    {RESTORE_SCRIPT} {ARTIFACTS_DIR} {RESTORED_DIR}
    diff -r {TEST_PAYLOAD_DIR} {RESTORED_DIR}/home/user/test_payload
    """

    # Run in a fresh bash login shell to trigger locale rotation
    result = subprocess.run(
        ['bash', '-l', '-c', roundtrip_script],
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )

    if result.returncode != 0:
        error_msg = (
            f"Round-trip #{run_number} failed.\n"
            f"Exit code: {result.returncode}\n"
            f"Stdout: {result.stdout[:1000] if result.stdout else '(empty)'}\n"
            f"Stderr: {result.stderr[:1000] if result.stderr else '(empty)'}"
        )
        return False, error_msg

    # Check that diff output is empty (no differences)
    if result.stdout.strip():
        return False, f"Round-trip #{run_number}: diff found differences:\n{result.stdout[:1000]}"

    return True, None


class TestRoundTripReliability:
    """
    Test that the archive/restore round-trip works reliably 5 times in succession.
    Each run is in a fresh bash login shell to trigger the locale rotation.
    """

    def test_roundtrip_run_1(self):
        """First round-trip test."""
        success, error = run_roundtrip_in_fresh_shell(1)
        assert success, error

    def test_roundtrip_run_2(self):
        """Second round-trip test."""
        success, error = run_roundtrip_in_fresh_shell(2)
        assert success, error

    def test_roundtrip_run_3(self):
        """Third round-trip test."""
        success, error = run_roundtrip_in_fresh_shell(3)
        assert success, error

    def test_roundtrip_run_4(self):
        """Fourth round-trip test."""
        success, error = run_roundtrip_in_fresh_shell(4)
        assert success, error

    def test_roundtrip_run_5(self):
        """Fifth round-trip test."""
        success, error = run_roundtrip_in_fresh_shell(5)
        assert success, error


class TestArchiveProducesChunks:
    """Test that archive.sh produces the expected chunk files."""

    def test_archive_creates_chunks(self):
        """Run archive and verify chunks are created."""
        # Clean up
        if os.path.exists(ARTIFACTS_DIR):
            shutil.rmtree(ARTIFACTS_DIR)

        # Run archive
        result = subprocess.run(
            ['bash', '-l', '-c', f'{ARCHIVE_SCRIPT} {TEST_PAYLOAD_DIR} {ARTIFACTS_DIR}'],
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, (
            f"Archive script failed.\n"
            f"Exit code: {result.returncode}\n"
            f"Stderr: {result.stderr}"
        )

        assert os.path.isdir(ARTIFACTS_DIR), f"Artifacts directory {ARTIFACTS_DIR} was not created"

        # Check that chunk files exist
        chunks = [f for f in os.listdir(ARTIFACTS_DIR) if f.startswith('chunk_')]
        assert len(chunks) >= 3, (
            f"Expected at least 3 chunk files (for ~180MB payload), "
            f"but found {len(chunks)}: {chunks}"
        )

    def test_chunks_are_approximately_50mb(self):
        """Verify that most chunks are approximately 50MB."""
        if not os.path.exists(ARTIFACTS_DIR):
            # Run archive first
            subprocess.run(
                ['bash', '-l', '-c', f'{ARCHIVE_SCRIPT} {TEST_PAYLOAD_DIR} {ARTIFACTS_DIR}'],
                capture_output=True,
                timeout=120
            )

        chunks = [f for f in os.listdir(ARTIFACTS_DIR) if f.startswith('chunk_')]
        if not chunks:
            pytest.skip("No chunks found, skipping size check")

        chunk_sizes = []
        for chunk in chunks:
            chunk_path = os.path.join(ARTIFACTS_DIR, chunk)
            chunk_sizes.append(os.path.getsize(chunk_path))

        # All chunks except possibly the last should be exactly 50MB
        expected_size = 50 * 1024 * 1024
        for i, size in enumerate(chunk_sizes[:-1]):  # Exclude last chunk
            assert abs(size - expected_size) < 1024, (
                f"Chunk {i} size is {size}, expected {expected_size} (50MB)"
            )


class TestRestoreWithDifferentLocales:
    """Test that restore works correctly under different locale settings."""

    def test_restore_with_c_locale(self):
        """Test restore works with LC_COLLATE=C."""
        # Clean up and archive
        cleanup_and_archive = f"""
        rm -rf {ARTIFACTS_DIR} {RESTORED_DIR}
        {ARCHIVE_SCRIPT} {TEST_PAYLOAD_DIR} {ARTIFACTS_DIR}
        """
        subprocess.run(['bash', '-c', cleanup_and_archive], capture_output=True, timeout=120)

        # Restore with C locale
        restore_script = f"""
        export LC_COLLATE=C
        export LC_ALL=C
        {RESTORE_SCRIPT} {ARTIFACTS_DIR} {RESTORED_DIR}
        diff -r {TEST_PAYLOAD_DIR} {RESTORED_DIR}/home/user/test_payload
        """

        result = subprocess.run(
            ['bash', '-c', restore_script],
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, (
            f"Restore with LC_COLLATE=C failed.\n"
            f"Exit code: {result.returncode}\n"
            f"Stderr: {result.stderr}"
        )

    def test_restore_with_utf8_locale(self):
        """Test restore works with LC_COLLATE=en_US.UTF-8."""
        # Clean up and archive
        cleanup_and_archive = f"""
        rm -rf {ARTIFACTS_DIR} {RESTORED_DIR}
        {ARCHIVE_SCRIPT} {TEST_PAYLOAD_DIR} {ARTIFACTS_DIR}
        """
        subprocess.run(['bash', '-c', cleanup_and_archive], capture_output=True, timeout=120)

        # Restore with UTF-8 locale
        restore_script = f"""
        export LC_COLLATE=en_US.UTF-8
        export LC_ALL=en_US.UTF-8
        {RESTORE_SCRIPT} {ARTIFACTS_DIR} {RESTORED_DIR}
        diff -r {TEST_PAYLOAD_DIR} {RESTORED_DIR}/home/user/test_payload
        """

        result = subprocess.run(
            ['bash', '-c', restore_script],
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, (
            f"Restore with LC_COLLATE=en_US.UTF-8 failed.\n"
            f"Exit code: {result.returncode}\n"
            f"Stderr: {result.stderr}"
        )
