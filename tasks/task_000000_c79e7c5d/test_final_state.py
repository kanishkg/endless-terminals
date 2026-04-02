# test_final_state.py

import os
import json
import pytest

# Define expected paths
SERVICES_DIR = "/home/user/microservices/services/"
LOGS_DIR = "/home/user/microservices/logs/"
LOG_FILE_PATH = f"{LOGS_DIR}processing_summary.log"
MAPPINGS_JSON_PATH = "/home/user/microservices/config/mappings.json"

# Expected service JSON content
EXPECTED_SERVICE_A_JSON = {
    "service_name": "service-a",
    "port": 8080,
    "environment_vars": {
        "NEW_ENV1": "value1",
        "NEW_ENV2": "value2"
    }
}

EXPECTED_SERVICE_B_JSON = {
    "service_name": "service-b",
    "port": 9090,
    "environment_vars": {
        "NEW_ENV3": "value3",
        "env4": "value4"
    }
}

# Expected log file content
EXPECTED_LOG_CONTENT = """Service JSON files created:
- service-a.json
- service-b.json
Total environment variables processed: 4
Task completed successfully.
"""


def test_service_a_json_file_exists():
    file_path = f"{SERVICES_DIR}service-a.json"
    assert os.path.exists(file_path), f"Missing required file: {file_path}"

    with open(file_path, 'r') as f:
        content = json.load(f)

    assert content == EXPECTED_SERVICE_A_JSON, f"Content of {file_path} does not match expected content"


def test_service_b_json_file_exists():
    file_path = f"{SERVICES_DIR}service-b.json"
    assert os.path.exists(file_path), f"Missing required file: {file_path}"

    with open(file_path, 'r') as f:
        content = json.load(f)

    assert content == EXPECTED_SERVICE_B_JSON, f"Content of {file_path} does not match expected content"


def test_processing_summary_log_file_exists():
    assert os.path.exists(LOG_FILE_PATH), f"Missing required file: {LOG_FILE_PATH}"

    with open(LOG_FILE_PATH, 'r') as f:
        content = f.read()

    assert content == EXPECTED_LOG_CONTENT, f"Content of {LOG_FILE_PATH} does not match expected content"