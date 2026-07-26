# test_final_state.py

import os
import pytest
from pathlib import Path

# Define paths
HOME_PATH = Path("/home/user")
SYSLOG_PATH = Path("/var/log/syslog")
SUMMARY_FILE_PATH = HOME_PATH / "performance-summary-20250405.txt"

# Expected content for the summary file
EXPECTED_SUMMARY_CONTENT = [
    "Apr  5 16:02:32 host kernel: CPU usage at 75%\n",
    "Apr  5 16:30:41 host memory: Memory usage at 60%\n",
    "Apr  5 16:55:12 host cpu: High CPU load detected on core 3\n",
    "Apr  5 17:03:11 host kernel: CPU usage at 80%\n",
    "Apr  5 17:22:57 host memory: Memory usage at 65%\n",
    "Apr  5 17:45:02 host kernel: CPU usage at 85%\n",
]

# Expected owner and permissions for the summary file
import pwd as _pwd
EXPECTED_OWNER_UID = _pwd.getpwnam("user").pw_uid  # resolve dynamically
EXPECTED_PERMISSIONS = 0o600  # rw-------


def test_summary_file_exists():
    assert SUMMARY_FILE_PATH.exists(), f"Summary file {SUMMARY_FILE_PATH} does not exist. It must be created as part of the task completion."


def test_summary_file_owner():
    stat = os.stat(SUMMARY_FILE_PATH)
    assert stat.st_uid == EXPECTED_OWNER_UID, f"{SUMMARY_FILE_PATH} is not owned by user (UID {EXPECTED_OWNER_UID}). It is owned by UID {stat.st_uid}."


def test_summary_file_permissions():
    stat = os.stat(SUMMARY_FILE_PATH)
    actual_perms = stat.st_mode & 0o777
    assert actual_perms == EXPECTED_PERMISSIONS, f"{SUMMARY_FILE_PATH} has incorrect permissions. Expected {oct(EXPECTED_PERMISSIONS)}, got {oct(actual_perms)}."


def test_summary_file_content():
    with open(SUMMARY_FILE_PATH, "r") as f:
        lines = f.readlines()

    assert lines == EXPECTED_SUMMARY_CONTENT, f"Summary file content does not match expected lines. Found: {lines}, Expected: {EXPECTED_SUMMARY_CONTENT}"


def test_summary_file_sorted_chronologically():
    # This is already implied by the test_summary_file_content, but we can re-check
    with open(SUMMARY_FILE_PATH, "r") as f:
        lines = f.readlines()

    # Ensure the lines are in the correct chronological order
    expected_order = [
        "16:02:32",
        "16:30:41",
        "16:55:12",
        "17:03:11",
        "17:22:57",
        "17:45:02"
    ]

    for i, line in enumerate(lines):
        assert expected_order[i] in line, f"Line {i} is not in the correct chronological order. Expected timestamp {expected_order[i]} but found {line.split()[2]}"