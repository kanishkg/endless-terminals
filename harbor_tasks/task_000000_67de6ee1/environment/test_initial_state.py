# test_initial_state.py
"""
Tests to validate the initial state of the iOS CI build environment
before the student fixes the signing identity issue.
"""

import os
import subprocess
import stat
import pytest


PROJECT_ROOT = "/home/user/mobile-ci"
BUILD_SCRIPT = f"{PROJECT_ROOT}/scripts/build.sh"
FASTLANE_STUB = f"{PROJECT_ROOT}/scripts/fastlane_stub.sh"
BASE_ENV = f"{PROJECT_ROOT}/config/base.env"
CI_ENV = f"{PROJECT_ROOT}/config/ci.env"


class TestProjectStructure:
    """Test that the project directory structure exists."""

    def test_project_root_exists(self):
        """Project root directory must exist."""
        assert os.path.isdir(PROJECT_ROOT), f"Project root {PROJECT_ROOT} does not exist"

    def test_scripts_directory_exists(self):
        """Scripts directory must exist."""
        scripts_dir = f"{PROJECT_ROOT}/scripts"
        assert os.path.isdir(scripts_dir), f"Scripts directory {scripts_dir} does not exist"

    def test_config_directory_exists(self):
        """Config directory must exist."""
        config_dir = f"{PROJECT_ROOT}/config"
        assert os.path.isdir(config_dir), f"Config directory {config_dir} does not exist"


class TestBuildScript:
    """Test the build.sh script exists and has correct content."""

    def test_build_script_exists(self):
        """build.sh must exist."""
        assert os.path.isfile(BUILD_SCRIPT), f"Build script {BUILD_SCRIPT} does not exist"

    def test_build_script_is_executable(self):
        """build.sh must be executable."""
        assert os.access(BUILD_SCRIPT, os.X_OK), f"Build script {BUILD_SCRIPT} is not executable"

    def test_build_script_sources_base_env(self):
        """build.sh must source base.env."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        assert "source /home/user/mobile-ci/config/base.env" in content or \
               ". /home/user/mobile-ci/config/base.env" in content, \
               "build.sh must source base.env"

    def test_build_script_sources_ci_env(self):
        """build.sh must source ci.env."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        assert "source /home/user/mobile-ci/config/ci.env" in content or \
               ". /home/user/mobile-ci/config/ci.env" in content, \
               "build.sh must source ci.env"

    def test_build_script_has_legacy_shim(self):
        """build.sh must have the legacy compatibility shim with the problematic syntax."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        # Check for the specific problematic pattern
        assert 'CODE_SIGN_IDENTITY="${CODE_SIGN_IDENTITY:-}"' in content, \
               "build.sh must contain the legacy compatibility shim with ${CODE_SIGN_IDENTITY:-}"

    def test_build_script_calls_fastlane_stub(self):
        """build.sh must call fastlane_stub.sh."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        assert "fastlane_stub.sh" in content, "build.sh must call fastlane_stub.sh"


class TestFastlaneStub:
    """Test the fastlane stub script exists and has correct content."""

    def test_fastlane_stub_exists(self):
        """fastlane_stub.sh must exist."""
        assert os.path.isfile(FASTLANE_STUB), f"Fastlane stub {FASTLANE_STUB} does not exist"

    def test_fastlane_stub_is_executable(self):
        """fastlane_stub.sh must be executable."""
        assert os.access(FASTLANE_STUB, os.X_OK), f"Fastlane stub {FASTLANE_STUB} is not executable"

    def test_fastlane_stub_checks_code_sign_identity(self):
        """fastlane_stub.sh must check for CODE_SIGN_IDENTITY."""
        with open(FASTLANE_STUB, 'r') as f:
            content = f.read()
        assert 'if [ -z "$CODE_SIGN_IDENTITY" ]' in content, \
               "fastlane_stub.sh must check if CODE_SIGN_IDENTITY is empty"

    def test_fastlane_stub_has_error_message(self):
        """fastlane_stub.sh must output the specific error message."""
        with open(FASTLANE_STUB, 'r') as f:
            content = f.read()
        assert "Missing required signing identity" in content, \
               "fastlane_stub.sh must contain the error message 'Missing required signing identity'"

    def test_fastlane_stub_checks_provisioning_profile(self):
        """fastlane_stub.sh must check for PROVISIONING_PROFILE_SPECIFIER."""
        with open(FASTLANE_STUB, 'r') as f:
            content = f.read()
        assert 'PROVISIONING_PROFILE_SPECIFIER' in content, \
               "fastlane_stub.sh must check PROVISIONING_PROFILE_SPECIFIER"


class TestBaseEnv:
    """Test the base.env configuration file."""

    def test_base_env_exists(self):
        """base.env must exist."""
        assert os.path.isfile(BASE_ENV), f"Base env file {BASE_ENV} does not exist"

    def test_base_env_has_code_sign_identity(self):
        """base.env must define CODE_SIGN_IDENTITY with the correct value."""
        with open(BASE_ENV, 'r') as f:
            content = f.read()
        assert 'CODE_SIGN_IDENTITY="iPhone Distribution: ACME Corp (ABC123)"' in content, \
               "base.env must define CODE_SIGN_IDENTITY with the iPhone Distribution identity"

    def test_base_env_has_profile_spec(self):
        """base.env must define PROFILE_SPEC."""
        with open(BASE_ENV, 'r') as f:
            content = f.read()
        assert 'PROFILE_SPEC=ACME_AppStore_Profile' in content, \
               "base.env must define PROFILE_SPEC=ACME_AppStore_Profile"

    def test_base_env_has_team_id(self):
        """base.env must define TEAM_ID."""
        with open(BASE_ENV, 'r') as f:
            content = f.read()
        assert 'TEAM_ID=ABC123XYZ' in content, \
               "base.env must define TEAM_ID=ABC123XYZ"

    def test_base_env_has_bundle_id(self):
        """base.env must define BUNDLE_ID."""
        with open(BASE_ENV, 'r') as f:
            content = f.read()
        assert 'BUNDLE_ID=com.acme.app' in content, \
               "base.env must define BUNDLE_ID=com.acme.app"


class TestCiEnv:
    """Test the ci.env configuration file - this contains the bug."""

    def test_ci_env_exists(self):
        """ci.env must exist."""
        assert os.path.isfile(CI_ENV), f"CI env file {CI_ENV} does not exist"

    def test_ci_env_has_profile_spec_override(self):
        """ci.env must override PROFILE_SPEC to ACME_CI_Profile."""
        with open(CI_ENV, 'r') as f:
            content = f.read()
        assert 'PROFILE_SPEC=ACME_CI_Profile' in content, \
               "ci.env must override PROFILE_SPEC to ACME_CI_Profile"

    def test_ci_env_has_buggy_code_sign_identity(self):
        """ci.env must have the buggy empty CODE_SIGN_IDENTITY assignment."""
        with open(CI_ENV, 'r') as f:
            content = f.read()
        # The bug: CODE_SIGN_IDENTITY is set to empty string
        # This should be a line like "CODE_SIGN_IDENTITY=" (empty assignment)
        lines = content.split('\n')
        has_empty_assignment = False
        for line in lines:
            stripped = line.strip()
            # Check for explicit empty assignment (not a comment)
            if stripped == 'CODE_SIGN_IDENTITY=' or stripped == 'CODE_SIGN_IDENTITY=""' or stripped == "CODE_SIGN_IDENTITY=''":
                has_empty_assignment = True
                break
        assert has_empty_assignment, \
               "ci.env must have the buggy empty CODE_SIGN_IDENTITY= assignment (this is the bug to fix)"

    def test_ci_env_has_build_number(self):
        """ci.env must define BUILD_NUMBER."""
        with open(CI_ENV, 'r') as f:
            content = f.read()
        assert 'BUILD_NUMBER' in content, \
               "ci.env must define BUILD_NUMBER"


class TestBuildCurrentlyFails:
    """Test that the build currently fails with the signing identity error."""

    def test_build_fails_with_signing_error(self):
        """Running build.sh must currently fail with the signing identity error."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        assert result.returncode != 0, \
               "Build should currently fail (this is the bug state)"
        assert "Missing required signing identity" in result.stderr, \
               f"Build should fail with 'Missing required signing identity' error, got: {result.stderr}"

    def test_build_shows_empty_identity_search(self):
        """The error should indicate searching for an empty identity."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        # The stub outputs: "Searched for identity matching: ''"
        assert "Searched for identity matching: ''" in result.stderr, \
               f"Build error should show empty identity search, got: {result.stderr}"


class TestBashAvailable:
    """Test that bash is available for running scripts."""

    def test_bash_exists(self):
        """bash must be available."""
        result = subprocess.run(['which', 'bash'], capture_output=True, text=True)
        assert result.returncode == 0, "bash must be available on the system"

    def test_bash_can_execute(self):
        """bash must be able to execute simple commands."""
        result = subprocess.run(['bash', '-c', 'echo test'], capture_output=True, text=True)
        assert result.returncode == 0, "bash must be able to execute commands"
        assert 'test' in result.stdout, "bash must produce expected output"


class TestWriteAccess:
    """Test that the agent has write access to necessary locations."""

    def test_project_root_writable(self):
        """Project root must be writable."""
        assert os.access(PROJECT_ROOT, os.W_OK), f"Project root {PROJECT_ROOT} must be writable"

    def test_config_dir_writable(self):
        """Config directory must be writable."""
        config_dir = f"{PROJECT_ROOT}/config"
        assert os.access(config_dir, os.W_OK), f"Config directory {config_dir} must be writable"

    def test_scripts_dir_writable(self):
        """Scripts directory must be writable."""
        scripts_dir = f"{PROJECT_ROOT}/scripts"
        assert os.access(scripts_dir, os.W_OK), f"Scripts directory {scripts_dir} must be writable"

    def test_ci_env_writable(self):
        """ci.env must be writable (for fixing the bug)."""
        assert os.access(CI_ENV, os.W_OK), f"CI env file {CI_ENV} must be writable"

    def test_build_script_writable(self):
        """build.sh must be writable (in case fix is there)."""
        assert os.access(BUILD_SCRIPT, os.W_OK), f"Build script {BUILD_SCRIPT} must be writable"
