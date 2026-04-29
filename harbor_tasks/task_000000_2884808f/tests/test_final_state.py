# test_final_state.py
"""
Tests to validate the final state after the student has fixed the broken
symlinks in the k8s manifest repo. The staging overlay should now work
with kubectl apply --dry-run=client.
"""

import os
import subprocess
import pytest

MANIFESTS_DIR = "/home/user/manifests"
BASE_DIR = os.path.join(MANIFESTS_DIR, "base")
ENVS_DIR = os.path.join(MANIFESTS_DIR, "envs")
STAGING_DIR = os.path.join(ENVS_DIR, "staging")
PROD_DIR = os.path.join(ENVS_DIR, "prod")


class TestBaseDirectoryUnchanged:
    """Verify the base directory structure remains unchanged (invariant)."""

    def test_base_dir_exists(self):
        assert os.path.isdir(BASE_DIR), f"Directory {BASE_DIR} does not exist"

    def test_base_services_dir_exists(self):
        services_dir = os.path.join(BASE_DIR, "services")
        assert os.path.isdir(services_dir), f"Directory {services_dir} does not exist"

    def test_base_config_dir_exists(self):
        config_dir = os.path.join(BASE_DIR, "config")
        assert os.path.isdir(config_dir), f"Directory {config_dir} does not exist"

    def test_base_configmaps_dir_still_does_not_exist(self):
        """The old configmaps/ directory should NOT have been recreated."""
        configmaps_dir = os.path.join(BASE_DIR, "configmaps")
        assert not os.path.exists(configmaps_dir), \
            f"Directory {configmaps_dir} should not exist - base/ structure must not be changed"

    def test_api_deployment_yaml_exists_in_services(self):
        filepath = os.path.join(BASE_DIR, "services", "api-deployment.yaml")
        assert os.path.isfile(filepath), f"File {filepath} does not exist"

    def test_api_service_yaml_exists_in_services(self):
        filepath = os.path.join(BASE_DIR, "services", "api-service.yaml")
        assert os.path.isfile(filepath), f"File {filepath} does not exist"

    def test_configmap_yaml_exists_in_config(self):
        filepath = os.path.join(BASE_DIR, "config", "configmap.yaml")
        assert os.path.isfile(filepath), f"File {filepath} does not exist"

    def test_no_api_service_yaml_in_base_root(self):
        """api-service.yaml should NOT have been moved back to base/ root."""
        filepath = os.path.join(BASE_DIR, "api-service.yaml")
        assert not os.path.exists(filepath), \
            f"File {filepath} should not exist - base/ structure must not be changed"


class TestStagingSymlinksAreSymlinks:
    """Verify staging files are still symlinks (not replaced with regular files)."""

    def test_staging_deployment_is_symlink(self):
        filepath = os.path.join(STAGING_DIR, "deployment.yaml")
        assert os.path.islink(filepath), \
            f"{filepath} must be a symbolic link, not a regular file"

    def test_staging_service_is_symlink(self):
        filepath = os.path.join(STAGING_DIR, "service.yaml")
        assert os.path.islink(filepath), \
            f"{filepath} must be a symbolic link, not a regular file (anti-shortcut: cannot replace symlink with copy)"

    def test_staging_configmap_is_symlink(self):
        filepath = os.path.join(STAGING_DIR, "configmap.yaml")
        assert os.path.islink(filepath), \
            f"{filepath} must be a symbolic link, not a regular file (anti-shortcut: cannot replace symlink with copy)"

    def test_staging_ingress_is_regular_file(self):
        """staging-ingress.yaml should remain a regular file."""
        filepath = os.path.join(STAGING_DIR, "staging-ingress.yaml")
        assert os.path.isfile(filepath), f"{filepath} should exist"
        assert not os.path.islink(filepath), f"{filepath} should be a regular file, not a symlink"


class TestStagingSymlinksAreValid:
    """Verify all staging symlinks now point to valid targets."""

    def test_staging_deployment_symlink_valid(self):
        filepath = os.path.join(STAGING_DIR, "deployment.yaml")
        assert os.path.exists(filepath), \
            f"Symlink {filepath} is broken - does not point to a valid target"

    def test_staging_service_symlink_valid(self):
        filepath = os.path.join(STAGING_DIR, "service.yaml")
        assert os.path.exists(filepath), \
            f"Symlink {filepath} is broken - must point to a valid target (should be fixed to point to base/services/api-service.yaml)"

    def test_staging_configmap_symlink_valid(self):
        filepath = os.path.join(STAGING_DIR, "configmap.yaml")
        assert os.path.exists(filepath), \
            f"Symlink {filepath} is broken - must point to a valid target (should be fixed to point to base/config/configmap.yaml)"


class TestStagingSymlinkTargets:
    """Verify staging symlinks point to correct paths in base/."""

    def test_staging_service_symlink_target(self):
        """service.yaml must point to base/services/api-service.yaml."""
        filepath = os.path.join(STAGING_DIR, "service.yaml")
        target = os.readlink(filepath)
        assert "base/services/api-service.yaml" in target or target.endswith("services/api-service.yaml"), \
            f"Symlink {filepath} must contain 'base/services/api-service.yaml' in target path, got: {target}"

    def test_staging_configmap_symlink_target(self):
        """configmap.yaml must point to base/config/configmap.yaml."""
        filepath = os.path.join(STAGING_DIR, "configmap.yaml")
        target = os.readlink(filepath)
        assert "base/config/configmap.yaml" in target or target.endswith("config/configmap.yaml"), \
            f"Symlink {filepath} must contain 'base/config/configmap.yaml' in target path, got: {target}"
        # Also verify it does NOT point to old configmaps/ path
        assert "configmaps" not in target, \
            f"Symlink {filepath} must NOT point to old 'configmaps' directory, got: {target}"


class TestKubectlApplyStagingSucceeds:
    """Verify kubectl apply --dry-run=client -f envs/staging/ now succeeds."""

    def test_kubectl_apply_staging_succeeds(self):
        """The main success criterion: kubectl apply dry-run should exit 0."""
        result = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", "envs/staging/"],
            cwd=MANIFESTS_DIR,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            f"kubectl apply --dry-run=client -f envs/staging/ failed with exit code {result.returncode}.\n" \
            f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_kubectl_apply_staging_outputs_all_resources(self):
        """Verify all four resources are processed in the dry-run output."""
        result = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", "envs/staging/"],
            cwd=MANIFESTS_DIR,
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr  # dry-run output may go to either

        # Check for Deployment resource
        assert "deployment" in output.lower() or "Deployment" in output, \
            f"Expected Deployment resource in dry-run output, got: {output}"

        # Check for Service resource
        assert "service" in output.lower() or "Service" in output, \
            f"Expected Service resource in dry-run output, got: {output}"

        # Check for ConfigMap resource
        assert "configmap" in output.lower() or "ConfigMap" in output, \
            f"Expected ConfigMap resource in dry-run output, got: {output}"

        # Check for Ingress resource
        assert "ingress" in output.lower() or "Ingress" in output, \
            f"Expected Ingress resource in dry-run output, got: {output}"


class TestFileCommandVerification:
    """Anti-shortcut verification using file command."""

    def test_file_command_shows_symlinks(self):
        """Verify 'file' command reports symbolic link for service.yaml and configmap.yaml."""
        result = subprocess.run(
            ["file", "envs/staging/service.yaml", "envs/staging/configmap.yaml"],
            cwd=MANIFESTS_DIR,
            capture_output=True,
            text=True
        )
        output = result.stdout.lower()

        # Both should be reported as symbolic links
        assert "symbolic link" in output, \
            f"'file' command should report 'symbolic link' for service.yaml and configmap.yaml, got: {result.stdout}"


class TestReadlinkVerification:
    """Anti-shortcut verification using readlink command."""

    def test_readlink_service_yaml(self):
        """readlink envs/staging/service.yaml must contain 'base/services/api-service.yaml'."""
        result = subprocess.run(
            ["readlink", "envs/staging/service.yaml"],
            cwd=MANIFESTS_DIR,
            capture_output=True,
            text=True
        )
        target = result.stdout.strip()
        assert "base/services/api-service.yaml" in target or target.endswith("services/api-service.yaml"), \
            f"readlink envs/staging/service.yaml must contain 'base/services/api-service.yaml', got: {target}"

    def test_readlink_configmap_yaml(self):
        """readlink envs/staging/configmap.yaml must contain 'base/config/configmap.yaml'."""
        result = subprocess.run(
            ["readlink", "envs/staging/configmap.yaml"],
            cwd=MANIFESTS_DIR,
            capture_output=True,
            text=True
        )
        target = result.stdout.strip()
        assert "base/config/configmap.yaml" in target or target.endswith("config/configmap.yaml"), \
            f"readlink envs/staging/configmap.yaml must contain 'base/config/configmap.yaml', got: {target}"


class TestProdNotMadeWorse:
    """Verify prod overlay was not made worse (files still exist as symlinks)."""

    def test_prod_deployment_still_exists(self):
        filepath = os.path.join(PROD_DIR, "deployment.yaml")
        assert os.path.islink(filepath), f"{filepath} should still be a symlink"

    def test_prod_service_still_exists(self):
        filepath = os.path.join(PROD_DIR, "service.yaml")
        assert os.path.islink(filepath), f"{filepath} should still be a symlink"

    def test_prod_configmap_still_exists(self):
        filepath = os.path.join(PROD_DIR, "configmap.yaml")
        assert os.path.islink(filepath), f"{filepath} should still be a symlink"

    def test_prod_ingress_still_exists(self):
        filepath = os.path.join(PROD_DIR, "prod-ingress.yaml")
        assert os.path.isfile(filepath), f"{filepath} should still exist"
