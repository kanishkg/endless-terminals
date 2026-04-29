# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the rsync wrapper task.
"""

import os
import subprocess
import stat
import re
import pytest
from pathlib import Path


HOME = Path("/home/user")
BIN_DIR = HOME / "bin"
SCRIPT_PATH = BIN_DIR / "sync-docs.sh"
REMOTE_DOCS = HOME / "remote-docs"
LOCAL_DOCS = HOME / "local-docs"


class TestScriptExists:
    """Tests for /home/user/bin/sync-docs.sh existence and permissions."""

    def test_script_exists(self):
        """Verify /home/user/bin/sync-docs.sh exists."""
        assert SCRIPT_PATH.exists(), f"Script {SCRIPT_PATH} does not exist"

    def test_script_is_file(self):
        """Verify /home/user/bin/sync-docs.sh is a regular file."""
        assert SCRIPT_PATH.is_file(), f"{SCRIPT_PATH} is not a regular file"

    def test_script_is_executable(self):
        """Verify /home/user/bin/sync-docs.sh is executable (at least u+x)."""
        mode = SCRIPT_PATH.stat().st_mode
        user_execute = bool(mode & stat.S_IXUSR)
        assert user_execute, f"Script {SCRIPT_PATH} is not executable by user (mode: {oct(mode)})"


class TestScriptContent:
    """Tests to verify the script uses rsync with proper size filtering."""

    def test_script_contains_rsync(self):
        """Verify the script uses rsync command."""
        content = SCRIPT_PATH.read_text()
        assert "rsync" in content.lower(), "Script does not contain 'rsync' command"

    def test_script_contains_size_limit(self):
        """Verify the script has a size limit mechanism (--max-size or equivalent)."""
        content = SCRIPT_PATH.read_text()
        # Check for --max-size option which is the standard way to limit file size in rsync
        # Also accept variations like -max-size or max-size=
        has_max_size = bool(re.search(r'--max-size|--max-size=', content, re.IGNORECASE))
        assert has_max_size, (
            "Script does not contain '--max-size' option. "
            "The task requires using rsync with size filtering to skip files larger than 50MB."
        )

    def test_script_size_limit_value(self):
        """Verify the script sets size limit around 50MB."""
        content = SCRIPT_PATH.read_text()
        # Look for patterns like --max-size=50M, --max-size 50M, --max-size=50m, etc.
        # Also accept 50MB, 52428800 (bytes), etc.
        size_pattern = re.search(
            r'--max-size[=\s]+["\']?(\d+[KMGkmg]?[Bb]?|\d+)["\']?',
            content
        )
        assert size_pattern, "Could not find a size limit value in the script"

        size_value = size_pattern.group(1).upper().rstrip('B')
        # Parse the size value
        if size_value.endswith('M'):
            size_mb = int(size_value[:-1])
        elif size_value.endswith('K'):
            size_mb = int(size_value[:-1]) / 1024
        elif size_value.endswith('G'):
            size_mb = int(size_value[:-1]) * 1024
        else:
            # Assume bytes
            size_mb = int(size_value) / (1024 * 1024)

        # Should be around 50MB (allow 49-51MB range, or exactly 50)
        assert 49 <= size_mb <= 51, f"Size limit is {size_mb}MB, expected ~50MB"


class TestScriptExecution:
    """Tests for running the script."""

    def test_script_runs_successfully(self):
        """Verify running /home/user/bin/sync-docs.sh exits with code 0."""
        result = subprocess.run(
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(HOME)
        )
        assert result.returncode == 0, (
            f"Script exited with code {result.returncode}. "
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_script_is_idempotent(self):
        """Verify running the script a second time also succeeds (idempotent)."""
        # Run twice
        result1 = subprocess.run(
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(HOME)
        )
        result2 = subprocess.run(
            [str(SCRIPT_PATH)],
            capture_output=True,
            text=True,
            cwd=str(HOME)
        )
        assert result2.returncode == 0, (
            f"Second run of script failed with code {result2.returncode}. "
            f"stdout: {result2.stdout}\nstderr: {result2.stderr}"
        )


class TestSyncedFiles:
    """Tests for files that should be synced to local-docs."""

    @pytest.fixture(autouse=True)
    def run_script_first(self):
        """Ensure the script has been run before checking synced files."""
        subprocess.run([str(SCRIPT_PATH)], capture_output=True, cwd=str(HOME))

    def test_notes_txt_synced(self):
        """Verify notes.txt was synced to local-docs."""
        local_file = LOCAL_DOCS / "notes.txt"
        assert local_file.exists(), f"File {local_file} was not synced"

    def test_notes_txt_content_matches(self):
        """Verify notes.txt content matches the source."""
        local_file = LOCAL_DOCS / "notes.txt"
        remote_file = REMOTE_DOCS / "notes.txt"
        assert local_file.read_bytes() == remote_file.read_bytes(), "notes.txt content does not match source"

    def test_notes_txt_mtime_preserved(self):
        """Verify notes.txt modification time was preserved."""
        local_file = LOCAL_DOCS / "notes.txt"
        remote_file = REMOTE_DOCS / "notes.txt"
        local_mtime = local_file.stat().st_mtime
        remote_mtime = remote_file.stat().st_mtime
        # Allow 1 second tolerance for filesystem differences
        assert abs(local_mtime - remote_mtime) < 2, (
            f"notes.txt mtime not preserved. Local: {local_mtime}, Remote: {remote_mtime}"
        )

    def test_notes_txt_permissions_preserved(self):
        """Verify notes.txt permissions were preserved."""
        local_file = LOCAL_DOCS / "notes.txt"
        remote_file = REMOTE_DOCS / "notes.txt"
        local_mode = stat.S_IMODE(local_file.stat().st_mode)
        remote_mode = stat.S_IMODE(remote_file.stat().st_mode)
        assert local_mode == remote_mode, (
            f"notes.txt permissions not preserved. Local: {oct(local_mode)}, Remote: {oct(remote_mode)}"
        )

    def test_report_pdf_synced(self):
        """Verify report.pdf was synced to local-docs."""
        local_file = LOCAL_DOCS / "report.pdf"
        assert local_file.exists(), f"File {local_file} was not synced"

    def test_report_pdf_content_matches(self):
        """Verify report.pdf content matches the source."""
        local_file = LOCAL_DOCS / "report.pdf"
        remote_file = REMOTE_DOCS / "report.pdf"
        assert local_file.read_bytes() == remote_file.read_bytes(), "report.pdf content does not match source"

    def test_report_pdf_mtime_preserved(self):
        """Verify report.pdf modification time was preserved."""
        local_file = LOCAL_DOCS / "report.pdf"
        remote_file = REMOTE_DOCS / "report.pdf"
        local_mtime = local_file.stat().st_mtime
        remote_mtime = remote_file.stat().st_mtime
        assert abs(local_mtime - remote_mtime) < 2, (
            f"report.pdf mtime not preserved. Local: {local_mtime}, Remote: {remote_mtime}"
        )

    def test_report_pdf_permissions_preserved(self):
        """Verify report.pdf permissions were preserved."""
        local_file = LOCAL_DOCS / "report.pdf"
        remote_file = REMOTE_DOCS / "report.pdf"
        local_mode = stat.S_IMODE(local_file.stat().st_mode)
        remote_mode = stat.S_IMODE(remote_file.stat().st_mode)
        assert local_mode == remote_mode, (
            f"report.pdf permissions not preserved. Local: {oct(local_mode)}, Remote: {oct(remote_mode)}"
        )

    def test_slides_pptx_synced(self):
        """Verify slides.pptx was synced to local-docs."""
        local_file = LOCAL_DOCS / "slides.pptx"
        assert local_file.exists(), f"File {local_file} was not synced"

    def test_slides_pptx_content_matches(self):
        """Verify slides.pptx content matches the source."""
        local_file = LOCAL_DOCS / "slides.pptx"
        remote_file = REMOTE_DOCS / "slides.pptx"
        assert local_file.read_bytes() == remote_file.read_bytes(), "slides.pptx content does not match source"

    def test_slides_pptx_mtime_preserved(self):
        """Verify slides.pptx modification time was preserved."""
        local_file = LOCAL_DOCS / "slides.pptx"
        remote_file = REMOTE_DOCS / "slides.pptx"
        local_mtime = local_file.stat().st_mtime
        remote_mtime = remote_file.stat().st_mtime
        assert abs(local_mtime - remote_mtime) < 2, (
            f"slides.pptx mtime not preserved. Local: {local_mtime}, Remote: {remote_mtime}"
        )

    def test_archive_directory_created(self):
        """Verify archive/ subdirectory was created in local-docs."""
        archive_path = LOCAL_DOCS / "archive"
        assert archive_path.exists(), f"Directory {archive_path} was not created"
        assert archive_path.is_dir(), f"{archive_path} is not a directory"

    def test_archive_old_notes_synced(self):
        """Verify archive/old-notes.txt was synced."""
        local_file = LOCAL_DOCS / "archive" / "old-notes.txt"
        assert local_file.exists(), f"File {local_file} was not synced"

    def test_archive_old_notes_content_matches(self):
        """Verify archive/old-notes.txt content matches the source."""
        local_file = LOCAL_DOCS / "archive" / "old-notes.txt"
        remote_file = REMOTE_DOCS / "archive" / "old-notes.txt"
        assert local_file.read_bytes() == remote_file.read_bytes(), "archive/old-notes.txt content does not match source"

    def test_archive_old_notes_mtime_preserved(self):
        """Verify archive/old-notes.txt modification time was preserved."""
        local_file = LOCAL_DOCS / "archive" / "old-notes.txt"
        remote_file = REMOTE_DOCS / "archive" / "old-notes.txt"
        local_mtime = local_file.stat().st_mtime
        remote_mtime = remote_file.stat().st_mtime
        assert abs(local_mtime - remote_mtime) < 2, (
            f"archive/old-notes.txt mtime not preserved. Local: {local_mtime}, Remote: {remote_mtime}"
        )


class TestExcludedFiles:
    """Tests for files that should NOT be synced (exceed 50MB)."""

    @pytest.fixture(autouse=True)
    def run_script_first(self):
        """Ensure the script has been run before checking excluded files."""
        subprocess.run([str(SCRIPT_PATH)], capture_output=True, cwd=str(HOME))

    def test_training_video_not_synced(self):
        """Verify training-video.mp4 was NOT synced (exceeds 50MB)."""
        local_file = LOCAL_DOCS / "training-video.mp4"
        assert not local_file.exists(), (
            f"File {local_file} should NOT exist - it exceeds 50MB and should be skipped"
        )

    def test_demo_recording_not_synced(self):
        """Verify archive/demo-recording.mov was NOT synced (exceeds 50MB)."""
        local_file = LOCAL_DOCS / "archive" / "demo-recording.mov"
        assert not local_file.exists(), (
            f"File {local_file} should NOT exist - it exceeds 50MB and should be skipped"
        )


class TestRemoteDocsUnchanged:
    """Tests to verify remote-docs was not modified."""

    def test_remote_docs_still_exists(self):
        """Verify /home/user/remote-docs/ still exists."""
        assert REMOTE_DOCS.exists(), f"Directory {REMOTE_DOCS} no longer exists"

    def test_remote_notes_txt_exists(self):
        """Verify notes.txt still exists in remote-docs."""
        assert (REMOTE_DOCS / "notes.txt").exists(), "remote-docs/notes.txt was removed"

    def test_remote_report_pdf_exists(self):
        """Verify report.pdf still exists in remote-docs."""
        assert (REMOTE_DOCS / "report.pdf").exists(), "remote-docs/report.pdf was removed"

    def test_remote_slides_pptx_exists(self):
        """Verify slides.pptx still exists in remote-docs."""
        assert (REMOTE_DOCS / "slides.pptx").exists(), "remote-docs/slides.pptx was removed"

    def test_remote_training_video_exists(self):
        """Verify training-video.mp4 still exists in remote-docs."""
        assert (REMOTE_DOCS / "training-video.mp4").exists(), "remote-docs/training-video.mp4 was removed"

    def test_remote_archive_exists(self):
        """Verify archive/ still exists in remote-docs."""
        assert (REMOTE_DOCS / "archive").exists(), "remote-docs/archive/ was removed"

    def test_remote_archive_old_notes_exists(self):
        """Verify archive/old-notes.txt still exists in remote-docs."""
        assert (REMOTE_DOCS / "archive" / "old-notes.txt").exists(), "remote-docs/archive/old-notes.txt was removed"

    def test_remote_archive_demo_recording_exists(self):
        """Verify archive/demo-recording.mov still exists in remote-docs."""
        assert (REMOTE_DOCS / "archive" / "demo-recording.mov").exists(), "remote-docs/archive/demo-recording.mov was removed"
