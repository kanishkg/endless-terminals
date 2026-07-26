# test_initial_state.py
import os
import pytest
from pathlib import Path


# Define the home path
HOME_PATH = Path("/home/user")
SYSLOG_PATH = Path("/var/log/syslog")
SUMMARY_FILE_PATH = HOME_PATH / "performance-summary-20250405.txt"


def test_home_directory_exists():
    assert HOME_PATH.exists(), f"Home directory {HOME_PATH} does not exist."


def test_summary_file_does_not_exist():
    assert not SUMMARY_FILE_PATH.exists(), f"Summary file {SUMMARY_FILE_PATH} already exists. It should not exist before the task is performed."


def test_syslog_file_exists():
    assert SYSLOG_PATH.exists(), f"Syslog file {SYSLOG_PATH} does not exist. It is required for the task."
    assert os.path.isfile(SYSLOG_PATH), f"{SYSLOG_PATH} is not a regular file."


def test_correct_owner_of_syslog_file():
    # Check that the file is owned by root, as is typical for /var/log/syslog
    # This is an example, but in practice, this may be root, or a specific user/group.
    # If this is a test environment, the user may need to be adjusted accordingly.
    stat = os.stat(SYSLOG_PATH)
    assert stat.st_uid == 0, f"{SYSLOG_PATH} is not owned by root. It is owned by UID {stat.st_uid}."


def test_correct_permissions_of_syslog_file():
    stat = os.stat(SYSLOG_PATH)
    # Expected permissions: rw-r--r-- (644)
    expected_mode = 0o644
    assert stat.st_mode & 0o777 == expected_mode, f"{SYSLOG_PATH} has incorrect permissions. Expected {oct(expected_mode)}, got {oct(stat.st_mode & 0o777)}."


def test_correct_content_in_syslog_file():
    with open(SYSLOG_PATH, "r") as f:
        lines = f.readlines()

    expected_content = [
        "Apr  5 16:00:15 host systemd: System start completed in 2.000s\n",
        "Apr  5 16:02:32 host kernel: CPU usage at 75%\n",
        "Apr  5 16:10:00 host memory: Memory usage at 50%\n",
        "Apr  5 16:30:41 host memory: Memory usage at 60%\n",
        "Apr  5 16:40:03 host kernel: CPU usage at 78%\n",
        "Apr  5 16:55:12 host cpu: High CPU load detected on core 3\n",
        "Apr  5 17:00:20 host memory: Memory usage at 62%\n",
        "Apr  5 17:03:11 host kernel: CPU usage at 80%\n",
        "Apr  5 17:15:00 host systemd: Starting daily cron...\n",
        "Apr  5 17:22:57 host memory: Memory usage at 65%\n",
        "Apr  5 17:30:11 host systemd: Finished daily cron.\n",
        "Apr  5 17:45:02 host kernel: CPU usage at 85%\n",
        "Apr  5 18:00:05 host kernel: CPU usage at 90%\n",
    ]

    for expected_line in expected_content:
        assert expected_line in lines, f"Expected line '{expected_line.strip()}' not found in {SYSLOG_PATH}."


def test_correct_owner_of_home_directory():
    stat = os.stat(HOME_PATH)
    # Assuming the home directory is owned by user (UID 1000)
    expected_uid = 1000
    assert stat.st_uid == expected_uid, f"{HOME_PATH} is not owned by user (UID {expected_uid}). It is owned by UID {stat.st_uid}."


def test_correct_permissions_of_home_directory():
    stat = os.stat(HOME_PATH)
    # Expected permissions: drwxr-xr-x (755)
    expected_mode = 0o755
    assert stat.st_mode & 0o777 == expected_mode, f"{HOME_PATH} has incorrect permissions. Expected {oct(expected_mode)}, got {oct(stat.st_mode & 0o777)}."


def test_correct_permissions_of_summary_file_does_not_exist():
    # If the file does not exist, we don't need to check its permissions
    pass