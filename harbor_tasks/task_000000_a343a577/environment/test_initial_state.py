# test_initial_state.py
"""
Tests to validate the initial state before the student performs the task
of deleting all .tmp files under /home/user/project.
"""

import os
import subprocess
import pytest
from pathlib import Path


PROJECT_DIR = Path("/home/user/project")


def test_project_directory_exists():
    """Verify that /home/user/project directory exists."""
    assert PROJECT_DIR.exists(), f"Directory {PROJECT_DIR} does not exist"
    assert PROJECT_DIR.is_dir(), f"{PROJECT_DIR} is not a directory"


def test_project_directory_is_writable():
    """Verify that /home/user/project is writable."""
    assert os.access(PROJECT_DIR, os.W_OK), f"Directory {PROJECT_DIR} is not writable"


def test_nested_directory_structure_exists():
    """Verify that there is a nested directory structure (at least 3 levels deep)."""
    # Find the maximum depth of directories
    max_depth = 0
    for root, dirs, files in os.walk(PROJECT_DIR):
        # Calculate depth relative to PROJECT_DIR
        rel_path = Path(root).relative_to(PROJECT_DIR)
        depth = len(rel_path.parts)
        if depth > max_depth:
            max_depth = depth

    assert max_depth >= 3, (
        f"Directory structure is not deep enough. "
        f"Expected at least 3 levels deep, found {max_depth} levels."
    )


def test_exactly_50_tmp_files_exist():
    """Verify that exactly 50 .tmp files exist under /home/user/project."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-name", "*.tmp", "-type", "f"],
        capture_output=True,
        text=True
    )
    tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    assert len(tmp_files) == 50, (
        f"Expected exactly 50 .tmp files, found {len(tmp_files)}. "
        f"Files found: {tmp_files[:10]}..." if len(tmp_files) > 10 else f"Files found: {tmp_files}"
    )


def test_tmp_files_scattered_across_subdirs():
    """Verify that .tmp files are scattered across multiple subdirectories."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-name", "*.tmp", "-type", "f"],
        capture_output=True,
        text=True
    )
    tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    # Get unique parent directories
    parent_dirs = set()
    for f in tmp_files:
        parent_dirs.add(os.path.dirname(f))

    assert len(parent_dirs) >= 3, (
        f"Expected .tmp files to be scattered across at least 3 directories, "
        f"but found them in only {len(parent_dirs)} directories: {parent_dirs}"
    )


def test_non_tmp_files_exist():
    """Verify that non-.tmp files exist (at least 5)."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-type", "f", "!", "-name", "*.tmp"],
        capture_output=True,
        text=True
    )
    non_tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    assert len(non_tmp_files) >= 5, (
        f"Expected at least 5 non-.tmp files, found {len(non_tmp_files)}. "
        f"These files must be preserved during the task."
    )


def test_various_file_types_exist():
    """Verify that various file types exist (not just .tmp files)."""
    extensions_found = set()

    for root, dirs, files in os.walk(PROJECT_DIR):
        for f in files:
            _, ext = os.path.splitext(f)
            if ext and ext != '.tmp':
                extensions_found.add(ext)

    assert len(extensions_found) >= 1, (
        f"Expected to find at least one non-.tmp file type, "
        f"but found none. There should be .py, .txt, .json or other files."
    )


def test_subdirectories_are_writable():
    """Verify that subdirectories containing .tmp files are writable."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-name", "*.tmp", "-type", "f"],
        capture_output=True,
        text=True
    )
    tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    # Check a sample of parent directories
    parent_dirs = set()
    for f in tmp_files[:10]:  # Check first 10
        parent_dirs.add(os.path.dirname(f))

    for d in parent_dirs:
        assert os.access(d, os.W_OK), f"Directory {d} is not writable"


def test_tmp_files_are_regular_files():
    """Verify that .tmp files are regular files (not symlinks or directories)."""
    result = subprocess.run(
        ["find", str(PROJECT_DIR), "-name", "*.tmp", "-type", "f"],
        capture_output=True,
        text=True
    )
    tmp_files = [f for f in result.stdout.strip().split('\n') if f]

    for f in tmp_files:
        path = Path(f)
        assert path.is_file(), f"{f} is not a regular file"
        assert not path.is_symlink(), f"{f} is a symlink, expected regular file"
