# test_initial_state.py

import os
import pytest

# Define expected paths
CSV_FILE_PATH = "/home/user/microservices/config/services.csv"
MAPPINGS_JSON_PATH = "/home/user/microservices/config/mappings.json"
SERVICES_DIR = "/home/user/microservices/services/"
LOGS_DIR = "/home/user/microservices/logs/"

# Expected content of services.csv
EXPECTED_CSV_CONTENT = """service_name,port,environment_vars
service-a,8080,"{""env1"":""value1"", ""env2"":""value2""}"
service-b,9090,"{""env3"":""value3"", ""env4"":""value4""}"
"""

# Expected content of mappings.json
EXPECTED_MAPPINGS_JSON_CONTENT = """{
  "env1": "NEW_ENV1",
  "env2": "NEW_ENV2",
  "env3": "NEW_ENV3"
}
"""

def test_services_csv_file_exists():
    assert os.path.exists(CSV_FILE_PATH), f"Missing required file: {CSV_FILE_PATH}"
    with open(CSV_FILE_PATH, 'r') as f:
        content = f.read()
    assert content == EXPECTED_CSV_CONTENT, f"Content of {CSV_FILE_PATH} does not match expected content"


def test_mappings_json_file_exists():
    assert os.path.exists(MAPPINGS_JSON_PATH), f"Missing required file: {MAPPINGS_JSON_PATH}"
    with open(MAPPINGS_JSON_PATH, 'r') as f:
        content = f.read()
    assert content == EXPECTED_MAPPINGS_JSON_CONTENT, f"Content of {MAPPINGS_JSON_PATH} does not match expected content"


def test_services_directory_exists():
    assert os.path.isdir(SERVICES_DIR), f"Directory {SERVICES_DIR} does not exist"
    assert os.access(SERVICES_DIR, os.R_OK | os.W_OK), f"Directory {SERVICES_DIR} is not readable/writable"


def test_logs_directory_exists():
    assert os.path.isdir(LOGS_DIR), f"Directory {LOGS_DIR} does not exist"
    assert os.access(LOGS_DIR, os.R_OK | os.W_OK), f"Directory {LOGS_DIR} is not readable/writable"