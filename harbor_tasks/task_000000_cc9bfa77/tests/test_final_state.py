# test_final_state.py
"""
Tests to validate the final state after the WAL recovery task is completed.
Verifies that:
1. recover.sh exists and is executable
2. Running recover.sh produces a valid pgdata directory
3. The correct WAL segments were selected from the correct sources
4. The script contains diagnostic logic (not just hardcoded copies)
5. The recovered database is startable and has replayed WAL properly
"""

import os
import subprocess
import hashlib
import re
import time
import signal
import pytest

HOME = "/home/user"
WAL_RECOVERY_DIR = os.path.join(HOME, "wal_recovery")
PRIMARY_WAL_DIR = os.path.join(WAL_RECOVERY_DIR, "primary_wal")
REPLICA_WAL_DIR = os.path.join(WAL_RECOVERY_DIR, "replica_wal")
BASE_BACKUP = os.path.join(WAL_RECOVERY_DIR, "base_backup.tar.gz")
RECOVER_SCRIPT = os.path.join(WAL_RECOVERY_DIR, "recover.sh")
PGDATA_DIR = os.path.join(WAL_RECOVERY_DIR, "pgdata")


def get_file_md5(filepath):
    """Calculate MD5 hash of a file."""
    if not os.path.isfile(filepath):
        return None
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def run_command(cmd, timeout=120, cwd=None):
    """Run a command and return result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            shell=isinstance(cmd, str)
        )
        return result
    except subprocess.TimeoutExpired:
        return None


class TestRecoverScriptExists:
    """Test that the recovery script exists and is properly configured."""

    def test_recover_script_exists(self):
        """The recover.sh script must exist."""
        assert os.path.isfile(RECOVER_SCRIPT), \
            f"recover.sh does not exist at {RECOVER_SCRIPT}"

    def test_recover_script_is_executable(self):
        """The recover.sh script must be executable."""
        assert os.access(RECOVER_SCRIPT, os.X_OK), \
            f"recover.sh at {RECOVER_SCRIPT} is not executable"

    def test_recover_script_contains_diagnostic_logic(self):
        """The script must contain logic to diagnose WAL segment validity."""
        with open(RECOVER_SCRIPT, 'r') as f:
            script_content = f.read().lower()

        # Check for evidence of diagnostic tools being used
        diagnostic_patterns = [
            r'pg_waldump',
            r'md5sum|md5',
            r'sha\d*sum|sha\d*',
            r'checksum',
            r'cmp\s',
            r'diff\s',
            r'hexdump',
            r'xxd',
            r'od\s+-',
        ]

        found_diagnostic = False
        for pattern in diagnostic_patterns:
            if re.search(pattern, script_content):
                found_diagnostic = True
                break

        assert found_diagnostic, \
            "recover.sh must contain diagnostic logic (pg_waldump, checksum, md5, etc.) " \
            "to validate WAL segments, not just hardcoded file copies"


class TestRecoverScriptExecution:
    """Test that running the recovery script produces expected results."""

    @pytest.fixture(scope="class", autouse=True)
    def run_recover_script(self):
        """Run the recover script once before all tests in this class."""
        # Clean up any existing pgdata first
        if os.path.exists(PGDATA_DIR):
            subprocess.run(['rm', '-rf', PGDATA_DIR], check=False)

        # Run the recovery script
        result = run_command(['bash', RECOVER_SCRIPT], timeout=300, cwd=WAL_RECOVERY_DIR)

        if result is None:
            pytest.fail("recover.sh timed out after 300 seconds")

        # Store result for potential debugging
        self._script_result = result

        yield result

    def test_recover_script_runs_successfully(self, run_recover_script):
        """The recover.sh script should complete (exit code 0 or produce pgdata)."""
        # We check if pgdata was created rather than strict exit code
        # because some recovery approaches may have non-zero exit but still work
        assert os.path.isdir(PGDATA_DIR), \
            f"recover.sh did not create pgdata directory at {PGDATA_DIR}. " \
            f"Script stdout: {run_recover_script.stdout[:500] if run_recover_script else 'N/A'}... " \
            f"Script stderr: {run_recover_script.stderr[:500] if run_recover_script else 'N/A'}..."

    def test_pgdata_directory_exists(self, run_recover_script):
        """The pgdata directory must exist after running recover.sh."""
        assert os.path.isdir(PGDATA_DIR), \
            f"pgdata directory does not exist at {PGDATA_DIR}"

    def test_pgdata_has_pg_version(self, run_recover_script):
        """The pgdata directory must contain PG_VERSION file."""
        pg_version_path = os.path.join(PGDATA_DIR, "PG_VERSION")
        assert os.path.isfile(pg_version_path), \
            f"PG_VERSION file not found in pgdata at {pg_version_path}"

    def test_pgdata_has_postgresql_conf(self, run_recover_script):
        """The pgdata directory must contain postgresql.conf."""
        conf_path = os.path.join(PGDATA_DIR, "postgresql.conf")
        assert os.path.isfile(conf_path), \
            f"postgresql.conf not found in pgdata at {conf_path}"

    def test_pgdata_has_base_directory(self, run_recover_script):
        """The pgdata directory must contain base/ subdirectory."""
        base_path = os.path.join(PGDATA_DIR, "base")
        assert os.path.isdir(base_path), \
            f"base/ directory not found in pgdata at {base_path}"

    def test_pgdata_has_global_directory(self, run_recover_script):
        """The pgdata directory must contain global/ subdirectory."""
        global_path = os.path.join(PGDATA_DIR, "global")
        assert os.path.isdir(global_path), \
            f"global/ directory not found in pgdata at {global_path}"

    def test_pgdata_has_pg_wal_directory(self, run_recover_script):
        """The pgdata directory must contain pg_wal/ subdirectory."""
        pg_wal_path = os.path.join(PGDATA_DIR, "pg_wal")
        assert os.path.isdir(pg_wal_path), \
            f"pg_wal/ directory not found in pgdata at {pg_wal_path}"


class TestWalSegmentSelection:
    """Test that the correct WAL segments were selected from correct sources."""

    def test_segment_004_from_replica(self):
        """Segment 004 must be copied from replica_wal (not primary_wal)."""
        pgdata_seg4 = os.path.join(PGDATA_DIR, "pg_wal", "000000010000000000000004")
        replica_seg4 = os.path.join(REPLICA_WAL_DIR, "000000010000000000000004")
        primary_seg4 = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000004")

        if not os.path.isfile(pgdata_seg4):
            pytest.skip("Segment 004 not found in pgdata/pg_wal/ - may have been archived differently")

        pgdata_hash = get_file_md5(pgdata_seg4)
        replica_hash = get_file_md5(replica_seg4)
        primary_hash = get_file_md5(primary_seg4)

        assert pgdata_hash == replica_hash, \
            f"Segment 004 in pgdata must match replica_wal (valid copy), not primary_wal (corrupted). " \
            f"pgdata hash: {pgdata_hash}, replica hash: {replica_hash}, primary hash: {primary_hash}"

        # Also verify it's NOT from primary (which is corrupted)
        if primary_hash != replica_hash:
            assert pgdata_hash != primary_hash, \
                f"Segment 004 appears to be from primary_wal (corrupted) instead of replica_wal (valid)"

    def test_segment_005_from_primary(self):
        """Segment 005 must be copied from primary_wal (not replica_wal)."""
        pgdata_seg5 = os.path.join(PGDATA_DIR, "pg_wal", "000000010000000000000005")
        primary_seg5 = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000005")
        replica_seg5 = os.path.join(REPLICA_WAL_DIR, "000000010000000000000005")

        if not os.path.isfile(pgdata_seg5):
            pytest.skip("Segment 005 not found in pgdata/pg_wal/ - may have been archived differently")

        pgdata_hash = get_file_md5(pgdata_seg5)
        primary_hash = get_file_md5(primary_seg5)
        replica_hash = get_file_md5(replica_seg5)

        assert pgdata_hash == primary_hash, \
            f"Segment 005 in pgdata must match primary_wal (valid copy), not replica_wal (corrupted). " \
            f"pgdata hash: {pgdata_hash}, primary hash: {primary_hash}, replica hash: {replica_hash}"

        # Also verify it's NOT from replica (which is corrupted)
        if primary_hash != replica_hash:
            assert pgdata_hash != replica_hash, \
                f"Segment 005 appears to be from replica_wal (corrupted) instead of primary_wal (valid)"


class TestOriginalFilesUnchanged:
    """Test that original WAL files were not modified."""

    def test_primary_wal_segment_003_unchanged(self):
        """Primary WAL segment 003 should be unchanged."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000003")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Primary segment 003 size changed: {size} (expected 16MB)"

    def test_primary_wal_segment_004_unchanged(self):
        """Primary WAL segment 004 should be unchanged."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000004")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Primary segment 004 size changed: {size} (expected 16MB)"

    def test_primary_wal_segment_005_unchanged(self):
        """Primary WAL segment 005 should be unchanged."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000005")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Primary segment 005 size changed: {size} (expected 16MB)"

    def test_primary_wal_segment_006_unchanged(self):
        """Primary WAL segment 006 should be unchanged (partial)."""
        seg_path = os.path.join(PRIMARY_WAL_DIR, "000000010000000000000006")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 8 * 1024 * 1024, \
            f"Primary segment 006 size changed: {size} (expected 8MB)"

    def test_replica_wal_segment_003_unchanged(self):
        """Replica WAL segment 003 should be unchanged."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000003")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Replica segment 003 size changed: {size} (expected 16MB)"

    def test_replica_wal_segment_004_unchanged(self):
        """Replica WAL segment 004 should be unchanged."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000004")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Replica segment 004 size changed: {size} (expected 16MB)"

    def test_replica_wal_segment_005_unchanged(self):
        """Replica WAL segment 005 should be unchanged."""
        seg_path = os.path.join(REPLICA_WAL_DIR, "000000010000000000000005")
        assert os.path.isfile(seg_path), f"Original file {seg_path} is missing"
        size = os.path.getsize(seg_path)
        assert size == 16 * 1024 * 1024, \
            f"Replica segment 005 size changed: {size} (expected 16MB)"

    def test_base_backup_unchanged(self):
        """Base backup tarball should be unchanged."""
        assert os.path.isfile(BASE_BACKUP), f"Base backup {BASE_BACKUP} is missing"


class TestDatabaseStartable:
    """Test that the recovered database can be started."""

    @pytest.fixture(scope="class")
    def start_postgres(self):
        """Attempt to start PostgreSQL on the recovered data directory."""
        # First, ensure any existing postgres is stopped
        subprocess.run(
            ['pg_ctl', 'stop', '-D', PGDATA_DIR, '-m', 'immediate'],
            capture_output=True,
            timeout=30
        )
        time.sleep(1)

        # Ensure proper permissions
        subprocess.run(['chmod', '-R', '700', PGDATA_DIR], check=False)

        # Try to start postgres
        # Use -o options to set port to avoid conflicts
        port = 15432
        result = subprocess.run(
            ['pg_ctl', 'start', '-D', PGDATA_DIR, '-w', '-t', '60',
             '-o', f'-p {port} -c listen_addresses=localhost'],
            capture_output=True,
            text=True,
            timeout=120
        )

        started = result.returncode == 0

        yield {
            'started': started,
            'port': port,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }

        # Cleanup: stop postgres
        subprocess.run(
            ['pg_ctl', 'stop', '-D', PGDATA_DIR, '-m', 'immediate'],
            capture_output=True,
            timeout=30
        )

    def test_postgres_starts(self, start_postgres):
        """PostgreSQL should start successfully on the recovered pgdata."""
        assert start_postgres['started'], \
            f"PostgreSQL failed to start. " \
            f"Return code: {start_postgres['returncode']}. " \
            f"Stdout: {start_postgres['stdout'][:500]}... " \
            f"Stderr: {start_postgres['stderr'][:500]}..."

    def test_wal_lsn_indicates_replay(self, start_postgres):
        """After starting, the WAL LSN should indicate segments 3-5 were replayed."""
        if not start_postgres['started']:
            pytest.skip("PostgreSQL did not start, cannot check LSN")

        port = start_postgres['port']

        # Give postgres a moment to fully start
        time.sleep(2)

        # Query current WAL LSN
        result = subprocess.run(
            ['psql', '-p', str(port), '-d', 'postgres', '-t', '-A', '-c',
             'SELECT pg_current_wal_lsn();'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            # Try alternative query for recovery mode
            result = subprocess.run(
                ['psql', '-p', str(port), '-d', 'postgres', '-t', '-A', '-c',
                 'SELECT pg_last_wal_replay_lsn();'],
                capture_output=True,
                text=True,
                timeout=30
            )

        assert result.returncode == 0, \
            f"Failed to query WAL LSN. stderr: {result.stderr}"

        lsn_str = result.stdout.strip()

        # Parse LSN (format: X/YYYYYYYY)
        if '/' in lsn_str:
            parts = lsn_str.split('/')
            high = int(parts[0], 16)
            low = int(parts[1], 16)
            lsn_value = (high << 32) | low

            # 0/6000000 = 0x6000000 = 100663296
            min_expected_lsn = 0x6000000

            assert lsn_value >= min_expected_lsn, \
                f"WAL LSN {lsn_str} (decimal: {lsn_value}) is less than expected 0/6000000 " \
                f"(decimal: {min_expected_lsn}). WAL segments 3-5 may not have been fully replayed."
        else:
            # If we can't parse, at least verify we got something
            assert lsn_str, f"Empty LSN returned from database"


class TestPgdataIntegrity:
    """Additional integrity checks on the recovered pgdata."""

    def test_pg_control_exists(self):
        """pg_control file must exist in global/."""
        pg_control = os.path.join(PGDATA_DIR, "global", "pg_control")
        assert os.path.isfile(pg_control), \
            f"pg_control file not found at {pg_control}"

    def test_pg_control_valid(self):
        """pg_controldata should be able to read the control file."""
        result = subprocess.run(
            ['pg_controldata', PGDATA_DIR],
            capture_output=True,
            text=True,
            timeout=30
        )

        # pg_controldata should succeed or at least produce output
        # Even if there are warnings, we should see control data
        output = result.stdout + result.stderr

        assert 'pg_control' in output.lower() or 'database' in output.lower() or \
               'checkpoint' in output.lower() or 'wal' in output.lower(), \
            f"pg_controldata could not read control file. Output: {output[:500]}"

    def test_wal_segments_present_in_pgdata(self):
        """At least some WAL segments should be present in pgdata/pg_wal/."""
        pg_wal_dir = os.path.join(PGDATA_DIR, "pg_wal")

        if not os.path.isdir(pg_wal_dir):
            pytest.skip("pg_wal directory not found")

        wal_files = [f for f in os.listdir(pg_wal_dir) 
                     if f.startswith('0000') and len(f) == 24]

        # We expect at least segments 3, 4, 5 (and possibly 6)
        assert len(wal_files) >= 3, \
            f"Expected at least 3 WAL segments in pg_wal/, found {len(wal_files)}: {wal_files}"
