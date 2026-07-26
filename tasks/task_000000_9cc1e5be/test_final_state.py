# test_final_state.py

import os
import pytest
from datetime import datetime

# Define the expected final state
expected_alert_files = {
    "/home/user/monitoring/alerts/alert_20240405_101532.log": 0o644,
    "/home/user/monitoring/alerts/alert_20240406_084201.log": 0o644,
}

expected_directories = {
    "/home/user/monitoring/alert_landing": 0o755,
}

expected_symlinks = {
    "/home/user/monitoring/alert_landing/latest_alert_1": "/home/user/monitoring/alerts/alert_20240406_084201.log",
    "/home/user/monitoring/alert_landing/latest_alert_2": "/home/user/monitoring/alerts/alert_20240405_101532.log",
}

expected_log_file = {
    "path": "/home/user/monitoring/alert_setup.log",
    "content": "2024-04-08 14:30:10: Contents of /home/user/monitoring/alert_landing\n - latest_alert_1 -> /home/user/monitoring/alerts/alert_20240406_084201.log\n - latest_alert_2 -> /home/user/monitoring/alerts/alert_20240405_101532.log\n",
    "permissions": 0o644,
}

def test_alert_files_present():
    for path, expected_perms in expected_alert_files.items():
        assert os.path.exists(path), f"Alert file {path} does not exist"
        actual_perms = os.stat(path).st_mode & 0o777
        assert actual_perms == expected_perms, f"Permissions for {path} are {oct(actual_perms)} but should be {oct(expected_perms)}"

def test_alert_landing_directory_exists():
    for path, expected_perms in expected_directories.items():
        assert os.path.isdir(path), f"Directory {path} does not exist"
        actual_perms = os.stat(path).st_mode & 0o777
        assert actual_perms == expected_perms, f"Permissions for {path} are {oct(actual_perms)} but should be {oct(expected_perms)}"

def test_symlinks_correct():
    for path, expected_target in expected_symlinks.items():
        assert os.path.islink(path), f"Symlink {path} does not exist"
        actual_target = os.readlink(path)
        assert actual_target == expected_target, f"Symlink {path} points to {actual_target} but should point to {expected_target}"

def test_log_file_exists_and_content():
    path, content, expected_perms = expected_log_file["path"], expected_log_file["content"], expected_log_file["permissions"]
    assert os.path.exists(path), f"Log file {path} does not exist"
    actual_perms = os.stat(path).st_mode & 0o777
    assert actual_perms == expected_perms, f"Permissions for {path} are {oct(actual_perms)} but should be {oct(expected_perms)}"
    with open(path, "r") as f:
        actual_content = f.read()
    assert actual_content.strip() == content.strip(), f"Content of {path} does not match expected content"