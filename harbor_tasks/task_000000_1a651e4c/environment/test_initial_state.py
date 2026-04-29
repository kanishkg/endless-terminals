# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the PHP eval() scanning task.
"""

import os
import subprocess
import pytest


class TestDirectoryStructure:
    """Test that the required directory structure exists."""

    def test_webapp_directory_exists(self):
        """Verify /home/user/webapp directory exists."""
        path = "/home/user/webapp"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_webapp_lib_directory_exists(self):
        """Verify /home/user/webapp/lib directory exists."""
        path = "/home/user/webapp/lib"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_webapp_lib_legacy_directory_exists(self):
        """Verify /home/user/webapp/lib/legacy directory exists."""
        path = "/home/user/webapp/lib/legacy"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_webapp_uploads_directory_exists(self):
        """Verify /home/user/webapp/uploads directory exists."""
        path = "/home/user/webapp/uploads"
        assert os.path.isdir(path), f"Directory {path} does not exist"

    def test_webapp_config_directory_exists(self):
        """Verify /home/user/webapp/config directory exists."""
        path = "/home/user/webapp/config"
        assert os.path.isdir(path), f"Directory {path} does not exist"


class TestRequiredFilesExist:
    """Test that all required PHP files exist."""

    def test_index_php_exists(self):
        """Verify /home/user/webapp/index.php exists."""
        path = "/home/user/webapp/index.php"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_utils_php_exists(self):
        """Verify /home/user/webapp/lib/utils.php exists."""
        path = "/home/user/webapp/lib/utils.php"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_handler_php_exists(self):
        """Verify /home/user/webapp/lib/legacy/handler.php exists."""
        path = "/home/user/webapp/lib/legacy/handler.php"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_shell_php_exists(self):
        """Verify /home/user/webapp/uploads/shell.php exists."""
        path = "/home/user/webapp/uploads/shell.php"
        assert os.path.isfile(path), f"File {path} does not exist"

    def test_db_php_exists(self):
        """Verify /home/user/webapp/config/db.php exists."""
        path = "/home/user/webapp/config/db.php"
        assert os.path.isfile(path), f"File {path} does not exist"


class TestFileContents:
    """Test that files contain the expected content patterns."""

    def test_handler_php_contains_eval_post(self):
        """Verify handler.php contains eval($_POST pattern."""
        path = "/home/user/webapp/lib/legacy/handler.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_POST" in content, \
            f"File {path} should contain 'eval($_POST' pattern but doesn't"

    def test_shell_php_contains_eval_get(self):
        """Verify shell.php contains eval($_GET pattern."""
        path = "/home/user/webapp/uploads/shell.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_GET" in content, \
            f"File {path} should contain 'eval($_GET' pattern but doesn't"

    def test_index_php_is_clean(self):
        """Verify index.php does not contain eval($_ pattern."""
        path = "/home/user/webapp/index.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_" not in content, \
            f"File {path} should be clean (no 'eval($_' pattern)"

    def test_utils_php_is_clean(self):
        """Verify utils.php does not contain eval($_ pattern."""
        path = "/home/user/webapp/lib/utils.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_" not in content, \
            f"File {path} should be clean (no 'eval($_' pattern)"

    def test_db_php_is_clean(self):
        """Verify db.php does not contain eval($_ pattern."""
        path = "/home/user/webapp/config/db.php"
        with open(path, 'r') as f:
            content = f.read()
        assert "eval($_" not in content, \
            f"File {path} should be clean (no 'eval($_' pattern)"


class TestFilePermissions:
    """Test that files and directories are readable and writable."""

    def test_webapp_directory_readable(self):
        """Verify /home/user/webapp is readable."""
        path = "/home/user/webapp"
        assert os.access(path, os.R_OK), f"Directory {path} is not readable"

    def test_webapp_directory_writable(self):
        """Verify /home/user/webapp is writable."""
        path = "/home/user/webapp"
        assert os.access(path, os.W_OK), f"Directory {path} is not writable"

    def test_home_user_writable(self):
        """Verify /home/user is writable (for output file)."""
        path = "/home/user"
        assert os.access(path, os.W_OK), f"Directory {path} is not writable"

    def test_all_php_files_readable(self):
        """Verify all PHP files are readable."""
        php_files = [
            "/home/user/webapp/index.php",
            "/home/user/webapp/lib/utils.php",
            "/home/user/webapp/lib/legacy/handler.php",
            "/home/user/webapp/uploads/shell.php",
            "/home/user/webapp/config/db.php",
        ]
        for path in php_files:
            assert os.access(path, os.R_OK), f"File {path} is not readable"


class TestOutputFileNotExists:
    """Test that the output file does not exist initially."""

    def test_suspicious_txt_does_not_exist(self):
        """Verify /home/user/suspicious.txt does not exist initially."""
        path = "/home/user/suspicious.txt"
        assert not os.path.exists(path), \
            f"Output file {path} should not exist initially"


class TestRequiredToolsAvailable:
    """Test that required tools (grep, find) are available."""

    def test_grep_available(self):
        """Verify grep command is available."""
        result = subprocess.run(
            ["which", "grep"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "grep command is not available"

    def test_find_available(self):
        """Verify find command is available."""
        result = subprocess.run(
            ["which", "find"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "find command is not available"
