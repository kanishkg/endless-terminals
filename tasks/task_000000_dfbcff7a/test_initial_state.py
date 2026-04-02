# test_initial_state.py

import os
import pytest


# Define expected state based on the truth value
expected_directory = "/var/log/user_activity/"
expected_files = [
    "/var/log/user_activity/user_log_20250405_01.txt",
    "/var/log/user_activity/user_log_20250405_02.txt",
    "/var/log/user_activity/user_log_20250405_03.txt",
]
expected_tarball = "/home/user/user_activity_logs_20250405.tar.gz"
expected_verification_file = "/home/user/archive_verification_20250405.txt"


def test_directory_exists():
    assert os.path.isdir(expected_directory), f"Directory {expected_directory} does not exist."
    assert os.access(expected_directory, os.R_OK | os.X_OK), f"Directory {expected_directory} is not readable or executable by the current user."


def test_files_present():
    for file in expected_files:
        assert os.path.isfile(file), f"File {file} does not exist."
        assert os.access(file, os.R_OK), f"File {file} is not readable by the current user."


def test_correct_number_of_files():
    actual_files = [f for f in os.listdir(expected_directory) if f.endswith(".txt")]
    assert len(actual_files) == len(expected_files), f"Expected {len(expected_files)} .txt files in {expected_directory}, but found {len(actual_files)}."


def test_no_existing_tarball():
    assert not os.path.exists(expected_tarball), f"Tarball {expected_tarball} already exists. Initial state is not clean."


def test_no_existing_verification_file():
    assert not os.path.exists(expected_verification_file), f"Verification file {expected_verification_file} already exists. Initial state is not clean."