# test_initial_state.py

import os
import pytest

# Define the home path
HOME_PATH = "/home/user"

# Define the expected files and directories
EXPECTED_MODIFIED_FILES = [
    f"{HOME_PATH}/modified_files/ssh_config",
    f"{HOME_PATH}/modified_files/iptables_rules",
    f"{HOME_PATH}/modified_files/cron_jobs",
]

EXPECTED_ORIGINAL_FILES = [
    f"{HOME_PATH}/original_files/ssh_config_original",
    f"{HOME_PATH}/original_files/iptables_rules_original",
    f"{HOME_PATH}/original_files/cron_jobs_original",
]

EXPECTED_LOG_FILE = f"{HOME_PATH}/reconciliation_log.txt"

EXPECTED_DIRECTORIES = [
    f"{HOME_PATH}/modified_files",
    f"{HOME_PATH}/original_files",
]

def test_directories_present():
    for dir_path in EXPECTED_DIRECTORIES:
        assert os.path.isdir(dir_path), f"Directory {dir_path} is missing."

def test_modified_files_present():
    for file_path in EXPECTED_MODIFIED_FILES:
        assert os.path.isfile(file_path), f"Modified file {file_path} is missing."

def test_original_files_present():
    for file_path in EXPECTED_ORIGINAL_FILES:
        assert os.path.isfile(file_path), f"Original file {file_path} is missing."

def test_log_file_absent():
    assert not os.path.isfile(EXPECTED_LOG_FILE), f"Log file {EXPECTED_LOG_FILE} already exists."