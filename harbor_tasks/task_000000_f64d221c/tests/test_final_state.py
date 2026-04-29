# test_final_state.py
"""
Tests to validate the final state of the system after the student has completed the task.
This verifies that /home/user/ci/build.sh has been properly modified to include
export DOCKER_BUILDKIT=1 before any docker commands, while preserving all other content.
"""

import os
import stat
import re
import pytest


BUILD_SCRIPT_PATH = "/home/user/ci/build.sh"


class TestFinalState:
    """Test suite to validate the final state after the task is performed."""

    def test_build_script_exists(self):
        """Verify that /home/user/ci/build.sh still exists."""
        assert os.path.isfile(BUILD_SCRIPT_PATH), (
            f"File {BUILD_SCRIPT_PATH} does not exist. "
            "The build script must still exist after modification."
        )

    def test_build_script_is_executable(self):
        """Verify that /home/user/ci/build.sh is still executable."""
        assert os.path.isfile(BUILD_SCRIPT_PATH), f"File {BUILD_SCRIPT_PATH} does not exist."
        file_stat = os.stat(BUILD_SCRIPT_PATH)
        is_executable = file_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        assert is_executable, (
            f"File {BUILD_SCRIPT_PATH} is not executable. "
            "The build script must remain executable after modification."
        )

    def test_build_script_has_shebang(self):
        """Verify that the build script still starts with #!/bin/bash shebang."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            first_line = f.readline().strip()
        assert first_line == "#!/bin/bash", (
            f"Build script does not start with '#!/bin/bash'. "
            f"Found: '{first_line}'. The shebang must be preserved."
        )

    def test_build_script_has_set_e(self):
        """Verify that the build script still contains 'set -e'."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert "set -e" in content, (
            "Build script does not contain 'set -e'. "
            "The error handling must be preserved."
        )

    def test_build_script_has_docker_build_command(self):
        """Verify that the build script still contains the docker build command."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert "docker build -t myapp:latest ." in content, (
            "Build script does not contain 'docker build -t myapp:latest .'. "
            "The docker build command must be preserved."
        )

    def test_build_script_has_docker_tag_command(self):
        """Verify that the build script still contains the docker tag command."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert "docker tag myapp:latest registry.internal/myapp:latest" in content, (
            "Build script does not contain 'docker tag myapp:latest registry.internal/myapp:latest'. "
            "The docker tag command must be preserved."
        )

    def test_docker_buildkit_export_exists(self):
        """Verify that export DOCKER_BUILDKIT=1 exists in the file."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()

        assert "export DOCKER_BUILDKIT=1" in content, (
            f"'export DOCKER_BUILDKIT=1' not found in {BUILD_SCRIPT_PATH}. "
            "The DOCKER_BUILDKIT environment variable must be exported."
        )

    def test_docker_buildkit_export_on_own_line(self):
        """Verify that export DOCKER_BUILDKIT=1 appears on its own line."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            lines = f.readlines()

        # Find lines that contain export DOCKER_BUILDKIT=1 as the main command
        matching_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Check if the line is exactly or starts with export DOCKER_BUILDKIT=1
            if re.match(r'^export\s+DOCKER_BUILDKIT=1\s*$', stripped):
                matching_lines.append((i, stripped))

        assert len(matching_lines) >= 1, (
            "'export DOCKER_BUILDKIT=1' does not appear on its own line. "
            "The export must be on a dedicated line, not combined with other commands."
        )

    def test_exactly_one_docker_buildkit_export(self):
        """Verify that there is exactly one export DOCKER_BUILDKIT=1 line."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            lines = f.readlines()

        # Count lines matching the pattern
        matching_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if re.match(r'^export\s+DOCKER_BUILDKIT=1\s*$', stripped):
                matching_lines.append((i, stripped))

        assert len(matching_lines) == 1, (
            f"Expected exactly one 'export DOCKER_BUILDKIT=1' line, "
            f"but found {len(matching_lines)}. "
            f"Lines found: {matching_lines}"
        )

    def test_docker_buildkit_export_before_docker_build(self):
        """Verify that export DOCKER_BUILDKIT=1 appears before the docker build command."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            lines = f.readlines()

        export_line_num = None
        docker_build_line_num = None

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if re.match(r'^export\s+DOCKER_BUILDKIT=1\s*$', stripped) and export_line_num is None:
                export_line_num = i
            if "docker build" in line and docker_build_line_num is None:
                docker_build_line_num = i

        assert export_line_num is not None, (
            "'export DOCKER_BUILDKIT=1' not found on its own line in the script."
        )
        assert docker_build_line_num is not None, (
            "'docker build' command not found in the script."
        )
        assert export_line_num < docker_build_line_num, (
            f"'export DOCKER_BUILDKIT=1' (line {export_line_num}) must appear before "
            f"'docker build' command (line {docker_build_line_num}). "
            "The environment variable must be set before docker commands run."
        )

    def test_build_script_has_echo_statements(self):
        """Verify that the build script still contains the expected echo statements."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()
        assert 'echo "Starting build..."' in content, (
            "Build script does not contain 'echo \"Starting build...\"'. "
            "The original echo statements must be preserved."
        )
        assert 'echo "Build complete"' in content, (
            "Build script does not contain 'echo \"Build complete\"'. "
            "The original echo statements must be preserved."
        )

    def test_no_extra_environment_variables(self):
        """Verify that no other environment variables were added."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            lines = f.readlines()

        # Find all export statements
        export_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('export ') and 'DOCKER_BUILDKIT' not in stripped:
                export_lines.append((i, stripped))

        assert len(export_lines) == 0, (
            f"Unexpected export statements found in the script: {export_lines}. "
            "No other environment variables should be added."
        )

    def test_script_structure_preserved(self):
        """Verify that the overall script structure is preserved with the new export."""
        with open(BUILD_SCRIPT_PATH, 'r') as f:
            content = f.read()

        # Check that key elements are present in the right order
        shebang_pos = content.find("#!/bin/bash")
        set_e_pos = content.find("set -e")
        export_pos = content.find("export DOCKER_BUILDKIT=1")
        docker_build_pos = content.find("docker build")
        docker_tag_pos = content.find("docker tag")

        assert shebang_pos == 0, "Script must start with shebang"
        assert set_e_pos > shebang_pos, "'set -e' must come after shebang"
        assert export_pos > shebang_pos, "export must come after shebang"
        assert export_pos < docker_build_pos, "export must come before docker build"
        assert docker_build_pos < docker_tag_pos, "docker build must come before docker tag"
