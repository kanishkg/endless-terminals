# test_initial_state.py

import os
import pytest

# Define the home directory
HOME_DIR = "/home/user"
PROJECT_DIR = os.path.join(HOME_DIR, "projects", "coolapp")
VERSION_FILE = os.path.join(PROJECT_DIR, "VERSION")
CHANGELOG_FILE = os.path.join(PROJECT_DIR, "CHANGELOG.md")

# Define the truth values for the initial state
EXPECTED_VERSION_CONTENT = "v1.1"
EXPECTED_CHANGELOG_CONTENT = """## [v1.1.3] - 2025-03-20  
- Fixed bug in parser"""

# Check that the required directories and files exist
def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Directory {PROJECT_DIR} does not exist."

def test_version_file_exists():
    assert os.path.isfile(VERSION_FILE), f"File {VERSION_FILE} does not exist."

def test_changelog_file_exists():
    assert os.path.isfile(CHANGELOG_FILE), f"File {CHANGELOG_FILE} does not exist."

# Check the contents of the files
def test_version_file_content():
    with open(VERSION_FILE, "r") as f:
        content = f.read().strip()
    assert content == EXPECTED_VERSION_CONTENT, (
        f"Content of {VERSION_FILE} is incorrect. Expected: '{EXPECTED_VERSION_CONTENT}', "
        f"Got: '{content}'"
    )

def test_changelog_file_content():
    with open(CHANGELOG_FILE, "r") as f:
        content = f.read().strip()
    assert content == EXPECTED_CHANGELOG_CONTENT, (
        f"Content of {CHANGELOG_FILE} is incorrect. Expected: '{EXPECTED_CHANGELOG_CONTENT}', "
        f"Got: '{content}'"
    )