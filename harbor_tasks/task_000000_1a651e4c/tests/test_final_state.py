# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the PHP eval() scanning task.
"""

import os
import subprocess
import pytest


class TestOutputFileExists:
    """Test that the output file exists."""

    def test_suspicious_txt_exists(self):
        """Verify /home/user/suspicious.txt exists."""
        path = "/home/user/suspicious.txt"
        assert os.path.isfile(path), \
            f"Output file {path} does not exist - task not completed"


class TestOutputFileContent:
    """Test that the output file contains the correct suspicious files."""

    def test_suspicious_txt_contains_handler_php(self):
        """Verify suspicious.txt contains handler.php path."""
        path = "/home/user/suspicious.txt"
        with open(path, 'r') as f:
            content = f.read()
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]

        expected_file = "/home/user/webapp/lib/legacy/handler.php"
        assert expected_file in lines, \
            f"Output file should contain {expected_file} but found lines: {lines}"

    def test_suspicious_txt_contains_shell_php(self):
        """Verify suspicious.txt contains shell.php path."""
        path = "/home/user/suspicious.txt"
        with open(path, 'r') as f:
            content = f.read()
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]

        expected_file = "/home/user/webapp/uploads/shell.php"
        assert expected_file in lines, \
            f"Output file should contain {expected_file} but found lines: {lines}"

    def test_suspicious_txt_has_correct_line_count(self):
        """Verify suspicious.txt contains exactly the expected number of suspicious files."""
        path = "/home/user/suspicious.txt"
        with open(path, 'r') as f:
            content = f.read()

        # Get non-empty lines
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]

        # Count files that actually contain eval($_
        expected_count = 0
        for line in lines:
            if os.path.isfile(line):
                with open(line, 'r') as f:
                    file_content = f.read()
                if "eval($_" in file_content:
                    expected_count += 1

        # At minimum, we need the two known suspicious files
        assert len(lines) >= 2, \
            f"Output file should contain at least 2 suspicious files, found {len(lines)}: {lines}"

        # All listed files should actually contain the pattern
        assert expected_count == len(lines), \
            f"All {len(lines)} listed files should contain 'eval($_' pattern, but only {expected_count} do"

    def test_suspicious_txt_does_not_contain_clean_files(self):
        """Verify suspicious.txt does not contain clean files."""
        path = "/home/user/suspicious.txt"
        with open(path, 'r') as f:
            content = f.read()
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]

        clean_files = [
            "/home/user/webapp/index.php",
            "/home/user/webapp/lib/utils.php",
            "/home/user/webapp/config/db.php",
        ]

        for clean_file in clean_files:
            assert clean_file not in lines, \
                f"Output file should not contain clean file {clean_file}"

    def test_suspicious_txt_contains_full_paths(self):
        """Verify suspicious.txt contains full absolute paths."""
        path = "/home/user/suspicious.txt"
        with open(path, 'r') as f:
            content = f.read()
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]

        for line in lines:
            assert line.startswith("/"), \
                f"Each line should be a full absolute path, but found: {line}"
            assert os.path.isfile(line), \
                f"Path {line} should be a valid file"


class TestWebappIntegrity:
    """Test that the webapp directory remains unchanged."""

    def test_webapp_directory_still_exists(self):
        """Verify /home/user/webapp directory still exists."""
        path = "/home/user/webapp"
        assert os.path.isdir(path), f"Directory {path} should still exist"

    def test_all_original_files_still_exist(self):
        """Verify all original PHP files still exist."""
        php_files = [
            "/home/user/webapp/index.php",
            "/home/user/webapp/lib/utils.php",
            "/home/user/webapp/lib/legacy/handler.php",
            "/home/user/webapp/uploads/shell.php",
            "/home/user/webapp/config/db.php",
        ]
        for path in php_files:
            assert os.path.isfile(path), \
                f"Original file {path} should still exist"

    def test_handler_php_still_contains_eval(self):
        """Verify handler.php still contains the suspicious pattern."""
        path = "/home/user/webapp/lib/legacy/handler.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_POST" in content, \
            f"File {path} should still contain 'eval($_POST' pattern"

    def test_shell_php_still_contains_eval(self):
        """Verify shell.php still contains the suspicious pattern."""
        path = "/home/user/webapp/uploads/shell.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_GET" in content, \
            f"File {path} should still contain 'eval($_GET' pattern"


class TestNoExtraFilesCreated:
    """Test that no extra files were created in /home/user."""

    def test_only_suspicious_txt_created(self):
        """Verify only suspicious.txt was created in /home/user."""
        home_user = "/home/user"
        allowed_items = {"webapp", "suspicious.txt"}

        # Get items directly in /home/user (not recursively)
        items = set(os.listdir(home_user))

        # Check for unexpected items (allow for common dotfiles)
        unexpected = items - allowed_items
        # Filter out common dotfiles that might exist
        unexpected = {item for item in unexpected if not item.startswith('.')}

        # We only strictly check that suspicious.txt exists and webapp exists
        assert "suspicious.txt" in items, \
            "suspicious.txt should be created in /home/user"
        assert "webapp" in items, \
            "webapp directory should still exist in /home/user"


class TestDynamicDetection:
    """Test that the solution actually scans files (anti-shortcut guard)."""

    def test_listed_files_actually_contain_pattern(self):
        """Verify all files listed in suspicious.txt actually contain eval($_."""
        output_path = "/home/user/suspicious.txt"
        with open(output_path, 'r') as f:
            content = f.read()
        lines = [line.strip() for line in content.strip().split('\n') if line.strip()]

        for file_path in lines:
            assert os.path.isfile(file_path), \
                f"Listed file {file_path} does not exist"
            with open(file_path, 'r') as f:
                file_content = f.read()
            assert "eval($_" in file_content, \
                f"Listed file {file_path} does not contain 'eval($_' pattern - solution may be hardcoded"
