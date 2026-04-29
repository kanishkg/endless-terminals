# test_final_state.py
"""
Tests to validate the final state after the student has completed the three-way merge task.
The merged.txt file should correctly incorporate changes from both theirs and ours relative to base.
"""

import os
import pytest
import subprocess
import hashlib

WORKFLOW_DIR = "/home/user/workflow"
BASE_FILE = os.path.join(WORKFLOW_DIR, "base.txt")
THEIRS_FILE = os.path.join(WORKFLOW_DIR, "theirs.txt")
OURS_FILE = os.path.join(WORKFLOW_DIR, "ours.txt")
MERGED_FILE = os.path.join(WORKFLOW_DIR, "merged.txt")


def get_file_hash(filepath):
    """Get MD5 hash of a file for comparison."""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def read_file_normalized(filepath):
    """Read file content with normalized line endings (all LF)."""
    with open(filepath, 'rb') as f:
        content = f.read()
    # Normalize to LF
    return content.replace(b'\r\n', b'\n').replace(b'\r', b'\n').decode('utf-8', errors='replace')


def count_lines(filepath):
    """Count lines in a file, handling various line ending styles."""
    with open(filepath, 'rb') as f:
        content = f.read()
    # Normalize line endings and count
    normalized = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    lines = normalized.split(b'\n')
    # Remove empty trailing element if file ends with newline
    if lines and lines[-1] == b'':
        lines = lines[:-1]
    return len(lines)


class TestMergedFileExists:
    """Test that merged.txt exists and is accessible."""

    def test_merged_file_exists(self):
        assert os.path.exists(MERGED_FILE), (
            f"Merged file {MERGED_FILE} does not exist. "
            "You need to create the merged output file."
        )

    def test_merged_file_is_regular_file(self):
        assert os.path.isfile(MERGED_FILE), (
            f"{MERGED_FILE} exists but is not a regular file"
        )

    def test_merged_file_is_not_empty(self):
        assert os.path.getsize(MERGED_FILE) > 0, (
            f"{MERGED_FILE} exists but is empty"
        )


class TestInputFilesUnchanged:
    """Test that original input files were not modified."""

    def test_base_file_still_exists(self):
        assert os.path.exists(BASE_FILE), (
            f"base.txt was deleted or moved - it should remain unchanged"
        )

    def test_theirs_file_still_exists(self):
        assert os.path.exists(THEIRS_FILE), (
            f"theirs.txt was deleted or moved - it should remain unchanged"
        )

    def test_ours_file_still_exists(self):
        assert os.path.exists(OURS_FILE), (
            f"ours.txt was deleted or moved - it should remain unchanged"
        )

    def test_base_file_still_has_mixed_line_endings(self):
        """base.txt should still have mixed line endings (unchanged)."""
        with open(BASE_FILE, 'rb') as f:
            content = f.read()
        has_crlf = b'\r\n' in content
        assert has_crlf, (
            "base.txt was modified - it should still have CRLF line endings in some parts"
        )

    def test_theirs_file_still_normalized(self):
        """theirs.txt should still have only LF line endings."""
        with open(THEIRS_FILE, 'rb') as f:
            content = f.read()
        assert b'\r' not in content, (
            "theirs.txt was modified - it should still have only LF line endings"
        )

    def test_ours_file_still_has_crlf(self):
        """ours.txt should still have CRLF line endings."""
        with open(OURS_FILE, 'rb') as f:
            content = f.read()
        has_crlf = b'\r\n' in content
        assert has_crlf, (
            "ours.txt was modified - it should still have CRLF line endings"
        )


class TestMergedFileLineEndings:
    """Test that merged.txt has consistent line endings."""

    def test_merged_file_has_consistent_line_endings(self):
        """merged.txt should have consistent line endings (no mixed)."""
        with open(MERGED_FILE, 'rb') as f:
            content = f.read()

        has_crlf = b'\r\n' in content
        # Check for LF not preceded by CR
        has_lf_only = False
        i = 0
        while i < len(content):
            if content[i:i+1] == b'\n' and (i == 0 or content[i-1:i] != b'\r'):
                has_lf_only = True
                break
            i += 1

        # Either all CRLF or all LF, not mixed
        if has_crlf and has_lf_only:
            pytest.fail(
                "merged.txt has mixed line endings (both CRLF and LF-only). "
                "The output should have consistent line endings."
            )

    def test_merged_file_no_stray_cr(self):
        """Check for CR characters not part of CRLF (corruption indicator)."""
        with open(MERGED_FILE, 'rb') as f:
            content = f.read()

        # Find CR not followed by LF
        i = 0
        while i < len(content):
            if content[i:i+1] == b'\r':
                if i + 1 >= len(content) or content[i+1:i+2] != b'\n':
                    pytest.fail(
                        "merged.txt contains CR characters not part of CRLF sequences, "
                        "indicating possible corruption"
                    )
            i += 1


class TestMergedFileLineCount:
    """Test that merged.txt has the correct number of lines."""

    def test_merged_file_has_81_lines(self):
        """
        Expected: base (80) + theirs features (+2) - ours auth deletion (-1) = 81 lines
        """
        line_count = count_lines(MERGED_FILE)
        assert line_count == 81, (
            f"merged.txt should have exactly 81 lines "
            f"(base 80 + 2 feature additions - 1 auth deletion), "
            f"but has {line_count} lines. "
            "This suggests edits were lost or duplicated."
        )


class TestMergedFileHasAllSections:
    """Test that merged.txt contains all required sections."""

    def test_merged_has_database_section(self):
        content = read_file_normalized(MERGED_FILE)
        assert '[database]' in content, (
            "merged.txt is missing [database] section"
        )

    def test_merged_has_cache_section(self):
        content = read_file_normalized(MERGED_FILE)
        assert '[cache]' in content, (
            "merged.txt is missing [cache] section"
        )

    def test_merged_has_logging_section(self):
        content = read_file_normalized(MERGED_FILE)
        assert '[logging]' in content, (
            "merged.txt is missing [logging] section"
        )

    def test_merged_has_auth_section(self):
        content = read_file_normalized(MERGED_FILE)
        assert '[auth]' in content, (
            "merged.txt is missing [auth] section"
        )

    def test_merged_has_features_section(self):
        content = read_file_normalized(MERGED_FILE)
        assert '[features]' in content, (
            "merged.txt is missing [features] section"
        )


class TestTheirsChangesIncluded:
    """Test that changes from theirs branch are included in merged.txt."""

    def test_cache_ttl_from_theirs(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'cache_ttl=3600' in content, (
            "merged.txt is missing 'cache_ttl=3600' from theirs branch. "
            "The [cache] section changes from theirs were not merged correctly."
        )

    def test_cache_backend_from_theirs(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'cache_backend=redis' in content, (
            "merged.txt is missing 'cache_backend=redis' from theirs branch. "
            "The [cache] section changes from theirs were not merged correctly."
        )

    def test_cache_prefix_from_theirs(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'cache_prefix=v2_' in content, (
            "merged.txt is missing 'cache_prefix=v2_' from theirs branch. "
            "The [cache] section changes from theirs were not merged correctly."
        )

    def test_feature_dark_mode_from_theirs(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'feature_dark_mode=true' in content, (
            "merged.txt is missing 'feature_dark_mode=true' from theirs branch. "
            "The [features] section additions from theirs were not merged correctly."
        )

    def test_feature_export_from_theirs(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'feature_export=csv,json' in content, (
            "merged.txt is missing 'feature_export=csv,json' from theirs branch. "
            "The [features] section additions from theirs were not merged correctly."
        )


class TestOursChangesIncluded:
    """Test that changes from ours branch are included in merged.txt."""

    def test_log_level_from_ours(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'log_level=debug' in content, (
            "merged.txt is missing 'log_level=debug' from ours branch. "
            "The [logging] section changes from ours were not merged correctly."
        )

    def test_log_rotate_from_ours(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'log_rotate=weekly' in content, (
            "merged.txt is missing 'log_rotate=weekly' from ours branch. "
            "The [logging] section changes from ours were not merged correctly."
        )

    def test_auth_timeout_deleted_from_ours(self):
        content = read_file_normalized(MERGED_FILE)
        assert 'auth_timeout=' not in content, (
            "merged.txt still contains 'auth_timeout=' which should have been deleted "
            "according to ours branch. The [auth] section deletion was not merged correctly."
        )


class TestNoConflictMarkers:
    """Test that merged.txt has no unresolved conflict markers."""

    def test_no_conflict_start_marker(self):
        content = read_file_normalized(MERGED_FILE)
        assert '<<<<<<<' not in content, (
            "merged.txt contains unresolved conflict markers (<<<<<<<). "
            "The merge should be clean with no conflicts."
        )

    def test_no_conflict_separator_marker(self):
        content = read_file_normalized(MERGED_FILE)
        assert '=======' not in content, (
            "merged.txt contains unresolved conflict markers (=======). "
            "The merge should be clean with no conflicts."
        )

    def test_no_conflict_end_marker(self):
        content = read_file_normalized(MERGED_FILE)
        assert '>>>>>>>' not in content, (
            "merged.txt contains unresolved conflict markers (>>>>>>>). "
            "The merge should be clean with no conflicts."
        )


class TestNoDuplicatedContent:
    """Test that content is not duplicated in merged.txt."""

    def test_single_database_section(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('[database]')
        assert count == 1, (
            f"merged.txt contains [database] section {count} times. "
            "Each section should appear exactly once."
        )

    def test_single_cache_section(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('[cache]')
        assert count == 1, (
            f"merged.txt contains [cache] section {count} times. "
            "Each section should appear exactly once."
        )

    def test_single_logging_section(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('[logging]')
        assert count == 1, (
            f"merged.txt contains [logging] section {count} times. "
            "Each section should appear exactly once."
        )

    def test_single_auth_section(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('[auth]')
        assert count == 1, (
            f"merged.txt contains [auth] section {count} times. "
            "Each section should appear exactly once."
        )

    def test_single_features_section(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('[features]')
        assert count == 1, (
            f"merged.txt contains [features] section {count} times. "
            "Each section should appear exactly once."
        )

    def test_single_cache_ttl(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('cache_ttl=')
        assert count == 1, (
            f"merged.txt contains 'cache_ttl=' {count} times. "
            "This key should appear exactly once."
        )

    def test_single_log_level(self):
        content = read_file_normalized(MERGED_FILE)
        count = content.count('log_level=')
        assert count == 1, (
            f"merged.txt contains 'log_level=' {count} times. "
            "This key should appear exactly once."
        )


class TestMergedFileStructure:
    """Test the overall structure of merged.txt."""

    def test_sections_in_correct_order(self):
        """Sections should appear in the same order as in base.txt."""
        content = read_file_normalized(MERGED_FILE)

        db_pos = content.find('[database]')
        cache_pos = content.find('[cache]')
        log_pos = content.find('[logging]')
        auth_pos = content.find('[auth]')
        feat_pos = content.find('[features]')

        assert db_pos < cache_pos < log_pos < auth_pos < feat_pos, (
            "Sections in merged.txt are not in the expected order: "
            "[database], [cache], [logging], [auth], [features]. "
            "The merge may have corrupted the file structure."
        )

    def test_no_empty_lines_between_key_value_pairs(self):
        """
        Check that there are no unexpected large gaps of empty lines
        which might indicate corruption.
        """
        content = read_file_normalized(MERGED_FILE)
        # Check for 3+ consecutive newlines (indicating 2+ blank lines in a row)
        if '\n\n\n' in content:
            pytest.fail(
                "merged.txt contains multiple consecutive blank lines, "
                "which may indicate merge corruption or missing content."
            )


class TestSemanticMergeCorrectness:
    """Additional semantic checks to ensure proper merge."""

    def test_base_values_not_overwritten_incorrectly(self):
        """
        Ensure values that should come from base (unchanged in both branches)
        are present.
        """
        content = read_file_normalized(MERGED_FILE)
        # The database section should be unchanged from base
        # We check that it exists and has reasonable content
        assert '[database]' in content, "Database section missing"

    def test_theirs_cache_values_override_base(self):
        """
        theirs changed cache values, so merged should have theirs' values,
        not base's values.
        """
        content = read_file_normalized(MERGED_FILE)
        # These are the NEW values from theirs
        assert 'cache_ttl=3600' in content
        assert 'cache_backend=redis' in content
        assert 'cache_prefix=v2_' in content

    def test_ours_logging_values_override_base(self):
        """
        ours changed logging values, so merged should have ours' values,
        not base's values.
        """
        content = read_file_normalized(MERGED_FILE)
        assert 'log_level=debug' in content
        assert 'log_rotate=weekly' in content
