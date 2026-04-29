# test_final_state.py
"""
Tests to validate the final state of the system after the student has completed the task.
This verifies that the pre-push hook is in place and properly blocks commits with
world-readable key files, even when commits were made with --no-verify.
"""

import os
import stat
import subprocess
import tempfile
import pytest
from pathlib import Path


HOME = Path("/home/user")
REPO_PATH = HOME / "infra-configs"
GIT_DIR = REPO_PATH / ".git"
HOOKS_DIR = GIT_DIR / "hooks"
PRE_COMMIT_HOOK = HOOKS_DIR / "pre-commit"
PRE_PUSH_HOOK = HOOKS_DIR / "pre-push"


class TestRepoStillValid:
    """Test that the repository is still valid after modifications."""

    def test_repo_is_valid_git_repo(self):
        """The repository must still be a valid git repository."""
        result = subprocess.run(
            ["git", "status"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git status failed - repository may be corrupted: {result.stderr}"

    def test_repo_has_working_tree(self):
        """The repository must still have a working tree."""
        result = subprocess.run(
            ["git", "rev-parse", "--is-bare-repository"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git rev-parse failed: {result.stderr}"
        assert result.stdout.strip() == "false", "Repository should not be bare"


class TestPreCommitHookPreserved:
    """Test that the original pre-commit hook is still in place (defense in depth)."""

    def test_pre_commit_hook_still_exists(self):
        """The pre-commit hook must still exist."""
        assert PRE_COMMIT_HOOK.exists(), \
            f"Pre-commit hook {PRE_COMMIT_HOOK} was removed - it should be preserved for defense in depth"

    def test_pre_commit_hook_still_executable(self):
        """The pre-commit hook must still be executable."""
        mode = os.stat(PRE_COMMIT_HOOK).st_mode
        assert mode & stat.S_IXUSR, "Pre-commit hook is no longer executable by owner"

    def test_pre_commit_hook_still_checks_keys(self):
        """The pre-commit hook should still contain logic to check key files."""
        content = PRE_COMMIT_HOOK.read_text()
        has_key_check = any(x in content.lower() for x in [".pem", ".key", "pem", "key"])
        assert has_key_check, "Pre-commit hook no longer appears to check for key files"


class TestPrePushHookExists:
    """Test that a pre-push hook has been created."""

    def test_pre_push_hook_exists(self):
        """The pre-push hook must exist."""
        assert PRE_PUSH_HOOK.exists(), \
            f"Pre-push hook {PRE_PUSH_HOOK} does not exist - this is required to block bypassed commits"

    def test_pre_push_hook_is_file(self):
        """The pre-push hook must be a regular file."""
        assert PRE_PUSH_HOOK.is_file(), f"{PRE_PUSH_HOOK} is not a regular file"

    def test_pre_push_hook_is_executable(self):
        """The pre-push hook must be executable."""
        mode = os.stat(PRE_PUSH_HOOK).st_mode
        assert mode & stat.S_IXUSR, \
            f"Pre-push hook is not executable - it won't run. Current mode: {oct(mode)}"

    def test_pre_push_hook_has_content(self):
        """The pre-push hook must have meaningful content."""
        content = PRE_PUSH_HOOK.read_text()
        assert len(content.strip()) > 10, "Pre-push hook appears to be empty or trivial"

    def test_pre_push_hook_checks_for_key_files(self):
        """The pre-push hook should contain logic related to key file checking."""
        content = PRE_PUSH_HOOK.read_text().lower()
        # Should reference pem or key files somewhere
        has_key_reference = any(x in content for x in [".pem", ".key", "pem", "key", "644", "permission", "mode"])
        assert has_key_reference, \
            "Pre-push hook doesn't appear to check for .pem/.key files or permissions"


class TestBypassCommitSucceeds:
    """Test that commits with --no-verify still succeed (we block at push, not commit)."""

    def test_can_commit_bad_file_with_no_verify(self):
        """A commit with --no-verify adding a world-readable key file should succeed."""
        test_file = REPO_PATH / "test_bypass.pem"

        try:
            # Create a test key file with world-readable permissions
            test_file.write_text("-----BEGIN TEST KEY-----\ntest content\n-----END TEST KEY-----\n")
            os.chmod(test_file, 0o644)

            # Stage the file
            result = subprocess.run(
                ["git", "add", "test_bypass.pem"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, f"git add failed: {result.stderr}"

            # Commit with --no-verify (should succeed - we block at push)
            result = subprocess.run(
                ["git", "commit", "--no-verify", "-m", "test bypass commit"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"Commit with --no-verify should succeed (blocking happens at push): {result.stderr}"

        finally:
            # Clean up - reset the commit
            subprocess.run(
                ["git", "reset", "--hard", "HEAD~1"],
                cwd=REPO_PATH,
                capture_output=True
            )
            if test_file.exists():
                test_file.unlink()


class TestPrePushHookBlocksBadCommits:
    """Test that the pre-push hook blocks pushes containing world-readable key files."""

    def test_pre_push_hook_blocks_644_pem_file(self):
        """The pre-push hook should block a push containing a 0644 .pem file."""
        test_file = REPO_PATH / "grader_test.pem"
        original_head = None

        try:
            # Get original HEAD
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            original_head = result.stdout.strip()

            # Create a test key file with world-readable permissions
            test_file.write_text("-----BEGIN RSA PRIVATE KEY-----\ngraderkey\n-----END RSA PRIVATE KEY-----\n")
            os.chmod(test_file, 0o644)

            # Stage and commit with --no-verify
            subprocess.run(["git", "add", "grader_test.pem"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", "grader test commit"],
                cwd=REPO_PATH,
                capture_output=True
            )

            # Get new HEAD
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            new_head = result.stdout.strip()

            # Try to invoke pre-push hook directly (simulating a push)
            # The hook receives: <local ref> <local sha> <remote ref> <remote sha>
            # on stdin, one line per ref being pushed
            hook_input = f"{new_head} refs/heads/main {original_head} refs/heads/main\n"

            result = subprocess.run(
                [str(PRE_PUSH_HOOK), "origin", "https://example.com/repo.git"],
                cwd=REPO_PATH,
                input=hook_input,
                capture_output=True,
                text=True,
                env={**os.environ, "GIT_DIR": str(GIT_DIR)}
            )

            # The hook should exit non-zero to block the push
            assert result.returncode != 0, \
                f"Pre-push hook should have blocked the push but exited with code {result.returncode}. " \
                f"stdout: {result.stdout}, stderr: {result.stderr}"

        finally:
            # Clean up
            if original_head:
                subprocess.run(
                    ["git", "reset", "--hard", original_head],
                    cwd=REPO_PATH,
                    capture_output=True
                )
            if test_file.exists():
                test_file.unlink()

    def test_pre_push_hook_blocks_644_key_file(self):
        """The pre-push hook should block a push containing a 0644 .key file."""
        test_file = REPO_PATH / "grader_test.key"
        original_head = None

        try:
            # Get original HEAD
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            original_head = result.stdout.strip()

            # Create a test key file with world-readable permissions
            test_file.write_text("-----BEGIN PRIVATE KEY-----\ngraderkey\n-----END PRIVATE KEY-----\n")
            os.chmod(test_file, 0o644)

            # Stage and commit with --no-verify
            subprocess.run(["git", "add", "grader_test.key"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", "grader test key commit"],
                cwd=REPO_PATH,
                capture_output=True
            )

            # Get new HEAD
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            new_head = result.stdout.strip()

            # Invoke pre-push hook directly
            hook_input = f"{new_head} refs/heads/main {original_head} refs/heads/main\n"

            result = subprocess.run(
                [str(PRE_PUSH_HOOK), "origin", "https://example.com/repo.git"],
                cwd=REPO_PATH,
                input=hook_input,
                capture_output=True,
                text=True,
                env={**os.environ, "GIT_DIR": str(GIT_DIR)}
            )

            assert result.returncode != 0, \
                f"Pre-push hook should have blocked the push of .key file but exited with code {result.returncode}"

        finally:
            if original_head:
                subprocess.run(
                    ["git", "reset", "--hard", original_head],
                    cwd=REPO_PATH,
                    capture_output=True
                )
            if test_file.exists():
                test_file.unlink()

    def test_pre_push_hook_blocks_world_writable_key(self):
        """The pre-push hook should block a push containing a 0666 (world-writable) key file."""
        test_file = REPO_PATH / "world_writable.pem"
        original_head = None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            original_head = result.stdout.strip()

            test_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nworldwritable\n-----END RSA PRIVATE KEY-----\n")
            os.chmod(test_file, 0o666)  # Even looser than 644

            subprocess.run(["git", "add", "world_writable.pem"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", "world writable test"],
                cwd=REPO_PATH,
                capture_output=True
            )

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            new_head = result.stdout.strip()

            hook_input = f"{new_head} refs/heads/main {original_head} refs/heads/main\n"

            result = subprocess.run(
                [str(PRE_PUSH_HOOK), "origin", "https://example.com/repo.git"],
                cwd=REPO_PATH,
                input=hook_input,
                capture_output=True,
                text=True,
                env={**os.environ, "GIT_DIR": str(GIT_DIR)}
            )

            assert result.returncode != 0, \
                "Pre-push hook should block world-writable (0666) key files"

        finally:
            if original_head:
                subprocess.run(
                    ["git", "reset", "--hard", original_head],
                    cwd=REPO_PATH,
                    capture_output=True
                )
            if test_file.exists():
                test_file.unlink()


class TestPrePushHookAllowsGoodCommits:
    """Test that the pre-push hook allows pushes with properly secured key files."""

    def test_pre_push_allows_600_key_file(self):
        """The pre-push hook should allow a push containing a 0600 (secure) key file."""
        test_file = REPO_PATH / "secure_test.pem"
        original_head = None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            original_head = result.stdout.strip()

            # Create a properly secured key file
            test_file.write_text("-----BEGIN RSA PRIVATE KEY-----\nsecure\n-----END RSA PRIVATE KEY-----\n")
            os.chmod(test_file, 0o600)  # Secure permissions

            subprocess.run(["git", "add", "secure_test.pem"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", "secure key test"],
                cwd=REPO_PATH,
                capture_output=True
            )

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            new_head = result.stdout.strip()

            hook_input = f"{new_head} refs/heads/main {original_head} refs/heads/main\n"

            result = subprocess.run(
                [str(PRE_PUSH_HOOK), "origin", "https://example.com/repo.git"],
                cwd=REPO_PATH,
                input=hook_input,
                capture_output=True,
                text=True,
                env={**os.environ, "GIT_DIR": str(GIT_DIR)}
            )

            # Should succeed (exit 0) for properly secured files
            assert result.returncode == 0, \
                f"Pre-push hook should allow 0600 key files but blocked with: {result.stdout} {result.stderr}"

        finally:
            if original_head:
                subprocess.run(
                    ["git", "reset", "--hard", original_head],
                    cwd=REPO_PATH,
                    capture_output=True
                )
            if test_file.exists():
                test_file.unlink()

    def test_pre_push_allows_non_key_files(self):
        """The pre-push hook should allow pushes with regular (non-key) files."""
        test_file = REPO_PATH / "regular_file.txt"
        original_head = None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            original_head = result.stdout.strip()

            # Create a regular file (not .pem or .key)
            test_file.write_text("This is just a regular text file\n")
            os.chmod(test_file, 0o644)  # World-readable is fine for non-key files

            subprocess.run(["git", "add", "regular_file.txt"], cwd=REPO_PATH, capture_output=True)
            subprocess.run(
                ["git", "commit", "--no-verify", "-m", "regular file test"],
                cwd=REPO_PATH,
                capture_output=True
            )

            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True
            )
            new_head = result.stdout.strip()

            hook_input = f"{new_head} refs/heads/main {original_head} refs/heads/main\n"

            result = subprocess.run(
                [str(PRE_PUSH_HOOK), "origin", "https://example.com/repo.git"],
                cwd=REPO_PATH,
                input=hook_input,
                capture_output=True,
                text=True,
                env={**os.environ, "GIT_DIR": str(GIT_DIR)}
            )

            assert result.returncode == 0, \
                f"Pre-push hook should allow regular files but blocked with: {result.stdout} {result.stderr}"

        finally:
            if original_head:
                subprocess.run(
                    ["git", "reset", "--hard", original_head],
                    cwd=REPO_PATH,
                    capture_output=True
                )
            if test_file.exists():
                test_file.unlink()


class TestNoModificationOutsideRepo:
    """Test that no modifications were made outside the repository."""

    def test_jenkins_script_unchanged(self):
        """The jenkins deploy script should still exist and be read-only."""
        deploy_script = HOME / "jenkins-workspace" / "deploy.sh"
        assert deploy_script.exists(), "Jenkins deploy script should still exist"
        assert not os.access(deploy_script, os.W_OK), \
            "Jenkins deploy script should still be read-only"

    def test_jenkins_script_still_has_no_verify(self):
        """The jenkins script should still contain --no-verify (we can't modify it)."""
        deploy_script = HOME / "jenkins-workspace" / "deploy.sh"
        content = deploy_script.read_text()
        assert "--no-verify" in content, \
            "Jenkins script should still contain --no-verify (it's read-only, shouldn't have been modified)"
