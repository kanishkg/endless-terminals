# test_final_state.py
"""
Tests to validate the final state of the iOS CI build environment
after the student has fixed the signing identity issue.
"""

import os
import subprocess
import hashlib
import pytest


PROJECT_ROOT = "/home/user/mobile-ci"
BUILD_SCRIPT = f"{PROJECT_ROOT}/scripts/build.sh"
FASTLANE_STUB = f"{PROJECT_ROOT}/scripts/fastlane_stub.sh"
BASE_ENV = f"{PROJECT_ROOT}/config/base.env"
CI_ENV = f"{PROJECT_ROOT}/config/ci.env"

# Expected values
EXPECTED_CODE_SIGN_IDENTITY = "iPhone Distribution: ACME Corp (ABC123)"
EXPECTED_PROFILE_SPEC = "ACME_CI_Profile"

# SHA256 of the original fastlane_stub.sh content
ORIGINAL_FASTLANE_STUB_CONTENT = '''#!/bin/bash
# Stub for fastlane gym
if [ -z "$CODE_SIGN_IDENTITY" ]; then
    echo "Error: Missing required signing identity" >&2
    echo "Searched for identity matching: ''" >&2
    exit 1
fi

if [ -z "$PROVISIONING_PROFILE_SPECIFIER" ]; then
    echo "Error: Missing provisioning profile" >&2
    exit 1
fi

echo "Build succeeded with identity: $CODE_SIGN_IDENTITY"
echo "Using profile: $PROVISIONING_PROFILE_SPECIFIER"
echo "Team: $TEAM_ID"
echo "Bundle: $BUNDLE_ID"
exit 0
'''


class TestBuildSucceeds:
    """Test that the build now succeeds with correct output."""

    def test_build_exits_zero(self):
        """Running build.sh must now exit with code 0."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        assert result.returncode == 0, \
            f"Build should succeed (exit 0), but got exit code {result.returncode}.\n" \
            f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_build_output_has_correct_identity(self):
        """Build output must show the correct signing identity."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        expected_msg = f"Build succeeded with identity: {EXPECTED_CODE_SIGN_IDENTITY}"
        assert expected_msg in result.stdout, \
            f"Build output must contain '{expected_msg}'.\n" \
            f"Actual stdout: {result.stdout}"

    def test_build_output_has_ci_profile(self):
        """Build output must show the CI profile (ci.env override must work)."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        expected_msg = f"Using profile: {EXPECTED_PROFILE_SPEC}"
        assert expected_msg in result.stdout, \
            f"Build output must contain '{expected_msg}'.\n" \
            f"ci.env override for PROFILE_SPEC must still work.\n" \
            f"Actual stdout: {result.stdout}"

    def test_no_signing_error_in_output(self):
        """Build must not produce the signing identity error."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        assert "Missing required signing identity" not in result.stderr, \
            f"Build should not produce signing identity error.\nstderr: {result.stderr}"
        assert "Missing required signing identity" not in result.stdout, \
            f"Build should not produce signing identity error.\nstdout: {result.stdout}"


class TestFastlaneStubUnmodified:
    """Test that fastlane_stub.sh was not modified (anti-shortcut guard)."""

    def test_fastlane_stub_exists(self):
        """fastlane_stub.sh must still exist."""
        assert os.path.isfile(FASTLANE_STUB), \
            f"Fastlane stub {FASTLANE_STUB} must exist"

    def test_fastlane_stub_byte_identical(self):
        """fastlane_stub.sh must be byte-identical to the original."""
        with open(FASTLANE_STUB, 'r') as f:
            actual_content = f.read()

        # Calculate SHA256 of both
        expected_hash = hashlib.sha256(ORIGINAL_FASTLANE_STUB_CONTENT.encode()).hexdigest()
        actual_hash = hashlib.sha256(actual_content.encode()).hexdigest()

        assert actual_hash == expected_hash, \
            f"fastlane_stub.sh must be byte-identical to original.\n" \
            f"Expected SHA256: {expected_hash}\n" \
            f"Actual SHA256: {actual_hash}\n" \
            f"The fix must be in env files or build.sh, not by modifying fastlane behavior."


class TestLayeredEnvStructure:
    """Test that the layered environment loading structure is preserved."""

    def test_build_script_still_sources_base_env(self):
        """build.sh must still source base.env."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        sources_base = ("source /home/user/mobile-ci/config/base.env" in content or
                       ". /home/user/mobile-ci/config/base.env" in content or
                       "source ${" in content and "base.env" in content)
        # Also check for variable-based paths
        if not sources_base:
            sources_base = "base.env" in content and ("source" in content or ". " in content)
        assert sources_base, \
            "build.sh must still source base.env - layered loading structure must remain"

    def test_build_script_still_sources_ci_env(self):
        """build.sh must still source ci.env."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()
        sources_ci = ("source /home/user/mobile-ci/config/ci.env" in content or
                     ". /home/user/mobile-ci/config/ci.env" in content)
        # Also check for variable-based paths
        if not sources_ci:
            sources_ci = "ci.env" in content and ("source" in content or ". " in content)
        assert sources_ci, \
            "build.sh must still source ci.env - cannot remove ci.env from loading chain"

    def test_ci_env_still_exists(self):
        """ci.env must still exist."""
        assert os.path.isfile(CI_ENV), \
            f"ci.env must still exist at {CI_ENV}"

    def test_base_env_still_exists(self):
        """base.env must still exist."""
        assert os.path.isfile(BASE_ENV), \
            f"base.env must still exist at {BASE_ENV}"


class TestNoHardcodedIdentityInBuildScript:
    """Test that CODE_SIGN_IDENTITY is not hardcoded in build.sh after source commands."""

    def test_no_hardcoded_identity_export(self):
        """build.sh must not have CODE_SIGN_IDENTITY hardcoded with the iPhone value."""
        with open(BUILD_SCRIPT, 'r') as f:
            content = f.read()

        # Check that there's no line like: export CODE_SIGN_IDENTITY="iPhone...
        import re
        pattern = r'^export\s+CODE_SIGN_IDENTITY="iPhone'
        matches = re.findall(pattern, content, re.MULTILINE)

        assert len(matches) == 0, \
            f"build.sh must not hardcode CODE_SIGN_IDENTITY with the iPhone value.\n" \
            f"Found: {matches}\n" \
            f"The identity must come from the env layer, not be hardcoded in build.sh"


class TestCiEnvStillOverridesProfileSpec:
    """Test that ci.env still successfully overrides PROFILE_SPEC."""

    def test_ci_env_has_profile_spec_override(self):
        """ci.env must still contain PROFILE_SPEC=ACME_CI_Profile."""
        with open(CI_ENV, 'r') as f:
            content = f.read()
        assert 'PROFILE_SPEC=ACME_CI_Profile' in content, \
            "ci.env must still override PROFILE_SPEC to ACME_CI_Profile"

    def test_profile_spec_override_works(self):
        """The PROFILE_SPEC override from ci.env must actually work in the build."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        # The build output should show ACME_CI_Profile, not ACME_AppStore_Profile
        assert "ACME_CI_Profile" in result.stdout, \
            f"ci.env's PROFILE_SPEC override must work - expected ACME_CI_Profile in output.\n" \
            f"stdout: {result.stdout}"
        assert "ACME_AppStore_Profile" not in result.stdout, \
            f"base.env's PROFILE_SPEC should be overridden by ci.env.\n" \
            f"stdout: {result.stdout}"


class TestCodeSignIdentityResolvesCorrectly:
    """Test that CODE_SIGN_IDENTITY resolves to the correct value."""

    def test_identity_is_from_base_env(self):
        """The CODE_SIGN_IDENTITY must resolve to the value from base.env."""
        result = subprocess.run(
            ['bash', BUILD_SCRIPT],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        assert EXPECTED_CODE_SIGN_IDENTITY in result.stdout, \
            f"CODE_SIGN_IDENTITY must resolve to '{EXPECTED_CODE_SIGN_IDENTITY}'.\n" \
            f"stdout: {result.stdout}"

    def test_identity_not_empty(self):
        """CODE_SIGN_IDENTITY must not be empty in the build environment."""
        # Run a command that prints the variable value
        result = subprocess.run(
            ['bash', '-c', f'source {BASE_ENV} && source {CI_ENV} && echo "IDENTITY=$CODE_SIGN_IDENTITY"'],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT
        )
        # After fix, this should show the identity (either ci.env was fixed or build.sh handles it)
        # The actual test is that the build succeeds, but we verify the env loading here
        # Note: This test may show empty if the fix is in build.sh's handling
        # The definitive test is that the build succeeds with correct output


class TestFilesStillReadable:
    """Test that all required files are still readable and valid."""

    def test_build_script_is_valid_bash(self):
        """build.sh must be valid bash syntax."""
        result = subprocess.run(
            ['bash', '-n', BUILD_SCRIPT],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"build.sh must have valid bash syntax.\nError: {result.stderr}"

    def test_base_env_is_sourceable(self):
        """base.env must be sourceable without errors."""
        result = subprocess.run(
            ['bash', '-c', f'source {BASE_ENV}'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"base.env must be sourceable.\nError: {result.stderr}"

    def test_ci_env_is_sourceable(self):
        """ci.env must be sourceable without errors."""
        result = subprocess.run(
            ['bash', '-c', f'source {CI_ENV}'],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"ci.env must be sourceable.\nError: {result.stderr}"


class TestBuildScriptExecutable:
    """Test that build.sh remains executable."""

    def test_build_script_is_executable(self):
        """build.sh must be executable."""
        assert os.access(BUILD_SCRIPT, os.X_OK), \
            f"build.sh must be executable"

    def test_fastlane_stub_is_executable(self):
        """fastlane_stub.sh must be executable."""
        assert os.access(FASTLANE_STUB, os.X_OK), \
            f"fastlane_stub.sh must be executable"
