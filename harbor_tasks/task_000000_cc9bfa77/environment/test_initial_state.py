# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the WAL recovery task.
"""

import os
import subprocess
import tarfile
import json
import pytest

HOME = "/home/user"
WAL_RECOVERY_DIR = os.path.join(HOME, "wal_recovery")
PRIMARY_WAL_DIR = os.path.join(WAL_RECOVERY_DIR, "primary_wal")
REPLICA_WAL_DIR = os.path.join(WAL_RECOVERY_DIR, "replica_wal")
BASE_BACKUP = os.path.join(WAL_RECOVERY_DIR, "base_backup.tar.gz")
MANIFEST = os.path.join(WAL_RECOVERY_DIR, "manifest.json")


class TestWalRecoveryDirectoryStructure:
    """Test that the required directory structure exists."""

    def test_wal_recovery_dir_exists(self):
        """The main wal_recovery directory must exist."""
        assert os.path.isdir(WAL_RECOVERY_DIR), \
            f"Directory {WAL_RECOVERY_DIR} does not exist"

    def test_wal_recovery_dir_writable(self):
        """The wal_recovery directory must be writable."""
        assert os.access(WAL_RECOVERY_DIR, os.W_OK), \
            f"Directory {WAL_RECOVERY_DIR} is not writable"

    def test_primary_wal_dir_exists(self):
        """The primary_wal directory must exist."""
        assert os.path.isdir(PRIMARY_WAL_DIR), \
            f"Directory {PRIMARY_WAL_DIR} does not exist"

    def test_replica_wal_dir_exists(self):
        """The replica_wal directory must exist."""
        assert os.path.isdir(REPLICA_WAL_DIR), \
            f"Directory {REPLICA_WAL_DIR} does not exist"


class TestBaseBackup:
    """Test the base backup file."""

    def test_base_backup_exists(self):
        """The base backup tarball must exist."""
        assert os.path.isfile(BASE_BACKUP), \
            f"Base backup file {BASE_BACKUP} does not exist"

    def test_base_backup_is_valid_tarball(self):
        """The base backup must be a valid gzipped tarball."""
        try:
            with tarfile.open(BASE_BACKUP, 'r:gz') as tar:
                members = tar.getnames()
                assert len(members) > 0, "Base backup tarball is empty"
        except tarfile.TarError as e:
            pytest.fail(f"Base backup is not a valid tarball: {e}")

    def test_base_backup_contains_pgdata_structure(self):
        """The base backup must contain standard PostgreSQL data directory structure."""
        required_items = ['PG_VERSION', 'postgresql.conf', 'pg_hba.conf', 'base', 'global']
        with tarfile.open(BASE_BACKUP, 'r:gz') as tar:
            members = tar.getnames()
            # Check for required files/dirs (may be at root or in a subdirectory)
            for item in required_items:
                found = any(item in m for m in members)
                assert found, f"Base backup missing required PostgreSQL item: {item}"


class TestManifest:
    """Test the manifest.json file."""

    def test_manifest_exists(self):
        """The manifest.json file must exist."""
        assert os.path.isfile(MANIFEST), \
            f"Manifest file {MANIFEST} does not exist"

    def test_manifest_is_valid_json(self):
        """The manifest must be valid JSON."""
        try:
            with open(MANIFEST, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"Manifest is not valid JSON: {e}")

    def test_manifest_contains_required_fields(self):
        """The manifest must contain required metadata fields."""
        with open(MANIFEST, 'r') as f:
            data = json.load(f)

        required_fields = ['base_backup_lsn', 'crash_time', 'primary_last_lsn', 'replica_last_received_lsn']
        for field in required_fields:
            assert field in data, f"Manifest missing required field: {field}"


class TestPrimaryWalSegments:
    """Test the WAL segments in primary_wal directory."""

    def test_primary_segment_003_exists(self):
        """Primary WAL segment 000000010000000000000003 must exist."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000003")
        assert os.path.isfile(seg_path), \
            f"Primary WAL segment 000000010000000000000003 does not exist at {seg_path}"

    def test_primary_segment_003_size(self):
        """Primary WAL segment 003 should be 16MB."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000003")
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Primary segment 003 size is {size}, expected 16MB (16777216 bytes)"

    def test_primary_segment_004_exists(self):
        """Primary WAL segment 000000010000000000000004 must exist (corrupted)."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000004")
        assert os.path.isfile(seg_path), \
            f"Primary WAL segment 000000010000000000000004 does not exist at {seg_path}"

    def test_primary_segment_004_size(self):
        """Primary WAL segment 004 should be 16MB."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000004")
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Primary segment 004 size is {size}, expected 16MB (16777216 bytes)"

    def test_primary_segment_005_exists(self):
        """Primary WAL segment 000000010000000000000005 must exist."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000005")
        assert os.path.isfile(seg_path), \
            f"Primary WAL segment 000000010000000000000005 does not exist at {seg_path}"

    def test_primary_segment_005_size(self):
        """Primary WAL segment 005 should be 16MB."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000005")
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Primary segment 005 size is {size}, expected 16MB (16777216 bytes)"

    def test_primary_segment_006_exists(self):
        """Primary WAL segment 000000010000000000000006 must exist (partial)."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000006")
        assert os.path.isfile(seg_path), \
            f"Primary WAL segment 000000010000000000000006 does not exist at {seg_path}"

    def test_primary_segment_006_is_partial(self):
        """Primary WAL segment 006 should be partial (8MB, not full 16MB)."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000006")
        size = os.path.getsize(seg_path)
        assert size == 8 * 1024 * 1024, \
            f"Primary segment 006 size is {size}, expected 8MB (8388608 bytes) - partial segment"


class TestReplicaWalSegments:
    """Test the WAL segments in replica_wal directory."""

    def test_replica_segment_003_exists(self):
        """Replica WAL segment 000000010000000000000003 must exist."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000003")
        assert os.path.isfile(seg_path), \
            f"Replica WAL segment 000000010000000000000003 does not exist at {seg_path}"

    def test_replica_segment_003_size(self):
        """Replica WAL segment 003 should be 16MB."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000003")
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Replica segment 003 size is {size}, expected 16MB (16777216 bytes)"

    def test_replica_segment_004_exists(self):
        """Replica WAL segment 000000010000000000000004 must exist (valid copy)."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000004")
        assert os.path.isfile(seg_path), \
            f"Replica WAL segment 000000010000000000000004 does not exist at {seg_path}"

    def test_replica_segment_004_size(self):
        """Replica WAL segment 004 should be 16MB."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000004")
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Replica segment 004 size is {size}, expected 16MB (16777216 bytes)"

    def test_replica_segment_005_exists(self):
        """Replica WAL segment 000000010000000000000005 must exist (corrupted)."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000005")
        assert os.path.isfile(seg_path), \
            f"Replica WAL segment 000000010000000000000005 does not exist at {seg_path}"

    def test_replica_segment_005_size(self):
        """Replica WAL segment 005 should be 16MB."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000005")
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Replica segment 005 size is {size}, expected 16MB (16777216 bytes)"

    def test_replica_segment_006_does_not_exist(self):
        """Replica WAL segment 006 should NOT exist (never received)."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000006")
        assert not os.path.exists(seg_path), \
            f"Replica WAL segment 006 should not exist but found at {seg_path}"


class TestSegmentCorruption:
    """Test that the corruption patterns are as expected."""

    def test_segment_003_identical_on_both(self):
        """Segment 003 should be identical on primary and replica."""
        primary_seg = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000003")
        replica_seg = os.path.join(REPLICA_WAL_DIR, "000000010000000000000003")

        result_primary = subprocess.run(['md5sum', primary_seg], capture_output=True, text=True)
        result_replica = subprocess.run(['md5sum', replica_seg], capture_output=True, text=True)

        primary_hash = result_primary.stdout.split()[0]
        replica_hash = result_replica.stdout.split()[0]

        assert primary_hash == replica_hash, \
            f"Segment 003 differs between primary ({primary_hash}) and replica ({replica_hash})"

    def test_segment_004_differs_between_sources(self):
        """Segment 004 should differ between primary (corrupted) and replica (valid)."""
        primary_seg = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000004")
        replica_seg = os.path.join(REPLICA_WAL_DIR, "000000010000000000000004")

        result_primary = subprocess.run(['md5sum', primary_seg], capture_output=True, text=True)
        result_replica = subprocess.run(['md5sum', replica_seg], capture_output=True, text=True)

        primary_hash = result_primary.stdout.split()[0]
        replica_hash = result_replica.stdout.split()[0]

        assert primary_hash != replica_hash, \
            f"Segment 004 should differ between primary and replica (corruption test), but both have hash {primary_hash}"

    def test_segment_005_differs_between_sources(self):
        """Segment 005 should differ between primary (valid) and replica (corrupted)."""
        primary_seg = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000005")
        replica_seg = os.path.join(REPLICA_WAL_DIR, "000000010000000000000005")

        result_primary = subprocess.run(['md5sum', primary_seg], capture_output=True, text=True)
        result_replica = subprocess.run(['md5sum', replica_seg], capture_output=True, text=True)

        primary_hash = result_primary.stdout.split()[0]
        replica_hash = result_replica.stdout.split()[0]

        assert primary_hash != replica_hash, \
            f"Segment 005 should differ between primary and replica (corruption test), but both have hash {primary_hash}"


class TestPostgresTools:
    """Test that required PostgreSQL tools are available."""

    def test_pg_waldump_available(self):
        """pg_waldump must be available in PATH."""
        result = subprocess.run(['which', 'pg_waldump'], capture_output=True, text=True)
        assert result.returncode == 0, \
            "pg_waldump is not available in PATH. PostgreSQL 15 tools must be installed."

    def test_pg_resetwal_available(self):
        """pg_resetwal must be available in PATH."""
        result = subprocess.run(['which', 'pg_resetwal'], capture_output=True, text=True)
        assert result.returncode == 0, \
            "pg_resetwal is not available in PATH. PostgreSQL 15 tools must be installed."

    def test_pg_ctl_available(self):
        """pg_ctl must be available in PATH."""
        result = subprocess.run(['which', 'pg_ctl'], capture_output=True, text=True)
        assert result.returncode == 0, \
            "pg_ctl is not available in PATH. PostgreSQL 15 tools must be installed."

    def test_postgres_version(self):
        """PostgreSQL version should be 15."""
        result = subprocess.run(['pg_waldump', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "Failed to get pg_waldump version"
        assert '15' in result.stdout or 'PostgreSQL' in result.stdout, \
            f"PostgreSQL 15 expected, got: {result.stdout.strip()}"


class TestOutputFilesDoNotExist:
    """Ensure output files/directories don't exist yet (clean initial state)."""

    def test_recover_script_does_not_exist(self):
        """The recover.sh script should not exist yet."""
        script_path = os.path.join(WAL_RECOVERY_DIR, "recover.sh")
        assert not os.path.exists(script_path), \
            f"recover.sh already exists at {script_path} - initial state should be clean"

    def test_pgdata_does_not_exist(self):
        """The pgdata directory should not exist yet."""
        pgdata_path = os.path.join(WAL_RECOVERY_DIR, "pgdata")
        assert not os.path.exists(pgdata_path), \
            f"pgdata directory already exists at {pgdata_path} - initial state should be clean"
