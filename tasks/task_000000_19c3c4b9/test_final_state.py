# test_final_state.py
import os
import pytest
import subprocess
import re

# Define expected paths and values
EXPECTED_DIR = "/home/user/python_env/hardened_env"
EXPECTED_OWNER = "user"
EXPECTED_GROUP = "user"
EXPECTED_PERMISSIONS = 0o755

EXPECTED_REQUIREMENTS_TXT_CONTENT = """flask==2.0.1
requests==2.26.0
pycryptodome==3.10.1
pytz==2021.3
"""

EXPECTED_AUDIT_LOG_CONTENT = """flask==2.0.1: secure
requests==2.26.0: secure
pycryptodome==3.10.1: secure
pytz==2021.3: secure
"""

EXPECTED_INSTALLED_PACKAGES = {
    "flask": "2.0.1",
    "requests": "2.26.0",
    "pycryptodome": "3.10.1",
    "pytz": "2021.3",
}

def test_virtualenv_directory_exists():
    assert os.path.isdir(EXPECTED_DIR), f"Directory {EXPECTED_DIR} does not exist."

def test_virtualenv_directory_permissions():
    mode = os.stat(EXPECTED_DIR).st_mode
    assert oct(mode & 0o777) == oct(EXPECTED_PERMISSIONS), (
        f"Permissions on {EXPECTED_DIR} are incorrect. "
        f"Expected {oct(EXPECTED_PERMISSIONS)}, got {oct(mode & 0o777)}"
    )

def test_virtualenv_directory_ownership():
    import pwd, grp
    stat = os.stat(EXPECTED_DIR)
    uid = stat.st_uid
    gid = stat.st_gid
    user = pwd.getpwuid(uid).pw_name
    group = grp.getgrgid(gid).gr_name
    assert user == EXPECTED_OWNER, f"Owner of {EXPECTED_DIR} is not {EXPECTED_OWNER}, got {user}"
    assert group == EXPECTED_GROUP, f"Group of {EXPECTED_DIR} is not {EXPECTED_GROUP}, got {group}"

def test_requirements_txt_exists_and_has_correct_content():
    req_path = os.path.join(EXPECTED_DIR, "requirements.txt")
    assert os.path.exists(req_path), f"File {req_path} does not exist."
    with open(req_path, "r") as f:
        content = f.read()
    assert content == EXPECTED_REQUIREMENTS_TXT_CONTENT, (
        f"Content of {req_path} is incorrect.\nExpected:\n{EXPECTED_REQUIREMENTS_TXT_CONTENT}\nGot:\n{content}"
    )

def test_audit_log_exists_and_has_correct_content():
    audit_path = os.path.join(EXPECTED_DIR, "audit.log")
    assert os.path.exists(audit_path), f"File {audit_path} does not exist."
    with open(audit_path, "r") as f:
        content = f.read()
    assert content == EXPECTED_AUDIT_LOG_CONTENT, (
        f"Content of {audit_path} is incorrect.\nExpected:\n{EXPECTED_AUDIT_LOG_CONTENT}\nGot:\n{content}"
    )

def test_virtualenv_activated():
    assert "VIRTUAL_ENV" in os.environ, "Virtual environment is not activated."
    assert os.environ["VIRTUAL_ENV"] == EXPECTED_DIR, (
        f"Virtual environment is activated, but not the correct one. "
        f"Expected {EXPECTED_DIR}, got {os.environ['VIRTUAL_ENV']}"
    )

def test_correct_packages_installed():
    # Run pip freeze inside the virtual environment
    pip_freeze_path = os.path.join(EXPECTED_DIR, "bin", "pip")
    result = subprocess.run(
        [pip_freeze_path, "freeze"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Failed to run pip freeze: {result.stderr}"

    installed_packages = {}
    for line in result.stdout.splitlines():
        if "==" in line:
            name, version = line.split("==", 1)
            installed_packages[name.lower()] = version.strip()

    for name, version in EXPECTED_INSTALLED_PACKAGES.items():
        assert name in installed_packages, f"Package {name} is not installed."
        assert installed_packages[name] == version, (
            f"Version of {name} is incorrect. Expected {version}, got {installed_packages[name]}"
        )

def test_no_global_packages_installed():
    # Ensure no packages are installed outside the virtualenv
    pip_global_path = "pip"
    result = subprocess.run(
        [pip_global_path, "list"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Failed to run pip list: {result.stderr}"

    for line in result.stdout.splitlines():
        if "==" in line:
            name, version = line.split("==", 1)
            # Skip the pip package itself
            if name.lower() == "pip":
                continue
            assert name.lower() not in EXPECTED_INSTALLED_PACKAGES, (
                f"Package {name} is installed globally. This is not allowed."
            )