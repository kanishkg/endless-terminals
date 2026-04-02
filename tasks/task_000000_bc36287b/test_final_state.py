# test_final_state.py

import os
import re
import subprocess
import filecmp
import pytest

HOME_PATH = "/home/user"

MODIFIED_FILES = [
    f"{HOME_PATH}/modified_files/ssh_config",
    f"{HOME_PATH}/modified_files/iptables_rules",
    f"{HOME_PATH}/modified_files/cron_jobs",
]

ORIGINAL_FILES = [
    f"{HOME_PATH}/original_files/ssh_config_original",
    f"{HOME_PATH}/original_files/iptables_rules_original",
    f"{HOME_PATH}/original_files/cron_jobs_original",
]

LOG_FILE = f"{HOME_PATH}/reconciliation_log.txt"

# Compute expected diff bodies at test time from actual container files.
# This avoids hardcoding timestamps that change with each build.
def _diff_body(orig, modified):
    """Return diff -u output with timestamps stripped from header lines."""
    result = subprocess.run(["diff", "-u", orig, modified], capture_output=True, text=True)
    lines = result.stdout.splitlines()
    stripped = []
    for line in lines:
        if line.startswith("--- ") or line.startswith("+++ "):
            stripped.append(re.sub(r'\t\d{4}-\d{2}-\d{2}.*$', '', line))
        else:
            stripped.append(line)
    return "\n".join(stripped)

EXPECTED_DIFF_BODIES = [_diff_body(o, m) for o, m in zip(ORIGINAL_FILES, MODIFIED_FILES)]


def test_log_file_exists():
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} is missing."


def test_modified_files_restored():
    for modified, original in zip(MODIFIED_FILES, ORIGINAL_FILES):
        assert filecmp.cmp(modified, original, shallow=False), (
            f"File {modified} does not match its original version {original}."
        )


def test_log_content_matches_expected():
    with open(LOG_FILE, "r") as f:
        log_content = f.read()

    # Normalise timestamps in log content the same way
    def normalise(text):
        return re.sub(r'\t\d{4}-\d{2}-\d{2}[^\n]*', '', text)

    normalised_log = normalise(log_content)

    for modified, diff_body in zip(MODIFIED_FILES, EXPECTED_DIFF_BODIES):
        assert f"File: {modified}" in normalised_log, (
            f"Log missing entry for {modified}"
        )
        for line in diff_body.splitlines():
            if line.startswith("--- ") or line.startswith("+++ "):
                path = line[4:].split("\t")[0]
                assert path in normalised_log, f"Log missing diff path: {path}"
            elif line:
                assert line in normalised_log, (
                    f"Log missing diff line: {line!r}"
                )

    assert "Patch Applied Successfully: YES" in log_content, (
        "Log missing 'Patch Applied Successfully: YES'"
    )
    assert "Verification: File contents match original: YES" in log_content, (
        "Log missing 'Verification: File contents match original: YES'"
    )
