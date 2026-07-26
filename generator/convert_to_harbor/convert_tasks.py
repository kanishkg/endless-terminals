"""Convert Endless Terminals tasks to Harbor format.

Reads task directories (with task.json, test_final_state.py, container.def)
and writes Harbor-compatible output (instruction.md, environment/Dockerfile,
tests/test_final_state.py, tests/test.sh).
"""
from __future__ import annotations

import json
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional

from generator.convert_to_harbor.convert_sif_docker import convert_def_to_dockerfile


def load_task_json(task_dir: Path) -> Optional[Dict[str, Any]]:
    """Load and parse task.json from a task directory. Returns None on failure."""
    task_json = task_dir / "task.json"
    if not task_json.exists():
        return None
    try:
        return json.loads(task_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def create_instruction_md(task_data: Dict[str, Any]) -> str:
    """Generate instruction.md content from task metadata."""
    description = (
        task_data.get("task_description")
        or task_data.get("description")
        or "No description available"
    )
    task_id = task_data.get("task_id")
    lines = ["# Task", "", description, ""]
    if task_id:
        lines.append(f"<!-- Task ID: {task_id} -->")
    return "\n".join(lines)


def get_task_directories(tasks_dir: Path) -> List[Path]:
    """Return sorted list of valid task directories (contain task.json, name starts with 'task')."""
    if not tasks_dir.exists():
        return []
    return sorted(
        d for d in tasks_dir.iterdir()
        if d.is_dir() and "task" in d.name and (d / "task.json").exists()
    )


def convert_task_to_harbor(
    task_dir: Path,
    output_dir: Path,
    reuse_dockerfile: bool = False,
    model: str = "gpt-5.1",
    provider: str = "openai",
) -> Dict[str, Any]:
    """Convert a single Endless Terminals task directory to Harbor format.

    Args:
        task_dir: Source task directory (must contain task.json, test_final_state.py, container.def).
        output_dir: Destination root; Harbor task is written to output_dir/task_dir.name/.
        reuse_dockerfile: Skip LLM conversion if Dockerfile already exists.
        model: LLM model for def→Dockerfile conversion.
        provider: LLM provider ("openai" or "anthropic").

    Returns:
        Dict with keys ``success`` (bool) and ``error`` (str or None).
    """
    required = [
        task_dir / "task.json",
        task_dir / "test_final_state.py",
        task_dir / "container.def",
    ]
    missing = [str(f) for f in required if not f.exists()]
    if missing:
        return {"success": False, "error": f"Missing required files: {missing}"}

    task_data = load_task_json(task_dir)
    if task_data is None:
        return {"success": False, "error": "Failed to load task.json"}

    harbor_dir = output_dir / task_dir.name
    env_dir = harbor_dir / "environment"
    tests_dir = harbor_dir / "tests"

    harbor_dir.mkdir(parents=True, exist_ok=True)
    env_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)

    # instruction.md
    (harbor_dir / "instruction.md").write_text(
        create_instruction_md(task_data), encoding="utf-8"
    )

    # Dockerfile — reuse if present, otherwise convert via LLM
    dockerfile_path = env_dir / "Dockerfile"
    if reuse_dockerfile and dockerfile_path.exists():
        pass  # keep existing
    else:
        def_content = (task_dir / "container.def").read_text(encoding="utf-8")
        dockerfile_content = convert_def_to_dockerfile(
            def_content, model=model, provider=provider
        )
        if not dockerfile_content:
            return {"success": False, "error": "Dockerfile conversion failed"}
        dockerfile_path.write_text(dockerfile_content, encoding="utf-8")

    # tests/test_final_state.py
    test_src = (task_dir / "test_final_state.py").read_text(encoding="utf-8")
    (tests_dir / "test_final_state.py").write_text(test_src, encoding="utf-8")

    # tests/test.sh
    test_sh = tests_dir / "test.sh"
    test_sh.write_text(
        "#!/bin/bash\nset -e\npython3 -m pytest /tests/test_final_state.py -v\n",
        encoding="utf-8",
    )
    test_sh.chmod(test_sh.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return {"success": True, "error": None}
