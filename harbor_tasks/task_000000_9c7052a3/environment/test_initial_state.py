# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
creates the Makefile for building markdown docs into HTML.
"""

import os
import subprocess
import pytest


class TestDirectoryStructure:
    """Test that required directories exist and have correct permissions."""

    def test_docs_directory_exists(self):
        """Verify /home/user/docs/ exists."""
        assert os.path.isdir("/home/user/docs"), \
            "Directory /home/user/docs/ does not exist"

    def test_docs_directory_is_writable(self):
        """Verify /home/user/docs/ is writable."""
        assert os.access("/home/user/docs", os.W_OK), \
            "Directory /home/user/docs/ is not writable"

    def test_src_directory_exists(self):
        """Verify /home/user/docs/src/ exists."""
        assert os.path.isdir("/home/user/docs/src"), \
            "Directory /home/user/docs/src/ does not exist"

    def test_build_directory_exists(self):
        """Verify /home/user/docs/build/ exists."""
        assert os.path.isdir("/home/user/docs/build"), \
            "Directory /home/user/docs/build/ does not exist"

    def test_build_directory_is_empty(self):
        """Verify /home/user/docs/build/ is empty."""
        build_contents = os.listdir("/home/user/docs/build")
        assert len(build_contents) == 0, \
            f"Directory /home/user/docs/build/ should be empty but contains: {build_contents}"


class TestSourceMarkdownFiles:
    """Test that required markdown source files exist with valid content."""

    @pytest.mark.parametrize("filename", ["intro.md", "guide.md", "reference.md"])
    def test_markdown_file_exists(self, filename):
        """Verify each required markdown file exists in src/."""
        filepath = f"/home/user/docs/src/{filename}"
        assert os.path.isfile(filepath), \
            f"Markdown file {filepath} does not exist"

    @pytest.mark.parametrize("filename", ["intro.md", "guide.md", "reference.md"])
    def test_markdown_file_has_content(self, filename):
        """Verify each markdown file has non-empty content."""
        filepath = f"/home/user/docs/src/{filename}"
        with open(filepath, 'r') as f:
            content = f.read()
        assert len(content.strip()) > 0, \
            f"Markdown file {filepath} is empty"

    @pytest.mark.parametrize("filename", ["intro.md", "guide.md", "reference.md"])
    def test_markdown_file_has_valid_markdown(self, filename):
        """Verify each markdown file contains valid markdown elements (headers, paragraphs, lists)."""
        filepath = f"/home/user/docs/src/{filename}"
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for at least a header (line starting with #)
        has_header = any(line.strip().startswith('#') for line in content.split('\n'))
        assert has_header, \
            f"Markdown file {filepath} does not contain any headers (lines starting with #)"

    def test_only_expected_markdown_files_in_src(self):
        """Verify src/ contains exactly the three expected markdown files."""
        expected_files = {"intro.md", "guide.md", "reference.md"}
        actual_files = set(os.listdir("/home/user/docs/src"))
        md_files = {f for f in actual_files if f.endswith('.md')}

        assert md_files == expected_files, \
            f"Expected markdown files {expected_files} in src/, but found {md_files}"


class TestMakefileDoesNotExist:
    """Test that Makefile does not exist yet (student needs to create it)."""

    def test_makefile_does_not_exist(self):
        """Verify /home/user/docs/Makefile does not exist."""
        makefile_path = "/home/user/docs/Makefile"
        assert not os.path.exists(makefile_path), \
            f"Makefile already exists at {makefile_path} - it should not exist in initial state"


class TestRequiredToolsInstalled:
    """Test that required tools (pandoc, make) are installed and available."""

    def test_pandoc_is_installed(self):
        """Verify pandoc is installed and available in PATH."""
        result = subprocess.run(
            ["which", "pandoc"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "pandoc is not installed or not available in PATH"

    def test_pandoc_is_executable(self):
        """Verify pandoc can be executed."""
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"pandoc cannot be executed: {result.stderr}"

    def test_make_is_installed(self):
        """Verify GNU make is installed and available in PATH."""
        result = subprocess.run(
            ["which", "make"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "make (GNU Make) is not installed or not available in PATH"

    def test_make_is_executable(self):
        """Verify make can be executed."""
        result = subprocess.run(
            ["make", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"make cannot be executed: {result.stderr}"

    def test_make_is_gnu_make(self):
        """Verify that make is GNU Make."""
        result = subprocess.run(
            ["make", "--version"],
            capture_output=True,
            text=True
        )
        assert "GNU Make" in result.stdout, \
            f"make is not GNU Make. Version output: {result.stdout}"
