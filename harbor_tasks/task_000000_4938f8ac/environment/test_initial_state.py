# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the patch reconstruction task.
"""

import os
import subprocess
import pytest

AUDIT_DIR = "/home/user/audit"
BASELINE_LOG = os.path.join(AUDIT_DIR, "baseline.log")
CHANGES_PATCH = os.path.join(AUDIT_DIR, "changes.patch")
REFERENCE_FRAGMENT = os.path.join(AUDIT_DIR, "reference_fragment.txt")


class TestDirectoryStructure:
    """Test that required directories exist and are accessible."""

    def test_audit_directory_exists(self):
        """The /home/user/audit directory must exist."""
        assert os.path.isdir(AUDIT_DIR), f"Directory {AUDIT_DIR} does not exist"

    def test_audit_directory_writable(self):
        """The /home/user/audit directory must be writable."""
        assert os.access(AUDIT_DIR, os.W_OK), f"Directory {AUDIT_DIR} is not writable"


class TestBaselineLog:
    """Test that baseline.log exists with expected properties."""

    def test_baseline_log_exists(self):
        """baseline.log must exist."""
        assert os.path.isfile(BASELINE_LOG), f"File {BASELINE_LOG} does not exist"

    def test_baseline_log_readable(self):
        """baseline.log must be readable."""
        assert os.access(BASELINE_LOG, os.R_OK), f"File {BASELINE_LOG} is not readable"

    def test_baseline_log_has_1200_lines(self):
        """baseline.log must have exactly 1200 lines."""
        with open(BASELINE_LOG, 'r') as f:
            line_count = sum(1 for _ in f)
        assert line_count == 1200, f"baseline.log has {line_count} lines, expected 1200"

    def test_baseline_log_format(self):
        """baseline.log entries should follow the expected timestamp format."""
        import re
        pattern = re.compile(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[\w+\] \[\w+\]')

        with open(BASELINE_LOG, 'r') as f:
            # Check first 10 lines to verify format
            for i, line in enumerate(f):
                if i >= 10:
                    break
                assert pattern.match(line), (
                    f"Line {i+1} of baseline.log does not match expected format "
                    f"'[YYYY-MM-DD HH:MM:SS] [LEVEL] [component] message'. "
                    f"Got: {line[:60]}..."
                )


class TestChangesPatch:
    """Test that changes.patch exists with expected corruption characteristics."""

    def test_changes_patch_exists(self):
        """changes.patch must exist."""
        assert os.path.isfile(CHANGES_PATCH), f"File {CHANGES_PATCH} does not exist"

    def test_changes_patch_readable(self):
        """changes.patch must be readable."""
        assert os.access(CHANGES_PATCH, os.R_OK), f"File {CHANGES_PATCH} is not readable"

    def test_changes_patch_is_unified_diff(self):
        """changes.patch must be a unified diff format (starts with ---)."""
        with open(CHANGES_PATCH, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('---'), (
            f"changes.patch does not appear to be a unified diff. "
            f"First line should start with '---', got: {first_line[:40]}"
        )

    def test_changes_patch_has_hunks(self):
        """changes.patch must contain hunk headers (@@)."""
        with open(CHANGES_PATCH, 'r') as f:
            content = f.read()
        hunk_count = content.count('\n@@')
        # Account for @@ at start of line
        import re
        hunk_headers = re.findall(r'^@@', content, re.MULTILINE)
        assert len(hunk_headers) >= 6, (
            f"changes.patch should have at least 6 hunks, found {len(hunk_headers)}"
        )

    def test_changes_patch_fails_to_apply(self):
        """changes.patch must fail to apply cleanly (it's corrupted)."""
        result = subprocess.run(
            ['patch', '--dry-run', BASELINE_LOG],
            stdin=open(CHANGES_PATCH, 'r'),
            capture_output=True,
            text=True,
            cwd=AUDIT_DIR
        )
        # The patch should fail (non-zero exit or "FAILED" in output)
        patch_failed = (result.returncode != 0) or ('FAILED' in result.stdout) or ('FAILED' in result.stderr)
        assert patch_failed, (
            "changes.patch should be corrupted and fail to apply, but it applied successfully. "
            "This test expects the patch to be corrupted."
        )


class TestReferenceFragment:
    """Test that reference_fragment.txt exists with expected properties."""

    def test_reference_fragment_exists(self):
        """reference_fragment.txt must exist."""
        assert os.path.isfile(REFERENCE_FRAGMENT), f"File {REFERENCE_FRAGMENT} does not exist"

    def test_reference_fragment_readable(self):
        """reference_fragment.txt must be readable."""
        assert os.access(REFERENCE_FRAGMENT, os.R_OK), f"File {REFERENCE_FRAGMENT} is not readable"

    def test_reference_fragment_has_55_lines(self):
        """reference_fragment.txt must have exactly 55 lines (lines 847-901)."""
        with open(REFERENCE_FRAGMENT, 'r') as f:
            line_count = sum(1 for _ in f)
        assert line_count == 55, (
            f"reference_fragment.txt has {line_count} lines, expected 55 (lines 847-901)"
        )

    def test_reference_fragment_format(self):
        """reference_fragment.txt entries should follow the expected timestamp format."""
        import re
        pattern = re.compile(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[\w+\] \[\w+\]')

        with open(REFERENCE_FRAGMENT, 'r') as f:
            # Check first few lines to verify format
            for i, line in enumerate(f):
                if i >= 5:
                    break
                assert pattern.match(line), (
                    f"Line {i+1} of reference_fragment.txt does not match expected format "
                    f"'[YYYY-MM-DD HH:MM:SS] [LEVEL] [component] message'. "
                    f"Got: {line[:60]}..."
                )


class TestRequiredUtilities:
    """Test that required utilities are available."""

    def test_patch_utility_available(self):
        """GNU patch utility must be available."""
        result = subprocess.run(['which', 'patch'], capture_output=True, text=True)
        assert result.returncode == 0, "patch utility is not available in PATH"

    def test_patch_version(self):
        """patch utility should be GNU patch."""
        result = subprocess.run(['patch', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "Failed to get patch version"
        assert 'GNU patch' in result.stdout, (
            f"Expected GNU patch, got: {result.stdout.split(chr(10))[0]}"
        )

    def test_diff_utility_available(self):
        """diff utility must be available."""
        result = subprocess.run(['which', 'diff'], capture_output=True, text=True)
        assert result.returncode == 0, "diff utility is not available in PATH"

    def test_python3_available(self):
        """Python 3 must be available."""
        result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
        assert result.returncode == 0, "Python 3 is not available"
        # Check it's Python 3.11 or compatible
        version_str = result.stdout.strip()
        assert 'Python 3' in version_str, f"Expected Python 3, got: {version_str}"


class TestNoOutputFilesExist:
    """Verify that expected output files do not exist yet."""

    def test_fixed_patch_does_not_exist(self):
        """fixed.patch should not exist before the task is performed."""
        fixed_patch = os.path.join(AUDIT_DIR, "fixed.patch")
        # Note: This test verifies initial state. If fixed.patch exists,
        # it might be from a previous attempt and should be cleaned up.
        # We don't fail here but warn, as the task might allow overwriting.
        if os.path.exists(fixed_patch):
            pytest.skip(
                f"Warning: {fixed_patch} already exists. "
                "This may be from a previous attempt."
            )

    def test_test_log_does_not_exist(self):
        """test.log should not exist before the task is performed."""
        test_log = os.path.join(AUDIT_DIR, "test.log")
        if os.path.exists(test_log):
            pytest.skip(
                f"Warning: {test_log} already exists. "
                "This may be from a previous attempt."
            )
