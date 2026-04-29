# test_final_state.py
"""
Tests to validate the final state of the OS/filesystem after the student
has completed the task of generating requirements-lock.txt for /home/user/webapp.
"""

import os
import re
import subprocess
import pytest


class TestRequirementsLockExists:
    """Verify requirements-lock.txt exists in the correct location."""

    def test_requirements_lock_file_exists(self):
        lock_path = "/home/user/webapp/requirements-lock.txt"
        assert os.path.exists(lock_path), (
            f"File {lock_path} does not exist - student needs to create requirements-lock.txt"
        )
        assert os.path.isfile(lock_path), f"{lock_path} exists but is not a regular file"

    def test_requirements_lock_is_readable(self):
        lock_path = "/home/user/webapp/requirements-lock.txt"
        assert os.access(lock_path, os.R_OK), f"File {lock_path} is not readable"


class TestRequirementsLockContent:
    """Verify requirements-lock.txt contains properly pinned versions."""

    def test_file_has_pinned_format(self):
        """Check that entries follow the pkg==x.y.z format."""
        lock_path = "/home/user/webapp/requirements-lock.txt"
        with open(lock_path, "r") as f:
            content = f.read()

        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

        assert len(lines) > 0, "requirements-lock.txt is empty or contains only comments"

        # Pattern for pinned package: name==version (allowing various version formats)
        pin_pattern = re.compile(r'^[a-zA-Z0-9_-]+==\d+(\.\d+)*.*$', re.IGNORECASE)

        for line in lines:
            # Skip lines that might be editable installs or other special formats
            if line.startswith("-e") or line.startswith("@"):
                continue
            assert pin_pattern.match(line), (
                f"Line '{line}' does not match expected pinned format 'package==x.y.z'"
            )

    def test_contains_flask_pinned(self):
        """Check that flask==2.3.2 is present."""
        lock_path = "/home/user/webapp/requirements-lock.txt"
        with open(lock_path, "r") as f:
            content = f.read().lower()

        assert "flask==2.3.2" in content, (
            "requirements-lock.txt must contain 'flask==2.3.2' (exact version)"
        )

    def test_contains_requests_pinned(self):
        """Check that requests==2.31.0 is present."""
        lock_path = "/home/user/webapp/requirements-lock.txt"
        with open(lock_path, "r") as f:
            content = f.read().lower()

        assert "requests==2.31.0" in content, (
            "requirements-lock.txt must contain 'requests==2.31.0' (exact version)"
        )

    def test_contains_click_pinned(self):
        """Check that click==8.1.3 is present."""
        lock_path = "/home/user/webapp/requirements-lock.txt"
        with open(lock_path, "r") as f:
            content = f.read().lower()

        assert "click==8.1.3" in content, (
            "requirements-lock.txt must contain 'click==8.1.3' (exact version)"
        )

    def test_contains_transitive_dependencies(self):
        """Check that transitive dependencies are included (anti-shortcut guard)."""
        lock_path = "/home/user/webapp/requirements-lock.txt"
        with open(lock_path, "r") as f:
            content = f.read().lower()

        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith("#")]

        # Must have at least 8 lines (3 top-level + their deps)
        assert len(lines) >= 8, (
            f"requirements-lock.txt has only {len(lines)} lines, expected at least 8 "
            "(the 3 top-level packages plus their transitive dependencies)"
        )

        # Check for some expected transitive dependencies
        expected_deps = ["werkzeug", "jinja2", "markupsafe", "itsdangerous", "certifi", "urllib3"]
        found_deps = []
        for dep in expected_deps:
            if dep in content:
                found_deps.append(dep)

        assert len(found_deps) >= 4, (
            f"requirements-lock.txt should contain transitive dependencies. "
            f"Expected some of {expected_deps}, found only: {found_deps}"
        )


class TestOriginalRequirementsTxtUnchanged:
    """Verify the original requirements.txt was not modified."""

    def test_requirements_txt_still_exists(self):
        req_path = "/home/user/webapp/requirements.txt"
        assert os.path.exists(req_path), f"Original {req_path} was deleted or moved"
        assert os.path.isfile(req_path), f"{req_path} is not a regular file"

    def test_requirements_txt_still_unpinned(self):
        """Verify requirements.txt still contains unpinned packages (not modified)."""
        req_path = "/home/user/webapp/requirements.txt"
        with open(req_path, "r") as f:
            content = f.read()

        lines = [line.strip().lower() for line in content.splitlines() if line.strip()]

        # Check that flask, requests, click are present and unpinned
        assert "flask" in lines, "requirements.txt should still contain 'flask'"
        assert "requests" in lines, "requirements.txt should still contain 'requests'"
        assert "click" in lines, "requirements.txt should still contain 'click'"

        # Verify they are still unpinned (no == in the package names)
        for line in lines:
            if line in ["flask", "requests", "click"]:
                assert "==" not in line, (
                    f"requirements.txt was modified - '{line}' should remain unpinned"
                )


class TestVirtualenvStillFunctional:
    """Verify the virtualenv remains functional after the task."""

    def test_venv_python_still_works(self):
        python_path = "/home/user/webapp/venv/bin/python"
        assert os.path.exists(python_path), f"Virtualenv python at {python_path} is missing"

        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Virtualenv python failed to run: {result.stderr}"

    def test_venv_pip_still_works(self):
        pip_path = "/home/user/webapp/venv/bin/pip"
        assert os.path.exists(pip_path), f"Virtualenv pip at {pip_path} is missing"

        result = subprocess.run(
            [pip_path, "--version"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Virtualenv pip failed to run: {result.stderr}"

    def test_packages_still_installed(self):
        """Verify the original packages are still installed in the venv."""
        pip_path = "/home/user/webapp/venv/bin/pip"
        result = subprocess.run(
            [pip_path, "freeze"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"pip freeze failed: {result.stderr}"

        installed = result.stdout.lower()
        assert "flask==2.3.2" in installed, "flask==2.3.2 should still be installed in venv"
        assert "requests==2.31.0" in installed, "requests==2.31.0 should still be installed in venv"
        assert "click==8.1.3" in installed, "click==8.1.3 should still be installed in venv"


class TestRequirementsLockIsValidPipFormat:
    """Verify that requirements-lock.txt can be used with pip install."""

    def test_pip_can_parse_requirements_lock(self):
        """Verify pip can parse the requirements-lock.txt file (dry run check)."""
        pip_path = "/home/user/webapp/venv/bin/pip"
        lock_path = "/home/user/webapp/requirements-lock.txt"

        # Use pip's --dry-run to verify the file is valid without actually installing
        result = subprocess.run(
            [pip_path, "install", "--dry-run", "-r", lock_path],
            capture_output=True,
            text=True
        )

        # The command should succeed (exit code 0) even if packages are already installed
        assert result.returncode == 0, (
            f"pip cannot parse requirements-lock.txt - invalid format. "
            f"stderr: {result.stderr}"
        )
