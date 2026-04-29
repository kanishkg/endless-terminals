# test_initial_state.py
"""
Tests to validate the initial state before the student fixes the Makefile parallel build issue.
"""

import os
import subprocess
import pytest

HOME = "/home/user"
PROJECT = os.path.join(HOME, "project")


class TestProjectStructure:
    """Test that the project directory structure exists."""

    def test_project_directory_exists(self):
        assert os.path.isdir(PROJECT), f"Project directory {PROJECT} does not exist"

    def test_makefile_exists(self):
        makefile = os.path.join(PROJECT, "Makefile")
        assert os.path.isfile(makefile), f"Makefile does not exist at {makefile}"

    def test_makefile_is_writable(self):
        makefile = os.path.join(PROJECT, "Makefile")
        assert os.access(makefile, os.W_OK), f"Makefile at {makefile} is not writable"

    def test_src_directory_exists(self):
        src_dir = os.path.join(PROJECT, "src")
        assert os.path.isdir(src_dir), f"Source directory {src_dir} does not exist"

    def test_include_directory_exists(self):
        include_dir = os.path.join(PROJECT, "include")
        assert os.path.isdir(include_dir), f"Include directory {include_dir} does not exist"

    def test_docs_directory_exists(self):
        docs_dir = os.path.join(PROJECT, "docs")
        assert os.path.isdir(docs_dir), f"Docs directory {docs_dir} does not exist"


class TestSourceFiles:
    """Test that required source files exist."""

    def test_foo_c_exists(self):
        foo_c = os.path.join(PROJECT, "src", "foo.c")
        assert os.path.isfile(foo_c), f"Source file {foo_c} does not exist"

    def test_bar_c_exists(self):
        bar_c = os.path.join(PROJECT, "src", "bar.c")
        assert os.path.isfile(bar_c), f"Source file {bar_c} does not exist"

    def test_main_c_exists(self):
        main_c = os.path.join(PROJECT, "src", "main.c")
        assert os.path.isfile(main_c), f"Source file {main_c} does not exist"

    def test_foo_h_exists(self):
        foo_h = os.path.join(PROJECT, "include", "foo.h")
        assert os.path.isfile(foo_h), f"Header file {foo_h} does not exist"

    def test_manual_md_exists(self):
        manual_md = os.path.join(PROJECT, "docs", "manual.md")
        assert os.path.isfile(manual_md), f"Documentation source {manual_md} does not exist"


class TestRequiredTools:
    """Test that required build tools are installed."""

    def test_gcc_installed(self):
        result = subprocess.run(["which", "gcc"], capture_output=True)
        assert result.returncode == 0, "gcc is not installed or not in PATH"

    def test_ar_installed(self):
        result = subprocess.run(["which", "ar"], capture_output=True)
        assert result.returncode == 0, "ar is not installed or not in PATH"

    def test_pandoc_installed(self):
        result = subprocess.run(["which", "pandoc"], capture_output=True)
        assert result.returncode == 0, "pandoc is not installed or not in PATH"

    def test_make_installed(self):
        result = subprocess.run(["which", "make"], capture_output=True)
        assert result.returncode == 0, "make is not installed or not in PATH"


class TestMakefileContent:
    """Test that the Makefile has the expected structure with the bug."""

    def test_makefile_has_phony_declaration(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert ".PHONY:" in content, "Makefile should contain .PHONY declaration"

    def test_makefile_has_all_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "all:" in content, "Makefile should contain 'all' target"

    def test_makefile_has_lib_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "lib:" in content, "Makefile should contain 'lib' target"

    def test_makefile_has_app_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "app:" in content, "Makefile should contain 'app' target"

    def test_makefile_has_docs_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "docs:" in content, "Makefile should contain 'docs' target"

    def test_makefile_has_clean_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "clean:" in content, "Makefile should contain 'clean' target"

    def test_makefile_has_libfoo_a_rule(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "lib/libfoo.a:" in content, "Makefile should contain rule for lib/libfoo.a"

    def test_makefile_has_bin_app_rule(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "bin/app:" in content, "Makefile should contain rule for bin/app"

    def test_makefile_has_manual_html_rule(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "docs/manual.html:" in content, "Makefile should contain rule for docs/manual.html"

    def test_makefile_does_not_have_notparallel(self):
        """Ensure .NOTPARALLEL is not already in the Makefile (that would be cheating)."""
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        # It's okay if it's not there initially, but we're checking initial state
        # The anti-shortcut guard will be in the final state test


class TestSequentialBuildWorks:
    """Test that sequential build works (as stated in the problem)."""

    def test_sequential_make_all_succeeds(self):
        """Verify that 'make all' (sequential) works correctly."""
        # First clean
        clean_result = subprocess.run(
            ["make", "clean"],
            cwd=PROJECT,
            capture_output=True,
            text=True
        )
        # Clean might fail if nothing to clean, that's okay

        # Then build sequentially
        build_result = subprocess.run(
            ["make", "all"],
            cwd=PROJECT,
            capture_output=True,
            text=True
        )
        assert build_result.returncode == 0, (
            f"Sequential 'make all' should succeed but failed with:\n"
            f"stdout: {build_result.stdout}\n"
            f"stderr: {build_result.stderr}"
        )

        # Verify outputs exist
        assert os.path.isfile(os.path.join(PROJECT, "lib", "libfoo.a")), \
            "lib/libfoo.a should exist after sequential build"
        assert os.path.isfile(os.path.join(PROJECT, "bin", "app")), \
            "bin/app should exist after sequential build"
        assert os.path.isfile(os.path.join(PROJECT, "docs", "manual.html")), \
            "docs/manual.html should exist after sequential build"

        # Clean up for the student
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)


class TestExplicitParallelBuildWorks:
    """Test that explicit parallel build works (as stated in the problem)."""

    def test_explicit_parallel_build_succeeds(self):
        """Verify that 'make -j4 lib app docs' works correctly."""
        # First clean
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)

        # Then build with explicit targets
        build_result = subprocess.run(
            ["make", "-j4", "lib", "app", "docs"],
            cwd=PROJECT,
            capture_output=True,
            text=True
        )
        assert build_result.returncode == 0, (
            f"Explicit 'make -j4 lib app docs' should succeed but failed with:\n"
            f"stdout: {build_result.stdout}\n"
            f"stderr: {build_result.stderr}"
        )

        # Clean up for the student
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)
