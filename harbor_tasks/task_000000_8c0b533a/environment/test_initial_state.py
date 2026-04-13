# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
performs the JSON to CSV conversion task.
"""

import json
import os
import pytest


class TestInitialState:
    """Tests to verify the initial filesystem state before task execution."""

    def test_data_directory_exists(self):
        """Verify that /home/user/data/ directory exists."""
        data_dir = "/home/user/data"
        assert os.path.exists(data_dir), (
            f"Directory {data_dir} does not exist. "
            "The data directory must be present before starting the task."
        )
        assert os.path.isdir(data_dir), (
            f"{data_dir} exists but is not a directory. "
            "Expected a directory at this path."
        )

    def test_data_directory_is_readable(self):
        """Verify that /home/user/data/ directory has read permissions."""
        data_dir = "/home/user/data"
        assert os.access(data_dir, os.R_OK), (
            f"Directory {data_dir} is not readable. "
            "The user must have read permissions on the data directory."
        )

    def test_users_json_file_exists(self):
        """Verify that the input JSON file exists at the expected location."""
        json_file = "/home/user/data/users.json"
        assert os.path.exists(json_file), (
            f"Input file {json_file} does not exist. "
            "The users.json file must be present before starting the task."
        )
        assert os.path.isfile(json_file), (
            f"{json_file} exists but is not a regular file. "
            "Expected a file at this path."
        )

    def test_users_json_file_is_readable(self):
        """Verify that the input JSON file has read permissions."""
        json_file = "/home/user/data/users.json"
        assert os.access(json_file, os.R_OK), (
            f"File {json_file} is not readable. "
            "The user must have read permissions on the input file."
        )

    def test_users_json_contains_valid_json(self):
        """Verify that the input file contains valid JSON."""
        json_file = "/home/user/data/users.json"
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {json_file} does not contain valid JSON. "
                f"JSON parsing error: {e}"
            )

    def test_users_json_contains_array(self):
        """Verify that the JSON file contains an array at the root level."""
        json_file = "/home/user/data/users.json"
        with open(json_file, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list), (
            f"The JSON file {json_file} should contain an array at the root level. "
            f"Found type: {type(data).__name__}"
        )

    def test_users_json_contains_three_users(self):
        """Verify that the JSON file contains exactly 3 user objects."""
        json_file = "/home/user/data/users.json"
        with open(json_file, 'r') as f:
            data = json.load(f)

        assert len(data) == 3, (
            f"The JSON file should contain exactly 3 users. "
            f"Found {len(data)} users."
        )

    def test_users_json_has_required_fields(self):
        """Verify that each user object has the required fields."""
        json_file = "/home/user/data/users.json"
        required_fields = {"id", "name", "email", "signup_date"}

        with open(json_file, 'r') as f:
            data = json.load(f)

        for i, user in enumerate(data):
            assert isinstance(user, dict), (
                f"User at index {i} is not a dictionary/object. "
                f"Found type: {type(user).__name__}"
            )
            missing_fields = required_fields - set(user.keys())
            assert not missing_fields, (
                f"User at index {i} is missing required fields: {missing_fields}. "
                f"Each user must have: {required_fields}"
            )

    def test_users_json_content_matches_expected(self):
        """Verify that the JSON file contains the expected user data."""
        json_file = "/home/user/data/users.json"

        expected_data = [
            {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "signup_date": "2024-01-15"},
            {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "signup_date": "2024-02-20"},
            {"id": 3, "name": "Carol Davis", "email": "carol@example.com", "signup_date": "2024-03-10"}
        ]

        with open(json_file, 'r') as f:
            data = json.load(f)

        assert data == expected_data, (
            f"The content of {json_file} does not match the expected user data.\n"
            f"Expected:\n{json.dumps(expected_data, indent=2)}\n"
            f"Found:\n{json.dumps(data, indent=2)}"
        )

    def test_output_directory_does_not_exist(self):
        """Verify that /home/user/output/ directory does NOT exist initially."""
        output_dir = "/home/user/output"
        assert not os.path.exists(output_dir), (
            f"Directory {output_dir} already exists. "
            "The output directory should NOT exist initially - "
            "the student must create it as part of the task."
        )

    def test_output_csv_does_not_exist(self):
        """Verify that the output CSV file does NOT exist initially."""
        output_file = "/home/user/output/users.csv"
        assert not os.path.exists(output_file), (
            f"Output file {output_file} already exists. "
            "The output file should NOT exist initially - "
            "the student must create it as part of the task."
        )

    def test_home_user_directory_exists(self):
        """Verify that /home/user directory exists."""
        home_dir = "/home/user"
        assert os.path.exists(home_dir), (
            f"Home directory {home_dir} does not exist. "
            "The user's home directory must be present."
        )
        assert os.path.isdir(home_dir), (
            f"{home_dir} exists but is not a directory."
        )
