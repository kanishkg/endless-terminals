# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has created the Makefile for building markdown docs into HTML.
"""

import os
import subprocess
import pytest


class TestMakefileExists:
    """Test that the Makefile exists and has required content."""

    def test_makefile_exists(self):
        """Verify /home/user/docs/Makefile exists."""
        makefile_path = "/home/user/docs/Makefile"
        assert os.path.isfile(makefile_path), \
            f"Makefile does not exist at {makefile_path}"

    def test_makefile_contains_pandoc_reference(self):
        """Verify Makefile references pandoc."""
        makefile_path = "/home/user/docs/Makefile"
        result = subprocess.run(
            ["grep", "-i", "pandoc", makefile_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "Makefile does not contain a reference to pandoc"

    def test_makefile_has_html_target(self):
        """Verify Makefile has an 'html' target."""
        makefile_path = "/home/user/docs/Makefile"

        # Check if make recognizes 'html' as a valid target
        result = subprocess.run(
            ["make", "-n", "html"],
            capture_output=True,
            text=True,
            cwd="/home/user/docs"
        )
        # If 'html' target doesn't exist, make will report an error
        assert result.returncode == 0 or "Nothing to be done" in result.stdout, \
            f"Makefile does not have a valid 'html' target. Error: {result.stderr}"


class TestMakeHtmlExecution:
    """Test that 'make html' runs successfully."""

    def test_make_html_exits_zero(self):
        """Verify 'make html' exits with code 0."""
        result = subprocess.run(
            ["make", "html"],
            capture_output=True,
            text=True,
            cwd="/home/user/docs"
        )
        assert result.returncode == 0, \
            f"'make html' failed with exit code {result.returncode}. stderr: {result.stderr}, stdout: {result.stdout}"


class TestHtmlOutputFiles:
    """Test that HTML output files are generated correctly."""

    @pytest.mark.parametrize("html_file", ["intro.html", "guide.html", "reference.html"])
    def test_html_file_exists(self, html_file):
        """Verify each expected HTML file exists in build/."""
        # First ensure make html has been run
        subprocess.run(
            ["make", "html"],
            capture_output=True,
            cwd="/home/user/docs"
        )

        filepath = f"/home/user/docs/build/{html_file}"
        assert os.path.isfile(filepath), \
            f"HTML file {filepath} does not exist after running 'make html'"

    @pytest.mark.parametrize("html_file", ["intro.html", "guide.html", "reference.html"])
    def test_html_file_has_content(self, html_file):
        """Verify each HTML file has non-empty content."""
        # First ensure make html has been run
        subprocess.run(
            ["make", "html"],
            capture_output=True,
            cwd="/home/user/docs"
        )

        filepath = f"/home/user/docs/build/{html_file}"
        with open(filepath, 'r') as f:
            content = f.read()
        assert len(content.strip()) > 0, \
            f"HTML file {filepath} is empty"

    @pytest.mark.parametrize("html_file", ["intro.html", "guide.html", "reference.html"])
    def test_html_file_is_valid_html(self, html_file):
        """Verify each HTML file contains valid HTML markers from pandoc output."""
        # First ensure make html has been run
        subprocess.run(
            ["make", "html"],
            capture_output=True,
            cwd="/home/user/docs"
        )

        filepath = f"/home/user/docs/build/{html_file}"
        with open(filepath, 'r') as f:
            content = f.read().lower()

        # Check for HTML markers - pandoc output should contain at least one of these
        has_html_marker = (
            "<html" in content or
            "<!doctype" in content or
            "<body" in content or
            "<h1" in content or
            "<p>" in content
        )
        assert has_html_marker, \
            f"HTML file {filepath} does not appear to be valid HTML output from pandoc"


class TestIdempotency:
    """Test that running 'make html' multiple times is idempotent."""

    def test_make_html_idempotent(self):
        """Verify running 'make html' twice succeeds without error."""
        # First run
        result1 = subprocess.run(
            ["make", "html"],
            capture_output=True,
            text=True,
            cwd="/home/user/docs"
        )
        assert result1.returncode == 0, \
            f"First 'make html' failed: {result1.stderr}"

        # Second run (should either do nothing or succeed)
        result2 = subprocess.run(
            ["make", "html"],
            capture_output=True,
            text=True,
            cwd="/home/user/docs"
        )
        assert result2.returncode == 0, \
            f"Second 'make html' failed (not idempotent): {result2.stderr}"


class TestSourceFilesUnchanged:
    """Test that source markdown files remain unchanged."""

    @pytest.mark.parametrize("filename", ["intro.md", "guide.md", "reference.md"])
    def test_source_file_still_exists(self, filename):
        """Verify source markdown files still exist after make html."""
        # Run make html first
        subprocess.run(
            ["make", "html"],
            capture_output=True,
            cwd="/home/user/docs"
        )

        filepath = f"/home/user/docs/src/{filename}"
        assert os.path.isfile(filepath), \
            f"Source file {filepath} no longer exists after running 'make html'"

    @pytest.mark.parametrize("filename", ["intro.md", "guide.md", "reference.md"])
    def test_source_file_has_content(self, filename):
        """Verify source markdown files still have content."""
        filepath = f"/home/user/docs/src/{filename}"
        with open(filepath, 'r') as f:
            content = f.read()
        assert len(content.strip()) > 0, \
            f"Source file {filepath} is empty"


class TestNoFilesOutsideDocsDirectory:
    """Test that no files are created outside /home/user/docs/."""

    def test_build_files_in_correct_location(self):
        """Verify HTML files are only in /home/user/docs/build/."""
        # Run make html
        subprocess.run(
            ["make", "html"],
            capture_output=True,
            cwd="/home/user/docs"
        )

        # Check that HTML files exist in build directory
        build_dir = "/home/user/docs/build"
        html_files = [f for f in os.listdir(build_dir) if f.endswith('.html')]

        expected_html = {"intro.html", "guide.html", "reference.html"}
        actual_html = set(html_files)

        assert expected_html.issubset(actual_html), \
            f"Expected HTML files {expected_html} in build/, but found {actual_html}"

    def test_no_html_in_src_directory(self):
        """Verify no HTML files are created in src/ directory."""
        src_dir = "/home/user/docs/src"
        html_files = [f for f in os.listdir(src_dir) if f.endswith('.html')]

        assert len(html_files) == 0, \
            f"HTML files should not be created in src/ directory, but found: {html_files}"

    def test_no_html_in_docs_root(self):
        """Verify no HTML files are created in docs/ root directory."""
        docs_dir = "/home/user/docs"
        html_files = [f for f in os.listdir(docs_dir) if f.endswith('.html')]

        assert len(html_files) == 0, \
            f"HTML files should not be created in docs/ root directory, but found: {html_files}"
