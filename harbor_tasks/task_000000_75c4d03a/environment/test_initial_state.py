# test_initial_state.py
"""
Tests to validate the initial state before the student performs the rsync fix task.
"""

import os
import subprocess
import pytest

HOME = "/home/user"
PROJECT_DIR = os.path.join(HOME, "project")
BACKUP_DIR = os.path.join(HOME, "backup")
RSYNCRC = os.path.join(HOME, ".rsyncrc")


class TestRsyncInstalled:
    """Verify rsync is installed and available."""

    def test_rsync_is_installed(self):
        """rsync command should be available."""
        result = subprocess.run(["which", "rsync"], capture_output=True)
        assert result.returncode == 0, "rsync is not installed or not in PATH"


class TestProjectDirectory:
    """Verify /home/user/project/ structure and contents."""

    def test_project_directory_exists(self):
        """Project directory should exist."""
        assert os.path.isdir(PROJECT_DIR), f"Directory {PROJECT_DIR} does not exist"

    def test_readme_exists_with_content(self):
        """README.md should exist with correct content."""
        readme_path = os.path.join(PROJECT_DIR, "README.md")
        assert os.path.isfile(readme_path), f"File {readme_path} does not exist"
        with open(readme_path, "r") as f:
            content = f.read()
        assert content == "# Project", f"README.md has unexpected content: {content!r}"

    def test_src_main_py_exists_with_content(self):
        """src/main.py should exist with correct content."""
        main_py_path = os.path.join(PROJECT_DIR, "src", "main.py")
        assert os.path.isfile(main_py_path), f"File {main_py_path} does not exist"
        with open(main_py_path, "r") as f:
            content = f.read()
        assert content == "print('hello')", f"src/main.py has unexpected content: {content!r}"

    def test_env_file_exists_with_content(self):
        """.env should exist with correct content."""
        env_path = os.path.join(PROJECT_DIR, ".env")
        assert os.path.isfile(env_path), f"File {env_path} does not exist"
        with open(env_path, "r") as f:
            content = f.read()
        assert content == "API_KEY=secret123", f".env has unexpected content: {content!r}"

    def test_gitignore_exists_with_content(self):
        """.gitignore should exist with correct content."""
        gitignore_path = os.path.join(PROJECT_DIR, ".gitignore")
        assert os.path.isfile(gitignore_path), f"File {gitignore_path} does not exist"
        with open(gitignore_path, "r") as f:
            content = f.read()
        assert content == "*.pyc", f".gitignore has unexpected content: {content!r}"

    def test_config_hidden_exists_with_content(self):
        """config/.hidden should exist with correct content."""
        hidden_path = os.path.join(PROJECT_DIR, "config", ".hidden")
        assert os.path.isfile(hidden_path), f"File {hidden_path} does not exist"
        with open(hidden_path, "r") as f:
            content = f.read()
        assert content == "hidden config", f"config/.hidden has unexpected content: {content!r}"


class TestBackupDirectory:
    """Verify /home/user/backup/ exists and is empty."""

    def test_backup_directory_exists(self):
        """Backup directory should exist."""
        assert os.path.isdir(BACKUP_DIR), f"Directory {BACKUP_DIR} does not exist"

    def test_backup_directory_is_empty(self):
        """Backup directory should be empty initially."""
        contents = os.listdir(BACKUP_DIR)
        assert len(contents) == 0, f"Backup directory should be empty but contains: {contents}"

    def test_backup_directory_is_writable(self):
        """Backup directory should be writable."""
        assert os.access(BACKUP_DIR, os.W_OK), f"Directory {BACKUP_DIR} is not writable"


class TestRsyncrc:
    """Verify /home/user/.rsyncrc exists with expected problematic content."""

    def test_rsyncrc_exists(self):
        """.rsyncrc file should exist."""
        assert os.path.isfile(RSYNCRC), f"File {RSYNCRC} does not exist"

    def test_rsyncrc_contains_exclude_pattern(self):
        """.rsyncrc should contain the problematic --exclude=.* pattern."""
        with open(RSYNCRC, "r") as f:
            content = f.read()
        assert "--exclude=.*" in content, f".rsyncrc should contain '--exclude=.*' but has: {content!r}"

    def test_rsyncrc_contains_archive_flag(self):
        """.rsyncrc should contain --archive flag."""
        with open(RSYNCRC, "r") as f:
            content = f.read()
        assert "--archive" in content, f".rsyncrc should contain '--archive' but has: {content!r}"

    def test_rsyncrc_is_writable(self):
        """.rsyncrc should be writable."""
        assert os.access(RSYNCRC, os.W_OK), f"File {RSYNCRC} is not writable"

    def test_rsyncrc_has_expected_content(self):
        """.rsyncrc should have exactly the expected lines."""
        with open(RSYNCRC, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        expected_lines = ["--exclude=.*", "--archive"]
        assert set(lines) == set(expected_lines), f".rsyncrc should contain {expected_lines} but has: {lines}"
