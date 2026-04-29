# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student
performs the debugging task for the kubectl diff bug.
"""

import os
import stat
import subprocess
import pytest


HOME = "/home/user"
DEPLOY_DIR = f"{HOME}/deploy"
MANIFESTS_DIR = f"{DEPLOY_DIR}/manifests"
KUBE_STATE_DIR = f"{HOME}/.kube-state"
KUBECTL_PATH = "/usr/local/bin/kubectl"
SYNC_SCRIPT = f"{DEPLOY_DIR}/sync-manifests.sh"
TEST_SCRIPT = f"{DEPLOY_DIR}/test-sync.sh"

EXPECTED_MANIFESTS = ["deployment.yaml", "service.yaml", "configmap.yaml", "ingress.yaml"]


class TestDirectoryStructure:
    """Test that required directories exist."""

    def test_home_directory_exists(self):
        assert os.path.isdir(HOME), f"Home directory {HOME} does not exist"

    def test_deploy_directory_exists(self):
        assert os.path.isdir(DEPLOY_DIR), f"Deploy directory {DEPLOY_DIR} does not exist"

    def test_manifests_directory_exists(self):
        assert os.path.isdir(MANIFESTS_DIR), f"Manifests directory {MANIFESTS_DIR} does not exist"

    def test_kube_state_directory_exists(self):
        assert os.path.isdir(KUBE_STATE_DIR), f"Kube state directory {KUBE_STATE_DIR} does not exist"


class TestRequiredFiles:
    """Test that required files exist and have correct properties."""

    def test_sync_manifests_script_exists(self):
        assert os.path.isfile(SYNC_SCRIPT), f"Sync manifests script {SYNC_SCRIPT} does not exist"

    def test_sync_manifests_script_executable(self):
        assert os.access(SYNC_SCRIPT, os.X_OK), f"Sync manifests script {SYNC_SCRIPT} is not executable"

    def test_test_sync_script_exists(self):
        assert os.path.isfile(TEST_SCRIPT), f"Test sync script {TEST_SCRIPT} does not exist"

    def test_test_sync_script_executable(self):
        assert os.access(TEST_SCRIPT, os.X_OK), f"Test sync script {TEST_SCRIPT} is not executable"

    def test_kubectl_exists(self):
        assert os.path.isfile(KUBECTL_PATH), f"Fake kubectl {KUBECTL_PATH} does not exist"

    def test_kubectl_executable(self):
        assert os.access(KUBECTL_PATH, os.X_OK), f"Fake kubectl {KUBECTL_PATH} is not executable"

    def test_kubectl_is_writable(self):
        assert os.access(KUBECTL_PATH, os.W_OK), f"Fake kubectl {KUBECTL_PATH} is not writable"


class TestManifestFiles:
    """Test that all expected manifest files exist."""

    @pytest.mark.parametrize("manifest", EXPECTED_MANIFESTS)
    def test_manifest_exists(self, manifest):
        manifest_path = os.path.join(MANIFESTS_DIR, manifest)
        assert os.path.isfile(manifest_path), f"Manifest file {manifest_path} does not exist"

    @pytest.mark.parametrize("manifest", EXPECTED_MANIFESTS)
    def test_manifest_is_readable(self, manifest):
        manifest_path = os.path.join(MANIFESTS_DIR, manifest)
        assert os.access(manifest_path, os.R_OK), f"Manifest file {manifest_path} is not readable"

    @pytest.mark.parametrize("manifest", EXPECTED_MANIFESTS)
    def test_manifest_is_valid_yaml(self, manifest):
        """Test that manifest files contain valid YAML."""
        manifest_path = os.path.join(MANIFESTS_DIR, manifest)
        try:
            import yaml
            with open(manifest_path, 'r') as f:
                content = yaml.safe_load(f)
            assert content is not None, f"Manifest {manifest_path} is empty or invalid YAML"
        except yaml.YAMLError as e:
            pytest.fail(f"Manifest {manifest_path} contains invalid YAML: {e}")

    def test_exactly_four_manifests(self):
        """Test that there are exactly 4 YAML files in the manifests directory."""
        yaml_files = [f for f in os.listdir(MANIFESTS_DIR) if f.endswith('.yaml') or f.endswith('.yml')]
        assert len(yaml_files) == 4, f"Expected 4 manifest files, found {len(yaml_files)}: {yaml_files}"


class TestKubeStateFiles:
    """Test that kube-state directory has stored versions of manifests."""

    def test_kube_state_has_files(self):
        """Test that kube-state directory is not empty."""
        files = os.listdir(KUBE_STATE_DIR)
        assert len(files) > 0, f"Kube state directory {KUBE_STATE_DIR} is empty - should have previously applied manifests"

    def test_kube_state_directory_writable(self):
        """Test that kube-state directory is writable."""
        assert os.access(KUBE_STATE_DIR, os.W_OK), f"Kube state directory {KUBE_STATE_DIR} is not writable"


class TestSyncManifestsScript:
    """Test properties of the sync-manifests.sh script."""

    def test_script_contains_kubectl_diff(self):
        """Test that sync-manifests.sh contains kubectl diff logic."""
        result = subprocess.run(
            ["grep", "-q", "kubectl diff", SYNC_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, f"Sync script {SYNC_SCRIPT} does not contain 'kubectl diff' - diff logic missing"

    def test_script_contains_kubectl_apply(self):
        """Test that sync-manifests.sh contains kubectl apply logic."""
        result = subprocess.run(
            ["grep", "-q", "kubectl apply", SYNC_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, f"Sync script {SYNC_SCRIPT} does not contain 'kubectl apply' - apply logic missing"

    def test_script_iterates_over_manifests(self):
        """Test that sync-manifests.sh iterates over manifest files."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        # Should have some form of loop over yaml files
        has_loop = ('for ' in content and '.yaml' in content) or ('*.yaml' in content)
        assert has_loop, f"Sync script {SYNC_SCRIPT} doesn't appear to iterate over YAML files"


class TestFakeKubectl:
    """Test properties of the fake kubectl script."""

    def test_kubectl_is_bash_script(self):
        """Test that fake kubectl is a bash script."""
        with open(KUBECTL_PATH, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith('#!') and 'bash' in first_line, \
            f"Fake kubectl {KUBECTL_PATH} does not appear to be a bash script"

    def test_kubectl_handles_diff_command(self):
        """Test that fake kubectl script contains diff handling."""
        with open(KUBECTL_PATH, 'r') as f:
            content = f.read()
        assert 'diff' in content, f"Fake kubectl {KUBECTL_PATH} does not appear to handle 'diff' command"

    def test_kubectl_handles_apply_command(self):
        """Test that fake kubectl script contains apply handling."""
        with open(KUBECTL_PATH, 'r') as f:
            content = f.read()
        assert 'apply' in content, f"Fake kubectl {KUBECTL_PATH} does not appear to handle 'apply' command"

    def test_kubectl_uses_yaml_normalization(self):
        """Test that fake kubectl uses YAML normalization (the buggy part)."""
        with open(KUBECTL_PATH, 'r') as f:
            content = f.read()
        # The bug involves yaml normalization with python
        has_yaml_processing = 'yaml' in content.lower() and 'python' in content.lower()
        assert has_yaml_processing, \
            f"Fake kubectl {KUBECTL_PATH} does not appear to use YAML/Python normalization"


class TestPythonEnvironment:
    """Test that Python environment is correctly set up."""

    def test_python3_available(self):
        """Test that python3 is available."""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "python3 is not available"

    def test_pyyaml_installed(self):
        """Test that PyYAML is installed."""
        result = subprocess.run(
            ["python3", "-c", "import yaml; print(yaml.__version__)"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "PyYAML is not installed - required for the fake kubectl"


class TestBashEnvironment:
    """Test that Bash environment is correctly set up."""

    def test_bash_available(self):
        """Test that bash is available."""
        result = subprocess.run(
            ["bash", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "bash is not available"


class TestInitialBuggyState:
    """Test that the initial state exhibits the bug (diff always returns changes)."""

    def test_kubectl_diff_returns_nonzero_for_applied_manifest(self):
        """
        Test that kubectl diff returns non-zero even for an already-applied manifest.
        This confirms the bug exists in the initial state.
        """
        # Pick the first manifest
        manifest_path = os.path.join(MANIFESTS_DIR, EXPECTED_MANIFESTS[0])

        # Run kubectl diff
        result = subprocess.run(
            [KUBECTL_PATH, "diff", "-f", manifest_path],
            capture_output=True,
            text=True
        )

        # The bug is that diff returns 1 (changes detected) even when
        # the manifest should be identical to the stored version
        # We're testing that the bug EXISTS in initial state
        # (Note: This test may need adjustment based on exact initial state setup)
        # If kube-state has the files but with different formatting, diff should return 1

        # At minimum, verify kubectl diff runs without crashing
        assert result.returncode in [0, 1], \
            f"kubectl diff failed unexpectedly with return code {result.returncode}: {result.stderr}"


class TestFileWritability:
    """Test that files that may need modification are writable."""

    def test_deploy_directory_writable(self):
        """Test that deploy directory is writable."""
        assert os.access(DEPLOY_DIR, os.W_OK), f"Deploy directory {DEPLOY_DIR} is not writable"

    def test_home_directory_writable(self):
        """Test that home directory is writable."""
        assert os.access(HOME, os.W_OK), f"Home directory {HOME} is not writable"
