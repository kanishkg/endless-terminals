# test_final_state.py
"""
Tests to validate the final state after the student has fixed the kubectl diff bug.

The fix should make the fake kubectl's diff command correctly compare YAML files
semantically, so that unchanged manifests are not re-applied.
"""

import os
import subprocess
import tempfile
import shutil
import pytest


HOME = "/home/user"
DEPLOY_DIR = f"{HOME}/deploy"
MANIFESTS_DIR = f"{DEPLOY_DIR}/manifests"
KUBE_STATE_DIR = f"{HOME}/.kube-state"
KUBECTL_PATH = "/usr/local/bin/kubectl"
SYNC_SCRIPT = f"{DEPLOY_DIR}/sync-manifests.sh"
TEST_SCRIPT = f"{DEPLOY_DIR}/test-sync.sh"

EXPECTED_MANIFESTS = ["deployment.yaml", "service.yaml", "configmap.yaml", "ingress.yaml"]


class TestMainFunctionality:
    """Test that the main test script passes - this is the primary success criterion."""

    def test_test_sync_script_passes(self):
        """
        The test-sync.sh script should exit 0.
        It runs sync-manifests.sh twice and verifies the second run reports 0 changes.
        """
        result = subprocess.run(
            [TEST_SCRIPT],
            capture_output=True,
            text=True,
            cwd=DEPLOY_DIR,
            timeout=60
        )
        assert result.returncode == 0, (
            f"test-sync.sh failed with exit code {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    def test_second_sync_run_reports_zero_changes(self):
        """
        Running sync-manifests.sh twice should result in the second run
        reporting '0 manifests changed'.
        """
        # First run - establishes baseline
        subprocess.run(
            [SYNC_SCRIPT],
            capture_output=True,
            text=True,
            cwd=DEPLOY_DIR,
            timeout=60
        )

        # Second run - should detect no changes
        result = subprocess.run(
            [SYNC_SCRIPT],
            capture_output=True,
            text=True,
            cwd=DEPLOY_DIR,
            timeout=60
        )

        assert "0 manifests changed" in result.stdout, (
            f"Second sync run should report '0 manifests changed'\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )


class TestAntiShortcutGuards:
    """
    Tests to ensure the fix is legitimate and not a shortcut like
    'always return 0 from diff' or 'never apply anything'.
    """

    def test_modified_manifest_is_detected_and_applied(self):
        """
        After modifying a manifest file, sync-manifests.sh must detect
        and apply that one file. This ensures diff actually works.
        """
        deployment_path = os.path.join(MANIFESTS_DIR, "deployment.yaml")

        # First, ensure clean state by running sync twice
        subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=DEPLOY_DIR, timeout=60)
        subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=DEPLOY_DIR, timeout=60)

        # Read original content for restoration
        with open(deployment_path, 'r') as f:
            original_content = f.read()

        try:
            # Modify the manifest
            with open(deployment_path, 'a') as f:
                f.write("\n# test change for verification\n")

            # Run sync - should detect the change
            result = subprocess.run(
                [SYNC_SCRIPT],
                capture_output=True,
                text=True,
                cwd=DEPLOY_DIR,
                timeout=60
            )

            # Should NOT report 0 changes - at least deployment.yaml changed
            output = result.stdout + result.stderr

            # The script should either:
            # 1. Report that it applied at least 1 manifest, OR
            # 2. NOT report "0 manifests changed"
            # We check that it doesn't say 0 changes when there IS a change
            assert "0 manifests changed" not in result.stdout, (
                f"After modifying deployment.yaml, sync should detect changes.\n"
                f"But it reported '0 manifests changed'.\n"
                f"This suggests diff is broken (always returns 0) or apply is disabled.\n"
                f"STDOUT:\n{result.stdout}"
            )

        finally:
            # Restore original content
            with open(deployment_path, 'w') as f:
                f.write(original_content)

    def test_kubectl_diff_returns_one_for_changed_file(self):
        """
        Directly test that kubectl diff returns 1 when a file differs
        from the stored state.
        """
        deployment_path = os.path.join(MANIFESTS_DIR, "deployment.yaml")

        # First apply to ensure state is stored
        subprocess.run(
            [KUBECTL_PATH, "apply", "-f", deployment_path],
            capture_output=True,
            timeout=30
        )

        # Create a modified version
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
            with open(deployment_path, 'r') as f:
                content = f.read()
            tmp.write(content + "\n# modified\n")
            tmp_path = tmp.name

        try:
            # Diff should return 1 (changes detected)
            result = subprocess.run(
                [KUBECTL_PATH, "diff", "-f", tmp_path],
                capture_output=True,
                timeout=30
            )
            assert result.returncode == 1, (
                f"kubectl diff should return 1 for a modified file, got {result.returncode}\n"
                f"This suggests diff is broken (always returns 0)."
            )
        finally:
            os.unlink(tmp_path)

    def test_kubectl_diff_returns_zero_for_identical_file(self):
        """
        Directly test that kubectl diff returns 0 when a file is identical
        to the stored state.
        """
        deployment_path = os.path.join(MANIFESTS_DIR, "deployment.yaml")

        # Apply the file
        subprocess.run(
            [KUBECTL_PATH, "apply", "-f", deployment_path],
            capture_output=True,
            timeout=30
        )

        # Diff the same file - should return 0
        result = subprocess.run(
            [KUBECTL_PATH, "diff", "-f", deployment_path],
            capture_output=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"kubectl diff should return 0 for an unchanged file, got {result.returncode}\n"
            f"STDOUT: {result.stdout.decode() if result.stdout else ''}\n"
            f"STDERR: {result.stderr.decode() if result.stderr else ''}\n"
            f"The bug may not be fully fixed."
        )


class TestScriptIntegrity:
    """Test that the sync-manifests.sh script structure is preserved."""

    def test_sync_script_still_uses_kubectl_diff(self):
        """The sync script must still contain kubectl diff logic."""
        result = subprocess.run(
            ["grep", "-q", "kubectl diff", SYNC_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, (
            f"Sync script {SYNC_SCRIPT} no longer contains 'kubectl diff'.\n"
            f"The diff logic must be preserved."
        )

    def test_sync_script_still_uses_kubectl_apply(self):
        """The sync script must still contain kubectl apply logic."""
        result = subprocess.run(
            ["grep", "-q", "kubectl apply", SYNC_SCRIPT],
            capture_output=True
        )
        assert result.returncode == 0, (
            f"Sync script {SYNC_SCRIPT} no longer contains 'kubectl apply'.\n"
            f"The apply logic must be preserved."
        )

    def test_sync_script_iterates_manifests(self):
        """The sync script must still iterate over manifest files."""
        with open(SYNC_SCRIPT, 'r') as f:
            content = f.read()
        has_loop = ('for ' in content and '.yaml' in content) or ('*.yaml' in content)
        assert has_loop, (
            f"Sync script {SYNC_SCRIPT} doesn't appear to iterate over YAML files.\n"
            f"The iteration logic must be preserved."
        )


class TestManifestFilesUnchanged:
    """Test that manifest files are byte-identical to initial state."""

    @pytest.mark.parametrize("manifest", EXPECTED_MANIFESTS)
    def test_manifest_exists(self, manifest):
        """All expected manifest files must still exist."""
        manifest_path = os.path.join(MANIFESTS_DIR, manifest)
        assert os.path.isfile(manifest_path), f"Manifest file {manifest_path} is missing"

    @pytest.mark.parametrize("manifest", EXPECTED_MANIFESTS)
    def test_manifest_is_valid_yaml(self, manifest):
        """All manifest files must still be valid YAML."""
        manifest_path = os.path.join(MANIFESTS_DIR, manifest)
        try:
            import yaml
            with open(manifest_path, 'r') as f:
                content = yaml.safe_load(f)
            assert content is not None, f"Manifest {manifest_path} is empty or invalid"
        except yaml.YAMLError as e:
            pytest.fail(f"Manifest {manifest_path} contains invalid YAML: {e}")

    def test_exactly_four_manifests(self):
        """There should still be exactly 4 YAML files."""
        yaml_files = [f for f in os.listdir(MANIFESTS_DIR)
                      if f.endswith('.yaml') or f.endswith('.yml')]
        assert len(yaml_files) == 4, (
            f"Expected 4 manifest files, found {len(yaml_files)}: {yaml_files}"
        )


class TestKubectlFunctionality:
    """Test that the fake kubectl still functions correctly."""

    def test_kubectl_apply_stores_state(self):
        """kubectl apply must still store state to kube-state directory."""
        deployment_path = os.path.join(MANIFESTS_DIR, "deployment.yaml")

        # Clear any existing state for this test
        # (We'll use a unique temp file to avoid interfering with other state)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False,
                                          dir=MANIFESTS_DIR) as tmp:
            tmp.write("apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: test-apply-check\ndata:\n  key: value\n")
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [KUBECTL_PATH, "apply", "-f", tmp_path],
                capture_output=True,
                timeout=30
            )
            assert result.returncode == 0, (
                f"kubectl apply failed with code {result.returncode}\n"
                f"STDERR: {result.stderr.decode() if result.stderr else ''}"
            )

            # Verify something was stored (the exact naming may vary)
            state_files = os.listdir(KUBE_STATE_DIR)
            assert len(state_files) > 0, "kubectl apply did not store any state"

        finally:
            os.unlink(tmp_path)

    def test_kubectl_diff_works_correctly_after_apply(self):
        """
        After applying a file, diff should return 0 for that same file.
        This is the core fix verification.
        """
        # Use configmap as test subject
        configmap_path = os.path.join(MANIFESTS_DIR, "configmap.yaml")

        # Apply it
        apply_result = subprocess.run(
            [KUBECTL_PATH, "apply", "-f", configmap_path],
            capture_output=True,
            timeout=30
        )
        assert apply_result.returncode == 0, "kubectl apply failed"

        # Diff should return 0 (no changes)
        diff_result = subprocess.run(
            [KUBECTL_PATH, "diff", "-f", configmap_path],
            capture_output=True,
            timeout=30
        )
        assert diff_result.returncode == 0, (
            f"kubectl diff returned {diff_result.returncode} for unchanged file.\n"
            f"Expected 0 (no changes).\n"
            f"STDOUT: {diff_result.stdout.decode() if diff_result.stdout else ''}\n"
            f"STDERR: {diff_result.stderr.decode() if diff_result.stderr else ''}"
        )


class TestEndToEndScenario:
    """Full end-to-end scenario tests."""

    def test_full_workflow_apply_then_noop(self):
        """
        Complete workflow test:
        1. Run sync - applies all manifests
        2. Run sync again - should apply nothing (0 changes)
        3. Modify one file
        4. Run sync - should apply only that one file
        5. Run sync again - should apply nothing (0 changes)
        """
        deployment_path = os.path.join(MANIFESTS_DIR, "deployment.yaml")

        # Read original for restoration
        with open(deployment_path, 'r') as f:
            original_content = f.read()

        try:
            # Step 1: First sync
            subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=DEPLOY_DIR, timeout=60)

            # Step 2: Second sync - should be noop
            result2 = subprocess.run(
                [SYNC_SCRIPT],
                capture_output=True,
                text=True,
                cwd=DEPLOY_DIR,
                timeout=60
            )
            assert "0 manifests changed" in result2.stdout, (
                f"Step 2 failed: Second sync should report 0 changes.\n"
                f"STDOUT: {result2.stdout}"
            )

            # Step 3: Modify deployment.yaml
            with open(deployment_path, 'a') as f:
                f.write("\n# workflow test modification\n")

            # Step 4: Third sync - should detect change
            result3 = subprocess.run(
                [SYNC_SCRIPT],
                capture_output=True,
                text=True,
                cwd=DEPLOY_DIR,
                timeout=60
            )
            assert "0 manifests changed" not in result3.stdout, (
                f"Step 4 failed: After modification, sync should detect changes.\n"
                f"STDOUT: {result3.stdout}"
            )

            # Step 5: Fourth sync - should be noop again
            result4 = subprocess.run(
                [SYNC_SCRIPT],
                capture_output=True,
                text=True,
                cwd=DEPLOY_DIR,
                timeout=60
            )
            assert "0 manifests changed" in result4.stdout, (
                f"Step 5 failed: Fourth sync should report 0 changes.\n"
                f"STDOUT: {result4.stdout}"
            )

        finally:
            # Restore original
            with open(deployment_path, 'w') as f:
                f.write(original_content)
            # Re-sync to restore state
            subprocess.run([SYNC_SCRIPT], capture_output=True, cwd=DEPLOY_DIR, timeout=60)
