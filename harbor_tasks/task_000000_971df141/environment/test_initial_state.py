# test_initial_state.py
"""
Tests to validate the initial state before the student performs the action
of flattening .perf files from nested subdirectories into /home/user/captures.
"""

import os
import pytest


class TestInitialState:
    """Test that the initial filesystem state is correct before the task."""

    BASE_DIR = "/home/user/captures"

    # Expected .perf files in their initial nested locations
    EXPECTED_PERF_FILES = [
        "/home/user/captures/session1/trace_001.perf",
        "/home/user/captures/session1/trace_002.perf",
        "/home/user/captures/session1/trace_003.perf",
        "/home/user/captures/session2/trace_004.perf",
        "/home/user/captures/session2/tuesday/trace_005.perf",
        "/home/user/captures/session2/tuesday/trace_006.perf",
        "/home/user/captures/session2/wednesday/trace_007.perf",
        "/home/user/captures/old/trace_008.perf",
        "/home/user/captures/old/backup/trace_009.perf",
        "/home/user/captures/old/backup/trace_010.perf",
        "/home/user/captures/old/backup/deep/trace_011.perf",
        "/home/user/captures/misc/trace_012.perf",
    ]

    # Expected subdirectories
    EXPECTED_SUBDIRS = [
        "/home/user/captures/session1",
        "/home/user/captures/session2",
        "/home/user/captures/session2/tuesday",
        "/home/user/captures/session2/wednesday",
        "/home/user/captures/old",
        "/home/user/captures/old/backup",
        "/home/user/captures/old/backup/deep",
        "/home/user/captures/misc",
    ]

    def test_base_directory_exists(self):
        """Test that /home/user/captures directory exists."""
        assert os.path.exists(self.BASE_DIR), (
            f"Base directory {self.BASE_DIR} does not exist. "
            "The captures directory must exist before the task."
        )
        assert os.path.isdir(self.BASE_DIR), (
            f"{self.BASE_DIR} exists but is not a directory."
        )

    def test_base_directory_is_writable(self):
        """Test that /home/user/captures is writable by the user."""
        assert os.access(self.BASE_DIR, os.W_OK), (
            f"Base directory {self.BASE_DIR} is not writable. "
            "User must have write permissions to move files."
        )

    @pytest.mark.parametrize("subdir", EXPECTED_SUBDIRS)
    def test_subdirectory_exists(self, subdir):
        """Test that each expected subdirectory exists."""
        assert os.path.exists(subdir), (
            f"Subdirectory {subdir} does not exist. "
            "All nested subdirectories must be present in the initial state."
        )
        assert os.path.isdir(subdir), (
            f"{subdir} exists but is not a directory."
        )

    @pytest.mark.parametrize("subdir", EXPECTED_SUBDIRS)
    def test_subdirectory_is_writable(self, subdir):
        """Test that each subdirectory is writable."""
        assert os.access(subdir, os.W_OK), (
            f"Subdirectory {subdir} is not writable. "
            "User must have write permissions to move files from subdirectories."
        )

    @pytest.mark.parametrize("perf_file", EXPECTED_PERF_FILES)
    def test_perf_file_exists(self, perf_file):
        """Test that each expected .perf file exists in its initial location."""
        assert os.path.exists(perf_file), (
            f"Perf file {perf_file} does not exist. "
            "All 12 .perf files must be present in their nested locations."
        )
        assert os.path.isfile(perf_file), (
            f"{perf_file} exists but is not a regular file."
        )

    @pytest.mark.parametrize("perf_file", EXPECTED_PERF_FILES)
    def test_perf_file_is_non_empty(self, perf_file):
        """Test that each .perf file is non-empty (approximately 1KB)."""
        if os.path.exists(perf_file):
            file_size = os.path.getsize(perf_file)
            assert file_size > 0, (
                f"Perf file {perf_file} is empty (0 bytes). "
                "All .perf files should contain placeholder binary data (~1KB)."
            )
            # Check it's approximately 1KB (allow 100 bytes to 10KB range)
            assert 100 <= file_size <= 10240, (
                f"Perf file {perf_file} has unexpected size {file_size} bytes. "
                "Expected approximately 1KB of placeholder data."
            )

    def test_total_perf_file_count(self):
        """Test that there are exactly 12 .perf files in the directory tree."""
        perf_count = 0
        for root, dirs, files in os.walk(self.BASE_DIR):
            for f in files:
                if f.endswith('.perf'):
                    perf_count += 1

        assert perf_count == 12, (
            f"Expected 12 .perf files in {self.BASE_DIR} tree, but found {perf_count}. "
            "The initial state should have exactly 12 .perf files scattered across subdirectories."
        )

    def test_no_perf_files_at_top_level_initially(self):
        """Test that no .perf files are directly in /home/user/captures (all are nested)."""
        top_level_perf_files = [
            f for f in os.listdir(self.BASE_DIR)
            if f.endswith('.perf') and os.path.isfile(os.path.join(self.BASE_DIR, f))
        ]

        assert len(top_level_perf_files) == 0, (
            f"Found {len(top_level_perf_files)} .perf file(s) at top level of {self.BASE_DIR}: "
            f"{top_level_perf_files}. In the initial state, all .perf files should be in subdirectories."
        )

    def test_all_perf_files_are_in_subdirs(self):
        """Test that all .perf files are at depth >= 2 (in subdirectories)."""
        nested_perf_count = 0
        for root, dirs, files in os.walk(self.BASE_DIR):
            # Skip the base directory itself
            if root == self.BASE_DIR:
                continue
            for f in files:
                if f.endswith('.perf'):
                    nested_perf_count += 1

        assert nested_perf_count == 12, (
            f"Expected 12 .perf files in subdirectories, but found {nested_perf_count}. "
            "All .perf files should be nested within subdirectories initially."
        )

    def test_unique_perf_filenames(self):
        """Test that all .perf filenames are unique (no collisions)."""
        perf_filenames = []
        for root, dirs, files in os.walk(self.BASE_DIR):
            for f in files:
                if f.endswith('.perf'):
                    perf_filenames.append(f)

        unique_filenames = set(perf_filenames)
        assert len(perf_filenames) == len(unique_filenames), (
            f"Found duplicate .perf filenames. Total files: {len(perf_filenames)}, "
            f"Unique names: {len(unique_filenames)}. "
            "All trace_NNN.perf names should be unique to avoid collisions when flattening."
        )

    def test_perf_files_are_readable(self):
        """Test that all .perf files are readable."""
        for perf_file in self.EXPECTED_PERF_FILES:
            if os.path.exists(perf_file):
                assert os.access(perf_file, os.R_OK), (
                    f"Perf file {perf_file} is not readable. "
                    "User must have read permissions on all .perf files."
                )
