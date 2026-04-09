# test_initial_state.py
"""
Tests to validate the initial state of the operating system/filesystem
before the student performs the GPG encryption/signing task.
"""

import pytest
import os
import json
import hashlib


class TestInitialState:
    """Test the initial state before the task is performed."""

    def test_home_directory_exists(self):
        """Verify the home directory exists."""
        home_dir = "/home/user"
        assert os.path.isdir(home_dir), f"Home directory {home_dir} does not exist"

    def test_api_payload_file_exists(self):
        """Verify the api_payload.json file exists."""
        payload_file = "/home/user/api_payload.json"
        assert os.path.isfile(payload_file), (
            f"Required input file {payload_file} does not exist. "
            "This file must be present before the task can be performed."
        )

    def test_api_payload_file_is_readable(self):
        """Verify the api_payload.json file is readable."""
        payload_file = "/home/user/api_payload.json"
        assert os.access(payload_file, os.R_OK), (
            f"File {payload_file} exists but is not readable. "
            "The file must be readable for GPG operations."
        )

    def test_api_payload_file_is_valid_json(self):
        """Verify the api_payload.json file contains valid JSON."""
        payload_file = "/home/user/api_payload.json"
        try:
            with open(payload_file, 'r') as f:
                content = f.read()
                json.loads(content)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"File {payload_file} does not contain valid JSON: {e}"
            )
        except IOError as e:
            pytest.fail(
                f"Could not read file {payload_file}: {e}"
            )

    def test_api_payload_file_has_expected_structure(self):
        """Verify the api_payload.json file has the expected structure."""
        payload_file = "/home/user/api_payload.json"
        with open(payload_file, 'r') as f:
            data = json.load(f)

        # Check for expected keys in the JSON structure
        expected_keys = ["api_version", "endpoint", "method", "test_id", "payload"]
        for key in expected_keys:
            assert key in data, (
                f"File {payload_file} is missing expected key '{key}'. "
                f"Expected keys: {expected_keys}"
            )

        # Check payload sub-structure
        payload_keys = ["amount", "currency", "merchant_id"]
        for key in payload_keys:
            assert key in data["payload"], (
                f"File {payload_file} payload is missing expected key '{key}'. "
                f"Expected payload keys: {payload_keys}"
            )

    def test_api_payload_file_has_expected_content(self):
        """Verify the api_payload.json file has the expected content values."""
        payload_file = "/home/user/api_payload.json"
        with open(payload_file, 'r') as f:
            data = json.load(f)

        assert data["api_version"] == "2.1", (
            f"api_version should be '2.1', got '{data['api_version']}'"
        )
        assert data["endpoint"] == "/v2/transactions", (
            f"endpoint should be '/v2/transactions', got '{data['endpoint']}'"
        )
        assert data["method"] == "POST", (
            f"method should be 'POST', got '{data['method']}'"
        )
        assert data["test_id"] == "TX-20240115-001", (
            f"test_id should be 'TX-20240115-001', got '{data['test_id']}'"
        )
        assert data["payload"]["amount"] == 150.00, (
            f"payload.amount should be 150.00, got {data['payload']['amount']}"
        )
        assert data["payload"]["currency"] == "USD", (
            f"payload.currency should be 'USD', got '{data['payload']['currency']}'"
        )
        assert data["payload"]["merchant_id"] == "MERCH-9876", (
            f"payload.merchant_id should be 'MERCH-9876', got '{data['payload']['merchant_id']}'"
        )

    def test_api_payload_file_not_empty(self):
        """Verify the api_payload.json file is not empty."""
        payload_file = "/home/user/api_payload.json"
        file_size = os.path.getsize(payload_file)
        assert file_size > 0, (
            f"File {payload_file} is empty (0 bytes). "
            "The file must contain the API payload JSON."
        )

    def test_output_signature_file_does_not_exist(self):
        """Verify the output signature file does not exist yet."""
        sig_file = "/home/user/api_payload.json.sig"
        assert not os.path.exists(sig_file), (
            f"Output file {sig_file} already exists. "
            "This file should be created by the task, not exist beforehand."
        )

    def test_output_encrypted_file_does_not_exist(self):
        """Verify the output encrypted file does not exist yet."""
        gpg_file = "/home/user/api_payload.json.gpg"
        assert not os.path.exists(gpg_file), (
            f"Output file {gpg_file} already exists. "
            "This file should be created by the task, not exist beforehand."
        )

    def test_output_log_file_does_not_exist(self):
        """Verify the output log file does not exist yet."""
        log_file = "/home/user/gpg_test_results.log"
        assert not os.path.exists(log_file), (
            f"Output file {log_file} already exists. "
            "This file should be created by the task, not exist beforehand."
        )
