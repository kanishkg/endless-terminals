# test_final_state.py
"""
Tests to validate the final state after the student has flattened all .perf files
from nested subdirectories into /home/user/captures directly.
"""

import os
import subprocess
import pytest


class TestFinalState:
    """Test that the final filesystem state is correct after the task."""

    BASE_DIR = "/home/user/captures"

    # Expected .perf files in their final flattened locations
    EXPECTED_FLATTENED_FILES = [
        "/home/user/captures/trace_001.perf",
        "/home/user/captures/trace_002.perf",
        "/home/user/captures/trace_003.perf",
        "/home/user/captures/trace_004.perf",
        "/home/user/captures/trace_005.perf",
        "/home/user/captures/trace_006.perf",
        "/home/user/captures/trace_007.perf",
        "/home/user/captures/trace_008.perf",
        "/home/user/captures/trace_009.perf",
        "/home/user/captures/trace_010.perf",
        "/home/user/captures/trace_011.perf",
        "/home/user/captures/trace_012.perf",
    ]

    def test_base_directory_exists(self):
        """Test that /home/user/captures directory still exists."""
        assert os.path.exists(self.BASE_DIR), (
            f"Base directory {self.BASE_DIR} does not exist. "
            "The captures directory must exist after the task."
        )
        assert os.path.isdir(self.BASE_DIR), (
            f"{self.BASE_DIR} exists but is not a directory."
        )

    @pytest.mark.parametrize("perf_file", EXPECTED_FLATTENED_FILES)
    def test_perf_file_exists_at_top_level(self, perf_file):
        """Test that each expected .perf file exists directly in /home/user/captures."""
        assert os.path.exists(perf_file), (
            f"Perf file {perf_file} does not exist at the top level. "
            "All 12 .perf files must be moved to /home/user/captures directly."
        )
        assert os.path.isfile(perf_file), (
            f"{perf_file} exists but is not a regular file."
        )

    @pytest.mark.parametrize("perf_file", EXPECTED_FLATTENED_FILES)
    def test_perf_file_is_non_empty(self, perf_file):
        """Test that each .perf file is non-empty (content preserved)."""
        if os.path.exists(perf_file):
            file_size = os.path.getsize(perf_file)
            assert file_size > 0, (
                f"Perf file {perf_file} is empty (0 bytes). "
                "Files must retain their original content after being moved."
            )
            # Check it's approximately 1KB (allow 100 bytes to 10KB range)
            assert 100 <= file_size <= 10240, (
                f"Perf file {perf_file} has unexpected size {file_size} bytes. "
                "Expected approximately 1KB - file content may have been corrupted."
            )

    def test_exactly_12_perf_files_at_top_level(self):
        """Test that there are exactly 12 .perf files directly in /home/user/captures."""
        top_level_perf_files = [
            f for f in os.listdir(self.BASE_DIR)
            if f.endswith('.perf') and os.path.isfile(os.path.join(self.BASE_DIR, f))
        ]

        assert len(top_level_perf_files) == 12, (
            f"Expected 12 .perf files at top level of {self.BASE_DIR}, "
            f"but found {len(top_level_perf_files)}: {sorted(top_level_perf_files)}. "
            "All 12 .perf files must be moved to the top level."
        )

    def test_no_perf_files_in_subdirectories(self):
        """Test that no .perf files remain in any subdirectories."""
        nested_perf_files = []
        for root, dirs, files in os.walk(self.BASE_DIR):
            # Skip the base directory itself
            if root == self.BASE_DIR:
                continue
            for f in files:
                if f.endswith('.perf'):
                    nested_perf_files.append(os.path.join(root, f))

        assert len(nested_perf_files) == 0, (
            f"Found {len(nested_perf_files)} .perf file(s) still in subdirectories: "
            f"{nested_perf_files}. All .perf files must be moved to the top level."
        )

    def test_find_maxdepth_1_returns_12(self):
        """Test that find command with maxdepth 1 returns 12 .perf files."""
        result = subprocess.run(
            ["find", self.BASE_DIR, "-maxdepth", "1", "-name", "*.perf"],
            capture_output=True,
            text=True
        )
        # Count non-empty lines
        found_files = [line for line in result.stdout.strip().split('\n') if line]
        count = len(found_files)

        assert count == 12, (
            f"'find {self.BASE_DIR} -maxdepth 1 -name *.perf' returned {count} files, "
            f"expected 12. Found: {found_files}"
        )

    def test_find_mindepth_2_returns_0(self):
        """Test that find command with mindepth 2 returns 0 .perf files."""
        result = subprocess.run(
            ["find", self.BASE_DIR, "-mindepth", "2", "-name", "*.perf"],
            capture_output=True,
            text=True
        )
        # Count non-empty lines
        found_files = [line for line in result.stdout.strip().split('\n') if line]
        count = len(found_files)

        assert count == 0, (
            f"'find {self.BASE_DIR} -mindepth 2 -name *.perf' returned {count} files, "
            f"expected 0. Files still in subdirs: {found_files}"
        )

    def test_total_perf_file_count_unchanged(self):
        """Test that total number of .perf files is still 12 (none deleted)."""
        perf_count = 0
        for root, dirs, files in os.walk(self.BASE_DIR):
            for f in files:
                if f.endswith('.perf'):
                    perf_count += 1

        assert perf_count == 12, (
            f"Expected 12 .perf files total in {self.BASE_DIR} tree, but found {perf_count}. "
            "Files may have been deleted or duplicated during the move operation."
        )

    def test_all_expected_filenames_present(self):
        """Test that all expected trace_NNN.perf filenames are present."""
        expected_names = {f"trace_{i:03d}.perf" for i in range(1, 13)}

        actual_names = set()
        for f in os.listdir(self.BASE_DIR):
            if f.endswith('.perf') and os.path.isfile(os.path.join(self.BASE_DIR, f)):
                actual_names.add(f)

        missing = expected_names - actual_names
        extra = actual_names - expected_names

        assert missing == set(), (
            f"Missing .perf files at top level: {sorted(missing)}. "
            "All trace_001.perf through trace_012.perf must be present."
        )

        if extra:
            # Extra files might be okay if they're the expected ones, just warn
            pass

    @pytest.mark.parametrize("perf_file", EXPECTED_FLATTENED_FILES)
    def test_perf_file_is_readable(self, perf_file):
        """Test that all .perf files are readable (not corrupted)."""
        if os.path.exists(perf_file):
            assert os.access(perf_file, os.R_OK), (
                f"Perf file {perf_file} is not readable. "
                "Files may have been corrupted during the move operation."
            )
            # Try to read the file to ensure it's not corrupted
            try:
                with open(perf_file, 'rb') as f:
                    content = f.read()
                assert len(content) > 0, (
                    f"Perf file {perf_file} has no content when read."
                )
            except Exception as e:
                pytest.fail(f"Failed to read {perf_file}: {e}")
