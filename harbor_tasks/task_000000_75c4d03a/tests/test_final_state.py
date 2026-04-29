# test_final_state.py
"""
Tests to validate the final state after the student has fixed the rsync dotfile exclusion issue.
"""

import os
import subprocess
import pytest

HOME = "/home/user"
PROJECT_DIR = os.path.join(HOME, "project")
BACKUP_DIR = os.path.join(HOME, "backup")
RSYNCRC = os.path.join(HOME, ".rsyncrc")


class TestRsyncrcFixed:
    """Verify /home/user/.rsyncrc has been fixed."""

    def test_rsyncrc_exists(self):
        """.rsyncrc file should still exist."""
        assert os.path.isfile(RSYNCRC), f"File {RSYNCRC} does not exist"

    def test_rsyncrc_no_longer_excludes_dotfiles(self):
        """.rsyncrc should not contain active --exclude=.* pattern."""
        with open(RSYNCRC, "r") as f:
            lines = f.readlines()

        for line in lines:
            stripped = line.strip()
            # Skip empty lines and comments
            if not stripped or stripped.startswith("#"):
                continue
            # Check that no active line contains the problematic exclude pattern
            assert "--exclude=.*" not in stripped, \
                f".rsyncrc still contains active '--exclude=.*' pattern: {stripped!r}"

    def test_rsyncrc_still_has_archive_flag(self):
        """.rsyncrc should still contain --archive or -a flag."""
        with open(RSYNCRC, "r") as f:
            content = f.read()

        # Check for --archive or -a (common equivalent)
        has_archive = "--archive" in content or "-a" in content
        assert has_archive, f".rsyncrc should contain '--archive' or '-a' flag but has: {content!r}"


class TestProjectDirectoryUnchanged:
    """Verify /home/user/project/ contents are unchanged (invariant)."""

    def test_project_directory_exists(self):
        """Project directory should still exist."""
        assert os.path.isdir(PROJECT_DIR), f"Directory {PROJECT_DIR} does not exist"

    def test_readme_unchanged(self):
        """README.md should be unchanged."""
        readme_path = os.path.join(PROJECT_DIR, "README.md")
        assert os.path.isfile(readme_path), f"File {readme_path} does not exist"
        with open(readme_path, "r") as f:
            content = f.read()
        assert content == "# Project", f"README.md was modified: {content!r}"

    def test_src_main_py_unchanged(self):
        """src/main.py should be unchanged."""
        main_py_path = os.path.join(PROJECT_DIR, "src", "main.py")
        assert os.path.isfile(main_py_path), f"File {main_py_path} does not exist"
        with open(main_py_path, "r") as f:
            content = f.read()
        assert content == "print('hello')", f"src/main.py was modified: {content!r}"

    def test_env_file_unchanged(self):
        """.env should be unchanged."""
        env_path = os.path.join(PROJECT_DIR, ".env")
        assert os.path.isfile(env_path), f"File {env_path} does not exist"
        with open(env_path, "r") as f:
            content = f.read()
        assert content == "API_KEY=secret123", f".env was modified: {content!r}"

    def test_gitignore_unchanged(self):
        """.gitignore should be unchanged."""
        gitignore_path = os.path.join(PROJECT_DIR, ".gitignore")
        assert os.path.isfile(gitignore_path), f"File {gitignore_path} does not exist"
        with open(gitignore_path, "r") as f:
            content = f.read()
        assert content == "*.pyc", f".gitignore was modified: {content!r}"

    def test_config_hidden_unchanged(self):
        """config/.hidden should be unchanged."""
        hidden_path = os.path.join(PROJECT_DIR, "config", ".hidden")
        assert os.path.isfile(hidden_path), f"File {hidden_path} does not exist"
        with open(hidden_path, "r") as f:
            content = f.read()
        assert content == "hidden config", f"config/.hidden was modified: {content!r}"


class TestRsyncCommandProducesCorrectBackup:
    """
    Run the rsync command using .rsyncrc and verify all files including dotfiles are synced.
    This is the anti-shortcut guard - we run rsync with the fixed .rsyncrc.
    """

    @pytest.fixture(autouse=True)
    def run_rsync_with_rsyncrc(self):
        """Run rsync using the .rsyncrc file before testing backup contents."""
        # Clear backup directory first to ensure we're testing the rsync result
        if os.path.isdir(BACKUP_DIR):
            for root, dirs, files in os.walk(BACKUP_DIR, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

        # Run rsync with the .rsyncrc configuration
        cmd = f"rsync $(cat {RSYNCRC} | tr '\\n' ' ') {PROJECT_DIR}/ {BACKUP_DIR}/"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Store result for potential debugging
        self.rsync_result = result
        yield

    def test_rsync_command_succeeds(self):
        """The rsync command should complete successfully."""
        assert self.rsync_result.returncode == 0, \
            f"rsync command failed with code {self.rsync_result.returncode}: {self.rsync_result.stderr}"

    def test_backup_env_file_exists_with_correct_content(self):
        """/home/user/backup/.env should exist with correct content after rsync."""
        env_path = os.path.join(BACKUP_DIR, ".env")
        assert os.path.isfile(env_path), \
            f"File {env_path} does not exist - dotfiles are still being excluded"
        with open(env_path, "r") as f:
            content = f.read()
        assert content == "API_KEY=secret123", \
            f".env has wrong content: {content!r}"

    def test_backup_gitignore_exists_with_correct_content(self):
        """/home/user/backup/.gitignore should exist with correct content after rsync."""
        gitignore_path = os.path.join(BACKUP_DIR, ".gitignore")
        assert os.path.isfile(gitignore_path), \
            f"File {gitignore_path} does not exist - dotfiles are still being excluded"
        with open(gitignore_path, "r") as f:
            content = f.read()
        assert content == "*.pyc", \
            f".gitignore has wrong content: {content!r}"

    def test_backup_config_hidden_exists_with_correct_content(self):
        """/home/user/backup/config/.hidden should exist with correct content after rsync."""
        hidden_path = os.path.join(BACKUP_DIR, "config", ".hidden")
        assert os.path.isfile(hidden_path), \
            f"File {hidden_path} does not exist - dotfiles are still being excluded"
        with open(hidden_path, "r") as f:
            content = f.read()
        assert content == "hidden config", \
            f"config/.hidden has wrong content: {content!r}"

    def test_backup_readme_exists_with_correct_content(self):
        """/home/user/backup/README.md should exist with correct content after rsync."""
        readme_path = os.path.join(BACKUP_DIR, "README.md")
        assert os.path.isfile(readme_path), \
            f"File {readme_path} does not exist"
        with open(readme_path, "r") as f:
            content = f.read()
        assert content == "# Project", \
            f"README.md has wrong content: {content!r}"

    def test_backup_src_main_py_exists_with_correct_content(self):
        """/home/user/backup/src/main.py should exist with correct content after rsync."""
        main_py_path = os.path.join(BACKUP_DIR, "src", "main.py")
        assert os.path.isfile(main_py_path), \
            f"File {main_py_path} does not exist"
        with open(main_py_path, "r") as f:
            content = f.read()
        assert content == "print('hello')", \
            f"src/main.py has wrong content: {content!r}"
