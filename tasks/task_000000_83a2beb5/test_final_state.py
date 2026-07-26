# test_final_state.py

import os
import pytest
from datetime import datetime

# Define the home directory
HOME_DIR = "/home/user"
PROJECT_DIR = os.path.join(HOME_DIR, "projects", "coolapp")
VERSION_FILE = os.path.join(PROJECT_DIR, "VERSION")
CHANGELOG_FILE = os.path.join(PROJECT_DIR, "CHANGELOG.md")
LOG_FILE = os.path.join(PROJECT_DIR, ".version-bump.log")

TODAY = datetime.today().strftime("%Y-%m-%d")

# Define the truth values for the final state
EXPECTED_VERSION_CONTENT = "v1.2.0"
# Compare line-by-line with trailing whitespace stripped to avoid fragile space matching
EXPECTED_CHANGELOG_LINES = [
    f"## [v1.2.0] - {TODAY}",
    "- Updated minor version",
    "",
    "## [v1.1.3] - 2025-03-20",
    "- Fixed bug in parser",
]
EXPECTED_LOG_CONTENT = f"Version bumped from v1.1 to v1.2.0\nChangelog updated with version v1.2.0 and date {TODAY}"

# Check that the new files exist and have correct content
def test_version_file_exists_and_content():
    assert os.path.isfile(VERSION_FILE), f"File {VERSION_FILE} does not exist."

    with open(VERSION_FILE, "r") as f:
        content = f.read().strip()
    assert content == EXPECTED_VERSION_CONTENT, (
        f"Content of {VERSION_FILE} is incorrect. Expected: '{EXPECTED_VERSION_CONTENT}', "
        f"Got: '{content}'"
    )

def test_changelog_file_exists_and_content():
    assert os.path.isfile(CHANGELOG_FILE), f"File {CHANGELOG_FILE} does not exist."

    with open(CHANGELOG_FILE, "r") as f:
        content = f.read()
    lines = [l.rstrip() for l in content.rstrip("\n").split("\n")]
    assert lines == EXPECTED_CHANGELOG_LINES, (
        f"Content of {CHANGELOG_FILE} is incorrect. Expected: '{EXPECTED_CHANGELOG_LINES}', "
        f"Got: '{lines}'"
    )

def test_version_bump_log_exists_and_content():
    assert os.path.isfile(LOG_FILE), f"File {LOG_FILE} does not exist."

    with open(LOG_FILE, "r") as f:
        content = f.read()
    lines = [l.rstrip() for l in content.rstrip("\n").split("\n")]
    expected_lines = [l.rstrip() for l in EXPECTED_LOG_CONTENT.split("\n")]
    assert lines == expected_lines, (
        f"Content of {LOG_FILE} is incorrect. Expected: '{expected_lines}', "
        f"Got: '{lines}'"
    )