# test_initial_state.py
import os
import pwd
import pytest

# Define the paths to verify
BINARY_DIR = "/home/user/artifacts/binaries"
TRUSTED_DIR = "/home/user/artifacts/binaries/trusted"
LOG_FILE = "/home/user/artifacts/permissions_log.txt"

# Define the user
USER = "artifactmgr"


@pytest.fixture
def user_uid():
    """Return the UID of the user 'artifactmgr'."""
    try:
        return pwd.getpwnam(USER).pw_uid
    except KeyError:
        pytest.fail(f"User '{USER}' does not exist.")


def test_binary_directory_does_not_exist():
    """Ensure that the binaries directory does not exist before the student performs the action."""
    assert not os.path.exists(BINARY_DIR), f"{BINARY_DIR} already exists. It should not exist initially."


def test_trusted_subdirectory_does_not_exist():
    """Ensure that the trusted subdirectory does not exist before the student performs the action."""
    assert not os.path.exists(TRUSTED_DIR), f"{TRUSTED_DIR} already exists. It should not exist initially."


def test_permissions_log_does_not_exist():
    """Ensure that the permissions log file does not exist before the student performs the action."""
    assert not os.path.exists(LOG_FILE), f"{LOG_FILE} already exists. It should not exist initially."