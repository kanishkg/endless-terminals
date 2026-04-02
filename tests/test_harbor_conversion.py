"""
Unit tests for Harbor task conversion functionality.

Tests the convert_tasks.py module that converts Endless Terminals tasks
to Harbor format.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from generator.convert_to_harbor.convert_tasks import (
    load_task_json,
    create_instruction_md,
    convert_task_to_harbor,
    get_task_directories,
)


class TestLoadTaskJson:
    """Test loading task.json files."""

    def test_load_valid_task_json(self, tmp_path):
        """Test loading a valid task.json file."""
        task_dir = tmp_path / "task_001"
        task_dir.mkdir()

        task_data = {
            "task_id": "001",
            "task_description": "Test task description",
            "category": "test",
        }

        task_json = task_dir / "task.json"
        task_json.write_text(json.dumps(task_data))

        result = load_task_json(task_dir)
        assert result is not None
        assert result["task_id"] == "001"
        assert result["task_description"] == "Test task description"

    def test_load_missing_task_json(self, tmp_path):
        """Test loading from directory without task.json."""
        task_dir = tmp_path / "task_002"
        task_dir.mkdir()

        result = load_task_json(task_dir)
        assert result is None

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON file."""
        task_dir = tmp_path / "task_003"
        task_dir.mkdir()

        task_json = task_dir / "task.json"
        task_json.write_text("{ invalid json }")

        result = load_task_json(task_dir)
        assert result is None


class TestCreateInstructionMd:
    """Test instruction.md generation from task data."""

    def test_create_instruction_with_description(self):
        """Test creating instruction.md with task description."""
        task_data = {
            "task_description": "Create a Python script that sorts numbers.",
            "task_id": "001",
        }

        result = create_instruction_md(task_data)

        assert "# Task" in result
        assert "Create a Python script that sorts numbers." in result
        assert "<!-- Task ID: 001 -->" in result

    def test_create_instruction_without_task_id(self):
        """Test creating instruction.md without task_id."""
        task_data = {
            "task_description": "Write a bash script.",
        }

        result = create_instruction_md(task_data)

        assert "# Task" in result
        assert "Write a bash script." in result
        assert "<!-- Task ID" not in result

    def test_create_instruction_with_fallback_description(self):
        """Test fallback when task_description is missing."""
        task_data = {
            "description": "Alternative description field",
        }

        result = create_instruction_md(task_data)

        assert "Alternative description field" in result

    def test_create_instruction_no_description(self):
        """Test fallback when no description exists."""
        task_data = {}

        result = create_instruction_md(task_data)

        assert "No description available" in result


class TestGetTaskDirectories:
    """Test task directory discovery."""

    def test_get_task_directories_valid(self, tmp_path):
        """Test finding valid task directories."""
        # Create task directories with task.json
        for i in range(3):
            task_dir = tmp_path / f"task_{i:03d}_hash"
            task_dir.mkdir()
            (task_dir / "task.json").write_text("{}")

        # Create invalid directory (no task.json)
        invalid_dir = tmp_path / "task_invalid"
        invalid_dir.mkdir()

        # Create non-task directory
        other_dir = tmp_path / "other_dir"
        other_dir.mkdir()
        (other_dir / "task.json").write_text("{}")

        result = get_task_directories(tmp_path)

        assert len(result) == 3
        assert all("task" in d.name for d in result)

    def test_get_task_directories_empty(self, tmp_path):
        """Test with empty directory."""
        result = get_task_directories(tmp_path)
        assert len(result) == 0

    def test_get_task_directories_nonexistent(self, tmp_path):
        """Test with nonexistent directory."""
        nonexistent = tmp_path / "nonexistent"
        result = get_task_directories(nonexistent)
        assert len(result) == 0


class TestConvertTaskToHarbor:
    """Test end-to-end task conversion."""

    @pytest.fixture
    def sample_task_dir(self, tmp_path):
        """Create a sample Endless Terminals task directory."""
        task_dir = tmp_path / "source" / "task_001_abcd"
        task_dir.mkdir(parents=True)

        # Create task.json
        task_data = {
            "task_id": "001",
            "task_description": "Test task for unit testing",
        }
        (task_dir / "task.json").write_text(json.dumps(task_data))

        # Create test_final_state.py
        test_code = "def test_example():\n    assert True\n"
        (task_dir / "test_final_state.py").write_text(test_code)

        # Create container.def
        container_def = "Bootstrap: docker\nFrom: ubuntu:22.04\n"
        (task_dir / "container.def").write_text(container_def)

        return task_dir

    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create output directory for Harbor tasks."""
        output = tmp_path / "output"
        output.mkdir()
        return output

    def test_convert_task_success(self, sample_task_dir, output_dir):
        """Test successful task conversion."""
        with mock.patch("generator.convert_to_harbor.convert_tasks.convert_def_to_dockerfile") as mock_convert:
            mock_convert.return_value = "FROM ubuntu:22.04\nRUN echo test"

            result = convert_task_to_harbor(
                sample_task_dir,
                output_dir,
                reuse_dockerfile=False,
            )

            assert result["success"] is True
            assert result["error"] is None

            # Check Harbor directory was created
            harbor_dir = output_dir / sample_task_dir.name
            assert harbor_dir.exists()

            # Check instruction.md
            assert (harbor_dir / "instruction.md").exists()

            # Check environment/Dockerfile
            assert (harbor_dir / "environment" / "Dockerfile").exists()

            # Check tests/
            assert (harbor_dir / "tests" / "test_final_state.py").exists()
            assert (harbor_dir / "tests" / "test.sh").exists()

            # Check test.sh is executable
            test_sh = harbor_dir / "tests" / "test.sh"
            assert test_sh.stat().st_mode & 0o111  # Executable bit

    def test_convert_task_missing_files(self, tmp_path, output_dir):
        """Test conversion with missing required files."""
        task_dir = tmp_path / "incomplete_task"
        task_dir.mkdir()

        # Only create task.json, missing other files
        task_data = {"task_description": "Incomplete task"}
        (task_dir / "task.json").write_text(json.dumps(task_data))

        result = convert_task_to_harbor(task_dir, output_dir)

        assert result["success"] is False
        assert "Missing required files" in result["error"]

    def test_convert_task_reuse_dockerfile(self, sample_task_dir, output_dir):
        """Test conversion with reuse_dockerfile option."""
        # Pre-create Harbor directory with Dockerfile
        harbor_dir = output_dir / sample_task_dir.name
        harbor_dir.mkdir()
        (harbor_dir / "environment").mkdir()
        existing_dockerfile = harbor_dir / "environment" / "Dockerfile"
        existing_dockerfile.write_text("FROM ubuntu:22.04\nRUN echo existing")

        with mock.patch("generator.convert_to_harbor.convert_tasks.convert_def_to_dockerfile") as mock_convert:
            result = convert_task_to_harbor(
                sample_task_dir,
                output_dir,
                reuse_dockerfile=True,
            )

            # Should not call LLM conversion
            mock_convert.assert_not_called()
            assert result["success"] is True


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def test_batch_conversion(self, tmp_path):
        """Test converting multiple tasks in batch."""
        # Create source tasks
        source_dir = tmp_path / "tasks"
        source_dir.mkdir()

        for i in range(5):
            task_dir = source_dir / f"task_{i:03d}_hash"
            task_dir.mkdir()

            task_data = {"task_description": f"Task {i}"}
            (task_dir / "task.json").write_text(json.dumps(task_data))
            (task_dir / "test_final_state.py").write_text("def test(): pass")
            (task_dir / "container.def").write_text("Bootstrap: docker\nFrom: ubuntu:22.04")

        # Get task directories
        tasks = get_task_directories(source_dir)
        assert len(tasks) == 5

        # Convert all (mock the LLM call)
        output_dir = tmp_path / "harbor"
        output_dir.mkdir()

        with mock.patch("generator.convert_to_harbor.convert_tasks.convert_def_to_dockerfile") as mock_convert:
            mock_convert.return_value = "FROM ubuntu:22.04"

            results = []
            for task in tasks:
                result = convert_task_to_harbor(task, output_dir)
                results.append(result)

            # Check all succeeded
            assert all(r["success"] for r in results)
            assert len(list(output_dir.iterdir())) == 5
