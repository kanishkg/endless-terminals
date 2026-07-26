# test_final_state.py

import os
import json
import pwd
import grp
import pytest
from datetime import datetime

# Define paths
PACKAGE_JSON_PATH = "/home/user/myproject/package.json"
CHANGELOG_MD_PATH = "/home/user/myproject/CHANGELOG.md"
PROJECT_DIR = "/home/user/myproject"

# Expected final version after bumping
EXPECTED_VERSION = "1.2.4"

# Expected changelog header and content
EXPECTED_CHANGELOG_HEADER = f"## [{EXPECTED_VERSION}] - {TODAY}\n"
EXPECTED_CHANGELOG_LINE1 = "- Fix issue with login form validation (#732)"
EXPECTED_CHANGELOG_LINE2 = "- Update documentation for deployment steps"

# Validate that the version in package.json has been updated
def test_package_json_version_bumped():
    with open(PACKAGE_JSON_PATH, 'r') as f:
        data = json.load(f)
        assert "version" in data, f"Field 'version' missing in {PACKAGE_JSON_PATH}"
        assert data["version"] == EXPECTED_VERSION, f"Expected version '{EXPECTED_VERSION}' in {PACKAGE_JSON_PATH}, but got {data['version']}"

# Validate that the new changelog entry is at the top of the file
def test_changelog_updated_with_new_version():
    with open(CHANGELOG_MD_PATH, 'r') as f:
        lines = f.readlines()
        assert lines[0] == EXPECTED_CHANGELOG_HEADER, f"Expected changelog header '{EXPECTED_CHANGELOG_HEADER.strip()}' at the top of {CHANGELOG_MD_PATH}, but got '{lines[0].strip()}'"
        assert lines[1].strip() == EXPECTED_CHANGELOG_LINE1, f"Expected '{EXPECTED_CHANGELOG_LINE1}' at line 2 of {CHANGELOG_MD_PATH}, but got '{lines[1].strip()}'"
        assert lines[2].strip() == EXPECTED_CHANGELOG_LINE2, f"Expected '{EXPECTED_CHANGELOG_LINE2}' at line 3 of {CHANGELOG_MD_PATH}, but got '{lines[2].strip()}'"

# Validate file ownership and permissions for package.json
def test_package_json_permissions_and_ownership_final():
    stat = os.stat(PACKAGE_JSON_PATH)
    user = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name

    assert user == "user", f"File {PACKAGE_JSON_PATH} is not owned by user 'user'"
    assert group == "user", f"File {PACKAGE_JSON_PATH} is not in group 'user'"
    assert oct(stat.st_mode)[-3:] == "664", f"File {PACKAGE_JSON_PATH} has incorrect permissions. Expected 664, got {oct(stat.st_mode)[-3:]}"

# Validate file ownership and permissions for CHANGELOG.md
def test_changelog_md_permissions_and_ownership_final():
    stat = os.stat(CHANGELOG_MD_PATH)
    user = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name

    assert user == "user", f"File {CHANGELOG_MD_PATH} is not owned by user 'user'"
    assert group == "user", f"File {CHANGELOG_MD_PATH} is not in group 'user'"
    assert oct(stat.st_mode)[-3:] == "664", f"File {CHANGELOG_MD_PATH} has incorrect permissions. Expected 664, got {oct(stat.st_mode)[-3:]}"

# Ensure no other files were created or modified
def test_no_other_files_modified():
    expected_files = {
        os.path.basename(PACKAGE_JSON_PATH),
        os.path.basename(CHANGELOG_MD_PATH),
    }
    actual_files = set(os.listdir(PROJECT_DIR))
    assert actual_files == expected_files, f"Unexpected files found in {PROJECT_DIR}: {actual_files - expected_files}"