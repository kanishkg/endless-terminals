# test_final_state.py
"""
Tests to validate the final state after the student fixes the Makefile parallel build issue.
"""

import os
import subprocess
import pytest
import tarfile
import tempfile

HOME = "/home/user"
PROJECT = os.path.join(HOME, "project")


class TestProjectStructurePreserved:
    """Test that the project directory structure is preserved."""

    def test_project_directory_exists(self):
        assert os.path.isdir(PROJECT), f"Project directory {PROJECT} does not exist"

    def test_makefile_exists(self):
        makefile = os.path.join(PROJECT, "Makefile")
        assert os.path.isfile(makefile), f"Makefile does not exist at {makefile}"

    def test_src_directory_exists(self):
        src_dir = os.path.join(PROJECT, "src")
        assert os.path.isdir(src_dir), f"Source directory {src_dir} does not exist"

    def test_include_directory_exists(self):
        include_dir = os.path.join(PROJECT, "include")
        assert os.path.isdir(include_dir), f"Include directory {include_dir} does not exist"

    def test_docs_directory_exists(self):
        docs_dir = os.path.join(PROJECT, "docs")
        assert os.path.isdir(docs_dir), f"Docs directory {docs_dir} does not exist"


class TestSourceFilesPreserved:
    """Test that source files are unchanged."""

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


class TestMakefileStructurePreserved:
    """Test that the Makefile maintains required structure."""

    def test_makefile_has_phony_declaration(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert ".PHONY:" in content, "Makefile should contain .PHONY declaration"

    def test_makefile_has_all_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "all:" in content or "all :" in content, "Makefile should contain 'all' target"

    def test_makefile_has_lib_phony_target(self):
        """lib must remain a usable phony target."""
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        # Check that lib is declared as phony
        assert "lib" in content, "Makefile should reference 'lib' target"
        # Verify lib is in .PHONY
        for line in content.split('\n'):
            if line.strip().startswith('.PHONY'):
                assert 'lib' in line, "lib should be declared as .PHONY"
                break

    def test_makefile_has_app_phony_target(self):
        """app must remain a usable phony target."""
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "app" in content, "Makefile should reference 'app' target"
        # Verify app is in .PHONY
        for line in content.split('\n'):
            if line.strip().startswith('.PHONY'):
                assert 'app' in line, "app should be declared as .PHONY"
                break

    def test_makefile_has_docs_phony_target(self):
        """docs must remain a usable phony target."""
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "docs" in content, "Makefile should reference 'docs' target"
        # Verify docs is in .PHONY
        for line in content.split('\n'):
            if line.strip().startswith('.PHONY'):
                assert 'docs' in line, "docs should be declared as .PHONY"
                break

    def test_makefile_has_clean_target(self):
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert "clean:" in content or "clean :" in content, "Makefile should contain 'clean' target"


class TestAntiShortcutGuards:
    """Ensure the student didn't use forbidden shortcuts."""

    def test_no_notparallel(self):
        """Cannot use .NOTPARALLEL to disable parallel builds."""
        makefile = os.path.join(PROJECT, "Makefile")
        with open(makefile, "r") as f:
            content = f.read()
        assert ".NOTPARALLEL" not in content, \
            "Cannot use .NOTPARALLEL - the Makefile must support parallel builds"

    def test_phony_targets_still_usable(self):
        """Verify that lib, app, docs can be built individually."""
        # Clean first
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)

        # Build lib alone
        result = subprocess.run(["make", "lib"], cwd=PROJECT, capture_output=True, text=True)
        assert result.returncode == 0, f"'make lib' should work: {result.stderr}"
        assert os.path.isfile(os.path.join(PROJECT, "lib", "libfoo.a")), \
            "'make lib' should create lib/libfoo.a"

        # Build app alone (lib already built)
        result = subprocess.run(["make", "app"], cwd=PROJECT, capture_output=True, text=True)
        assert result.returncode == 0, f"'make app' should work: {result.stderr}"
        assert os.path.isfile(os.path.join(PROJECT, "bin", "app")), \
            "'make app' should create bin/app"

        # Build docs alone
        result = subprocess.run(["make", "docs"], cwd=PROJECT, capture_output=True, text=True)
        assert result.returncode == 0, f"'make docs' should work: {result.stderr}"
        assert os.path.isfile(os.path.join(PROJECT, "docs", "manual.html")), \
            "'make docs' should create docs/manual.html"

        # Clean up
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)


class TestSequentialBuildStillWorks:
    """Test that sequential build still works."""

    def test_sequential_make_all_succeeds(self):
        """Verify that 'make all' (sequential) still works correctly."""
        # Clean
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)

        # Build sequentially
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

        # Clean up
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)


class TestParallelBuildReliability:
    """Test that parallel build now works reliably."""

    @pytest.mark.parametrize("iteration", range(10))
    def test_parallel_make_all_succeeds(self, iteration):
        """Run 'make -j4 all' 10 times - all must succeed."""
        # Clean
        clean_result = subprocess.run(
            ["make", "clean"],
            cwd=PROJECT,
            capture_output=True,
            text=True
        )

        # Build in parallel
        build_result = subprocess.run(
            ["make", "-j4", "all"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=60  # Prevent infinite hangs
        )

        assert build_result.returncode == 0, (
            f"Parallel 'make -j4 all' failed on iteration {iteration + 1}/10:\n"
            f"stdout: {build_result.stdout}\n"
            f"stderr: {build_result.stderr}"
        )

        # Verify all outputs exist
        libfoo_path = os.path.join(PROJECT, "lib", "libfoo.a")
        app_path = os.path.join(PROJECT, "bin", "app")
        manual_path = os.path.join(PROJECT, "docs", "manual.html")

        assert os.path.isfile(libfoo_path), \
            f"lib/libfoo.a missing after parallel build iteration {iteration + 1}"
        assert os.path.isfile(app_path), \
            f"bin/app missing after parallel build iteration {iteration + 1}"
        assert os.path.isfile(manual_path), \
            f"docs/manual.html missing after parallel build iteration {iteration + 1}"


class TestBuildArtifactsCorrect:
    """Test that build artifacts are correct."""

    @pytest.fixture(autouse=True)
    def setup_build(self):
        """Build before testing artifacts."""
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)
        result = subprocess.run(
            ["make", "-j4", "all"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"
        yield
        # Don't clean up - leave artifacts for inspection if needed

    def test_libfoo_is_valid_archive(self):
        """lib/libfoo.a should be a valid ar archive containing foo.o and bar.o."""
        libfoo_path = os.path.join(PROJECT, "lib", "libfoo.a")
        assert os.path.isfile(libfoo_path), "lib/libfoo.a does not exist"

        # Check it's a valid ar archive and contains expected members
        result = subprocess.run(
            ["ar", "-t", libfoo_path],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"lib/libfoo.a is not a valid ar archive: {result.stderr}"

        members = result.stdout.strip().split('\n')
        assert "foo.o" in members, "lib/libfoo.a should contain foo.o"
        assert "bar.o" in members, "lib/libfoo.a should contain bar.o"

    def test_app_is_executable(self):
        """bin/app should exist and be executable."""
        app_path = os.path.join(PROJECT, "bin", "app")
        assert os.path.isfile(app_path), "bin/app does not exist"
        assert os.access(app_path, os.X_OK), "bin/app is not executable"

    def test_app_runs_without_library_errors(self):
        """bin/app should run without 'library not found' errors."""
        app_path = os.path.join(PROJECT, "bin", "app")

        # Try to run the app - it might do anything, but shouldn't fail with library errors
        result = subprocess.run(
            [app_path],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=PROJECT
        )

        # Check stderr doesn't contain library-related errors
        stderr_lower = result.stderr.lower()
        assert "library not found" not in stderr_lower, \
            f"bin/app has library errors: {result.stderr}"
        assert "cannot open shared object" not in stderr_lower, \
            f"bin/app has shared library errors: {result.stderr}"
        assert "undefined symbol" not in stderr_lower, \
            f"bin/app has undefined symbol errors: {result.stderr}"

    def test_manual_html_exists_and_is_html(self):
        """docs/manual.html should exist and be valid HTML."""
        manual_path = os.path.join(PROJECT, "docs", "manual.html")
        assert os.path.isfile(manual_path), "docs/manual.html does not exist"

        with open(manual_path, "r") as f:
            content = f.read()

        # Basic HTML validation - should contain HTML-like content
        content_lower = content.lower()
        assert "<html" in content_lower or "<!doctype" in content_lower or "<body" in content_lower or "<p>" in content_lower, \
            "docs/manual.html does not appear to be valid HTML"


class TestBuildOutputsIdentical:
    """Test that parallel and sequential builds produce identical outputs."""

    def test_outputs_match_between_parallel_and_sequential(self):
        """Build artifacts should be the same between parallel and sequential builds."""
        # Do a sequential build
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)
        seq_result = subprocess.run(
            ["make", "all"],
            cwd=PROJECT,
            capture_output=True,
            text=True
        )
        assert seq_result.returncode == 0, f"Sequential build failed: {seq_result.stderr}"

        # Get sequential build artifact info
        seq_lib_members = subprocess.run(
            ["ar", "-t", os.path.join(PROJECT, "lib", "libfoo.a")],
            capture_output=True,
            text=True
        ).stdout.strip().split('\n')

        with open(os.path.join(PROJECT, "docs", "manual.html"), "r") as f:
            seq_html = f.read()

        # Do a parallel build
        subprocess.run(["make", "clean"], cwd=PROJECT, capture_output=True)
        par_result = subprocess.run(
            ["make", "-j4", "all"],
            cwd=PROJECT,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert par_result.returncode == 0, f"Parallel build failed: {par_result.stderr}"

        # Get parallel build artifact info
        par_lib_members = subprocess.run(
            ["ar", "-t", os.path.join(PROJECT, "lib", "libfoo.a")],
            capture_output=True,
            text=True
        ).stdout.strip().split('\n')

        with open(os.path.join(PROJECT, "docs", "manual.html"), "r") as f:
            par_html = f.read()

        # Compare
        assert set(seq_lib_members) == set(par_lib_members), \
            "lib/libfoo.a contents differ between sequential and parallel builds"
        assert seq_html == par_html, \
            "docs/manual.html differs between sequential and parallel builds"

        # Both should have produced working executables
        assert os.path.isfile(os.path.join(PROJECT, "bin", "app")), \
            "bin/app missing after parallel build"
