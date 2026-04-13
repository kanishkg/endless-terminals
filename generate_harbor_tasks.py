"""Generate terminal-agent tasks in Harbor framework format using AICore Claude Opus 4.5.

Usage:
    python generate_harbor_tasks.py --num-tasks 10 --out-dir harbor_tasks --model claude_opus

Each generated task follows the Harbor directory structure:
    task_{id}/
    ├── instruction.md
    ├── task.toml
    ├── environment/
    │   ├── Dockerfile
    │   ├── task.json
    │   └── test_initial_state.py
    ├── solution/
    └── tests/
        ├── test.sh
        └── test_final_state.py
"""
from __future__ import annotations

import argparse
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm import tqdm


# Monkey-patch the LLM backend: swap vLLM for AICore across all generator
# modules *before* importing their public API functions.
import generator
from generator.aicore_batch import chat_completion_batch as aicore_batch

generator.chat_completion_batch = aicore_batch

import generator.task_template_gen as ttg
import generator.initial_state_test_gen as istg
import generator.completion_test_gen as ctg
import generator.dockerfile_gen as dfg

for _mod in (ttg, istg, ctg, dfg):
    if hasattr(_mod, "chat_completion_batch"):
        _mod.chat_completion_batch = aicore_batch

# Override Apptainer mention in the task-template system prompt
ttg.SYSTEM_MSG = ttg.SYSTEM_MSG.replace(
    "We will be using apptainer to run the agent. So make sure that the task is valid when the container is built.",
    "We will be using Docker to run the agent. So make sure that the task is valid when the container is built.",
)

from generator.task_template_gen import generate_templates_batch
from generator.initial_state_test_gen import (
    generate_test_templates_batch as generate_initial_tests_batch,
)
from generator.completion_test_gen import (
    generate_test_templates_batch as generate_final_tests_batch,
)
from generator.dockerfile_gen import generate_dockerfiles_batch

@dataclass
class HarborPipelineConfig:
    num_tasks: int = 10
    out_dir: Path = Path("harbor_tasks")
    model: str = "claude_opus"
    max_tokens: int = 4096
    task_temperature: float = 1.0
    test_temperature: float = 0.6
    max_concurrency: int = 4
    batch_size: int = 10
    build_containers: bool = True
    author_name: str = "Endless Terminals"
    author_email: str = ""
    verbose: bool = False


TEST_SH_TEMPLATE = """#!/bin/bash

apt-get update
apt-get install -y curl
curl -LsSf https://astral.sh/uv/0.9.5/install.sh | sh
source $HOME/.local/bin/env
# Run pytest tests
cd /home/user
uvx \\
  --python 3.12 \\
  --with pytest==8.4.1 \\
  pytest /tests/test_final_state.py -v
# Check exit code and write reward
if [ $? -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
"""


def _generate_task_toml(
    cfg: HarborPipelineConfig,
    difficulty: str = "easy",
    category: str = "programming",
    tags: Optional[List[str]] = None,
) -> str:
    tags_list = tags or [category]
    tags_str = ", ".join(f'"{t}"' for t in tags_list)
    return (
        f'version = "0.1"\n'
        f"\n"
        f"[metadata]\n"
        f'author_name = "{cfg.author_name}"\n'
        f'author_email = "{cfg.author_email}"\n'
        f'difficulty = "{difficulty}"\n'
        f'category = "{category}"\n'
        f"tags = [{tags_str}]\n"
        f"\n"
        f"[verifier]\n"
        f"timeout_sec = 300.0\n"
        f"\n"
        f"[agent]\n"
        f"timeout_sec = 300.0\n"
        f"\n"
        f"[environment]\n"
        f"build_timeout_sec = 600.0\n"
        f"cpus = 1\n"
        f"memory_mb = 2048\n"
        f"storage_mb = 10240\n"
    )


def _safe_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _format_task_dir(base: Path, idx: int, width: int = 6) -> Path:
    suffix = uuid.uuid4().hex[:8]
    return base / f"task_{idx:0{width}d}_{suffix}"


def _save_harbor_task(
    task_dir: Path,
    description: str,
    truth: str,
    initial_test_code: str,
    final_test_code: str,
    dockerfile_text: str,
    cfg: HarborPipelineConfig,
) -> Path:
    """Write all files for a single Harbor-format task."""
    # instruction.md
    _safe_write(task_dir / "instruction.md", description + "\n")

    # task.toml
    _safe_write(task_dir / "task.toml", _generate_task_toml(cfg))

    # environment/
    env_dir = task_dir / "environment"
    _safe_write(env_dir / "Dockerfile", dockerfile_text + "\n")
    _safe_write(
        env_dir / "task.json",
        json.dumps(
            {"description": description, "truth": truth, "name": task_dir.name},
            indent=4,
        )
        + "\n",
    )
    _safe_write(env_dir / "test_initial_state.py", initial_test_code + "\n")

    # solution/ (empty directory)
    (task_dir / "solution").mkdir(parents=True, exist_ok=True)

    # tests/
    _safe_write(task_dir / "tests" / "test.sh", TEST_SH_TEMPLATE)
    (task_dir / "tests" / "test.sh").chmod(0o755)
    _safe_write(task_dir / "tests" / "test_final_state.py", final_test_code + "\n")

    return task_dir


def _generate_harbor_batch(
    cfg: HarborPipelineConfig, batch_count: int
) -> List[Optional[Path]]:
    """Run the full 5-stage pipeline for one batch."""

    # Stage 1: Task templates
    print(f"[1/5] Generating {batch_count} task templates ...")
    task_templates = generate_templates_batch(
        batch_count,
        model=cfg.model,
        temperature=cfg.task_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
    )
    if not task_templates:
        print("  No task templates generated")
        return []

    descriptions = [t.get("description", "").strip() for t in task_templates]
    truths = [t.get("truth", "").strip() for t in task_templates]

    valid = [i for i, (d, tr) in enumerate(zip(descriptions, truths)) if d and tr]
    if not valid:
        print("  No valid task templates")
        return []
    descriptions = [descriptions[i] for i in valid]
    truths = [truths[i] for i in valid]
    print(f"  Valid templates: {len(descriptions)}")

    # Stage 2: Initial state tests
    print(f"[2/5] Generating {len(descriptions)} initial-state tests ...")
    init_tests = generate_initial_tests_batch(
        list(zip(descriptions, truths)),
        model=cfg.model,
        temperature=cfg.test_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
    )
    valid = [i for i, t in enumerate(init_tests) if t]
    descriptions = [descriptions[i] for i in valid]
    truths = [truths[i] for i in valid]
    init_tests = [init_tests[i] for i in valid]
    print(f"  Valid initial tests: {len(init_tests)}")

    # Stage 3: Final state tests
    print(f"[3/5] Generating {len(descriptions)} final-state tests ...")
    final_tests = generate_final_tests_batch(
        list(zip(descriptions, truths, init_tests)),
        model=cfg.model,
        temperature=cfg.test_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
    )
    valid = [i for i, t in enumerate(final_tests) if t]
    descriptions = [descriptions[i] for i in valid]
    truths = [truths[i] for i in valid]
    init_tests = [init_tests[i] for i in valid]
    final_tests = [final_tests[i] for i in valid]
    print(f"  Valid final tests: {len(final_tests)}")

    # Stage 4: Dockerfiles + build/test
    print(f"[4/5] Generating {len(descriptions)} Dockerfiles ...")
    dockerfiles = generate_dockerfiles_batch(
        list(zip(descriptions, truths, init_tests)),
        model=cfg.model,
        temperature=cfg.test_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
        build_containers=cfg.build_containers,
    )
    valid = [i for i, d in enumerate(dockerfiles) if d]
    descriptions = [descriptions[i] for i in valid]
    truths = [truths[i] for i in valid]
    init_tests = [init_tests[i] for i in valid]
    final_tests = [final_tests[i] for i in valid]
    dockerfiles = [dockerfiles[i] for i in valid]
    print(f"  Valid Dockerfiles: {len(dockerfiles)}")

    # Stage 5: Save Harbor bundles
    print(f"[5/5] Saving {len(descriptions)} task bundles ...")
    saved: List[Optional[Path]] = []
    for i in range(len(descriptions)):
        if not all([descriptions[i], truths[i], init_tests[i], final_tests[i], dockerfiles[i]]):
            saved.append(None)
            continue

        task_dir = _format_task_dir(cfg.out_dir, idx=0)
        task_dir = _save_harbor_task(
            task_dir,
            descriptions[i],
            truths[i],
            init_tests[i],
            final_tests[i],
            dockerfiles[i],
            cfg,
        )
        saved.append(task_dir)

    return saved


def run_harbor_pipeline(cfg: HarborPipelineConfig) -> Dict[str, Any]:
    """Orchestrate batched task generation."""
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    requested = cfg.num_tasks
    batch_size = max(1, cfg.batch_size)
    all_saved: List[Optional[Path]] = []
    remaining = requested

    for _ in tqdm(range((requested + batch_size - 1) // batch_size), desc="Batches"):
        count = min(batch_size, remaining)
        results = _generate_harbor_batch(cfg, count)
        all_saved.extend(results)
        remaining -= count

    saved = [p for p in all_saved if p is not None]
    summary = {
        "requested": requested,
        "succeeded": len(saved),
        "success_rate": (len(saved) / requested) if requested else 0.0,
        "saved_dirs": [str(p) for p in saved],
    }
    return summary


def parse_args() -> HarborPipelineConfig:
    ap = argparse.ArgumentParser(
        description="Generate Harbor-format terminal-agent tasks using AICore Claude Opus 4.5.",
    )
    ap.add_argument("--num-tasks", type=int, default=10)
    ap.add_argument("--out-dir", type=Path, default=Path("harbor_tasks"))
    ap.add_argument("--model", type=str, default="claude_opus")
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--task-temperature", type=float, default=1.0)
    ap.add_argument("--test-temperature", type=float, default=0.6)
    ap.add_argument("--max-concurrency", type=int, default=4)
    ap.add_argument("--batch-size", type=int, default=10)
    ap.add_argument("--skip-build", action="store_true", help="Skip Docker build/test")
    ap.add_argument("--author-name", type=str, default="Endless Terminals")
    ap.add_argument("--author-email", type=str, default="")
    ap.add_argument("--verbose", action="store_true")

    args = ap.parse_args()
    return HarborPipelineConfig(
        num_tasks=args.num_tasks,
        out_dir=args.out_dir,
        model=args.model,
        max_tokens=args.max_tokens,
        task_temperature=args.task_temperature,
        test_temperature=args.test_temperature,
        max_concurrency=max(1, args.max_concurrency),
        batch_size=max(1, args.batch_size),
        build_containers=not args.skip_build,
        author_name=args.author_name,
        author_email=args.author_email,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    cfg = parse_args()
    summary = run_harbor_pipeline(cfg)
    print(json.dumps(summary, indent=4))
