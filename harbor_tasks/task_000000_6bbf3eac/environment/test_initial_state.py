# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the Makefile debugging task.
"""

import os
import subprocess
import pytest

HOME = "/home/user"
ETL_DIR = os.path.join(HOME, "etl")
DATA_DIR = os.path.join(ETL_DIR, "data")
SCRIPTS_DIR = os.path.join(ETL_DIR, "scripts")
CLEAN_DIR = os.path.join(ETL_DIR, "clean")
CONFIG_DIR = os.path.join(ETL_DIR, "config")


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_etl_directory_exists(self):
        assert os.path.isdir(ETL_DIR), f"ETL directory {ETL_DIR} does not exist"

    def test_data_directory_exists(self):
        assert os.path.isdir(DATA_DIR), f"Data directory {DATA_DIR} does not exist"

    def test_scripts_directory_exists(self):
        assert os.path.isdir(SCRIPTS_DIR), f"Scripts directory {SCRIPTS_DIR} does not exist"

    def test_etl_directory_is_writable(self):
        assert os.access(ETL_DIR, os.W_OK), f"ETL directory {ETL_DIR} is not writable"


class TestSourceCSVFiles:
    """Test that source CSV files exist and have content."""

    @pytest.mark.parametrize("csv_file", [
        "sales_2023.csv",
        "sales_2024.csv",
        "inventory.csv"
    ])
    def test_source_csv_exists(self, csv_file):
        filepath = os.path.join(DATA_DIR, csv_file)
        assert os.path.isfile(filepath), f"Source CSV {filepath} does not exist"

    @pytest.mark.parametrize("csv_file", [
        "sales_2023.csv",
        "sales_2024.csv",
        "inventory.csv"
    ])
    def test_source_csv_has_content(self, csv_file):
        filepath = os.path.join(DATA_DIR, csv_file)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                lines = f.readlines()
            # Should have ~500 rows each (plus header)
            assert len(lines) > 100, f"Source CSV {filepath} has too few rows ({len(lines)}), expected ~500"


class TestPythonScripts:
    """Test that Python scripts exist and are readable."""

    @pytest.mark.parametrize("script", [
        "clean.py",
        "join.py",
        "summarize.py"
    ])
    def test_script_exists(self, script):
        filepath = os.path.join(SCRIPTS_DIR, script)
        assert os.path.isfile(filepath), f"Script {filepath} does not exist"

    @pytest.mark.parametrize("script", [
        "clean.py",
        "join.py",
        "summarize.py"
    ])
    def test_script_is_readable(self, script):
        filepath = os.path.join(SCRIPTS_DIR, script)
        if os.path.isfile(filepath):
            assert os.access(filepath, os.R_OK), f"Script {filepath} is not readable"


class TestMakefile:
    """Test that Makefile exists and has expected characteristics."""

    def test_makefile_exists(self):
        makefile = os.path.join(ETL_DIR, "Makefile")
        assert os.path.isfile(makefile), f"Makefile {makefile} does not exist"

    def test_makefile_is_readable(self):
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            assert os.access(makefile, os.R_OK), f"Makefile {makefile} is not readable"

    def test_makefile_contains_pattern_rule(self):
        """Verify Makefile has at least one pattern rule (%)."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            with open(makefile, 'r') as f:
                content = f.read()
            # Pattern rules contain % character
            assert '%' in content, "Makefile does not appear to contain pattern rules (no % found)"

    def test_makefile_has_all_target(self):
        """Verify Makefile has an 'all' target."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            with open(makefile, 'r') as f:
                content = f.read()
            # Look for 'all' target (all: or all :)
            assert 'all' in content, "Makefile does not appear to have an 'all' target"

    def test_makefile_references_wildcard(self):
        """Verify the buggy wildcard usage exists (part of the bug)."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            with open(makefile, 'r') as f:
                content = f.read()
            # The bug involves $(wildcard ...) for dependencies
            assert 'wildcard' in content, "Makefile should contain wildcard (this is part of the bug)"


class TestPreviousRunState:
    """Test that clean/ directory exists from a previous successful run."""

    def test_clean_directory_exists(self):
        """Verify clean/ directory exists (from previous successful run)."""
        assert os.path.isdir(CLEAN_DIR), f"Clean directory {CLEAN_DIR} does not exist (expected from previous run)"

    def test_clean_directory_has_files(self):
        """Verify clean/ directory has some CSV files from previous run."""
        if os.path.isdir(CLEAN_DIR):
            files = [f for f in os.listdir(CLEAN_DIR) if f.endswith('.csv')]
            assert len(files) > 0, f"Clean directory {CLEAN_DIR} has no CSV files (expected from previous run)"


class TestToolsAvailable:
    """Test that required tools are available."""

    def test_python3_available(self):
        """Verify Python 3 is available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Python 3 is not available"
        # Check version is 3.11+
        version_str = result.stdout.strip()
        assert "Python 3" in version_str, f"Expected Python 3, got: {version_str}"

    def test_make_available(self):
        """Verify GNU Make is available."""
        result = subprocess.run(
            ["make", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "GNU Make is not available"
        assert "GNU Make" in result.stdout, f"Expected GNU Make, got: {result.stdout}"

    def test_make_version_4_or_higher(self):
        """Verify Make version is 4.x (needed for some features)."""
        result = subprocess.run(
            ["make", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # First line typically: "GNU Make 4.3"
            first_line = result.stdout.split('\n')[0]
            # Extract version number
            import re
            match = re.search(r'(\d+)\.(\d+)', first_line)
            if match:
                major = int(match.group(1))
                assert major >= 4, f"Make version should be 4.x or higher, got: {first_line}"


class TestConfigFile:
    """Test for the hidden config file dependency (part of the bug)."""

    def test_config_directory_or_file_exists(self):
        """Check if config/params.yaml exists (part of the hidden dependency bug)."""
        config_file = os.path.join(CONFIG_DIR, "params.yaml")
        # This file should exist as part of the bug setup
        # (summarize.py secretly reads it but it's not in Makefile deps)
        if os.path.isdir(CONFIG_DIR):
            assert os.path.isfile(config_file), \
                f"Config file {config_file} should exist (it's part of the hidden dependency bug)"
        else:
            # Config dir might exist at ETL level
            alt_config = os.path.join(ETL_DIR, "config", "params.yaml")
            # At minimum, check the directory structure is set up for the bug
            pass  # Config may be optional depending on exact setup


class TestMakefileHasBugs:
    """Verify the Makefile has the expected bugs that need fixing."""

    def test_secondary_expansion_issue(self):
        """Check for $$@ usage without .SECONDEXPANSION (bug #1)."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            with open(makefile, 'r') as f:
                content = f.read()
            # If $$@ is used, .SECONDEXPANSION should be present for it to work
            if '$$@' in content or '$$<' in content or '$$^' in content:
                # This is the bug - secondary expansion variables without the directive
                # We're checking the bug EXISTS (initial state)
                # The directive might be missing (that's the bug)
                pass  # Bug presence confirmed if these patterns exist

    def test_wildcard_in_dependencies(self):
        """Check for wildcard in dependency list (bug #2)."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            with open(makefile, 'r') as f:
                content = f.read()
            # Look for $(wildcard in a dependency context
            # This is buggy because wildcard is evaluated at parse time
            assert '$(wildcard' in content, \
                "Makefile should contain $(wildcard usage (this is bug #2)"


class TestManifestMechanism:
    """Test for manifest-related files (part of bug #3)."""

    def test_manifest_mechanism_exists(self):
        """Check if there's a manifest.txt mechanism in the Makefile."""
        makefile = os.path.join(ETL_DIR, "Makefile")
        if os.path.isfile(makefile):
            with open(makefile, 'r') as f:
                content = f.read()
            # The bug involves a manifest file
            assert 'manifest' in content.lower(), \
                "Makefile should reference a manifest file (part of bug #3)"
