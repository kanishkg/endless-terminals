# test_final_state.py
"""
Tests to validate the final state after the student has fixed the Makefile
for the ETL pipeline incremental build issues.
"""

import os
import subprocess
import time
import re
import pytest

HOME = "/home/user"
ETL_DIR = os.path.join(HOME, "etl")
DATA_DIR = os.path.join(ETL_DIR, "data")
SCRIPTS_DIR = os.path.join(ETL_DIR, "scripts")
CLEAN_DIR = os.path.join(ETL_DIR, "clean")
CONFIG_DIR = os.path.join(ETL_DIR, "config")


def run_make(target="all", parallel=False, cwd=ETL_DIR, timeout=60):
    """Run make with given target and return result."""
    cmd = ["make"]
    if parallel:
        cmd.append("-j4")
    cmd.append(target)
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def get_file_mtime(filepath):
    """Get modification time of a file in seconds since epoch."""
    return os.path.getmtime(filepath)


class TestMakefileStructure:
    """Test that Makefile still has required structure."""

    def test_makefile_exists(self):
        makefile = os.path.join(ETL_DIR, "Makefile")
        assert os.path.isfile(makefile), f"Makefile {makefile} does not exist"

    def test_makefile_contains_pattern_rule(self):
        """Verify Makefile still has at least one pattern rule (%)."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        with open(makefile, 'r') as f:
            content = f.read()
        # Pattern rules contain % character in a rule context
        # Look for something like "%.csv:" or "clean/%.csv:"
        pattern_rule_regex = r'[^\s]*%[^\s]*\s*:'
        assert re.search(pattern_rule_regex, content), \
            "Makefile must still contain at least one pattern rule (%) - not just explicit targets"

    def test_makefile_has_all_target(self):
        """Verify Makefile has an 'all' target."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        with open(makefile, 'r') as f:
            content = f.read()
        assert re.search(r'^all\s*:', content, re.MULTILINE), \
            "Makefile must have an 'all' target"

    def test_makefile_has_clean_target(self):
        """Verify Makefile has a 'clean' target."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        with open(makefile, 'r') as f:
            content = f.read()
        assert re.search(r'^clean\s*:', content, re.MULTILINE), \
            "Makefile must have a 'clean' target"


class TestSourceFilesUnchanged:
    """Test that source CSV files were not modified."""

    @pytest.mark.parametrize("csv_file", [
        "sales_2023.csv",
        "sales_2024.csv",
        "inventory.csv"
    ])
    def test_source_csv_exists(self, csv_file):
        filepath = os.path.join(DATA_DIR, csv_file)
        assert os.path.isfile(filepath), f"Source CSV {filepath} must still exist"

    @pytest.mark.parametrize("csv_file", [
        "sales_2023.csv",
        "sales_2024.csv",
        "inventory.csv"
    ])
    def test_source_csv_has_content(self, csv_file):
        filepath = os.path.join(DATA_DIR, csv_file)
        with open(filepath, 'r') as f:
            lines = f.readlines()
        assert len(lines) > 100, f"Source CSV {filepath} should have ~500 rows"


class TestPythonScriptsUnchanged:
    """Test that Python scripts were not modified (bugs are in Makefile)."""

    @pytest.mark.parametrize("script", [
        "clean.py",
        "join.py",
        "summarize.py"
    ])
    def test_script_exists(self, script):
        filepath = os.path.join(SCRIPTS_DIR, script)
        assert os.path.isfile(filepath), f"Script {filepath} must still exist"


class TestBaselineBuild:
    """Test that make clean && make all succeeds."""

    def test_make_clean_succeeds(self):
        """Test that make clean runs without error."""
        result = run_make("clean")
        assert result.returncode == 0, \
            f"'make clean' failed with exit code {result.returncode}.\nstderr: {result.stderr}\nstdout: {result.stdout}"

    def test_make_all_succeeds_after_clean(self):
        """Test that make all succeeds after clean."""
        # First clean
        clean_result = run_make("clean")
        assert clean_result.returncode == 0, f"'make clean' failed: {clean_result.stderr}"

        # Then build
        result = run_make("all")
        assert result.returncode == 0, \
            f"'make all' failed with exit code {result.returncode}.\nstderr: {result.stderr}\nstdout: {result.stdout}"

    def test_summary_csv_created(self):
        """Test that summary.csv is created after build."""
        # Clean and build
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"'make all' failed: {result.stderr}"

        summary_path = os.path.join(ETL_DIR, "summary.csv")
        assert os.path.isfile(summary_path), \
            f"summary.csv was not created at {summary_path}"

    def test_joined_csv_created(self):
        """Test that joined.csv is created after build."""
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"'make all' failed: {result.stderr}"

        joined_path = os.path.join(ETL_DIR, "joined.csv")
        assert os.path.isfile(joined_path), \
            f"joined.csv was not created at {joined_path}"

    def test_clean_csvs_created(self):
        """Test that cleaned CSVs are created in clean/ directory."""
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"'make all' failed: {result.stderr}"

        assert os.path.isdir(CLEAN_DIR), f"clean/ directory should exist"
        clean_files = [f for f in os.listdir(CLEAN_DIR) if f.endswith('.csv')]
        assert len(clean_files) >= 3, \
            f"Expected at least 3 cleaned CSV files, found {len(clean_files)}: {clean_files}"


class TestIncrementalBuild:
    """Test that incremental builds work correctly."""

    def test_touch_one_source_only_rebuilds_chain(self):
        """
        After touching one source file, only that file's chain should rebuild.
        Other cleaned files should NOT be rebuilt.
        """
        # Start fresh
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"Initial 'make all' failed: {result.stderr}"

        # Wait a moment to ensure timestamp difference
        time.sleep(1.1)

        # Record timestamps of all clean files BEFORE touch
        clean_sales_2024 = os.path.join(CLEAN_DIR, "sales_2024.csv")
        clean_inventory = os.path.join(CLEAN_DIR, "inventory.csv")
        clean_sales_2023 = os.path.join(CLEAN_DIR, "sales_2023.csv")

        # Check files exist
        for f in [clean_sales_2024, clean_inventory, clean_sales_2023]:
            assert os.path.isfile(f), f"Expected {f} to exist after initial build"

        mtime_2024_before = get_file_mtime(clean_sales_2024)
        mtime_inventory_before = get_file_mtime(clean_inventory)

        # Touch only sales_2023.csv
        source_2023 = os.path.join(DATA_DIR, "sales_2023.csv")
        os.utime(source_2023, None)  # Touch the file

        # Wait to ensure timestamp difference
        time.sleep(1.1)

        # Rebuild
        result = run_make("all")
        assert result.returncode == 0, \
            f"'make all' after touch failed: {result.stderr}\nstdout: {result.stdout}"

        # Check that sales_2024.csv and inventory.csv were NOT rebuilt
        mtime_2024_after = get_file_mtime(clean_sales_2024)
        mtime_inventory_after = get_file_mtime(clean_inventory)

        assert mtime_2024_after == mtime_2024_before, \
            f"clean/sales_2024.csv was rebuilt when it shouldn't have been. " \
            f"Before: {mtime_2024_before}, After: {mtime_2024_after}"

        assert mtime_inventory_after == mtime_inventory_before, \
            f"clean/inventory.csv was rebuilt when it shouldn't have been. " \
            f"Before: {mtime_inventory_before}, After: {mtime_inventory_after}"

        # Check that sales_2023.csv WAS rebuilt (newer than the others)
        mtime_2023_after = get_file_mtime(clean_sales_2023)
        assert mtime_2023_after > mtime_2024_after, \
            f"clean/sales_2023.csv should be newer than clean/sales_2024.csv after rebuild"

    def test_no_changes_is_noop(self):
        """Running make all immediately after should be a no-op."""
        # Start fresh
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"Initial 'make all' failed: {result.stderr}"

        # Run again immediately
        result = run_make("all")
        assert result.returncode == 0, f"Second 'make all' failed: {result.stderr}"

        # Check output indicates nothing to do
        output = result.stdout.lower() + result.stderr.lower()
        # Common make messages for no-op
        noop_indicators = [
            "nothing to be done",
            "up to date",
            "is up to date"
        ]
        is_noop = any(indicator in output for indicator in noop_indicators)
        # If no output at all, that's also a no-op (some makes are silent)
        if not is_noop and result.stdout.strip() == "" and result.stderr.strip() == "":
            is_noop = True

        assert is_noop, \
            f"'make all' should be a no-op when nothing changed.\nstdout: {result.stdout}\nstderr: {result.stderr}"


class TestParallelBuild:
    """Test that parallel builds work without race conditions."""

    def test_parallel_build_succeeds_multiple_times(self):
        """make -j4 all must succeed 5 times in a row without failure."""
        for i in range(5):
            # Clean first
            clean_result = run_make("clean")
            assert clean_result.returncode == 0, \
                f"'make clean' failed on iteration {i+1}: {clean_result.stderr}"

            # Parallel build
            result = run_make("all", parallel=True)
            assert result.returncode == 0, \
                f"'make -j4 all' failed on iteration {i+1} of 5.\n" \
                f"stderr: {result.stderr}\nstdout: {result.stdout}"

            # Verify summary.csv exists and has content
            summary_path = os.path.join(ETL_DIR, "summary.csv")
            assert os.path.isfile(summary_path), \
                f"summary.csv not created on parallel build iteration {i+1}"

            with open(summary_path, 'r') as f:
                content = f.read()
            assert len(content) > 0, \
                f"summary.csv is empty on parallel build iteration {i+1}"

    def test_parallel_incremental_build(self):
        """Parallel incremental build should also work correctly."""
        # Start fresh with parallel
        run_make("clean")
        result = run_make("all", parallel=True)
        assert result.returncode == 0, f"Initial parallel build failed: {result.stderr}"

        time.sleep(1.1)

        # Touch one source
        source_2023 = os.path.join(DATA_DIR, "sales_2023.csv")
        os.utime(source_2023, None)

        # Incremental parallel rebuild
        result = run_make("all", parallel=True)
        assert result.returncode == 0, \
            f"Parallel incremental build failed: {result.stderr}\nstdout: {result.stdout}"


class TestOutputCorrectness:
    """Test that output files have correct content."""

    def test_summary_csv_has_content(self):
        """summary.csv should have meaningful content."""
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"'make all' failed: {result.stderr}"

        summary_path = os.path.join(ETL_DIR, "summary.csv")
        with open(summary_path, 'r') as f:
            lines = f.readlines()

        # Should have at least a header and some data
        assert len(lines) >= 2, \
            f"summary.csv should have at least header + data, got {len(lines)} lines"

    def test_joined_csv_has_content(self):
        """joined.csv should have content from all sources."""
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"'make all' failed: {result.stderr}"

        joined_path = os.path.join(ETL_DIR, "joined.csv")
        with open(joined_path, 'r') as f:
            lines = f.readlines()

        # Should have substantial content (joined from multiple sources)
        assert len(lines) > 100, \
            f"joined.csv should have many rows (joined data), got {len(lines)} lines"

    def test_clean_files_have_content(self):
        """Cleaned CSV files should have content."""
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"'make all' failed: {result.stderr}"

        for csv_name in ["sales_2023.csv", "sales_2024.csv", "inventory.csv"]:
            clean_path = os.path.join(CLEAN_DIR, csv_name)
            if os.path.isfile(clean_path):
                with open(clean_path, 'r') as f:
                    lines = f.readlines()
                assert len(lines) > 50, \
                    f"{clean_path} should have content, got {len(lines)} lines"


class TestTimestampVerification:
    """Detailed timestamp verification for incremental builds."""

    def test_timestamp_ordering_after_incremental(self):
        """
        After touching one source and rebuilding, verify exact timestamp ordering:
        - Untouched clean files should have older timestamps than touched one
        """
        run_make("clean")
        result = run_make("all")
        assert result.returncode == 0, f"Initial build failed: {result.stderr}"

        time.sleep(1.5)

        # Get timestamps before
        clean_files = {}
        for name in ["sales_2023.csv", "sales_2024.csv", "inventory.csv"]:
            path = os.path.join(CLEAN_DIR, name)
            if os.path.isfile(path):
                clean_files[name] = get_file_mtime(path)

        # Touch sales_2023
        source = os.path.join(DATA_DIR, "sales_2023.csv")
        os.utime(source, None)

        time.sleep(1.5)

        # Rebuild
        result = run_make("all")
        assert result.returncode == 0, f"Incremental build failed: {result.stderr}"

        # Verify timestamps
        new_mtime_2023 = get_file_mtime(os.path.join(CLEAN_DIR, "sales_2023.csv"))
        new_mtime_2024 = get_file_mtime(os.path.join(CLEAN_DIR, "sales_2024.csv"))
        new_mtime_inv = get_file_mtime(os.path.join(CLEAN_DIR, "inventory.csv"))

        # sales_2023 should be newer
        assert new_mtime_2023 > clean_files["sales_2023.csv"], \
            "clean/sales_2023.csv should have been rebuilt (newer timestamp)"

        # Others should be unchanged
        assert new_mtime_2024 == clean_files["sales_2024.csv"], \
            "clean/sales_2024.csv should NOT have been rebuilt"
        assert new_mtime_inv == clean_files["inventory.csv"], \
            "clean/inventory.csv should NOT have been rebuilt"

        # sales_2023 should be newer than the others
        assert new_mtime_2023 > new_mtime_2024, \
            "clean/sales_2023.csv should be newer than clean/sales_2024.csv"
        assert new_mtime_2023 > new_mtime_inv, \
            "clean/sales_2023.csv should be newer than clean/inventory.csv"
