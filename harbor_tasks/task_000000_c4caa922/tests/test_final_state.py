# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the CSV to JSON conversion task.
"""

import os
import json
import subprocess
import pytest


class TestFinalState:
    """Test the final state after the task is performed."""

    def test_json_file_exists(self):
        """Verify the output JSON file exists."""
        json_path = "/home/user/restore/users.json"
        assert os.path.isfile(json_path), (
            f"JSON file {json_path} does not exist. "
            "The task requires creating this file."
        )

    def test_json_file_is_readable(self):
        """Verify the JSON file is readable."""
        json_path = "/home/user/restore/users.json"
        assert os.access(json_path, os.R_OK), (
            f"JSON file {json_path} is not readable."
        )

    def test_json_file_is_valid_json(self):
        """Verify the JSON file contains valid JSON."""
        json_path = "/home/user/restore/users.json"
        try:
            with open(json_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"JSON file {json_path} contains invalid JSON: {e}"
            )

    def test_json_parseable_by_python3_command(self):
        """Verify JSON is parseable by python3 command as specified."""
        result = subprocess.run(
            ["python3", "-c", "import json; json.load(open('/home/user/restore/users.json'))"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, (
            f"JSON file is not parseable by python3 command. "
            f"Error: {result.stderr}"
        )

    def test_json_is_array(self):
        """Verify the JSON root is an array."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list), (
            f"JSON root should be an array, but got {type(data).__name__}. "
            "The task requires an array of objects."
        )

    def test_json_has_three_objects(self):
        """Verify the JSON array contains exactly 3 objects."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        assert len(data) == 3, (
            f"JSON array should contain 3 objects, but contains {len(data)}. "
            "The CSV has 3 data rows that should be converted."
        )

    def test_json_objects_have_correct_keys(self):
        """Verify each JSON object has the required keys."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        required_keys = {"id", "name", "email", "created_at"}

        for i, obj in enumerate(data):
            assert isinstance(obj, dict), (
                f"Item {i} in JSON array should be an object, but got {type(obj).__name__}"
            )
            obj_keys = set(obj.keys())
            assert required_keys <= obj_keys, (
                f"Object {i} is missing required keys. "
                f"Required: {required_keys}, Found: {obj_keys}, "
                f"Missing: {required_keys - obj_keys}"
            )

    def test_first_record_alice_chen(self):
        """Verify the first record contains Alice Chen's data."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Find Alice Chen's record
        alice_record = None
        for obj in data:
            if obj.get("name") == "Alice Chen":
                alice_record = obj
                break

        assert alice_record is not None, (
            "No record found with name 'Alice Chen'. "
            "The JSON should contain Alice Chen's data from the CSV."
        )

        # Check id (could be string or int depending on conversion)
        assert str(alice_record.get("id")) == "1", (
            f"Alice Chen's id should be '1', got '{alice_record.get('id')}'"
        )

        assert alice_record.get("email") == "alice@example.com", (
            f"Alice Chen's email should be 'alice@example.com', "
            f"got '{alice_record.get('email')}'"
        )

        assert alice_record.get("created_at") == "2023-06-12", (
            f"Alice Chen's created_at should be '2023-06-12', "
            f"got '{alice_record.get('created_at')}'"
        )

    def test_second_record_bob_martinez(self):
        """Verify the second record contains Bob Martinez's data."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Find Bob Martinez's record
        bob_record = None
        for obj in data:
            if obj.get("name") == "Bob Martinez":
                bob_record = obj
                break

        assert bob_record is not None, (
            "No record found with name 'Bob Martinez'. "
            "The JSON should contain Bob Martinez's data from the CSV."
        )

        assert str(bob_record.get("id")) == "2", (
            f"Bob Martinez's id should be '2', got '{bob_record.get('id')}'"
        )

        assert bob_record.get("email") == "bob@example.com", (
            f"Bob Martinez's email should be 'bob@example.com', "
            f"got '{bob_record.get('email')}'"
        )

        assert bob_record.get("created_at") == "2023-08-24", (
            f"Bob Martinez's created_at should be '2023-08-24', "
            f"got '{bob_record.get('created_at')}'"
        )

    def test_third_record_carol_smith(self):
        """Verify the third record contains Carol Smith's data."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Find Carol Smith's record
        carol_record = None
        for obj in data:
            if obj.get("name") == "Carol Smith":
                carol_record = obj
                break

        assert carol_record is not None, (
            "No record found with name 'Carol Smith'. "
            "The JSON should contain Carol Smith's data from the CSV."
        )

        assert str(carol_record.get("id")) == "3", (
            f"Carol Smith's id should be '3', got '{carol_record.get('id')}'"
        )

        assert carol_record.get("email") == "carol@example.com", (
            f"Carol Smith's email should be 'carol@example.com', "
            f"got '{carol_record.get('email')}'"
        )

        assert carol_record.get("created_at") == "2024-01-03", (
            f"Carol Smith's created_at should be '2024-01-03', "
            f"got '{carol_record.get('created_at')}'"
        )

    def test_source_csv_unchanged(self):
        """Verify the source CSV file is unchanged (invariant)."""
        csv_path = "/home/user/backups/users_20240115.csv"

        assert os.path.isfile(csv_path), (
            f"Source CSV file {csv_path} no longer exists. "
            "The source file should remain unchanged."
        )

        with open(csv_path, 'r') as f:
            content = f.read()

        expected_content = """id,name,email,created_at
1,Alice Chen,alice@example.com,2023-06-12
2,Bob Martinez,bob@example.com,2023-08-24
3,Carol Smith,carol@example.com,2024-01-03"""

        content_normalized = content.strip()
        expected_normalized = expected_content.strip()

        assert content_normalized == expected_normalized, (
            f"Source CSV file has been modified. "
            f"Expected:\n{expected_normalized}\n\nGot:\n{content_normalized}"
        )

    def test_json_not_empty_array(self):
        """Anti-shortcut: Verify JSON is not an empty array."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        assert data != [], (
            "JSON file contains an empty array. "
            "It should contain 3 user records from the CSV."
        )

    def test_json_not_stub_data(self):
        """Anti-shortcut: Verify JSON contains actual data, not stubs."""
        json_path = "/home/user/restore/users.json"
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Check that we have actual email addresses from the CSV
        emails = [obj.get("email") for obj in data if isinstance(obj, dict)]
        expected_emails = {"alice@example.com", "bob@example.com", "carol@example.com"}

        assert expected_emails <= set(emails), (
            f"JSON does not contain all expected email addresses. "
            f"Expected: {expected_emails}, Found: {set(emails)}"
        )
