# test_final_state.py
import os
import pwd
import grp
import pytest


# Define the paths to verify
BINARY_DIR = "/home/user/artifacts/binaries"
TRUSTED_DIR = "/home/user/artifacts/binaries/trusted"
LOG_FILE = "/home/user/artifacts/permissions_log.txt"

# Define the user and group
USER = "artifactmgr"
GROUP = "artifactmgr"


@pytest.fixture
def user_uid():
    """Return the UID of the user 'artifactmgr'."""
    try:
        return pwd.getpwnam(USER).pw_uid
    except KeyError:
        pytest.fail(f"User '{USER}' does not exist.")


@pytest.fixture
def user_gid(user_uid):
    """Return the GID of the user 'artifactmgr'."""
    user_info = pwd.getpwuid(user_uid)
    try:
        return grp.getgrnam(user_info.pw_name).gr_gid
    except KeyError:
        pytest.fail(f"Group for user '{USER}' does not exist.")


def test_binary_directory_exists():
    """Ensure that the binaries directory exists."""
    assert os.path.isdir(BINARY_DIR), f"{BINARY_DIR} does not exist."


def test_binary_directory_permissions(user_uid, user_gid):
    """Ensure that the binaries directory has the correct permissions and ownership."""
    stat_info = os.stat(BINARY_DIR)
    assert stat_info.st_uid == user_uid, f"{BINARY_DIR} is not owned by user {USER}."
    assert stat_info.st_gid == user_gid, f"{BINARY_DIR} is not owned by group {GROUP}."
    expected_perms = 0o750
    actual_perms = stat_info.st_mode & 0o777
    assert actual_perms == expected_perms, f"{BINARY_DIR} has incorrect permissions. Expected {oct(expected_perms)}, got {oct(actual_perms)}."


def test_trusted_subdirectory_exists():
    """Ensure that the trusted subdirectory exists."""
    assert os.path.isdir(TRUSTED_DIR), f"{TRUSTED_DIR} does not exist."


def test_trusted_subdirectory_permissions(user_uid, user_gid):
    """Ensure that the trusted subdirectory has the correct permissions and ownership."""
    stat_info = os.stat(TRUSTED_DIR)
    assert stat_info.st_uid == user_uid, f"{TRUSTED_DIR} is not owned by user {USER}."
    assert stat_info.st_gid == user_gid, f"{TRUSTED_DIR} is not owned by group {GROUP}."
    expected_perms = 0o700
    actual_perms = stat_info.st_mode & 0o777
    assert actual_perms == expected_perms, f"{TRUSTED_DIR} has incorrect permissions. Expected {oct(expected_perms)}, got {oct(actual_perms)}."


def test_permissions_log_exists(user_uid, user_gid):
    """Ensure that the permissions log file exists and has the correct ownership and permissions."""
    assert os.path.isfile(LOG_FILE), f"{LOG_FILE} does not exist."

    stat_info = os.stat(LOG_FILE)
    assert stat_info.st_uid == user_uid, f"{LOG_FILE} is not owned by user {USER}."
    assert stat_info.st_gid == user_gid, f"{LOG_FILE} is not owned by group {GROUP}."
    expected_perms = 0o600
    actual_perms = stat_info.st_mode & 0o777
    assert actual_perms == expected_perms, f"{LOG_FILE} has incorrect permissions. Expected {oct(expected_perms)}, got {oct(actual_perms)}."


def test_permissions_log_contents():
    """Ensure that the permissions log file contains entries with correct permissions and ownership."""
    with open(LOG_FILE, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    assert len(lines) >= 2, (
        f"{LOG_FILE} should have at least 2 lines, got {len(lines)}: {lines}"
    )

    # Check the binaries entry: permissions drwxr-x--- owned by artifactmgr artifactmgr
    binaries_line = lines[0]
    assert binaries_line.startswith("drwxr-x---"), (
        f"First log entry should start with 'drwxr-x---', got: {binaries_line!r}"
    )
    assert "artifactmgr artifactmgr" in binaries_line, (
        f"First log entry should show 'artifactmgr artifactmgr' ownership, got: {binaries_line!r}"
    )
    assert "binaries" in binaries_line, (
        f"First log entry should reference 'binaries', got: {binaries_line!r}"
    )

    # Check the trusted entry: permissions drwx------ owned by artifactmgr artifactmgr
    trusted_line = lines[1]
    assert trusted_line.startswith("drwx------"), (
        f"Second log entry should start with 'drwx------', got: {trusted_line!r}"
    )
    assert "artifactmgr artifactmgr" in trusted_line, (
        f"Second log entry should show 'artifactmgr artifactmgr' ownership, got: {trusted_line!r}"
    )
    assert "trusted" in trusted_line, (
        f"Second log entry should reference 'trusted', got: {trusted_line!r}"
    )