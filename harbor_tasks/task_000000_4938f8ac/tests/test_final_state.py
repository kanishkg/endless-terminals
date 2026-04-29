# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the patch reconstruction task.
"""

import os
import subprocess
import pytest
import tempfile
import shutil

AUDIT_DIR = "/home/user/audit"
BASELINE_LOG = os.path.join(AUDIT_DIR, "baseline.log")
CHANGES_PATCH = os.path.join(AUDIT_DIR, "changes.patch")
REFERENCE_FRAGMENT = os.path.join(AUDIT_DIR, "reference_fragment.txt")
FIXED_PATCH = os.path.join(AUDIT_DIR, "fixed.patch")


class TestFixedPatchExists:
    """Test that fixed.patch exists and has basic valid structure."""

    def test_fixed_patch_exists(self):
        """fixed.patch must exist."""
        assert os.path.isfile(FIXED_PATCH), f"File {FIXED_PATCH} does not exist"

    def test_fixed_patch_readable(self):
        """fixed.patch must be readable."""
        assert os.access(FIXED_PATCH, os.R_OK), f"File {FIXED_PATCH} is not readable"

    def test_fixed_patch_not_empty(self):
        """fixed.patch must not be empty."""
        size = os.path.getsize(FIXED_PATCH)
        assert size > 0, f"File {FIXED_PATCH} is empty"

    def test_fixed_patch_starts_with_diff_header(self):
        """fixed.patch must start with '---' (unified diff format)."""
        with open(FIXED_PATCH, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('---'), (
            f"fixed.patch must start with '---' to be a valid unified diff. "
            f"Got first line: {first_line[:60]!r}"
        )

    def test_fixed_patch_has_hunks(self):
        """fixed.patch must contain at least one hunk header (@@)."""
        result = subprocess.run(
            ['grep', '-c', '^@@', FIXED_PATCH],
            capture_output=True,
            text=True
        )
        # grep -c returns the count, or exits non-zero if no matches
        hunk_count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert hunk_count >= 1, (
            f"fixed.patch must contain at least 1 hunk (@@), found {hunk_count}"
        )


class TestFixedPatchAppliesCleanly:
    """Test that fixed.patch applies cleanly to baseline.log."""

    def test_patch_dry_run_succeeds(self):
        """patch --dry-run must succeed with no FAILED hunks."""
        with open(FIXED_PATCH, 'r') as patch_file:
            result = subprocess.run(
                ['patch', '--dry-run', BASELINE_LOG],
                stdin=patch_file,
                capture_output=True,
                text=True,
                cwd=AUDIT_DIR
            )

        # Check exit code
        assert result.returncode == 0, (
            f"patch --dry-run failed with exit code {result.returncode}.\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

        # Check for FAILED in output
        combined_output = result.stdout + result.stderr
        assert 'FAILED' not in combined_output, (
            f"patch --dry-run reported FAILED hunks:\n{combined_output}"
        )

    def test_patch_actual_apply_succeeds(self):
        """Applying fixed.patch to a copy of baseline.log must succeed."""
        test_log = os.path.join(AUDIT_DIR, "test_apply.log")
        try:
            # Copy baseline.log to test file
            shutil.copy(BASELINE_LOG, test_log)

            with open(FIXED_PATCH, 'r') as patch_file:
                result = subprocess.run(
                    ['patch', test_log],
                    stdin=patch_file,
                    capture_output=True,
                    text=True,
                    cwd=AUDIT_DIR
                )

            assert result.returncode == 0, (
                f"patch failed with exit code {result.returncode}.\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )

            combined_output = result.stdout + result.stderr
            assert 'FAILED' not in combined_output, (
                f"patch reported FAILED hunks:\n{combined_output}"
            )
        finally:
            # Cleanup
            if os.path.exists(test_log):
                os.remove(test_log)
            # Also cleanup any .orig files
            orig_file = test_log + ".orig"
            if os.path.exists(orig_file):
                os.remove(orig_file)


class TestPatchedOutputMatchesReference:
    """Test that the patched output matches the reference fragment at lines 847-901."""

    def test_lines_847_to_901_match_reference(self):
        """Lines 847-901 of patched output must be byte-identical to reference_fragment.txt."""
        test_log = os.path.join(AUDIT_DIR, "test_reference.log")
        try:
            # Copy baseline.log to test file
            shutil.copy(BASELINE_LOG, test_log)

            # Apply the patch
            with open(FIXED_PATCH, 'r') as patch_file:
                result = subprocess.run(
                    ['patch', test_log],
                    stdin=patch_file,
                    capture_output=True,
                    text=True,
                    cwd=AUDIT_DIR
                )

            assert result.returncode == 0, (
                f"Failed to apply patch for reference comparison: {result.stderr}"
            )

            # Extract lines 847-901 and compare with reference
            result = subprocess.run(
                f"sed -n '847,901p' {test_log} | diff - {REFERENCE_FRAGMENT}",
                shell=True,
                capture_output=True,
                text=True,
                cwd=AUDIT_DIR
            )

            assert result.returncode == 0 and result.stdout == "", (
                f"Lines 847-901 of patched output do not match reference_fragment.txt.\n"
                f"Diff output:\n{result.stdout}\n"
                f"stderr: {result.stderr}"
            )
        finally:
            # Cleanup
            if os.path.exists(test_log):
                os.remove(test_log)
            orig_file = test_log + ".orig"
            if os.path.exists(orig_file):
                os.remove(orig_file)

    def test_reference_match_using_python(self):
        """Alternative Python-based verification of reference match."""
        test_log = os.path.join(AUDIT_DIR, "test_reference_py.log")
        try:
            # Copy baseline.log to test file
            shutil.copy(BASELINE_LOG, test_log)

            # Apply the patch
            with open(FIXED_PATCH, 'r') as patch_file:
                result = subprocess.run(
                    ['patch', test_log],
                    stdin=patch_file,
                    capture_output=True,
                    text=True,
                    cwd=AUDIT_DIR
                )

            assert result.returncode == 0, f"Failed to apply patch: {result.stderr}"

            # Read patched output lines 847-901 (1-indexed, so indices 846-900)
            with open(test_log, 'r') as f:
                patched_lines = f.readlines()

            patched_fragment = patched_lines[846:901]  # Lines 847-901 (0-indexed: 846-900)

            # Read reference fragment
            with open(REFERENCE_FRAGMENT, 'r') as f:
                reference_lines = f.readlines()

            assert len(patched_fragment) == len(reference_lines), (
                f"Line count mismatch: patched has {len(patched_fragment)} lines "
                f"in range 847-901, reference has {len(reference_lines)} lines"
            )

            for i, (patched_line, ref_line) in enumerate(zip(patched_fragment, reference_lines)):
                assert patched_line == ref_line, (
                    f"Mismatch at line {847 + i}:\n"
                    f"  Patched:   {patched_line!r}\n"
                    f"  Reference: {ref_line!r}"
                )
        finally:
            # Cleanup
            if os.path.exists(test_log):
                os.remove(test_log)
            orig_file = test_log + ".orig"
            if os.path.exists(orig_file):
                os.remove(orig_file)


class TestPatchedOutputSize:
    """Test that the patched output has a reasonable number of lines."""

    def test_patched_output_line_count(self):
        """Patched output must have between 1195 and 1210 lines."""
        test_log = os.path.join(AUDIT_DIR, "test_linecount.log")
        try:
            # Copy baseline.log to test file
            shutil.copy(BASELINE_LOG, test_log)

            # Apply the patch
            with open(FIXED_PATCH, 'r') as patch_file:
                result = subprocess.run(
                    ['patch', test_log],
                    stdin=patch_file,
                    capture_output=True,
                    text=True,
                    cwd=AUDIT_DIR
                )

            assert result.returncode == 0, f"Failed to apply patch: {result.stderr}"

            # Count lines
            with open(test_log, 'r') as f:
                line_count = sum(1 for _ in f)

            assert 1195 <= line_count <= 1210, (
                f"Patched output has {line_count} lines, expected between 1195 and 1210. "
                f"This suggests the patch may not be reconstructing the full output correctly."
            )
        finally:
            # Cleanup
            if os.path.exists(test_log):
                os.remove(test_log)
            orig_file = test_log + ".orig"
            if os.path.exists(orig_file):
                os.remove(orig_file)


class TestInvariants:
    """Test that invariant files have not been modified."""

    def test_baseline_log_unchanged(self):
        """baseline.log must not have been modified (still has 1200 lines)."""
        with open(BASELINE_LOG, 'r') as f:
            line_count = sum(1 for _ in f)
        assert line_count == 1200, (
            f"baseline.log has {line_count} lines, expected 1200. "
            f"The baseline file must not be modified."
        )

    def test_reference_fragment_unchanged(self):
        """reference_fragment.txt must not have been modified (still has 55 lines)."""
        with open(REFERENCE_FRAGMENT, 'r') as f:
            line_count = sum(1 for _ in f)
        assert line_count == 55, (
            f"reference_fragment.txt has {line_count} lines, expected 55. "
            f"The reference file must not be modified."
        )


class TestAntiShortcutGuards:
    """Tests to prevent shortcut solutions that don't actually fix the patch."""

    def test_fixed_patch_is_genuine_diff(self):
        """fixed.patch must be a genuine unified diff, not a script."""
        with open(FIXED_PATCH, 'r') as f:
            first_line = f.readline()

        assert first_line.startswith('---'), (
            f"fixed.patch first line must start with '---'. "
            f"Got: {first_line[:40]!r}"
        )

    def test_fixed_patch_has_multiple_hunks_or_content(self):
        """fixed.patch should have substantial diff content."""
        result = subprocess.run(
            ['grep', '-c', '^@@', FIXED_PATCH],
            capture_output=True,
            text=True
        )
        hunk_count = int(result.stdout.strip()) if result.returncode == 0 else 0

        # The original had 6 hunks, so we expect at least a few
        assert hunk_count >= 1, (
            f"fixed.patch must contain diff hunks. Found {hunk_count} hunk headers."
        )

    def test_patched_output_is_not_just_reference(self):
        """The patched output must be the full file, not just the 55-line reference."""
        test_log = os.path.join(AUDIT_DIR, "test_antishortcut.log")
        try:
            shutil.copy(BASELINE_LOG, test_log)

            with open(FIXED_PATCH, 'r') as patch_file:
                result = subprocess.run(
                    ['patch', test_log],
                    stdin=patch_file,
                    capture_output=True,
                    text=True,
                    cwd=AUDIT_DIR
                )

            if result.returncode != 0:
                pytest.skip("Patch failed to apply, other tests will catch this")

            with open(test_log, 'r') as f:
                line_count = sum(1 for _ in f)

            # Must be much more than 55 lines (the reference fragment)
            assert line_count > 100, (
                f"Patched output has only {line_count} lines. "
                f"The output must be the full patched file (~1200 lines), "
                f"not just the 55-line reference fragment."
            )
        finally:
            if os.path.exists(test_log):
                os.remove(test_log)
            orig_file = test_log + ".orig"
            if os.path.exists(orig_file):
                os.remove(orig_file)


class TestPatchedOutputFormat:
    """Test that the patched output maintains valid log format."""

    def test_patched_output_has_valid_format(self):
        """Patched output lines should follow the expected log format."""
        import re
        pattern = re.compile(r'^\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[\w+\] \[\w+\]')

        test_log = os.path.join(AUDIT_DIR, "test_format.log")
        try:
            shutil.copy(BASELINE_LOG, test_log)

            with open(FIXED_PATCH, 'r') as patch_file:
                result = subprocess.run(
                    ['patch', test_log],
                    stdin=patch_file,
                    capture_output=True,
                    text=True,
                    cwd=AUDIT_DIR
                )

            if result.returncode != 0:
                pytest.skip("Patch failed to apply, other tests will catch this")

            with open(test_log, 'r') as f:
                lines = f.readlines()

            # Check a sample of lines throughout the file
            sample_indices = [0, 100, 500, 847, 900, len(lines) - 1]
            for idx in sample_indices:
                if idx < len(lines):
                    line = lines[idx]
                    assert pattern.match(line), (
                        f"Line {idx + 1} does not match expected log format "
                        f"'[YYYY-MM-DD HH:MM:SS] [LEVEL] [component] message'. "
                        f"Got: {line[:80]!r}"
                    )
        finally:
            if os.path.exists(test_log):
                os.remove(test_log)
            orig_file = test_log + ".orig"
            if os.path.exists(orig_file):
                os.remove(orig_file)
