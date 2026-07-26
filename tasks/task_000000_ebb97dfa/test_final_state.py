# test_final_state.py
import os
import json
import pytest


# Define the base paths and expected files
BASE_DIR = "/home/user/api_docs"
REQUESTS_DIR = os.path.join(BASE_DIR, "requests")
SUMMARY_LOG_PATH = os.path.join(BASE_DIR, "results_summary.log")

# Expected files and their contents
EXPECTED_FILES = {
    os.path.join(REQUESTS_DIR, "get_response_users.json"): {
        "data": [
            {
                "id": 1,
                "username": "john",
                "email": "john@example.com"
            }
        ]
    },
    os.path.join(REQUESTS_DIR, "get_response_teams.json"): {
        "data": [
            {
                "id": 10,
                "name": "Engineering"
            }
        ]
    },
    os.path.join(REQUESTS_DIR, "get_response_projects.json"): {
        "data": [
            {
                "id": 5,
                "name": "Alpha",
                "status": "active"
            }
        ]
    },
    os.path.join(REQUESTS_DIR, "get_response_settings.json"): {
        "data": {
            "theme": "dark",
            "language": "en"
        }
    },
    os.path.join(REQUESTS_DIR, "post_response_users.json"): {
        "data": {
            "id": 2,
            "username": "newuser",
            "email": "newuser@example.com"
        }
    },
    os.path.join(REQUESTS_DIR, "put_response_projects.json"): {
        "data": {
            "id": 6,
            "name": "Project Beta",
            "status": "active"
        }
    },
}

EXPECTED_SUMMARY_LOG_LINES = [
    "2024-04-12 15:30:22 GET http://api.devtools.local:3000/users -> 200 OK",
    "2024-04-12 15:30:23 GET http://api.devtools.local:3000/teams -> 200 OK",
    "2024-04-12 15:30:23 GET http://api.devtools.local:3000/projects -> 200 OK",
    "2024-04-12 15:30:24 GET http://api.devtools.local:3000/settings -> 200 OK",
    "2024-04-12 15:30:25 POST http://api.devtools.local:3000/users -> 201 Created",
    "2024-04-12 15:30:26 PUT http://api.devtools.local:3000/projects -> 200 OK"
]


@pytest.mark.parametrize("path", EXPECTED_FILES.keys())
def test_expected_files_exist(path):
    assert os.path.exists(path), f"File {path} does not exist"


@pytest.mark.parametrize("path, content", EXPECTED_FILES.items())
def test_expected_file_content(path, content):
    with open(path, "r") as f:
        data = json.load(f)
    assert data == content, f"Content of file {path} does not match expected JSON"


def test_summary_log_exists():
    assert os.path.exists(SUMMARY_LOG_PATH), f"File {SUMMARY_LOG_PATH} does not exist"


def test_summary_log_content():
    with open(SUMMARY_LOG_PATH, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    assert lines == EXPECTED_SUMMARY_LOG_LINES, (
        f"Summary log content does not match expected lines:\n"
        f"Expected:\n{EXPECTED_SUMMARY_LOG_LINES}\n"
        f"Got:\n{lines}"
    )


def test_api_token_file_does_not_exist():
    api_token_path = "/home/user/.api_token"
    assert not os.path.exists(api_token_path), f"File {api_token_path} should not exist after the task is completed"