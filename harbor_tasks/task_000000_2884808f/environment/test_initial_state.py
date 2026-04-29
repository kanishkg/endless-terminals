# test_initial_state.py
"""
Tests to validate the initial state of the filesystem before the student
fixes the broken symlinks in the k8s manifest repo.
"""

import os
import subprocess
import pytest

MANIFESTS_DIR = "/home/user/manifests"
BASE_DIR = os.path.join(MANIFESTS_DIR, "base")
ENVS_DIR = os.path.join(MANIFESTS_DIR, "envs")
STAGING_DIR = os.path.join(ENVS_DIR, "staging")
PROD_DIR = os.path.join(ENVS_DIR, "prod")


class TestBaseDirectoryStructure:
    """Verify the base directory structure exists with valid manifests."""

    def test_manifests_dir_exists(self):
        assert os.path.isdir(MANIFESTS_DIR), f"Directory {MANIFESTS_DIR} does not exist"

    def test_base_dir_exists(self):
        assert os.path.isdir(BASE_DIR), f"Directory {BASE_DIR} does not exist"

    def test_base_services_dir_exists(self):
        services_dir = os.path.join(BASE_DIR, "services")
        assert os.path.isdir(services_dir), f"Directory {services_dir} does not exist"

    def test_base_config_dir_exists(self):
        config_dir = os.path.join(BASE_DIR, "config")
        assert os.path.isdir(config_dir), f"Directory {config_dir} does not exist (should have been renamed from configmaps/)"

    def test_base_configmaps_dir_does_not_exist(self):
        """The old configmaps/ directory should NOT exist (was renamed to config/)."""
        configmaps_dir = os.path.join(BASE_DIR, "configmaps")
        assert not os.path.exists(configmaps_dir), f"Directory {configmaps_dir} should not exist (was renamed to config/)"

    def test_api_deployment_yaml_exists(self):
        filepath = os.path.join(BASE_DIR, "services", "api-deployment.yaml")
        assert os.path.isfile(filepath), f"File {filepath} does not exist"

    def test_api_service_yaml_exists(self):
        filepath = os.path.join(BASE_DIR, "services", "api-service.yaml")
        assert os.path.isfile(filepath), f"File {filepath} does not exist"

    def test_configmap_yaml_exists(self):
        filepath = os.path.join(BASE_DIR, "config", "configmap.yaml")
        assert os.path.isfile(filepath), f"File {filepath} does not exist"

    def test_no_api_service_yaml_in_base_root(self):
        """api-service.yaml should NOT be in base/ root (was moved to services/)."""
        filepath = os.path.join(BASE_DIR, "api-service.yaml")
        assert not os.path.exists(filepath), f"File {filepath} should not exist (was moved to services/)"


class TestEnvsDirectoryStructure:
    """Verify the envs directory structure exists."""

    def test_envs_dir_exists(self):
        assert os.path.isdir(ENVS_DIR), f"Directory {ENVS_DIR} does not exist"

    def test_staging_dir_exists(self):
        assert os.path.isdir(STAGING_DIR), f"Directory {STAGING_DIR} does not exist"

    def test_prod_dir_exists(self):
        assert os.path.isdir(PROD_DIR), f"Directory {PROD_DIR} does not exist"


class TestStagingSymlinks:
    """Verify staging symlinks exist and their current (broken) state."""

    def test_staging_deployment_is_symlink(self):
        filepath = os.path.join(STAGING_DIR, "deployment.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"

    def test_staging_deployment_symlink_is_valid(self):
        """This symlink should be valid (points to correct location)."""
        filepath = os.path.join(STAGING_DIR, "deployment.yaml")
        assert os.path.exists(filepath), f"Symlink {filepath} should point to a valid target"

    def test_staging_service_is_symlink(self):
        filepath = os.path.join(STAGING_DIR, "service.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"

    def test_staging_service_symlink_is_broken(self):
        """This symlink should be BROKEN (points to old path before services/ subdir)."""
        filepath = os.path.join(STAGING_DIR, "service.yaml")
        # islink returns True even for broken symlinks, but exists returns False
        assert os.path.islink(filepath), f"{filepath} should be a symlink"
        assert not os.path.exists(filepath), f"Symlink {filepath} should be broken (pointing to non-existent target)"

    def test_staging_service_symlink_points_to_old_path(self):
        """Verify the symlink points to the old incorrect path."""
        filepath = os.path.join(STAGING_DIR, "service.yaml")
        target = os.readlink(filepath)
        # Should point to ../../base/api-service.yaml (old path, missing services/ subdir)
        assert "base/api-service.yaml" in target or target.endswith("base/api-service.yaml"), \
            f"Symlink {filepath} should point to old path containing 'base/api-service.yaml', got: {target}"
        assert "services" not in target, \
            f"Symlink {filepath} should NOT contain 'services' in path (that's the fix), got: {target}"

    def test_staging_configmap_is_symlink(self):
        filepath = os.path.join(STAGING_DIR, "configmap.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"

    def test_staging_configmap_symlink_is_broken(self):
        """This symlink should be BROKEN (points to old configmaps/ dir instead of config/)."""
        filepath = os.path.join(STAGING_DIR, "configmap.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"
        assert not os.path.exists(filepath), f"Symlink {filepath} should be broken (pointing to non-existent target)"

    def test_staging_configmap_symlink_points_to_old_path(self):
        """Verify the symlink points to the old configmaps/ directory."""
        filepath = os.path.join(STAGING_DIR, "configmap.yaml")
        target = os.readlink(filepath)
        # Should point to ../../base/configmaps/configmap.yaml (old path)
        assert "configmaps" in target, \
            f"Symlink {filepath} should point to old 'configmaps' directory, got: {target}"

    def test_staging_ingress_is_regular_file(self):
        filepath = os.path.join(STAGING_DIR, "staging-ingress.yaml")
        assert os.path.isfile(filepath), f"{filepath} should exist as a regular file"
        assert not os.path.islink(filepath), f"{filepath} should be a regular file, not a symlink"


class TestProdSymlinks:
    """Verify prod symlinks exist and their current state."""

    def test_prod_deployment_is_symlink(self):
        filepath = os.path.join(PROD_DIR, "deployment.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"

    def test_prod_service_is_symlink(self):
        filepath = os.path.join(PROD_DIR, "service.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"

    def test_prod_service_symlink_is_broken(self):
        """This symlink should be BROKEN (same issue as staging)."""
        filepath = os.path.join(PROD_DIR, "service.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"
        assert not os.path.exists(filepath), f"Symlink {filepath} should be broken"

    def test_prod_configmap_is_symlink(self):
        filepath = os.path.join(PROD_DIR, "configmap.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"

    def test_prod_configmap_symlink_is_broken(self):
        """This symlink should be BROKEN (same issue as staging)."""
        filepath = os.path.join(PROD_DIR, "configmap.yaml")
        assert os.path.islink(filepath), f"{filepath} should be a symlink"
        assert not os.path.exists(filepath), f"Symlink {filepath} should be broken"

    def test_prod_ingress_is_regular_file(self):
        filepath = os.path.join(PROD_DIR, "prod-ingress.yaml")
        assert os.path.isfile(filepath), f"{filepath} should exist as a regular file"
        assert not os.path.islink(filepath), f"{filepath} should be a regular file, not a symlink"


class TestKubectlAvailable:
    """Verify kubectl is installed and available."""

    def test_kubectl_exists(self):
        result = subprocess.run(["which", "kubectl"], capture_output=True)
        assert result.returncode == 0, "kubectl is not installed or not in PATH"

    def test_kubectl_version_works(self):
        result = subprocess.run(["kubectl", "version", "--client"], capture_output=True)
        assert result.returncode == 0, f"kubectl version --client failed: {result.stderr.decode()}"


class TestKubectlApplyCurrentlyFails:
    """Verify that kubectl apply --dry-run currently fails due to broken symlinks."""

    def test_kubectl_apply_staging_fails(self):
        """The apply should fail because of broken symlinks."""
        result = subprocess.run(
            ["kubectl", "apply", "--dry-run=client", "-f", "envs/staging/"],
            cwd=MANIFESTS_DIR,
            capture_output=True
        )
        assert result.returncode != 0, \
            "kubectl apply --dry-run=client -f envs/staging/ should currently FAIL (broken symlinks)"


class TestDirectoryWritable:
    """Verify the directories are writable by the agent."""

    def test_staging_dir_writable(self):
        assert os.access(STAGING_DIR, os.W_OK), f"Directory {STAGING_DIR} is not writable"

    def test_envs_dir_writable(self):
        assert os.access(ENVS_DIR, os.W_OK), f"Directory {ENVS_DIR} is not writable"
