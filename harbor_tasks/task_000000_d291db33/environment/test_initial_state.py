# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the rsync wrapper task.
"""

import os
import subprocess
import stat
import pytest
from pathlib import Path


HOME = Path("/home/user")
BIN_DIR = HOME / "bin"
SCRIPT_PATH = BIN_DIR / "sync-docs.sh"
REMOTE_DOCS = HOME / "remote-docs"
LOCAL_DOCS = HOME / "local-docs"


class TestBinDirectory:
    """Tests for /home/user/bin/ directory."""

    def test_bin_directory_exists(self):
        """Verify /home/user/bin/ exists."""
        assert BIN_DIR.exists(), f"Directory {BIN_DIR} does not exist"

    def test_bin_directory_is_directory(self):
        """Verify /home/user/bin/ is a directory."""
        assert BIN_DIR.is_dir(), f"{BIN_DIR} is not a directory"

    def test_bin_directory_is_writable(self):
        """Verify /home/user/bin/ is writable."""
        assert os.access(BIN_DIR, os.W_OK), f"Directory {BIN_DIR} is not writable"

    def test_sync_docs_script_does_not_exist(self):
        """Verify /home/user/bin/sync-docs.sh does not exist yet."""
        assert not SCRIPT_PATH.exists(), f"Script {SCRIPT_PATH} already exists but should not"


class TestRemoteDocsDirectory:
    """Tests for /home/user/remote-docs/ directory and its contents."""

    def test_remote_docs_exists(self):
        """Verify /home/user/remote-docs/ exists."""
        assert REMOTE_DOCS.exists(), f"Directory {REMOTE_DOCS} does not exist"

    def test_remote_docs_is_directory(self):
        """Verify /home/user/remote-docs/ is a directory."""
        assert REMOTE_DOCS.is_dir(), f"{REMOTE_DOCS} is not a directory"

    def test_notes_txt_exists(self):
        """Verify notes.txt exists in remote-docs."""
        notes_path = REMOTE_DOCS / "notes.txt"
        assert notes_path.exists(), f"File {notes_path} does not exist"

    def test_notes_txt_size(self):
        """Verify notes.txt is approximately 1KB."""
        notes_path = REMOTE_DOCS / "notes.txt"
        size = notes_path.stat().st_size
        # Allow some tolerance: 1KB = 1024 bytes, allow 500-2000 bytes
        assert 500 <= size <= 2000, f"notes.txt size is {size} bytes, expected ~1KB"

    def test_report_pdf_exists(self):
        """Verify report.pdf exists in remote-docs."""
        report_path = REMOTE_DOCS / "report.pdf"
        assert report_path.exists(), f"File {report_path} does not exist"

    def test_report_pdf_size(self):
        """Verify report.pdf is approximately 2MB."""
        report_path = REMOTE_DOCS / "report.pdf"
        size = report_path.stat().st_size
        # 2MB = 2097152 bytes, allow 1.5MB to 2.5MB
        assert 1_500_000 <= size <= 2_500_000, f"report.pdf size is {size} bytes, expected ~2MB"

    def test_slides_pptx_exists(self):
        """Verify slides.pptx exists in remote-docs."""
        slides_path = REMOTE_DOCS / "slides.pptx"
        assert slides_path.exists(), f"File {slides_path} does not exist"

    def test_slides_pptx_size(self):
        """Verify slides.pptx is approximately 8MB."""
        slides_path = REMOTE_DOCS / "slides.pptx"
        size = slides_path.stat().st_size
        # 8MB = 8388608 bytes, allow 7MB to 9MB
        assert 7_000_000 <= size <= 9_000_000, f"slides.pptx size is {size} bytes, expected ~8MB"

    def test_training_video_exists(self):
        """Verify training-video.mp4 exists in remote-docs."""
        video_path = REMOTE_DOCS / "training-video.mp4"
        assert video_path.exists(), f"File {video_path} does not exist"

    def test_training_video_size(self):
        """Verify training-video.mp4 is approximately 120MB (exceeds 50MB limit)."""
        video_path = REMOTE_DOCS / "training-video.mp4"
        size = video_path.stat().st_size
        # 120MB = 125829120 bytes, allow 100MB to 140MB
        assert 100_000_000 <= size <= 140_000_000, f"training-video.mp4 size is {size} bytes, expected ~120MB"

    def test_archive_directory_exists(self):
        """Verify archive/ subdirectory exists in remote-docs."""
        archive_path = REMOTE_DOCS / "archive"
        assert archive_path.exists(), f"Directory {archive_path} does not exist"
        assert archive_path.is_dir(), f"{archive_path} is not a directory"

    def test_archive_old_notes_exists(self):
        """Verify archive/old-notes.txt exists."""
        old_notes_path = REMOTE_DOCS / "archive" / "old-notes.txt"
        assert old_notes_path.exists(), f"File {old_notes_path} does not exist"

    def test_archive_old_notes_size(self):
        """Verify archive/old-notes.txt is approximately 500B."""
        old_notes_path = REMOTE_DOCS / "archive" / "old-notes.txt"
        size = old_notes_path.stat().st_size
        # Allow 200-1000 bytes
        assert 200 <= size <= 1000, f"old-notes.txt size is {size} bytes, expected ~500B"

    def test_archive_demo_recording_exists(self):
        """Verify archive/demo-recording.mov exists."""
        demo_path = REMOTE_DOCS / "archive" / "demo-recording.mov"
        assert demo_path.exists(), f"File {demo_path} does not exist"

    def test_archive_demo_recording_size(self):
        """Verify archive/demo-recording.mov is approximately 75MB (exceeds 50MB limit)."""
        demo_path = REMOTE_DOCS / "archive" / "demo-recording.mov"
        size = demo_path.stat().st_size
        # 75MB = 78643200 bytes, allow 60MB to 90MB
        assert 60_000_000 <= size <= 90_000_000, f"demo-recording.mov size is {size} bytes, expected ~75MB"


class TestLocalDocsDirectory:
    """Tests for /home/user/local-docs/ directory."""

    def test_local_docs_exists(self):
        """Verify /home/user/local-docs/ exists."""
        assert LOCAL_DOCS.exists(), f"Directory {LOCAL_DOCS} does not exist"

    def test_local_docs_is_directory(self):
        """Verify /home/user/local-docs/ is a directory."""
        assert LOCAL_DOCS.is_dir(), f"{LOCAL_DOCS} is not a directory"

    def test_local_docs_is_empty(self):
        """Verify /home/user/local-docs/ is empty."""
        contents = list(LOCAL_DOCS.iterdir())
        assert len(contents) == 0, f"Directory {LOCAL_DOCS} is not empty, contains: {contents}"


class TestRsyncInstalled:
    """Tests to verify rsync is installed and available."""

    def test_rsync_is_installed(self):
        """Verify rsync command is available."""
        result = subprocess.run(
            ["which", "rsync"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "rsync is not installed or not in PATH"

    def test_rsync_is_executable(self):
        """Verify rsync can be executed."""
        result = subprocess.run(
            ["rsync", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"rsync --version failed: {result.stderr}"
