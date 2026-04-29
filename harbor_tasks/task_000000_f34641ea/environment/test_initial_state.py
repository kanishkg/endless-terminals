# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
performs the three-way merge task.
"""

import os
import pytest
import subprocess

WORKFLOW_DIR = "/home/user/workflow"
BASE_FILE = os.path.join(WORKFLOW_DIR, "base.txt")
THEIRS_FILE = os.path.join(WORKFLOW_DIR, "theirs.txt")
OURS_FILE = os.path.join(WORKFLOW_DIR, "ours.txt")

# Output file - should NOT exist initially
MERGED_FILE = os.path.join(WORKFLOW_DIR, "merged.txt")


class TestWorkflowDirectoryExists:
    """Test that the workflow directory exists and is accessible."""

    def test_workflow_directory_exists(self):
        assert os.path.exists(WORKFLOW_DIR), (
            f"Workflow directory {WORKFLOW_DIR} does not exist"
        )

    def test_workflow_directory_is_directory(self):
        assert os.path.isdir(WORKFLOW_DIR), (
            f"{WORKFLOW_DIR} exists but is not a directory"
        )

    def test_workflow_directory_is_writable(self):
        assert os.access(WORKFLOW_DIR, os.W_OK), (
            f"{WORKFLOW_DIR} is not writable"
        )


class TestInputFilesExist:
    """Test that all required input files exist."""

    def test_base_file_exists(self):
        assert os.path.exists(BASE_FILE), (
            f"Base file {BASE_FILE} does not exist"
        )

    def test_theirs_file_exists(self):
        assert os.path.exists(THEIRS_FILE), (
            f"Theirs file {THEIRS_FILE} does not exist"
        )

    def test_ours_file_exists(self):
        assert os.path.exists(OURS_FILE), (
            f"Ours file {OURS_FILE} does not exist"
        )

    def test_base_file_is_regular_file(self):
        assert os.path.isfile(BASE_FILE), (
            f"{BASE_FILE} exists but is not a regular file"
        )

    def test_theirs_file_is_regular_file(self):
        assert os.path.isfile(THEIRS_FILE), (
            f"{THEIRS_FILE} exists but is not a regular file"
        )

    def test_ours_file_is_regular_file(self):
        assert os.path.isfile(OURS_FILE), (
            f"{OURS_FILE} exists but is not a regular file"
        )


class TestBaseFileContent:
    """Test that base.txt has the expected structure and line ending trap."""

    def test_base_file_has_80_lines(self):
        with open(BASE_FILE, 'rb') as f:
            content = f.read()
        # Count lines by splitting on \n (handles both LF and CRLF)
        lines = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n').split(b'\n')
        # Remove empty trailing element if file ends with newline
        if lines and lines[-1] == b'':
            lines = lines[:-1]
        assert len(lines) == 80, (
            f"base.txt should have 80 lines, but has {len(lines)} lines"
        )

    def test_base_file_has_required_sections(self):
        with open(BASE_FILE, 'r', errors='replace') as f:
            content = f.read()
        required_sections = ['[database]', '[cache]', '[logging]', '[auth]', '[features]']
        for section in required_sections:
            assert section in content, (
                f"base.txt is missing required section: {section}"
            )

    def test_base_file_has_mixed_line_endings(self):
        """The trap: base.txt should have mixed LF and CRLF line endings."""
        with open(BASE_FILE, 'rb') as f:
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

        assert has_crlf, (
            "base.txt should have CRLF line endings in some parts (the trap)"
        )
        assert has_lf_only, (
            "base.txt should have LF-only line endings in some parts (the trap)"
        )


class TestTheirsFileContent:
    """Test that theirs.txt has expected properties."""

    def test_theirs_file_has_normalized_line_endings(self):
        """theirs.txt should have all LF line endings (normalized)."""
        with open(THEIRS_FILE, 'rb') as f:
            content = f.read()

        assert b'\r' not in content, (
            "theirs.txt should have normalized LF line endings (no CR bytes), "
            "but contains CR characters"
        )

    def test_theirs_file_has_required_sections(self):
        with open(THEIRS_FILE, 'r') as f:
            content = f.read()
        required_sections = ['[database]', '[cache]', '[logging]', '[auth]', '[features]']
        for section in required_sections:
            assert section in content, (
                f"theirs.txt is missing required section: {section}"
            )

    def test_theirs_file_has_cache_changes(self):
        """theirs.txt should have the specific cache changes."""
        with open(THEIRS_FILE, 'r') as f:
            content = f.read()

        expected_values = ['cache_ttl=3600', 'cache_backend=redis', 'cache_prefix=v2_']
        for value in expected_values:
            assert value in content, (
                f"theirs.txt should contain '{value}' (cache change from theirs branch)"
            )

    def test_theirs_file_has_feature_additions(self):
        """theirs.txt should have the new feature keys."""
        with open(THEIRS_FILE, 'r') as f:
            content = f.read()

        expected_values = ['feature_dark_mode=true', 'feature_export=csv,json']
        for value in expected_values:
            assert value in content, (
                f"theirs.txt should contain '{value}' (feature addition from theirs branch)"
            )


class TestOursFileContent:
    """Test that ours.txt has expected properties."""

    def test_ours_file_has_mixed_line_endings(self):
        """ours.txt should preserve the mixed line endings from base."""
        with open(OURS_FILE, 'rb') as f:
            content = f.read()

        has_crlf = b'\r\n' in content
        assert has_crlf, (
            "ours.txt should preserve CRLF line endings from base.txt (part of the trap)"
        )

    def test_ours_file_has_required_sections(self):
        with open(OURS_FILE, 'r', errors='replace') as f:
            content = f.read()
        required_sections = ['[database]', '[cache]', '[logging]', '[auth]', '[features]']
        for section in required_sections:
            assert section in content, (
                f"ours.txt is missing required section: {section}"
            )

    def test_ours_file_has_logging_changes(self):
        """ours.txt should have the specific logging changes."""
        with open(OURS_FILE, 'r', errors='replace') as f:
            content = f.read()

        expected_values = ['log_level=debug', 'log_rotate=weekly']
        for value in expected_values:
            assert value in content, (
                f"ours.txt should contain '{value}' (logging change from ours branch)"
            )

    def test_ours_file_does_not_have_auth_timeout(self):
        """ours.txt should have auth_timeout deleted."""
        with open(OURS_FILE, 'r', errors='replace') as f:
            content = f.read()

        assert 'auth_timeout=' not in content, (
            "ours.txt should NOT contain 'auth_timeout=' (it was deleted in ours branch)"
        )


class TestRequiredToolsAvailable:
    """Test that required tools are available."""

    def test_diff_available(self):
        result = subprocess.run(['which', 'diff'], capture_output=True)
        assert result.returncode == 0, "diff command is not available"

    def test_patch_available(self):
        result = subprocess.run(['which', 'patch'], capture_output=True)
        assert result.returncode == 0, "patch command is not available"

    def test_diff3_available(self):
        result = subprocess.run(['which', 'diff3'], capture_output=True)
        assert result.returncode == 0, "diff3 command is not available"

    def test_merge_available(self):
        result = subprocess.run(['which', 'merge'], capture_output=True)
        # merge might not be available on all systems, but let's check
        # This is optional based on the task description
        pass  # Not strictly required

    def test_dos2unix_available(self):
        result = subprocess.run(['which', 'dos2unix'], capture_output=True)
        assert result.returncode == 0, "dos2unix command is not available"

    def test_python3_available(self):
        result = subprocess.run(['which', 'python3'], capture_output=True)
        assert result.returncode == 0, "python3 is not available"


class TestOutputFileDoesNotExist:
    """Test that the output file does not exist yet."""

    def test_merged_file_does_not_exist(self):
        assert not os.path.exists(MERGED_FILE), (
            f"Output file {MERGED_FILE} already exists - it should be created by the student"
        )


class TestBaseFileHasAuthTimeout:
    """Verify base.txt has auth_timeout that ours.txt deleted."""

    def test_base_has_auth_timeout(self):
        with open(BASE_FILE, 'r', errors='replace') as f:
            content = f.read()

        assert 'auth_timeout=' in content, (
            "base.txt should contain 'auth_timeout=' which gets deleted in ours branch"
        )
