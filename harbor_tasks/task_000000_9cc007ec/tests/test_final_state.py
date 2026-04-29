# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has fixed the cleanup script to correctly delete old .dSYM directories
that don't have matching .ipa files.
"""

import os
import subprocess
import pytest
from pathlib import Path
from datetime import datetime


# Base paths
BUILDS_DIR = Path("/home/user/builds")
SCRIPTS_DIR = Path("/home/user/scripts")
CLEANUP_SCRIPT = SCRIPTS_DIR / "cleanup.sh"


class TestCleanupScriptExecution:
    """Test that the cleanup script runs successfully."""

    def test_cleanup_script_exists(self):
        """The cleanup.sh script must still exist."""
        assert CLEANUP_SCRIPT.exists(), f"Script {CLEANUP_SCRIPT} does not exist"
        assert CLEANUP_SCRIPT.is_file(), f"{CLEANUP_SCRIPT} exists but is not a file"

    def test_cleanup_script_exits_zero(self):
        """Running the cleanup script should exit with code 0."""
        result = subprocess.run(
            ["bash", str(CLEANUP_SCRIPT)],
            capture_output=True,
            text=True,
            cwd=str(BUILDS_DIR)
        )
        assert result.returncode == 0, \
            f"Cleanup script exited with code {result.returncode}. " \
            f"stdout: {result.stdout}\nstderr: {result.stderr}"


class TestDeletedDSYMDirectories:
    """Test that the correct .dSYM directories have been deleted."""

    SHOULD_BE_DELETED = [
        "MyApp 2.1 (build 447).dSYM",
        "Release-Candidate.dSYM",
        "TestFlight (internal).dSYM",
    ]

    @pytest.mark.parametrize("dsym_name", SHOULD_BE_DELETED)
    def test_old_dsym_without_ipa_is_deleted(self, dsym_name):
        """Old .dSYM directories without matching .ipa files should be deleted."""
        dsym_path = BUILDS_DIR / dsym_name
        assert not dsym_path.exists(), \
            f"dSYM directory {dsym_path} should have been DELETED but still exists. " \
            f"This directory is older than 7 days and has no matching .ipa file."


class TestPreservedDSYMDirectories:
    """Test that the correct .dSYM directories have been preserved."""

    SHOULD_EXIST = [
        ("MyApp 2.2 (build 512).dSYM", "has a matching .ipa file"),
        ("Nightly [2024-01-15].dSYM", "is younger than 7 days"),
        ("Legacy App-v1.0.dSYM", "has a matching .ipa file"),
    ]

    @pytest.mark.parametrize("dsym_name,reason", SHOULD_EXIST)
    def test_dsym_that_should_be_kept_exists(self, dsym_name, reason):
        """dSYM directories that should be preserved must still exist."""
        dsym_path = BUILDS_DIR / dsym_name
        assert dsym_path.exists(), \
            f"dSYM directory {dsym_path} should NOT have been deleted because it {reason}."
        assert dsym_path.is_dir(), \
            f"{dsym_path} exists but is not a directory"


class TestPreservedIPAFiles:
    """Test that all .ipa files are preserved (never deleted)."""

    EXISTING_IPAS = [
        "MyApp 2.2 (build 512).ipa",
        "Legacy App-v1.0.ipa",
    ]

    @pytest.mark.parametrize("ipa_name", EXISTING_IPAS)
    def test_ipa_files_are_preserved(self, ipa_name):
        """All .ipa files that existed before must still exist."""
        ipa_path = BUILDS_DIR / ipa_name
        assert ipa_path.exists(), \
            f"IPA file {ipa_path} should still exist but was deleted. " \
            f"The cleanup script should NEVER delete .ipa files."
        assert ipa_path.is_file(), \
            f"{ipa_path} exists but is not a file"


class TestPreservedDSYMStructure:
    """Test that preserved .dSYM directories still have proper internal structure."""

    PRESERVED_DSYMS = [
        "MyApp 2.2 (build 512).dSYM",
        "Nightly [2024-01-15].dSYM",
        "Legacy App-v1.0.dSYM",
    ]

    @pytest.mark.parametrize("dsym_name", PRESERVED_DSYMS)
    def test_preserved_dsym_has_proper_structure(self, dsym_name):
        """Preserved .dSYM directories should still have Contents/Resources/DWARF/ structure."""
        dsym_path = BUILDS_DIR / dsym_name
        if not dsym_path.exists():
            pytest.skip(f"{dsym_name} doesn't exist (tested elsewhere)")

        dwarf_path = dsym_path / "Contents" / "Resources" / "DWARF"
        assert dwarf_path.exists(), \
            f"Preserved dSYM {dsym_name} is missing Contents/Resources/DWARF/ structure"
        assert dwarf_path.is_dir(), \
            f"{dwarf_path} exists but is not a directory"


class TestNoHardcodedFilenames:
    """Verify the script doesn't have hardcoded filenames (anti-shortcut guard)."""

    def test_script_has_no_hardcoded_deletions(self):
        """Script should not have hardcoded specific filenames to delete."""
        result = subprocess.run(
            ["grep", "-cE", r"rm.*MyApp|rm.*Release|rm.*TestFlight", str(CLEANUP_SCRIPT)],
            capture_output=True,
            text=True
        )
        # grep -c returns the count; if files are hardcoded, count > 0
        # grep returns exit code 1 if no matches (count=0), which is what we want
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        assert count == 0, \
            f"Script appears to have hardcoded filenames for deletion (found {count} matches). " \
            f"The script must handle the general case, not hardcode specific files."

    def test_script_still_uses_find(self):
        """Script should still use find command for the general case."""
        content = CLEANUP_SCRIPT.read_text()
        assert "find" in content, \
            "Script must still use 'find' command to locate .dSYM directories"


class TestScriptHandlesSpecialCharacters:
    """Test that the script correctly handles filenames with special characters."""

    def test_spaces_handled_correctly(self):
        """Files with spaces should be handled correctly."""
        # MyApp 2.2 (build 512).dSYM has spaces and should be preserved
        dsym_path = BUILDS_DIR / "MyApp 2.2 (build 512).dSYM"
        assert dsym_path.exists(), \
            "Script failed to correctly handle filename with spaces - " \
            "'MyApp 2.2 (build 512).dSYM' was incorrectly deleted"

    def test_parentheses_handled_correctly(self):
        """Files with parentheses should be handled correctly."""
        # MyApp 2.2 (build 512).dSYM has parentheses and should be preserved
        dsym_path = BUILDS_DIR / "MyApp 2.2 (build 512).dSYM"
        assert dsym_path.exists(), \
            "Script failed to correctly handle filename with parentheses - " \
            "'MyApp 2.2 (build 512).dSYM' was incorrectly deleted"

    def test_brackets_handled_correctly(self):
        """Files with square brackets should be handled correctly."""
        # Nightly [2024-01-15].dSYM has brackets and should be preserved (too young)
        dsym_path = BUILDS_DIR / "Nightly [2024-01-15].dSYM"
        assert dsym_path.exists(), \
            "Script failed to correctly handle filename with brackets - " \
            "'Nightly [2024-01-15].dSYM' was incorrectly deleted"


class TestRerunIdempotency:
    """Test that running the script again doesn't cause errors or delete more files."""

    def test_script_can_run_again_safely(self):
        """Running the cleanup script a second time should still exit 0."""
        # First run (may have already happened)
        result1 = subprocess.run(
            ["bash", str(CLEANUP_SCRIPT)],
            capture_output=True,
            text=True
        )

        # Second run - should be idempotent
        result2 = subprocess.run(
            ["bash", str(CLEANUP_SCRIPT)],
            capture_output=True,
            text=True
        )
        assert result2.returncode == 0, \
            f"Cleanup script failed on second run with code {result2.returncode}. " \
            f"Script should be idempotent. stderr: {result2.stderr}"

    def test_preserved_files_still_exist_after_rerun(self):
        """After running script twice, preserved files should still exist."""
        # Run script again
        subprocess.run(["bash", str(CLEANUP_SCRIPT)], capture_output=True)

        # Check preserved files
        preserved = [
            BUILDS_DIR / "MyApp 2.2 (build 512).dSYM",
            BUILDS_DIR / "MyApp 2.2 (build 512).ipa",
            BUILDS_DIR / "Nightly [2024-01-15].dSYM",
            BUILDS_DIR / "Legacy App-v1.0.dSYM",
            BUILDS_DIR / "Legacy App-v1.0.ipa",
        ]
        for path in preserved:
            assert path.exists(), \
                f"{path} was deleted after running script multiple times"


class TestBuildsDirIntegrity:
    """Test overall integrity of the builds directory."""

    def test_builds_directory_still_exists(self):
        """The builds directory itself should still exist."""
        assert BUILDS_DIR.exists(), \
            f"The builds directory {BUILDS_DIR} was deleted!"
        assert BUILDS_DIR.is_dir(), \
            f"{BUILDS_DIR} exists but is not a directory"

    def test_expected_file_count(self):
        """The builds directory should have the expected number of items."""
        # Should have:
        # - MyApp 2.2 (build 512).dSYM (dir)
        # - MyApp 2.2 (build 512).ipa (file)
        # - Nightly [2024-01-15].dSYM (dir)
        # - Legacy App-v1.0.dSYM (dir)
        # - Legacy App-v1.0.ipa (file)
        # Total: 5 items
        items = list(BUILDS_DIR.iterdir())
        assert len(items) == 5, \
            f"Expected 5 items in builds directory after cleanup, found {len(items)}: {[i.name for i in items]}"

    def test_no_unexpected_deletions(self):
        """Verify no unexpected items were deleted."""
        expected_items = {
            "MyApp 2.2 (build 512).dSYM",
            "MyApp 2.2 (build 512).ipa",
            "Nightly [2024-01-15].dSYM",
            "Legacy App-v1.0.dSYM",
            "Legacy App-v1.0.ipa",
        }
        actual_items = {item.name for item in BUILDS_DIR.iterdir()}

        missing = expected_items - actual_items
        assert not missing, \
            f"Expected items are missing from builds directory: {missing}"

        extra = actual_items - expected_items
        # Extra items that should have been deleted
        should_be_deleted = {
            "MyApp 2.1 (build 447).dSYM",
            "Release-Candidate.dSYM", 
            "TestFlight (internal).dSYM",
        }
        unexpected_extra = extra - should_be_deleted
        if unexpected_extra:
            # This is informational - unexpected files aren't necessarily wrong
            pass
