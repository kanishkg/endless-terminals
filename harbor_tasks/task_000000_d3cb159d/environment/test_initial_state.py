# test_initial_state.py
"""
Tests to validate the initial state of the system before the student performs the task.
This verifies the git repository setup, hooks, and the conditions that led to the bypass.
"""

import os
import stat
import subprocess
import pytest
from pathlib import Path


HOME = Path("/home/user")
REPO_PATH = HOME / "infra-configs"
GIT_DIR = REPO_PATH / ".git"
HOOKS_DIR = GIT_DIR / "hooks"
PRE_COMMIT_HOOK = HOOKS_DIR / "pre-commit"
JENKINS_WORKSPACE = HOME / "jenkins-workspace"
DEPLOY_SCRIPT = JENKINS_WORKSPACE / "deploy.sh"
REFLOG_PATH = GIT_DIR / "logs" / "HEAD"


class TestRepoExists:
    """Test that the infra-configs repository exists and is valid."""

    def test_repo_directory_exists(self):
        """The /home/user/infra-configs directory must exist."""
        assert REPO_PATH.exists(), f"Repository directory {REPO_PATH} does not exist"
        assert REPO_PATH.is_dir(), f"{REPO_PATH} is not a directory"

    def test_git_directory_exists(self):
        """The .git directory must exist inside the repo."""
        assert GIT_DIR.exists(), f"Git directory {GIT_DIR} does not exist"
        assert GIT_DIR.is_dir(), f"{GIT_DIR} is not a directory"

    def test_repo_is_valid_git_repo(self):
        """The repository must be a valid git repository."""
        result = subprocess.run(
            ["git", "status"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git status failed: {result.stderr}"

    def test_repo_has_working_tree(self):
        """The repository must have a working tree (not bare)."""
        result = subprocess.run(
            ["git", "rev-parse", "--is-bare-repository"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git rev-parse failed: {result.stderr}"
        assert result.stdout.strip() == "false", "Repository should not be bare"


class TestPreCommitHook:
    """Test that the pre-commit hook exists and is properly configured."""

    def test_pre_commit_hook_exists(self):
        """The pre-commit hook must exist."""
        assert PRE_COMMIT_HOOK.exists(), f"Pre-commit hook {PRE_COMMIT_HOOK} does not exist"

    def test_pre_commit_hook_is_file(self):
        """The pre-commit hook must be a regular file."""
        assert PRE_COMMIT_HOOK.is_file(), f"{PRE_COMMIT_HOOK} is not a regular file"

    def test_pre_commit_hook_is_executable(self):
        """The pre-commit hook must be executable (mode 0755)."""
        mode = os.stat(PRE_COMMIT_HOOK).st_mode
        assert mode & stat.S_IXUSR, f"Pre-commit hook is not executable by owner"
        assert mode & stat.S_IXGRP, f"Pre-commit hook is not executable by group"
        assert mode & stat.S_IXOTH, f"Pre-commit hook is not executable by others"

    def test_pre_commit_hook_checks_key_files(self):
        """The pre-commit hook should contain logic to check .pem and .key files."""
        content = PRE_COMMIT_HOOK.read_text()
        # Should reference pem or key files
        assert ".pem" in content or ".key" in content or "pem" in content or "key" in content, \
            "Pre-commit hook doesn't appear to check for .pem or .key files"

    def test_hooks_path_is_unset(self):
        """core.hooksPath should be unset (using default repo hooks)."""
        result = subprocess.run(
            ["git", "config", "core.hooksPath"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        # Exit code 1 means the config is not set, which is what we expect
        assert result.returncode == 1 or result.stdout.strip() == "", \
            f"core.hooksPath should be unset but is: {result.stdout.strip()}"


class TestBadCommitExists:
    """Test that the problematic commit from jenkins-bot exists in history."""

    def test_commit_with_jenkins_bot_author_exists(self):
        """A commit by jenkins-bot should exist in the history."""
        result = subprocess.run(
            ["git", "log", "--all", "--author=jenkins-bot", "--oneline"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git log failed: {result.stderr}"
        assert result.stdout.strip(), "No commits by jenkins-bot found in history"

    def test_deploy_key_file_in_history(self):
        """The secrets/deploy.key file should exist in the commit history."""
        result = subprocess.run(
            ["git", "log", "--all", "--name-only", "--oneline"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git log failed: {result.stderr}"
        # Check if deploy.key appears in the history
        assert "deploy.key" in result.stdout, \
            "secrets/deploy.key not found in commit history"

    def test_bad_commit_reachable_from_head(self):
        """The bad commit should be reachable from HEAD."""
        result = subprocess.run(
            ["git", "log", "--author=jenkins-bot", "--format=%H"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git log failed: {result.stderr}"
        assert result.stdout.strip(), "Bad commit by jenkins-bot not reachable from HEAD"


class TestJenkinsWorkspace:
    """Test that the jenkins workspace and deploy script exist with proper permissions."""

    def test_jenkins_workspace_exists(self):
        """The jenkins-workspace directory must exist."""
        assert JENKINS_WORKSPACE.exists(), f"Jenkins workspace {JENKINS_WORKSPACE} does not exist"
        assert JENKINS_WORKSPACE.is_dir(), f"{JENKINS_WORKSPACE} is not a directory"

    def test_deploy_script_exists(self):
        """The deploy.sh script must exist."""
        assert DEPLOY_SCRIPT.exists(), f"Deploy script {DEPLOY_SCRIPT} does not exist"
        assert DEPLOY_SCRIPT.is_file(), f"{DEPLOY_SCRIPT} is not a regular file"

    def test_deploy_script_is_readable(self):
        """The deploy.sh script must be readable."""
        assert os.access(DEPLOY_SCRIPT, os.R_OK), f"Deploy script {DEPLOY_SCRIPT} is not readable"

    def test_deploy_script_is_not_writable(self):
        """The deploy.sh script must NOT be writable (owned by another team)."""
        assert not os.access(DEPLOY_SCRIPT, os.W_OK), \
            f"Deploy script {DEPLOY_SCRIPT} should not be writable"

    def test_deploy_script_contains_no_verify(self):
        """The deploy.sh script should contain --no-verify flag."""
        content = DEPLOY_SCRIPT.read_text()
        assert "--no-verify" in content, \
            "Deploy script doesn't contain --no-verify (this is the bypass mechanism)"

    def test_deploy_script_contains_git_commit(self):
        """The deploy.sh script should contain a git commit command."""
        content = DEPLOY_SCRIPT.read_text()
        assert "git commit" in content, \
            "Deploy script doesn't contain 'git commit'"


class TestReflog:
    """Test that the reflog exists and contains evidence of the bad commit."""

    def test_reflog_exists(self):
        """The HEAD reflog must exist."""
        assert REFLOG_PATH.exists(), f"Reflog {REFLOG_PATH} does not exist"

    def test_reflog_has_entries(self):
        """The reflog should have entries."""
        result = subprocess.run(
            ["git", "reflog"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git reflog failed: {result.stderr}"
        assert result.stdout.strip(), "Reflog is empty"


class TestGitVersion:
    """Test that git version is 2.34+."""

    def test_git_version(self):
        """Git version should be 2.34 or higher."""
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"git --version failed: {result.stderr}"
        # Parse version like "git version 2.34.1"
        version_str = result.stdout.strip()
        parts = version_str.split()
        if len(parts) >= 3:
            version = parts[2]
            version_parts = version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            assert major > 2 or (major == 2 and minor >= 34), \
                f"Git version should be 2.34+, got {version}"


class TestRepoWritable:
    """Test that the repository is writable."""

    def test_repo_is_writable(self):
        """The /home/user/infra-configs directory must be writable."""
        assert os.access(REPO_PATH, os.W_OK), f"Repository {REPO_PATH} is not writable"

    def test_git_dir_is_writable(self):
        """The .git directory must be writable."""
        assert os.access(GIT_DIR, os.W_OK), f"Git directory {GIT_DIR} is not writable"

    def test_hooks_dir_is_writable(self):
        """The hooks directory must be writable."""
        assert os.access(HOOKS_DIR, os.W_OK), f"Hooks directory {HOOKS_DIR} is not writable"


class TestNoPrePushHook:
    """Test that pre-push hook does not exist yet (this is what needs to be created)."""

    def test_no_pre_push_hook(self):
        """The pre-push hook should NOT exist initially."""
        pre_push_hook = HOOKS_DIR / "pre-push"
        assert not pre_push_hook.exists(), \
            f"Pre-push hook {pre_push_hook} already exists - this should be created by the student"


class TestLocalRepoNotBare:
    """Test that this is a local working copy, not a bare repo with server-side hooks."""

    def test_not_bare_repo(self):
        """Repository should not be bare."""
        result = subprocess.run(
            ["git", "rev-parse", "--is-bare-repository"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert result.stdout.strip() == "false", "Repository should be a working copy, not bare"

    def test_has_working_tree(self):
        """Repository should have a working tree."""
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, "Repository should have a working tree"
        assert result.stdout.strip() == str(REPO_PATH), \
            f"Working tree should be at {REPO_PATH}"
