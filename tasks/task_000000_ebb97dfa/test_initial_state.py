# test_initial_state.py
import os
import pytest


@pytest.mark.parametrize("path", [
    "/home/user/api_docs/",
    "/home/user/api_docs/requests/"
])
def test_directories_exist(path):
    assert os.path.isdir(path), f"Directory {path} does not exist"


@pytest.mark.parametrize("path", [
    "/home/user/api_docs/requests/get_response_users.json",
    "/home/user/api_docs/requests/get_response_teams.json",
    "/home/user/api_docs/requests/get_response_projects.json",
    "/home/user/api_docs/requests/get_response_settings.json",
    "/home/user/api_docs/requests/post_response_users.json",
    "/home/user/api_docs/requests/put_response_projects.json",
    "/home/user/api_docs/results_summary.log"
])
def test_output_files_do_not_exist(path):
    assert not os.path.exists(path), f"File {path} should not exist before the task starts"


def test_api_token_file_does_not_exist():
    api_token_path = "/home/user/.api_token"
    assert not os.path.exists(api_token_path), f"File {api_token_path} should not exist before the task starts"