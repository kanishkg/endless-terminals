# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
BEFORE the student performs the web scraping task.
"""

import pytest
import os
import subprocess
import shutil


class TestInitialState:
    """Test the initial state before the scraping task is performed."""

    def test_home_directory_exists(self):
        """Verify the home directory /home/user exists."""
        home_path = "/home/user"
        assert os.path.isdir(home_path), f"Home directory {home_path} does not exist"

    def test_project_directory_does_not_exist_or_is_empty(self):
        """
        Verify that the output directory does not exist yet or is empty.
        The student needs to create /home/user/project/scraped_data/
        """
        scraped_data_path = "/home/user/project/scraped_data"
        hn_titles_path = "/home/user/project/scraped_data/hn_titles.txt"
        scrape_log_path = "/home/user/project/scraped_data/scrape_log.txt"

        # The output files should NOT exist yet (student needs to create them)
        assert not os.path.exists(hn_titles_path), (
            f"Output file {hn_titles_path} already exists. "
            "This file should be created by the student during the task."
        )
        assert not os.path.exists(scrape_log_path), (
            f"Output file {scrape_log_path} already exists. "
            "This file should be created by the student during the task."
        )

    def test_nodejs_is_available(self):
        """Verify that Node.js is installed and available."""
        node_path = shutil.which("node")
        assert node_path is not None, (
            "Node.js is not installed or not in PATH. "
            "Node.js is required to run Puppeteer or Playwright for headless browser scraping."
        )

        # Also verify node actually runs
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"Node.js is installed but failed to run: {result.stderr}"
        )

    def test_npm_is_available(self):
        """Verify that npm is installed and available."""
        npm_path = shutil.which("npm")
        assert npm_path is not None, (
            "npm is not installed or not in PATH. "
            "npm is required to install Puppeteer or Playwright packages."
        )

        # Also verify npm actually runs
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"npm is installed but failed to run: {result.stderr}"
        )

    def test_network_connectivity_to_hacker_news(self):
        """Verify that the target website https://news.ycombinator.com is reachable."""
        import urllib.request
        import urllib.error

        url = "https://news.ycombinator.com"
        try:
            # Set a reasonable timeout
            response = urllib.request.urlopen(url, timeout=10)
            status_code = response.getcode()
            assert status_code == 200, (
                f"Hacker News returned status code {status_code}, expected 200"
            )
        except urllib.error.URLError as e:
            pytest.fail(
                f"Cannot connect to {url}. Network connectivity is required for this task. "
                f"Error: {e}"
            )
        except Exception as e:
            pytest.fail(
                f"Unexpected error connecting to {url}: {e}"
            )

    def test_can_write_to_home_user(self):
        """Verify that we have write permissions in /home/user."""
        home_path = "/home/user"
        test_file = os.path.join(home_path, ".write_test_temp")

        try:
            # Try to create a temporary file
            with open(test_file, "w") as f:
                f.write("test")
            # Clean up
            os.remove(test_file)
        except PermissionError:
            pytest.fail(
                f"Cannot write to {home_path}. Write permissions are required "
                "to create the project directory structure."
            )
        except Exception as e:
            pytest.fail(f"Unexpected error testing write permissions: {e}")

    def test_python_available_as_alternative(self):
        """
        Verify Python is available as an alternative tool for the task.
        (Python with Playwright or Selenium can also be used)
        """
        python_path = shutil.which("python3") or shutil.which("python")
        assert python_path is not None, (
            "Python is not installed or not in PATH. "
            "Python can be used as an alternative with Playwright or Selenium."
        )
