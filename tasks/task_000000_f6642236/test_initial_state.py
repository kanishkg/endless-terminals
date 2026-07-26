# test_initial_state.py
import os
import stat
import pytest


# Define the home directory
HOME_DIR = "/home/user"

# Define the expected directories and their metadata
expected_directories = {
    f"{HOME_DIR}/config/network": {
        "exists": True,
        "permissions": 0o755,
        "owner": "user",
        "group": "user",
    },
    f"{HOME_DIR}/logs": {
        "exists": True,
        "permissions": 0o755,
        "owner": "user",
        "group": "user",
    },
}

# Define the expected files and their metadata
expected_files = {
    f"{HOME_DIR}/config/network/config.yaml": {
        "exists": True,
        "content": "service:\n  port: 80\n  enabled: true\n  timeout: 15",
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
    f"{HOME_DIR}/config/network/new-config.yaml": {
        "exists": True,
        "content": "service:\n  port: 443\n  enabled: true\n  timeout: 15\n  ssl: true",
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
    f"{HOME_DIR}/config/network/original-config.yaml": {
        "exists": True,
        "content": "service:\n  port: 80\n  enabled: true\n  timeout: 15",
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
    f"{HOME_DIR}/config/network/config.diff": {
        "exists": True,
        "content": "--- config.yaml    2023-10-01 10:00:00.000000000 +0000\n+++ new-config.yaml    2023-10-01 10:00:00.000000000 +0000\n@@ -1,4 +1,5 @@\n service:\n   port: 80\n   enabled: true\n   timeout: 15\n+  ssl: true",
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
    f"{HOME_DIR}/logs/patch_verification.log": {
        "exists": True,
        "content": "Files Involved:\n- Original: /home/user/config/network/original-config.yaml\n- New: /home/user/config/network/new-config.yaml\n- Patch: /home/user/config/network/config.diff\n\nPatch Command: patch /home/user/config/network/original-config.yaml /home/user/config/network/config.diff\n\nChecksums:\n- Original (before patch): SHA256=0a82d4c69b516549d188a64b25f52e23d2854b49c0a1e1f28176f9f0e6a3\n- Updated (after patch): SHA256=1189a9127e98f9bfa9b88e2a449952d8a05b6f60e9e438a75f8e8b36e781\n- New: SHA256=1189a9127e98f9bfa9b88e2a449952d8a05b6f60e9e438a75f8e8b36e781\n\nPatch Verification Result: SUCCESS",
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
}


def check_file_permissions(path, expected_perms):
    """Check if file permissions match the expected octal value."""
    st = os.stat(path)
    return stat.S_IMODE(st.st_mode) == expected_perms


def check_file_content(path, expected_content):
    """Check if the content of a file matches the expected string."""
    with open(path, "r") as f:
        content = f.read()
    return content.strip() == expected_content.strip()


def check_ownership(path, expected_owner, expected_group):
    """Check if the file/directory is owned by the expected user and group."""
    st = os.stat(path)
    import pwd
    import grp
    uid_to_name = pwd.getpwuid(st.st_uid).pw_name
    gid_to_name = grp.getgrgid(st.st_gid).gr_name
    return uid_to_name == expected_owner and gid_to_name == expected_group


def test_directories_present():
    for path, metadata in expected_directories.items():
        assert os.path.isdir(path), f"Directory {path} does not exist."
        assert check_file_permissions(path, metadata["permissions"]), f"Permissions for {path} are incorrect."
        assert check_ownership(path, metadata["owner"], metadata["group"]), f"Ownership of {path} is incorrect."


def test_files_present():
    for path, metadata in expected_files.items():
        assert os.path.isfile(path), f"File {path} does not exist."
        assert check_file_permissions(path, metadata["permissions"]), f"Permissions for {path} are incorrect."
        assert check_ownership(path, metadata["owner"], metadata["group"]), f"Ownership of {path} is incorrect."
        assert check_file_content(path, metadata["content"]), f"Content of {path} does not match expected value."