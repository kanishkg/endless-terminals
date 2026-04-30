# test_final_state.py
"""
Tests to validate the final state after the student has deleted all .tmp files
under /home/user/project.
"""

import os
import subprocess
import pytest
from pathlib import Path


PROJECT_DIR = Path("/home/user/project")


def test_project_directory_still_exists():
    """Verify that /home/user/project directory still exists after the operation."""
    assert PROJECT_DIR.exists(), f"Directory {PROJECT_DIR} should still exist after deleting .tmp files"
    assert PROJECT_DIR.is_dir(), f"{PROJECT_DIR} should still be a directory"


def test_no_tmp_files_remain():
    """Verify that no .tmp files exist anywhere under /home/user/project."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-name", "*.tmp", "-type", "f"],
        capture_output=True,
        text=True
    )
    tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    assert len(tmp_files) == 0, (
        f"Expected 0 .tmp files, but found {len(tmp_files)} remaining. "
        f"Files still present: {tmp_files}"
    )


def test_no_tmp_files_using_wc():
    """Verify using find | wc -l that count of .tmp files is 0."""
    result = subprocess.run(
        "find /home/user/project -name '*.tmp' | wc -l",
        shell=True,
        capture_output=True,
        text=True
    )
    count = int(result.stdout.strip())

    assert count == 0, (
        f"Expected 'find /home/user/project -name '*.tmp' | wc -l' to return 0, "
        f"but got {count}"
    )


def test_non_tmp_files_preserved():
    """Verify that at least 5 non-.tmp files still exist (anti-shortcut guard)."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-type", "f", "!", "-name", "*.tmp"],
        capture_output=True,
        text=True
    )
    non_tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    assert len(non_tmp_files) >= 5, (
        f"Expected at least 5 non-.tmp files to be preserved, but found only {len(non_tmp_files)}. "
        f"The task was to delete only .tmp files, not all files. "
        f"Remaining files: {non_tmp_files}"
    )


def test_directory_structure_preserved():
    """Verify that the directory structure is preserved (at least some subdirectories exist)."""
    subdirs = []
    for root, dirs, files in os.walk(PROJECT_DIR):
        for d in dirs:
            subdirs.append(os.path.join(root, d))

    # There should be some directory structure remaining
    # (we don't require all empty dirs to be kept, but the structure shouldn't be completely flattened)
    assert len(subdirs) >= 1 or any(
        Path(root) != PROJECT_DIR 
        for root, dirs, files in os.walk(PROJECT_DIR) 
        if files
    ), (
        "Directory structure appears to have been destroyed. "
        "The task was only to delete .tmp files, not restructure directories."
    )


def test_no_tmp_files_in_any_form():
    """Additional check: verify no .tmp files exist using glob pattern."""
    tmp_files_found = list(PROJECT_DIR.rglob("*.tmp"))

    assert len(tmp_files_found) == 0, (
        f"Found {len(tmp_files_found)} .tmp files that should have been deleted: "
        f"{[str(f) for f in tmp_files_found[:10]]}"
        + ("..." if len(tmp_files_found) > 10 else "")
    )


def test_files_outside_project_unaffected():
    """Verify that common system directories outside /home/user/project are untouched."""
    # Just a sanity check that we didn't accidentally affect other areas
    # Check that /home/user still exists if it did before
    home_user = Path("/home/user")
    if home_user.exists():
        assert home_user.is_dir(), "/home/user should still be a directory"


def test_non_tmp_files_are_readable():
    """Verify that preserved non-.tmp files are still readable."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-type", "f", "!", "-name", "*.tmp"],
        capture_output=True,
        text=True
    )
    non_tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    # Check that at least some of the preserved files are readable
    readable_count = 0
    for f in non_tmp_files[:10]:  # Check first 10
        if os.access(f, os.R_OK):
            readable_count += 1

    assert readable_count > 0, (
        "None of the preserved non-.tmp files are readable. "
        "Something may have gone wrong with file permissions."
    )
