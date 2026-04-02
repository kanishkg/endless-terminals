# test_final_state.py

import os
import pytest
import tarfile


# Define expected paths and content based on the truth value
expected_directory = "/var/log/user_activity/"
expected_files = [
    "/var/log/user_activity/user_log_20250405_01.txt",
    "/var/log/user_activity/user_log_20250405_02.txt",
    "/var/log/user_activity/user_log_20250405_03.txt",
]
expected_tarball = "/home/user/user_activity_logs_20250405.tar.gz"
expected_verification_file = "/home/user/archive_verification_20250405.txt"


def test_tarball_exists_and_has_correct_permissions():
    assert os.path.isfile(expected_tarball), f"Tarball {expected_tarball} does not exist."
    assert os.stat(expected_tarball).st_uid == os.getuid(), f"Tarball {expected_tarball} is not owned by the current user."
    mode = oct(os.stat(expected_tarball).st_mode)[-3:]
    assert mode == "644", f"Tarball {expected_tarball} has incorrect permissions. Expected 0644, got {mode}."


def test_tarball_contains_correct_files():
    with tarfile.open(expected_tarball, "r:*") as tar:
        tar_members = sorted(tar.getnames())
        expected_members = sorted(os.path.basename(f) for f in expected_files)
        assert tar_members == expected_members, (
            f"Tarball {expected_tarball} does not contain the correct files. "
            f"Expected {expected_members}, but found {tar_members}."
        )


def test_verification_file_exists_and_has_correct_permissions():
    assert os.path.isfile(expected_verification_file), f"Verification file {expected_verification_file} does not exist."
    assert os.stat(expected_verification_file).st_uid == os.getuid(), f"Verification file {expected_verification_file} is not owned by the current user."
    mode = oct(os.stat(expected_verification_file).st_mode)[-3:]
    assert mode == "644", f"Verification file {expected_verification_file} has incorrect permissions. Expected 0644, got {mode}."


def test_verification_file_content():
    with open(expected_verification_file, "r") as f:
        lines = f.read().strip().splitlines()

    # Expected content format:
    # - First 3 lines: filenames (in any order)
    # - 4th line: size in bytes
    expected_filenames = {os.path.basename(f) for f in expected_files}
    actual_filenames = set(lines[:3])

    assert actual_filenames == expected_filenames, (
        f"Verification file {expected_verification_file} has incorrect filenames. "
        f"Expected {expected_filenames}, but found {actual_filenames}."
    )

    try:
        actual_size = int(lines[3])
    except (IndexError, ValueError):
        pytest.fail(f"Verification file {expected_verification_file} does not contain a valid size on the fourth line.")

    # Get the actual size of the tarball
    tarball_stat = os.stat(expected_tarball)
    expected_size = tarball_stat.st_size

    assert actual_size == expected_size, (
        f"Verification file {expected_verification_file} has incorrect size. "
        f"Expected {expected_size}, but found {actual_size}."
    )