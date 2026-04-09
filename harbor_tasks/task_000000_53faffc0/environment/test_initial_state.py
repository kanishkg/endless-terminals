# test_initial_state.py
"""
Tests to validate the initial state of the operating system before the student
performs the API integration and data pipeline task.
"""

import os
import pytest
import subprocess
import stat


class TestInitialState:
    """Test the initial state required for the API integration task."""

    def test_home_directory_exists(self):
        """Verify the home directory /home/user exists."""
        home_dir = "/home/user"
        assert os.path.isdir(home_dir), f"Home directory {home_dir} does not exist"

    def test_api_server_script_exists(self):
        """Verify the mock API server script exists at /home/user/api_server.py."""
        api_server_path = "/home/user/api_server.py"
        assert os.path.isfile(api_server_path), (
            f"Mock API server script not found at {api_server_path}. "
            "The task requires this file to be pre-created."
        )

    def test_api_server_script_is_executable(self):
        """Verify the mock API server script is executable."""
        api_server_path = "/home/user/api_server.py"
        assert os.path.isfile(api_server_path), (
            f"Cannot check executable status: {api_server_path} does not exist"
        )

        file_stat = os.stat(api_server_path)
        is_executable = file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        assert is_executable, (
            f"Mock API server script at {api_server_path} is not executable. "
            "It should have execute permissions (chmod +x)."
        )

    def test_api_server_script_content_valid(self):
        """Verify the mock API server script contains expected content."""
        api_server_path = "/home/user/api_server.py"
        assert os.path.isfile(api_server_path), (
            f"Cannot check content: {api_server_path} does not exist"
        )

        with open(api_server_path, 'r') as f:
            content = f.read()

        # Check for essential components of the mock API server
        assert 'HTTPServer' in content or 'http.server' in content, (
            "API server script should use HTTPServer or http.server module"
        )
        assert '/api/users' in content, (
            "API server script should define /api/users endpoint"
        )
        assert '/api/products' in content, (
            "API server script should define /api/products endpoint"
        )
        assert '/api/orders' in content, (
            "API server script should define /api/orders endpoint"
        )
        assert '8765' in content, (
            "API server script should be configured to run on port 8765"
        )
        assert '500' in content, (
            "API server script should return 500 error for /api/orders endpoint"
        )

    def test_api_server_script_has_python_shebang(self):
        """Verify the mock API server script has a proper Python shebang."""
        api_server_path = "/home/user/api_server.py"
        assert os.path.isfile(api_server_path), (
            f"Cannot check shebang: {api_server_path} does not exist"
        )

        with open(api_server_path, 'r') as f:
            first_line = f.readline().strip()

        assert first_line.startswith('#!') and 'python' in first_line, (
            f"API server script should have a Python shebang line. "
            f"Found: '{first_line}'"
        )

    def test_port_8765_is_free(self):
        """Verify port 8765 is not currently in use."""
        # Try using lsof to check if port is in use
        try:
            result = subprocess.run(
                ['lsof', '-i', ':8765'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # lsof returns 0 if it finds something, 1 if nothing found
            assert result.returncode != 0 or result.stdout.strip() == '', (
                f"Port 8765 is already in use. Output: {result.stdout}. "
                "Please stop any process using this port before starting the task."
            )
        except FileNotFoundError:
            # lsof not available, try netstat or ss
            try:
                result = subprocess.run(
                    ['ss', '-tuln'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                assert ':8765' not in result.stdout, (
                    "Port 8765 is already in use. "
                    "Please stop any process using this port before starting the task."
                )
            except FileNotFoundError:
                # Neither lsof nor ss available, skip this check
                pytest.skip("Cannot verify port status: lsof and ss not available")

    def test_api_server_not_running(self):
        """Verify the API server is not already running."""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'api_server.py'],
                capture_output=True,
                text=True,
                timeout=5
            )
            # pgrep returns 0 if process found, 1 if not found
            assert result.returncode != 0 or result.stdout.strip() == '', (
                f"API server process is already running (PIDs: {result.stdout.strip()}). "
                "The server should not be running at the start of the task."
            )
        except FileNotFoundError:
            pytest.skip("pgrep command not available")

    def test_python3_available(self):
        """Verify Python 3 is available to run the API server."""
        try:
            result = subprocess.run(
                ['python3', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, (
                "Python 3 is required but not available or not working properly"
            )
        except FileNotFoundError:
            pytest.fail("Python 3 is not installed or not in PATH")

    def test_curl_available(self):
        """Verify curl is available for making HTTP requests."""
        try:
            result = subprocess.run(
                ['curl', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            assert result.returncode == 0, (
                "curl is required but not available or not working properly"
            )
        except FileNotFoundError:
            # curl might not be required if student uses wget or other tools
            pytest.skip("curl not available, student may use alternative tools")

    def test_user_has_write_permission(self):
        """Verify user has write permission in /home/user directory."""
        home_dir = "/home/user"
        assert os.path.isdir(home_dir), f"Home directory {home_dir} does not exist"
        assert os.access(home_dir, os.W_OK), (
            f"No write permission in {home_dir}. "
            "User needs to be able to create files in this directory."
        )
