# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the tarball extraction task.
"""

import os
import subprocess
import tarfile
import pytest


HOME_DIR = "/home/user"
TARBALL_PATH = "/home/user/metrics-export.tar.gz"
DASHBOARDS_DIR = "/home/user/dashboards"

EXPECTED_DASHBOARD_FILES = [
    "system-overview.json",
    "network-traffic.json",
    "app-latency.json",
]

ARCHIVE_DASHBOARD_PATHS = {
    "system-overview.json": "metrics-export/grafana/dashboards/system-overview.json",
    "network-traffic.json": "metrics-export/grafana/dashboards/network-traffic.json",
    "app-latency.json": "metrics-export/grafana/dashboards/app-latency.json",
}


class TestFinalState:
    """Tests to verify the final state after the task is completed."""

    def test_tarball_still_exists(self):
        """Verify the original tarball was not deleted."""
        assert os.path.exists(TARBALL_PATH), (
            f"Tarball {TARBALL_PATH} no longer exists. "
            "The original archive should remain unchanged."
        )

    def test_tarball_is_still_valid(self):
        """Verify the original tarball is still a valid gzipped tar archive."""
        assert os.path.isfile(TARBALL_PATH), (
            f"{TARBALL_PATH} is not a regular file"
        )
        # Check gzip magic bytes
        with open(TARBALL_PATH, 'rb') as f:
            magic = f.read(2)
        assert magic == b'\x1f\x8b', (
            f"{TARBALL_PATH} is no longer a valid gzip file"
        )
        # Verify it can still be opened as tar
        try:
            with tarfile.open(TARBALL_PATH, 'r:gz') as tar:
                members = tar.getnames()
                assert len(members) > 0, "Tarball appears to be empty or corrupted"
        except tarfile.TarError as e:
            pytest.fail(f"{TARBALL_PATH} is no longer a valid tar archive: {e}")

    def test_dashboards_directory_exists(self):
        """Verify /home/user/dashboards/ exists."""
        assert os.path.exists(DASHBOARDS_DIR), (
            f"Output directory {DASHBOARDS_DIR} does not exist. "
            "You need to create this directory and extract the dashboard files into it."
        )

    def test_dashboards_directory_is_directory(self):
        """Verify /home/user/dashboards/ is a directory."""
        assert os.path.isdir(DASHBOARDS_DIR), (
            f"{DASHBOARDS_DIR} exists but is not a directory"
        )

    def test_system_overview_json_exists(self):
        """Verify system-overview.json exists in dashboards directory."""
        filepath = os.path.join(DASHBOARDS_DIR, "system-overview.json")
        assert os.path.exists(filepath), (
            f"{filepath} does not exist. "
            "Extract system-overview.json from the archive."
        )
        assert os.path.isfile(filepath), (
            f"{filepath} is not a regular file"
        )

    def test_network_traffic_json_exists(self):
        """Verify network-traffic.json exists in dashboards directory."""
        filepath = os.path.join(DASHBOARDS_DIR, "network-traffic.json")
        assert os.path.exists(filepath), (
            f"{filepath} does not exist. "
            "Extract network-traffic.json from the archive."
        )
        assert os.path.isfile(filepath), (
            f"{filepath} is not a regular file"
        )

    def test_app_latency_json_exists(self):
        """Verify app-latency.json exists in dashboards directory."""
        filepath = os.path.join(DASHBOARDS_DIR, "app-latency.json")
        assert os.path.exists(filepath), (
            f"{filepath} does not exist. "
            "Extract app-latency.json from the archive."
        )
        assert os.path.isfile(filepath), (
            f"{filepath} is not a regular file"
        )

    def test_exactly_three_files_in_dashboards(self):
        """Verify exactly 3 files exist in /home/user/dashboards/."""
        result = subprocess.run(
            ['ls', DASHBOARDS_DIR],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to list {DASHBOARDS_DIR}"

        files = [f for f in result.stdout.strip().split('\n') if f]
        assert len(files) == 3, (
            f"Expected exactly 3 files in {DASHBOARDS_DIR}, found {len(files)}: {files}. "
            "Only the three dashboard JSON files should be present."
        )

    def test_no_subdirectories_in_dashboards(self):
        """Verify no subdirectories exist in /home/user/dashboards/ (files are flat)."""
        result = subprocess.run(
            ['find', DASHBOARDS_DIR, '-type', 'd'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Failed to find directories in {DASHBOARDS_DIR}"

        dirs = [d for d in result.stdout.strip().split('\n') if d]
        assert len(dirs) == 1, (
            f"Expected only 1 directory (the dashboards dir itself), found {len(dirs)}: {dirs}. "
            "Files should be flat in /home/user/dashboards/, not nested in subdirectories."
        )
        assert dirs[0] == DASHBOARDS_DIR, (
            f"Unexpected directory structure: {dirs}"
        )

    def test_only_expected_files_present(self):
        """Verify only the expected dashboard files are present."""
        actual_files = set(os.listdir(DASHBOARDS_DIR))
        expected_files = set(EXPECTED_DASHBOARD_FILES)

        extra_files = actual_files - expected_files
        missing_files = expected_files - actual_files

        assert not extra_files, (
            f"Unexpected files found in {DASHBOARDS_DIR}: {extra_files}. "
            "Only dashboard JSON files should be extracted."
        )
        assert not missing_files, (
            f"Missing expected files in {DASHBOARDS_DIR}: {missing_files}"
        )

    def test_system_overview_content_matches_archive(self):
        """Verify system-overview.json content matches the archive."""
        self._verify_file_content_matches("system-overview.json")

    def test_network_traffic_content_matches_archive(self):
        """Verify network-traffic.json content matches the archive."""
        self._verify_file_content_matches("network-traffic.json")

    def test_app_latency_content_matches_archive(self):
        """Verify app-latency.json content matches the archive."""
        self._verify_file_content_matches("app-latency.json")

    def _verify_file_content_matches(self, filename):
        """Helper to verify extracted file content matches archive content."""
        extracted_path = os.path.join(DASHBOARDS_DIR, filename)
        archive_path = ARCHIVE_DASHBOARD_PATHS[filename]

        # Read extracted file
        with open(extracted_path, 'rb') as f:
            extracted_content = f.read()

        # Read from archive
        with tarfile.open(TARBALL_PATH, 'r:gz') as tar:
            member = tar.getmember(archive_path)
            f = tar.extractfile(member)
            archive_content = f.read()

        assert extracted_content == archive_content, (
            f"Content of {extracted_path} does not match the content in the archive. "
            f"Expected {len(archive_content)} bytes, got {len(extracted_content)} bytes."
        )

    def test_no_grafana_ini_extracted(self):
        """Verify grafana.ini was not extracted."""
        grafana_ini_path = os.path.join(DASHBOARDS_DIR, "grafana.ini")
        assert not os.path.exists(grafana_ini_path), (
            f"grafana.ini should not be extracted to {DASHBOARDS_DIR}. "
            "Only dashboard JSON files should be extracted."
        )

    def test_no_prometheus_files_extracted(self):
        """Verify no prometheus files were extracted."""
        for filename in ["prometheus.yml", "rules.yml"]:
            filepath = os.path.join(DASHBOARDS_DIR, filename)
            assert not os.path.exists(filepath), (
                f"{filename} should not be extracted to {DASHBOARDS_DIR}. "
                "Only dashboard JSON files should be extracted."
            )

    def test_no_alertmanager_files_extracted(self):
        """Verify no alertmanager files were extracted."""
        filepath = os.path.join(DASHBOARDS_DIR, "alertmanager.yml")
        assert not os.path.exists(filepath), (
            f"alertmanager.yml should not be extracted to {DASHBOARDS_DIR}. "
            "Only dashboard JSON files should be extracted."
        )

    def test_files_are_readable(self):
        """Verify all extracted files are readable."""
        for filename in EXPECTED_DASHBOARD_FILES:
            filepath = os.path.join(DASHBOARDS_DIR, filename)
            assert os.access(filepath, os.R_OK), (
                f"{filepath} is not readable"
            )

    def test_files_have_content(self):
        """Verify all extracted files have non-zero content."""
        for filename in EXPECTED_DASHBOARD_FILES:
            filepath = os.path.join(DASHBOARDS_DIR, filename)
            size = os.path.getsize(filepath)
            assert size > 0, (
                f"{filepath} is empty (0 bytes). "
                "The file should contain the dashboard JSON content."
            )
