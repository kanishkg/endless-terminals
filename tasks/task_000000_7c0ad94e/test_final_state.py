# test_final_state.py

import os
import subprocess
import pytest
from datetime import datetime

# Define the home directory
HOME_DIR = "/home/user"

# Define the log file path
LOG_FILE_PATH = "/home/user/dev-setup-complete.log"

# Get actual version strings from the container at test time
GIT_VERSION = subprocess.check_output(["git", "--version"]).decode().strip()
PYTHON3_VERSION = subprocess.check_output(["python3", "--version"]).decode().strip()

# Define the expected content in the log file (with placeholder for timestamp)
EXPECTED_CONTENT_LINES = [
    "Setup completed on: [YYYY-MM-DD HH:MM:SS]",
    "Git installed and functional",
    GIT_VERSION,
    "Python 3 installed and functional",
    PYTHON3_VERSION,
    "Development environment is ready for deployment updates"
]


def test_log_file_exists():
    """
    Ensure that the log file exists in the correct location.
    """
    assert os.path.exists(LOG_FILE_PATH), f"The log file {LOG_FILE_PATH} does not exist. Setup was not completed."


def test_log_file_content():
    """
    Ensure that the log file has the correct content in the correct order.
    """
    with open(LOG_FILE_PATH, 'r') as file:
        content = file.read().splitlines()

    assert len(content) == len(EXPECTED_CONTENT_LINES), (
        f"Log file has incorrect number of lines. Expected {len(EXPECTED_CONTENT_LINES)}, got {len(content)}.")

    for i, line in enumerate(content):
        expected_line = EXPECTED_CONTENT_LINES[i]

        # Handle timestamp line separately
        if i == 0:
            assert line.startswith("Setup completed on: "), (
                f"First line does not start with expected timestamp header: {line}")
        else:
            assert line == expected_line, (
                f"Line {i + 1} content is incorrect. Expected: {expected_line}, Got: {line}")
