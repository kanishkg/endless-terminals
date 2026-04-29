# test_final_state.py
"""
Post-task validation tests to verify the final state after the student
has completed the disk space analysis task.
"""

import os
import re
import pytest


class TestOutputFileExists:
    """Verify the output file exists and is valid."""

    def test_big_files_txt_exists(self):
        """Check that /home/user/big_files.txt exists."""
        assert os.path.exists("/home/user/big_files.txt"), \
            "/home/user/big_files.txt does not exist - task not completed"

    def test_big_files_txt_is_file(self):
        """Check that /home/user/big_files.txt is a regular file."""
        assert os.path.isfile("/home/user/big_files.txt"), \
            "/home/user/big_files.txt is not a regular file"

    def test_big_files_txt_is_readable(self):
        """Check that /home/user/big_files.txt is readable."""
        assert os.access("/home/user/big_files.txt", os.R_OK), \
            "/home/user/big_files.txt is not readable"

    def test_big_files_txt_not_empty(self):
        """Check that /home/user/big_files.txt is not empty."""
        size = os.path.getsize("/home/user/big_files.txt")
        assert size > 0, "/home/user/big_files.txt is empty"


class TestOutputFileContent:
    """Verify the output file contains all required large files."""

    EXPECTED_FILES = [
        "/var/data/logs/app.log.2024-01-15",
        "/var/data/logs/debug.log",
        "/var/data/cache/thumbnails.db",
        "/var/data/uploads/video_backup.tar",
        "/var/data/tmp/core.1847",
    ]

    def _read_output_file(self):
        """Helper to read the output file content."""
        with open("/home/user/big_files.txt", "r") as f:
            return f.read()

    def _get_output_lines(self):
        """Helper to get non-empty lines from output file."""
        content = self._read_output_file()
        return [line.strip() for line in content.splitlines() if line.strip()]

    def test_minimum_line_count(self):
        """Check that output file has at least 5 lines (one per large file)."""
        lines = self._get_output_lines()
        assert len(lines) >= 5, \
            f"Expected at least 5 lines in output, found {len(lines)}. " \
            f"All 5 files over 100MB must be listed."

    def test_contains_app_log(self):
        """Check that app.log.2024-01-15 is listed in output."""
        content = self._read_output_file()
        filepath = "/var/data/logs/app.log.2024-01-15"
        assert filepath in content, \
            f"Missing {filepath} from output - this 247MB file should be listed"

    def test_contains_debug_log(self):
        """Check that debug.log is listed in output."""
        content = self._read_output_file()
        filepath = "/var/data/logs/debug.log"
        assert filepath in content, \
            f"Missing {filepath} from output - this 189MB file should be listed"

    def test_contains_thumbnails_db(self):
        """Check that thumbnails.db is listed in output."""
        content = self._read_output_file()
        filepath = "/var/data/cache/thumbnails.db"
        assert filepath in content, \
            f"Missing {filepath} from output - this 312MB file should be listed"

    def test_contains_video_backup(self):
        """Check that video_backup.tar is listed in output."""
        content = self._read_output_file()
        filepath = "/var/data/uploads/video_backup.tar"
        assert filepath in content, \
            f"Missing {filepath} from output - this 524MB file should be listed"

    def test_contains_core_dump(self):
        """Check that core.1847 is listed in output."""
        content = self._read_output_file()
        filepath = "/var/data/tmp/core.1847"
        assert filepath in content, \
            f"Missing {filepath} from output - this 156MB file should be listed"

    def test_all_five_files_present(self):
        """Verify all 5 expected large files are in the output."""
        content = self._read_output_file()
        missing = []
        for filepath in self.EXPECTED_FILES:
            if filepath not in content:
                missing.append(filepath)
        assert not missing, \
            f"Missing files from output: {missing}"


class TestOutputSorting:
    """Verify the output is sorted by size, largest first."""

    # Expected order by size (largest first):
    # 1. video_backup.tar (524MB)
    # 2. thumbnails.db (312MB)
    # 3. app.log.2024-01-15 (247MB)
    # 4. debug.log (189MB)
    # 5. core.1847 (156MB)

    EXPECTED_ORDER = [
        ("video_backup.tar", 524),
        ("thumbnails.db", 312),
        ("app.log.2024-01-15", 247),
        ("debug.log", 189),
        ("core.1847", 156),
    ]

    def _get_output_lines(self):
        """Helper to get non-empty lines from output file."""
        with open("/home/user/big_files.txt", "r") as f:
            content = f.read()
        return [line.strip() for line in content.splitlines() if line.strip()]

    def _find_file_position(self, lines, filename):
        """Find the line index containing a specific filename."""
        for i, line in enumerate(lines):
            if filename in line:
                return i
        return -1

    def test_video_backup_is_first(self):
        """Check that video_backup.tar (524MB, largest) appears first."""
        lines = self._get_output_lines()
        pos = self._find_file_position(lines, "video_backup.tar")
        assert pos == 0, \
            f"video_backup.tar (524MB) should be first (position 0), found at position {pos}. " \
            f"Output should be sorted largest first."

    def test_correct_descending_order(self):
        """Check that files are in descending size order."""
        lines = self._get_output_lines()
        positions = []
        for filename, size in self.EXPECTED_ORDER:
            pos = self._find_file_position(lines, filename)
            if pos >= 0:
                positions.append((filename, size, pos))

        # Check that positions are in ascending order (0, 1, 2, 3, 4)
        for i in range(len(positions) - 1):
            curr_file, curr_size, curr_pos = positions[i]
            next_file, next_size, next_pos = positions[i + 1]
            assert curr_pos < next_pos, \
                f"Sort order wrong: {curr_file} ({curr_size}MB) at position {curr_pos} " \
                f"should come before {next_file} ({next_size}MB) at position {next_pos}. " \
                f"Files should be sorted largest first."

    def test_core_dump_is_last(self):
        """Check that core.1847 (156MB, smallest of the large files) appears last among the 5."""
        lines = self._get_output_lines()
        positions = {}
        for filename, _ in self.EXPECTED_ORDER:
            pos = self._find_file_position(lines, filename)
            if pos >= 0:
                positions[filename] = pos

        if "core.1847" in positions:
            core_pos = positions["core.1847"]
            for filename, pos in positions.items():
                if filename != "core.1847":
                    assert pos < core_pos, \
                        f"core.1847 (156MB) should be last among large files, " \
                        f"but {filename} appears after it"


class TestOutputFormat:
    """Verify each line includes size information."""

    def _get_output_lines(self):
        """Helper to get non-empty lines from output file."""
        with open("/home/user/big_files.txt", "r") as f:
            content = f.read()
        return [line.strip() for line in content.splitlines() if line.strip()]

    def test_lines_contain_size_info(self):
        """Check that lines contain some form of size information."""
        lines = self._get_output_lines()
        # At least the first 5 lines should have size info
        # Size can be in various formats: bytes, KB, MB, GB, or human-readable
        # Look for numbers that could represent sizes
        size_pattern = re.compile(r'\d+')

        for i, line in enumerate(lines[:5]):
            match = size_pattern.search(line)
            assert match is not None, \
                f"Line {i+1} does not appear to contain size information: '{line}'"


class TestVarDataIntegrity:
    """Verify /var/data files were not modified or deleted."""

    EXPECTED_FILES = {
        "/var/data/logs/app.log.2024-01-15": (240 * 1024 * 1024, 255 * 1024 * 1024),
        "/var/data/logs/debug.log": (180 * 1024 * 1024, 200 * 1024 * 1024),
        "/var/data/cache/thumbnails.db": (305 * 1024 * 1024, 320 * 1024 * 1024),
        "/var/data/uploads/video_backup.tar": (515 * 1024 * 1024, 535 * 1024 * 1024),
        "/var/data/tmp/core.1847": (150 * 1024 * 1024, 165 * 1024 * 1024),
    }

    def test_var_data_exists(self):
        """Check that /var/data still exists."""
        assert os.path.isdir("/var/data"), \
            "/var/data directory was deleted or modified"

    def test_all_large_files_still_exist(self):
        """Check that all original large files still exist."""
        for filepath in self.EXPECTED_FILES:
            assert os.path.isfile(filepath), \
                f"{filepath} was deleted - files should not be modified"

    def test_file_sizes_unchanged(self):
        """Check that file sizes haven't changed."""
        for filepath, (min_size, max_size) in self.EXPECTED_FILES.items():
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                assert min_size <= size <= max_size, \
                    f"{filepath} size changed - files should not be modified"

    def test_exactly_five_large_files_remain(self):
        """Verify there are still exactly 5 files over 100MB in /var/data."""
        threshold = 100 * 1024 * 1024
        large_files = []
        for root, dirs, files in os.walk("/var/data"):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    if os.path.getsize(filepath) >= threshold:
                        large_files.append(filepath)
                except OSError:
                    pass
        assert len(large_files) == 5, \
            f"Expected 5 files over 100MB, found {len(large_files)}. " \
            f"Files should not have been deleted or modified."
