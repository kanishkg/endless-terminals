# test_initial_state.py

import os
import pytest
from datetime import datetime

# Define the home directory
HOME_DIR = "/home/user"

# Define the log file path
LOG_FILE_PATH = os.path.join(HOME_DIR, "dev-setup-complete.log")

# Define the expected content in the log file (excluding the actual timestamp)
EXPECTED_CONTENT_LINES = [
    "Git installed and functional",
    "git version 2.30.1",
    "Python 3 installed and functional",
    "Python 3.10.6",
    "Development environment is ready for deployment updates"
]

# Define the expected tools and their commands
TOOL_COMMANDS = {
    "git": "git --version",
    "python3": "python3 --version"
}


@pytest.mark.parametrize("tool, command", TOOL_COMMANDS.items())
def test_tools_installed(tool, command):
    """
    Test that required tools are installed and accessible.
    """
    try:
        output = os.popen(command).read().strip()
        assert output, f"{tool} is not installed or not accessible."
    except Exception as e:
        pytest.fail(f"Failed to check {tool} installation: {e}")


def test_log_file_does_not_exist_yet():
    """
    Ensure that the log file does not exist yet.
    """
    assert not os.path.exists(LOG_FILE_PATH), f"The log file {LOG_FILE_PATH} already exists before setup." \
                                              "This would overwrite the truth value log file." \
                                              "Please remove it before running the task."