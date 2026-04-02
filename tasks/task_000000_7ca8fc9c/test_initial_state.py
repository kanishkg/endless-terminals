# test_initial_state.py
import os
import pytest

# Define the expected initial state
EXPECTED_FILES = {
    "/home/user/cloud_cost_report.csv": {
        "exists": True,
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
    "/home/user/region_cost_summary.log": {
        "exists": True,
        "permissions": 0o644,
        "owner": "user",
        "group": "user",
    },
}

def test_initial_state():
    for path, expected in EXPECTED_FILES.items():
        assert os.path.exists(path), f"File {path} is missing"

        # Check permissions
        actual_permissions = os.stat(path).st_mode & 0o777
        assert actual_permissions == expected["permissions"], (
            f"Permissions for {path} should be {oct(expected['permissions'])}, "
            f"but are {oct(actual_permissions)}"
        )

        # Check owner and group
        actual_uid = os.stat(path).st_uid
        actual_gid = os.stat(path).st_gid

        # Get username and group name from UID and GID
        import pwd
        import grp

        actual_owner = pwd.getpwuid(actual_uid).pw_name
        actual_group = grp.getgrgid(actual_gid).gr_name

        assert actual_owner == expected["owner"], (
            f"Owner of {path} should be {expected['owner']}, but is {actual_owner}"
        )
        assert actual_group == expected["group"], (
            f"Group of {path} should be {expected['group']}, but is {actual_group}"
        )