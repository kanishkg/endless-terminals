# test_final_state.py
import os
import hashlib
import pytest

HOME_DIR = "/home/user"
CONFIG_DIR = f"{HOME_DIR}/config/network"
LOGS_DIR = f"{HOME_DIR}/logs"

CONFIG_YAML = f"{CONFIG_DIR}/config.yaml"
NEW_CONFIG_YAML = f"{CONFIG_DIR}/new-config.yaml"
ORIGINAL_CONFIG_YAML = f"{CONFIG_DIR}/original-config.yaml"
DIFF_FILE = f"{CONFIG_DIR}/config.diff"
LOG_FILE = f"{LOGS_DIR}/patch_verification.log"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()


def test_directories_present():
    assert os.path.isdir(CONFIG_DIR), f"Directory {CONFIG_DIR} does not exist."
    assert os.path.isdir(LOGS_DIR), f"Directory {LOGS_DIR} does not exist."


def test_required_files_present():
    for path in [CONFIG_YAML, NEW_CONFIG_YAML, ORIGINAL_CONFIG_YAML, DIFF_FILE, LOG_FILE]:
        assert os.path.isfile(path), f"File {path} does not exist."


def test_patch_applied_correctly():
    """original-config.yaml should have been patched to match new-config.yaml."""
    new_checksum = sha256(NEW_CONFIG_YAML)
    updated_checksum = sha256(ORIGINAL_CONFIG_YAML)
    assert updated_checksum == new_checksum, (
        f"Patch failed: checksum of original-config.yaml after patching ({updated_checksum}) "
        f"does not match new-config.yaml ({new_checksum})"
    )


def test_log_file_content():
    with open(LOG_FILE, "r") as f:
        content = f.read()

    # Must reference the key files
    assert "original-config.yaml" in content, "Log missing reference to original-config.yaml"
    assert "new-config.yaml" in content, "Log missing reference to new-config.yaml"
    assert "config.diff" in content, "Log missing reference to config.diff"

    # Must contain a patch command
    assert "patch" in content, "Log missing patch command"

    # Must contain checksums — compute the real ones at test time
    new_checksum = sha256(NEW_CONFIG_YAML)
    assert new_checksum in content, (
        f"Log missing correct checksum for new-config.yaml ({new_checksum})"
    )

    # Must indicate success
    assert "SUCCESS" in content.upper(), "Log missing success indicator"
