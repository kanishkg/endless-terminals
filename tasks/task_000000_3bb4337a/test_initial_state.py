# test_initial_state.py

import os
import json
import pytest


# Define paths
PACKAGE_JSON_PATH = "/home/user/myproject/package.json"
CHANGELOG_MD_PATH = "/home/user/myproject/CHANGELOG.md"
PROJECT_DIR = "/home/user/myproject"

# Check for the existence of the project directory
def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Directory {PROJECT_DIR} does not exist."

# Check for the existence of package.json
def test_package_json_exists():
    assert os.path.isfile(PACKAGE_JSON_PATH), f"File {PACKAGE_JSON_PATH} does not exist."

# Check for the existence of CHANGELOG.md
def test_changelog_md_exists():
    assert os.path.isfile(CHANGELOG_MD_PATH), f"File {CHANGELOG_MD_PATH} does not exist."

# Check the current version in package.json
def test_current_version_in_package_json():
    with open(PACKAGE_JSON_PATH, 'r') as f:
        data = json.load(f)
        assert "version" in data, f"Field 'version' missing in {PACKAGE_JSON_PATH}"
        assert data["version"] == "1.2.3", f"Expected version '1.2.3' in {PACKAGE_JSON_PATH}, but got {data['version']}"

# Check the latest entry in CHANGELOG.md corresponds to version 1.2.3
def test_changelog_entry_for_1_2_3():
    with open(CHANGELOG_MD_PATH, 'r') as f:
        lines = f.readlines()
        # Find the first line that matches the version header pattern
        for line in lines:
            if line.startswith("## [1.2.3]"):
                assert True
                return
        pytest.fail(f"Expected changelog entry for version 1.2.3 not found in {CHANGELOG_MD_PATH}")

# Check file ownership and permissions for package.json
def test_package_json_permissions_and_ownership():
    import pwd
    import grp

    stat = os.stat(PACKAGE_JSON_PATH)
    user = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name

    assert user == "user", f"File {PACKAGE_JSON_PATH} is not owned by user 'user'"
    assert group == "user", f"File {PACKAGE_JSON_PATH} is not in group 'user'"
    assert oct(stat.st_mode)[-3:] == "664", f"File {PACKAGE_JSON_PATH} has incorrect permissions. Expected 664, got {oct(stat.st_mode)[-3:]}"

# Check file ownership and permissions for CHANGELOG.md
def test_changelog_md_permissions_and_ownership():
    import pwd
    import grp

    stat = os.stat(CHANGELOG_MD_PATH)
    user = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name

    assert user == "user", f"File {CHANGELOG_MD_PATH} is not owned by user 'user'"
    assert group == "user", f"File {CHANGELOG_MD_PATH} is not in group 'user'"
    assert oct(stat.st_mode)[-3:] == "664", f"File {CHANGELOG_MD_PATH} has incorrect permissions. Expected 664, got {oct(stat.st_mode)[-3:]}"

# Ensure no other files exist under the project directory
def test_no_other_files_in_project_directory():
    expected_files = {
        os.path.basename(PACKAGE_JSON_PATH),
        os.path.basename(CHANGELOG_MD_PATH),
    }
    actual_files = set(os.listdir(PROJECT_DIR))
    extra_files = actual_files - expected_files
    assert not extra_files, f"Unexpected files found in {PROJECT_DIR}: {extra_files}"