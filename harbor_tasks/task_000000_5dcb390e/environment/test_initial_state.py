# test_initial_state.py
"""
Tests to validate the initial state of the OS/filesystem before the student performs the task.
This validates the environment for the standard-version release script debugging task.
"""

import json
import os
import subprocess
import pytest


class TestProjectStructure:
    """Test that the project directory structure exists correctly."""

    def test_project_directory_exists(self):
        """Verify /home/user/project directory exists."""
        assert os.path.isdir("/home/user/project"), \
            "Project directory /home/user/project does not exist"

    def test_scripts_directory_exists(self):
        """Verify scripts directory exists."""
        assert os.path.isdir("/home/user/project/scripts"), \
            "Scripts directory /home/user/project/scripts does not exist"

    def test_git_directory_exists(self):
        """Verify .git directory exists (project is a git repo)."""
        assert os.path.isdir("/home/user/project/.git"), \
            "Git directory /home/user/project/.git does not exist - project must be a git repository"

    def test_node_modules_exists(self):
        """Verify node_modules directory exists."""
        assert os.path.isdir("/home/user/project/node_modules"), \
            "node_modules directory does not exist - npm packages must be installed"


class TestRequiredFiles:
    """Test that all required files exist."""

    def test_package_json_exists(self):
        """Verify package.json exists."""
        assert os.path.isfile("/home/user/project/package.json"), \
            "package.json does not exist at /home/user/project/package.json"

    def test_versionrc_json_exists(self):
        """Verify .versionrc.json config file exists."""
        assert os.path.isfile("/home/user/project/.versionrc.json"), \
            ".versionrc.json does not exist at /home/user/project/.versionrc.json"

    def test_version_file_exists(self):
        """Verify VERSION file exists."""
        assert os.path.isfile("/home/user/project/VERSION"), \
            "VERSION file does not exist at /home/user/project/VERSION"

    def test_changelog_exists(self):
        """Verify CHANGELOG.md exists."""
        assert os.path.isfile("/home/user/project/CHANGELOG.md"), \
            "CHANGELOG.md does not exist at /home/user/project/CHANGELOG.md"

    def test_release_script_exists(self):
        """Verify release.sh script exists."""
        assert os.path.isfile("/home/user/project/scripts/release.sh"), \
            "release.sh does not exist at /home/user/project/scripts/release.sh"

    def test_release_script_is_executable(self):
        """Verify release.sh is executable."""
        assert os.access("/home/user/project/scripts/release.sh", os.X_OK), \
            "release.sh at /home/user/project/scripts/release.sh is not executable"


class TestPackageJson:
    """Test package.json content."""

    @pytest.fixture
    def package_json(self):
        """Load package.json content."""
        with open("/home/user/project/package.json", "r") as f:
            return json.load(f)

    def test_package_json_has_version(self, package_json):
        """Verify package.json has version field."""
        assert "version" in package_json, \
            "package.json does not contain 'version' field"

    def test_package_json_version_is_2_4_0(self, package_json):
        """Verify package.json version is 2.4.0."""
        assert package_json["version"] == "2.4.0", \
            f"package.json version should be '2.4.0', but is '{package_json['version']}'"

    def test_package_json_has_standard_version_dependency(self, package_json):
        """Verify standard-version is in devDependencies."""
        dev_deps = package_json.get("devDependencies", {})
        assert "standard-version" in dev_deps, \
            "standard-version is not in devDependencies in package.json"


class TestVersionrcJson:
    """Test .versionrc.json configuration."""

    @pytest.fixture
    def versionrc(self):
        """Load .versionrc.json content."""
        with open("/home/user/project/.versionrc.json", "r") as f:
            return json.load(f)

    def test_versionrc_has_types(self, versionrc):
        """Verify .versionrc.json has types configuration."""
        assert "types" in versionrc, \
            ".versionrc.json does not contain 'types' configuration"

    def test_versionrc_has_tag_prefix(self, versionrc):
        """Verify .versionrc.json has tagPrefix set to 'v'."""
        assert versionrc.get("tagPrefix") == "v", \
            f".versionrc.json tagPrefix should be 'v', but is '{versionrc.get('tagPrefix')}'"

    def test_versionrc_has_bump_files(self, versionrc):
        """Verify .versionrc.json has bumpFiles configuration."""
        assert "bumpFiles" in versionrc, \
            ".versionrc.json does not contain 'bumpFiles' configuration"

    def test_versionrc_bump_files_includes_package_json(self, versionrc):
        """Verify bumpFiles includes package.json."""
        bump_files = versionrc.get("bumpFiles", [])
        filenames = [bf.get("filename") for bf in bump_files]
        assert "package.json" in filenames, \
            "bumpFiles does not include package.json"

    def test_versionrc_bump_files_includes_version_file(self, versionrc):
        """Verify bumpFiles includes VERSION file."""
        bump_files = versionrc.get("bumpFiles", [])
        filenames = [bf.get("filename") for bf in bump_files]
        assert "VERSION" in filenames, \
            "bumpFiles does not include VERSION file"

    def test_versionrc_version_file_is_plain_text_type(self, versionrc):
        """Verify VERSION file is configured as plain-text type."""
        bump_files = versionrc.get("bumpFiles", [])
        version_file_config = None
        for bf in bump_files:
            if bf.get("filename") == "VERSION":
                version_file_config = bf
                break
        assert version_file_config is not None, \
            "VERSION file not found in bumpFiles"
        assert version_file_config.get("type") == "plain-text", \
            f"VERSION file type should be 'plain-text', but is '{version_file_config.get('type')}'"


class TestVersionFile:
    """Test VERSION file content - this is where the bug is."""

    def test_version_file_contains_v_prefix(self):
        """Verify VERSION file contains the problematic 'v' prefix."""
        with open("/home/user/project/VERSION", "r") as f:
            content = f.read().strip()
        assert content == "v2.4.0", \
            f"VERSION file should contain 'v2.4.0' (the buggy state), but contains '{content}'"


class TestGitState:
    """Test git repository state."""

    def test_git_tag_v2_4_0_exists(self):
        """Verify git tag v2.4.0 exists."""
        result = subprocess.run(
            ["git", "tag", "-l", "v2.4.0"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert "v2.4.0" in result.stdout, \
            "Git tag 'v2.4.0' does not exist"

    def test_git_user_name_configured(self):
        """Verify git user.name is configured."""
        result = subprocess.run(
            ["git", "config", "user.name"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0 and result.stdout.strip(), \
            "Git user.name is not configured"

    def test_git_user_email_configured(self):
        """Verify git user.email is configured."""
        result = subprocess.run(
            ["git", "config", "user.email"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0 and result.stdout.strip(), \
            "Git user.email is not configured"

    def test_conventional_commits_exist(self):
        """Verify conventional commits exist after v2.4.0 tag."""
        result = subprocess.run(
            ["git", "log", "v2.4.0..HEAD", "--oneline"],
            cwd="/home/user/project",
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "Failed to get git log"
        commits = result.stdout.strip()
        assert commits, \
            "No commits found after v2.4.0 tag"
        # Check for feat and fix commits
        assert "feat:" in commits.lower() or "feat(" in commits.lower(), \
            "No 'feat' conventional commit found after v2.4.0"
        assert "fix:" in commits.lower() or "fix(" in commits.lower(), \
            "No 'fix' conventional commit found after v2.4.0"


class TestReleaseScript:
    """Test release script content."""

    def test_release_script_uses_standard_version(self):
        """Verify release script uses standard-version."""
        with open("/home/user/project/scripts/release.sh", "r") as f:
            content = f.read()
        assert "standard-version" in content, \
            "release.sh does not use standard-version"

    def test_release_script_uses_minor_release(self):
        """Verify release script uses --release-as minor."""
        with open("/home/user/project/scripts/release.sh", "r") as f:
            content = f.read()
        assert "--release-as minor" in content or "--release-as=minor" in content, \
            "release.sh does not use --release-as minor"


class TestNodeEnvironment:
    """Test Node.js environment."""

    def test_node_is_available(self):
        """Verify Node.js is available."""
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "Node.js is not available"
        version = result.stdout.strip()
        assert version.startswith("v"), \
            f"Unexpected Node.js version format: {version}"

    def test_npm_is_available(self):
        """Verify npm is available."""
        result = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "npm is not available"

    def test_npx_is_available(self):
        """Verify npx is available."""
        result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, \
            "npx is not available"

    def test_standard_version_installed_locally(self):
        """Verify standard-version is installed in node_modules."""
        assert os.path.isdir("/home/user/project/node_modules/standard-version"), \
            "standard-version is not installed in node_modules"


class TestProjectWritable:
    """Test that project directory is writable."""

    def test_project_directory_is_writable(self):
        """Verify /home/user/project is writable."""
        assert os.access("/home/user/project", os.W_OK), \
            "/home/user/project is not writable"

    def test_version_file_is_writable(self):
        """Verify VERSION file is writable."""
        assert os.access("/home/user/project/VERSION", os.W_OK), \
            "VERSION file is not writable"

    def test_package_json_is_writable(self):
        """Verify package.json is writable."""
        assert os.access("/home/user/project/package.json", os.W_OK), \
            "package.json is not writable"

    def test_changelog_is_writable(self):
        """Verify CHANGELOG.md is writable."""
        assert os.access("/home/user/project/CHANGELOG.md", os.W_OK), \
            "CHANGELOG.md is not writable"

    def test_versionrc_is_writable(self):
        """Verify .versionrc.json is writable."""
        assert os.access("/home/user/project/.versionrc.json", os.W_OK), \
            ".versionrc.json is not writable"
