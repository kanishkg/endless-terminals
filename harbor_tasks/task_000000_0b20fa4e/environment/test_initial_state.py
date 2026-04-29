# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the tarball extraction task.
"""

import os
import subprocess
import tarfile
import pytest


HOME_DIR = "/home/user"
TARBALL_PATH = "/home/user/metrics-export.tar.gz"
DASHBOARDS_DIR = "/home/user/dashboards"

# Expected archive structure
EXPECTED_ARCHIVE_MEMBERS = [
    "metrics-export/",
    "metrics-export/prometheus/",
    "metrics-export/prometheus/rules.yml",
    "metrics-export/prometheus/prometheus.yml",
    "metrics-export/grafana/",
    "metrics-export/grafana/dashboards/",
    "metrics-export/grafana/dashboards/system-overview.json",
    "metrics-export/grafana/dashboards/network-traffic.json",
    "metrics-export/grafana/dashboards/app-latency.json",
    "metrics-export/grafana/grafana.ini",
    "metrics-export/alertmanager/",
    "metrics-export/alertmanager/alertmanager.yml",
]

EXPECTED_DASHBOARD_FILES = [
    "metrics-export/grafana/dashboards/system-overview.json",
    "metrics-export/grafana/dashboards/network-traffic.json",
    "metrics-export/grafana/dashboards/app-latency.json",
]


class TestInitialState:
    """Tests to verify the initial state before the task is performed."""

    def test_home_directory_exists(self):
        """Verify /home/user exists and is a directory."""
        assert os.path.exists(HOME_DIR), f"Home directory {HOME_DIR} does not exist"
        assert os.path.isdir(HOME_DIR), f"{HOME_DIR} is not a directory"

    def test_home_directory_is_writable(self):
        """Verify /home/user is writable."""
        assert os.access(HOME_DIR, os.W_OK), f"{HOME_DIR} is not writable"

    def test_tarball_exists(self):
        """Verify the tarball exists at the expected location."""
        assert os.path.exists(TARBALL_PATH), (
            f"Tarball {TARBALL_PATH} does not exist. "
            "The metrics-export.tar.gz file must be present for this task."
        )

    def test_tarball_is_file(self):
        """Verify the tarball is a regular file."""
        assert os.path.isfile(TARBALL_PATH), (
            f"{TARBALL_PATH} exists but is not a regular file"
        )

    def test_tarball_is_valid_gzip(self):
        """Verify the tarball is a valid gzipped file."""
        # Check gzip magic bytes
        with open(TARBALL_PATH, 'rb') as f:
            magic = f.read(2)
        assert magic == b'\x1f\x8b', (
            f"{TARBALL_PATH} is not a valid gzip file (wrong magic bytes)"
        )

    def test_tarball_is_valid_tar(self):
        """Verify the tarball can be opened as a tar archive."""
        try:
            with tarfile.open(TARBALL_PATH, 'r:gz') as tar:
                # Just verify it opens successfully
                members = tar.getnames()
                assert len(members) > 0, "Tarball is empty"
        except tarfile.TarError as e:
            pytest.fail(f"{TARBALL_PATH} is not a valid tar archive: {e}")

    def test_tarball_contains_expected_structure(self):
        """Verify the tarball contains the expected directory structure."""
        with tarfile.open(TARBALL_PATH, 'r:gz') as tar:
            members = tar.getnames()

            # Normalize member names (remove trailing slashes for comparison)
            normalized_members = set()
            for m in members:
                normalized_members.add(m.rstrip('/'))

            # Check each expected member
            for expected in EXPECTED_ARCHIVE_MEMBERS:
                normalized_expected = expected.rstrip('/')
                assert normalized_expected in normalized_members, (
                    f"Expected archive member '{expected}' not found in tarball. "
                    f"Archive contains: {sorted(members)}"
                )

    def test_tarball_contains_dashboard_json_files(self):
        """Verify the tarball contains the expected dashboard JSON files."""
        with tarfile.open(TARBALL_PATH, 'r:gz') as tar:
            members = tar.getnames()

            for dashboard_file in EXPECTED_DASHBOARD_FILES:
                assert dashboard_file in members, (
                    f"Expected dashboard file '{dashboard_file}' not found in tarball"
                )

    def test_dashboard_files_are_readable_in_archive(self):
        """Verify the dashboard JSON files in the archive are readable."""
        with tarfile.open(TARBALL_PATH, 'r:gz') as tar:
            for dashboard_file in EXPECTED_DASHBOARD_FILES:
                member = tar.getmember(dashboard_file)
                assert member.isfile(), (
                    f"{dashboard_file} in archive is not a regular file"
                )
                # Try to extract and read the content
                f = tar.extractfile(member)
                assert f is not None, (
                    f"Could not extract {dashboard_file} from archive"
                )
                content = f.read()
                assert len(content) > 0, (
                    f"{dashboard_file} in archive is empty"
                )

    def test_dashboards_directory_does_not_exist(self):
        """Verify /home/user/dashboards/ does not exist initially."""
        assert not os.path.exists(DASHBOARDS_DIR), (
            f"Output directory {DASHBOARDS_DIR} already exists. "
            "It should not exist before the task is performed."
        )

    def test_tar_command_available(self):
        """Verify tar command is available."""
        result = subprocess.run(
            ['which', 'tar'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "tar command is not available. It must be installed for this task."
        )

    def test_gzip_command_available(self):
        """Verify gzip command is available."""
        result = subprocess.run(
            ['which', 'gzip'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            "gzip command is not available. It must be installed for this task."
        )

    def test_tar_can_list_archive(self):
        """Verify tar can list the contents of the archive."""
        result = subprocess.run(
            ['tar', '-tzf', TARBALL_PATH],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"tar command failed to list archive contents: {result.stderr}"
        )
        assert 'dashboards' in result.stdout.lower(), (
            "Archive listing does not contain 'dashboards' directory"
        )
