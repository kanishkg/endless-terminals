# test_initial_state.py
import os
import pytest

# Define the expected initial state
EXPECTED_DIR = "/home/user/python_env/hardened_env"
EXPECTED_OWNER = "user"
EXPECTED_GROUP = "user"
EXPECTED_PERMISSIONS = 0o755

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

def test_requirements_txt_not_exists():
    req_path = os.path.join(EXPECTED_DIR, "requirements.txt")
    assert not os.path.exists(req_path), f"File {req_path} already exists."

def test_audit_log_not_exists():
    audit_path = os.path.join(EXPECTED_DIR, "audit.log")
    assert not os.path.exists(audit_path), f"File {audit_path} already exists."

def test_global_site_packages_not_modified():
    import site
    assert not any(pkg for pkg in site.getsitepackages() if os.path.exists(os.path.join(pkg, "flask"))), (
        "Flask or other packages are installed globally, which is not allowed."
    )

def test_virtualenv_not_activated():
    import os
    assert "VIRTUAL_ENV" not in os.environ, "Virtual environment is already activated."

def test_no_virtualenv_binaries_present():
    bin_dir = os.path.join(EXPECTED_DIR, "bin")
    assert not os.path.exists(bin_dir), f"Virtualenv binaries already exist in {bin_dir}."