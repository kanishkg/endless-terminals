# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the cleanup script fix task.
"""

import os
import subprocess
import stat
import pytest
from pathlib import Path
from datetime import datetime, timedelta


# Base paths
BUILDS_DIR = Path("/home/user/builds")
SCRIPTS_DIR = Path("/home/user/scripts")
CLEANUP_SCRIPT = SCRIPTS_DIR / "cleanup.sh"


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_builds_directory_exists(self):
        """The /home/user/builds directory must exist."""
        assert BUILDS_DIR.exists(), f"Directory {BUILDS_DIR} does not exist"
        assert BUILDS_DIR.is_dir(), f"{BUILDS_DIR} exists but is not a directory"

    def test_scripts_directory_exists(self):
        """The /home/user/scripts directory must exist."""
        assert SCRIPTS_DIR.exists(), f"Directory {SCRIPTS_DIR} does not exist"
        assert SCRIPTS_DIR.is_dir(), f"{SCRIPTS_DIR} exists but is not a directory"


class TestCleanupScript:
    """Test that the cleanup script exists and has expected properties."""

    def test_cleanup_script_exists(self):
        """The cleanup.sh script must exist."""
        assert CLEANUP_SCRIPT.exists(), f"Script {CLEANUP_SCRIPT} does not exist"
        assert CLEANUP_SCRIPT.is_file(), f"{CLEANUP_SCRIPT} exists but is not a file"

    def test_cleanup_script_is_readable(self):
        """The cleanup.sh script must be readable."""
        assert os.access(CLEANUP_SCRIPT, os.R_OK), f"Script {CLEANUP_SCRIPT} is not readable"

    def test_cleanup_script_contains_expected_buggy_code(self):
        """The cleanup.sh script should contain the buggy implementation."""
        content = CLEANUP_SCRIPT.read_text()

        # Check for shebang
        assert content.startswith("#!/bin/bash"), "Script should start with #!/bin/bash"

        # Check for find command with the expected pattern
        assert "find" in content, "Script should contain 'find' command"
        assert "*.dSYM" in content, "Script should search for *.dSYM files"
        assert "-mtime +7" in content, "Script should filter by modification time > 7 days"
        assert "xargs" in content, "Script should use xargs"
        assert "rm -rf" in content, "Script should use rm -rf"

        # Check for the buggy pattern (ipa check without proper path handling)
        assert '.dSYM}.ipa' in content or '%.dSYM}.ipa' in content, \
            "Script should contain the ipa substitution pattern"


class TestDSYMDirectories:
    """Test that all required .dSYM directories exist with proper structure."""

    DSYM_DIRS = [
        "MyApp 2.1 (build 447).dSYM",
        "MyApp 2.2 (build 512).dSYM",
        "Release-Candidate.dSYM",
        "Nightly [2024-01-15].dSYM",
        "Legacy App-v1.0.dSYM",
        "TestFlight (internal).dSYM",
    ]

    def test_all_dsym_directories_exist(self):
        """All expected .dSYM directories must exist."""
        for dsym in self.DSYM_DIRS:
            dsym_path = BUILDS_DIR / dsym
            assert dsym_path.exists(), f"dSYM directory {dsym_path} does not exist"
            assert dsym_path.is_dir(), f"{dsym_path} exists but is not a directory"

    @pytest.mark.parametrize("dsym_name", DSYM_DIRS)
    def test_dsym_has_proper_structure(self, dsym_name):
        """Each .dSYM directory should have Contents/Resources/DWARF/ structure."""
        dsym_path = BUILDS_DIR / dsym_name
        dwarf_path = dsym_path / "Contents" / "Resources" / "DWARF"

        assert dwarf_path.exists(), \
            f"dSYM {dsym_name} missing Contents/Resources/DWARF/ structure at {dwarf_path}"
        assert dwarf_path.is_dir(), \
            f"{dwarf_path} exists but is not a directory"

        # Check that there's at least one file (binary) inside DWARF
        dwarf_contents = list(dwarf_path.iterdir())
        assert len(dwarf_contents) > 0, \
            f"DWARF directory {dwarf_path} should contain at least one binary file"


class TestIPAFiles:
    """Test that the expected .ipa files exist (and expected ones don't)."""

    EXISTING_IPAS = [
        "MyApp 2.2 (build 512).ipa",
        "Legacy App-v1.0.ipa",
    ]

    NON_EXISTING_IPAS = [
        "MyApp 2.1 (build 447).ipa",
        "Release-Candidate.ipa",
        "Nightly [2024-01-15].ipa",
        "TestFlight (internal).ipa",
    ]

    @pytest.mark.parametrize("ipa_name", EXISTING_IPAS)
    def test_existing_ipa_files(self, ipa_name):
        """IPA files that should exist must be present."""
        ipa_path = BUILDS_DIR / ipa_name
        assert ipa_path.exists(), f"IPA file {ipa_path} should exist but doesn't"
        assert ipa_path.is_file(), f"{ipa_path} exists but is not a file"

    @pytest.mark.parametrize("ipa_name", NON_EXISTING_IPAS)
    def test_non_existing_ipa_files(self, ipa_name):
        """IPA files that should NOT exist must be absent."""
        ipa_path = BUILDS_DIR / ipa_name
        assert not ipa_path.exists(), \
            f"IPA file {ipa_path} should NOT exist but does"


class TestFileAges:
    """Test that files have appropriate modification times set."""

    def get_file_age_days(self, path: Path) -> float:
        """Get the age of a file in days."""
        mtime = path.stat().st_mtime
        age_seconds = datetime.now().timestamp() - mtime
        return age_seconds / (24 * 60 * 60)

    def test_old_dsym_without_ipa_is_old_enough(self):
        """MyApp 2.1 (build 447).dSYM should be older than 7 days."""
        dsym_path = BUILDS_DIR / "MyApp 2.1 (build 447).dSYM"
        age = self.get_file_age_days(dsym_path)
        assert age > 7, \
            f"MyApp 2.1 (build 447).dSYM should be >7 days old, but is {age:.1f} days old"

    def test_old_dsym_with_ipa_is_old_enough(self):
        """MyApp 2.2 (build 512).dSYM should be older than 7 days."""
        dsym_path = BUILDS_DIR / "MyApp 2.2 (build 512).dSYM"
        age = self.get_file_age_days(dsym_path)
        assert age > 7, \
            f"MyApp 2.2 (build 512).dSYM should be >7 days old, but is {age:.1f} days old"

    def test_release_candidate_is_old_enough(self):
        """Release-Candidate.dSYM should be older than 7 days."""
        dsym_path = BUILDS_DIR / "Release-Candidate.dSYM"
        age = self.get_file_age_days(dsym_path)
        assert age > 7, \
            f"Release-Candidate.dSYM should be >7 days old, but is {age:.1f} days old"

    def test_nightly_is_young_enough(self):
        """Nightly [2024-01-15].dSYM should be younger than 7 days."""
        dsym_path = BUILDS_DIR / "Nightly [2024-01-15].dSYM"
        age = self.get_file_age_days(dsym_path)
        assert age < 7, \
            f"Nightly [2024-01-15].dSYM should be <7 days old, but is {age:.1f} days old"

    def test_legacy_app_is_old_enough(self):
        """Legacy App-v1.0.dSYM should be older than 7 days."""
        dsym_path = BUILDS_DIR / "Legacy App-v1.0.dSYM"
        age = self.get_file_age_days(dsym_path)
        assert age > 7, \
            f"Legacy App-v1.0.dSYM should be >7 days old, but is {age:.1f} days old"

    def test_testflight_is_old_enough(self):
        """TestFlight (internal).dSYM should be older than 7 days."""
        dsym_path = BUILDS_DIR / "TestFlight (internal).dSYM"
        age = self.get_file_age_days(dsym_path)
        assert age > 7, \
            f"TestFlight (internal).dSYM should be >7 days old, but is {age:.1f} days old"


class TestFilenamesWithSpecialCharacters:
    """Verify that test files have the expected special characters in names."""

    def test_files_with_spaces_exist(self):
        """Files with spaces in names must exist."""
        space_files = [
            BUILDS_DIR / "MyApp 2.1 (build 447).dSYM",
            BUILDS_DIR / "MyApp 2.2 (build 512).dSYM",
            BUILDS_DIR / "MyApp 2.2 (build 512).ipa",
            BUILDS_DIR / "Legacy App-v1.0.dSYM",
            BUILDS_DIR / "Legacy App-v1.0.ipa",
            BUILDS_DIR / "TestFlight (internal).dSYM",
        ]
        for f in space_files:
            assert f.exists(), f"File with spaces {f} must exist"

    def test_files_with_parentheses_exist(self):
        """Files with parentheses in names must exist."""
        paren_files = [
            BUILDS_DIR / "MyApp 2.1 (build 447).dSYM",
            BUILDS_DIR / "MyApp 2.2 (build 512).dSYM",
            BUILDS_DIR / "TestFlight (internal).dSYM",
        ]
        for f in paren_files:
            assert f.exists(), f"File with parentheses {f} must exist"

    def test_files_with_brackets_exist(self):
        """Files with square brackets in names must exist."""
        bracket_files = [
            BUILDS_DIR / "Nightly [2024-01-15].dSYM",
        ]
        for f in bracket_files:
            assert f.exists(), f"File with brackets {f} must exist"


class TestDirectoryPermissions:
    """Test that directories are writable for the cleanup operation."""

    def test_builds_directory_is_writable(self):
        """The builds directory must be writable."""
        assert os.access(BUILDS_DIR, os.W_OK), \
            f"Directory {BUILDS_DIR} is not writable"

    def test_scripts_directory_is_writable(self):
        """The scripts directory must be writable."""
        assert os.access(SCRIPTS_DIR, os.W_OK), \
            f"Directory {SCRIPTS_DIR} is not writable"


class TestNoHardcodedFilenames:
    """Verify the script doesn't already have hardcoded filenames (anti-shortcut)."""

    def test_script_has_no_hardcoded_deletions(self):
        """Script should not have hardcoded specific filenames to delete."""
        result = subprocess.run(
            ["grep", "-c", r"rm.*MyApp\|rm.*Release\|rm.*TestFlight", str(CLEANUP_SCRIPT)],
            capture_output=True,
            text=True
        )
        # grep -c returns the count; if files are hardcoded, count > 0
        # grep returns exit code 1 if no matches (count=0), which is what we want
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert count == 0, \
            f"Script appears to have hardcoded filenames for deletion (found {count} matches)"
