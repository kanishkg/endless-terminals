# test_final_state.py
import os
import pytest

# Define the expected final state for the region_cost_summary.log file
EXPECTED_REGION_COST_SUMMARY_CONTENT = [
    "Region: us-east-1 | TotalCost: 186.0",
    "Region: us-east-2 | TotalCost: 112.5",
    "Region: us-west-2 | TotalCost: 149.0"
]

EXPECTED_REGION_COST_SUMMARY_PATH = "/home/user/region_cost_summary.log"
EXPECTED_REGION_COST_SUMMARY_PERMISSIONS = 0o644
EXPECTED_REGION_COST_SUMMARY_OWNER = "user"
EXPECTED_REGION_COST_SUMMARY_GROUP = "user"

def test_region_cost_summary_file_exists():
    assert os.path.exists(EXPECTED_REGION_COST_SUMMARY_PATH), (
        f"The file {EXPECTED_REGION_COST_SUMMARY_PATH} does not exist."
    )

def test_region_cost_summary_file_permissions():
    actual_permissions = os.stat(EXPECTED_REGION_COST_SUMMARY_PATH).st_mode & 0o777
    assert actual_permissions == EXPECTED_REGION_COST_SUMMARY_PERMISSIONS, (
        f"Permissions for {EXPECTED_REGION_COST_SUMMARY_PATH} should be {oct(EXPECTED_REGION_COST_SUMMARY_PERMISSIONS)}, "
        f"but are {oct(actual_permissions)}"
    )

def test_region_cost_summary_file_owner():
    import pwd
    import grp

    actual_uid = os.stat(EXPECTED_REGION_COST_SUMMARY_PATH).st_uid
    actual_gid = os.stat(EXPECTED_REGION_COST_SUMMARY_PATH).st_gid

    actual_owner = pwd.getpwuid(actual_uid).pw_name
    actual_group = grp.getgrgid(actual_gid).gr_name

    assert actual_owner == EXPECTED_REGION_COST_SUMMARY_OWNER, (
        f"Owner of {EXPECTED_REGION_COST_SUMMARY_PATH} should be {EXPECTED_REGION_COST_SUMMARY_OWNER}, but is {actual_owner}"
    )
    assert actual_group == EXPECTED_REGION_COST_SUMMARY_GROUP, (
        f"Group of {EXPECTED_REGION_COST_SUMMARY_PATH} should be {EXPECTED_REGION_COST_SUMMARY_GROUP}, but is {actual_group}"
    )

def test_region_cost_summary_file_content():
    with open(EXPECTED_REGION_COST_SUMMARY_PATH, "r") as f:
        actual_lines = [line.strip() for line in f.readlines()]

    # Normalize floating point numbers for comparison
    # e.g., "148.99999999999999" should be treated as "149.0"
    normalized_actual_lines = []
    for line in actual_lines:
        parts = line.split(" | ")
        region = parts[0]
        total_cost = parts[1].split(": ")[1]
        try:
            total_cost = round(float(total_cost), 10)
        except ValueError:
            pass
        normalized_actual_lines.append(f"{region} | TotalCost: {total_cost}")

    # Normalize expected content
    normalized_expected_lines = []
    for line in EXPECTED_REGION_COST_SUMMARY_CONTENT:
        parts = line.split(" | ")
        region = parts[0]
        total_cost = parts[1].split(": ")[1]
        try:
            total_cost = round(float(total_cost), 10)
        except ValueError:
            pass
        normalized_expected_lines.append(f"{region} | TotalCost: {total_cost}")

    assert normalized_actual_lines == normalized_expected_lines, (
        f"The content of {EXPECTED_REGION_COST_SUMMARY_PATH} is not correct. "
        f"Expected: {normalized_expected_lines}, but got: {normalized_actual_lines}"
    )