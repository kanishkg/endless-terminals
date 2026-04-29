# test_initial_state.py
"""
Tests to validate the initial state of the system before the student performs the task.
This verifies that /home/user/ci/build.sh exists with the expected content and that
DOCKER_BUILDKIT=1 is NOT yet exported in the file.
"""

import os
import stat
import pytest


BUILD_SCRIPT_PATH = "/home/user/ci/build.sh"
CI_DIR_PATH = "/home/user/ci"


class TestInitialState:
    """Test suite to validate the initial state before the task is performed."""

    def test_ci_directory_exists(self):
        """Verify that /home/user/ci directory exists."""
        assert os.path.isdir(CI_DIR_PATH), (
            f"Directory {CI_DIR_PATH} does not exist. "
            "The CI directory must exist before the task can be performed."
        )

    def test_ci_directory_is_writable(self):
        """Verify that /home/user/ci directory is writable."""
        assert os.access(CI_DIR_PATH, os.W_OK), (
            f"Directory {CI_DIR_PATH} is not writable. "
            "The agent needs write access to modify the build script."
        )

    def test_build_script_exists(self):
        """Verify that /home/user/ci/build.sh exists."""
        assert os.path.isfile(BUILD_SCRIPT_PATH), (
            f"File {BUILD_SCRIPT_PATH} does not exist. "
            "The build script must exist before the task can be performed."
        )

    def test_build_script_is_executable(self):
        """Verify that /home/user/ci/build.sh is executable."""
        assert os.path.isfile(BUILD_SCRIPT_PATH), f"File {BUILD_SCRIPT_PATH} does not exist."
        file_stat = os.stat(BUILD_SCRIPT_PATH)
        is_executable = file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        assert is_executable, (
            f"File {BUILD_SCRIPT_PATH} is not executable. "
            "The build script must be executable."
        )

    def test_build_script_has_shebang(self):
        """Verify that the build script starts with #!/bin/bash shebang."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash", (
            f"Build script does not start with '#!/bin/bash'. "
            f"Found: '{first_line}'"
        )

    def test_build_script_has_set_e(self):
        """Verify that the build script contains 'set -e'."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert "set -e" in content, (
            "Build script does not contain 'set -e'. "
            "The script should have error handling enabled."
        )

    def test_build_script_has_docker_build_command(self):
        """Verify that the build script contains the docker build command."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert "docker build -t myapp:latest ." in content, (
            "Build script does not contain 'docker build -t myapp:latest .'. "
            "The docker build command must be present."
        )

    def test_build_script_has_docker_tag_command(self):
        """Verify that the build script contains the docker tag command."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert "docker tag myapp:latest registry.internal/myapp:latest" in content, (
            "Build script does not contain 'docker tag myapp:latest registry.internal/myapp:latest'. "
            "The docker tag command must be present."
        )

    def test_build_script_has_echo_statements(self):
        """Verify that the build script contains the expected echo statements."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'echo "Starting build..."' in content, (
            "Build script does not contain 'echo \"Starting build...\"'."
        )
        assert 'echo "Build complete"' in content, (
            "Build script does not contain 'echo \"Build complete\"'."
        )

    def test_no_docker_buildkit_export_exists(self):
        """Verify that DOCKER_BUILDKIT=1 is NOT exported in the file currently."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()

        # Check that there's no export DOCKER_BUILDKIT=1 line
        lines = content.split('\n')
        buildkit_exports = [line for line in lines if 'export DOCKER_BUILDKIT=1' in line]

        assert len(buildkit_exports) == 0, (
            f"DOCKER_BUILDKIT=1 export already exists in {BUILD_SCRIPT_PATH}. "
            f"Found {len(buildkit_exports)} occurrence(s). "
            "The initial state should NOT have this export."
        )

    def test_no_docker_buildkit_env_var_set(self):
        """Verify that DOCKER_BUILDKIT is not set anywhere in the file."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()

        # Check for any DOCKER_BUILDKIT setting (not just export)
        assert "DOCKER_BUILDKIT" not in content, (
            f"DOCKER_BUILDKIT is already referenced in {BUILD_SCRIPT_PATH}. "
            "The initial state should not have any DOCKER_BUILDKIT references."
        )

    def test_build_script_content_matches_expected(self):
        """Verify the complete content of the build script matches expected initial state."""
        expected_content = """#!/bin/bash
set -e

echo "Starting build..."
docker build -t myapp:latest .
docker tag myapp:latest registry.internal/myapp:latest
echo "Build complete"
"""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            actual_content = f.read()

        # Normalize line endings for comparison
        expected_normalized = expected_content.strip()
        actual_normalized = actual_content.strip()

        assert actual_normalized == expected_normalized, (
            f"Build script content does not match expected initial state.\n"
            f"Expected:\n{expected_normalized}\n\n"
            f"Actual:\n{actual_normalized}"
        )
