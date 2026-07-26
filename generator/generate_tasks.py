from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import uuid
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
import asyncio

from tqdm import tqdm


from generator.task_template_gen import generate_templates_batch
from generator.initial_state_test_gen import generate_test_templates_batch as generate_initial_tests_batch
from generator.apptainer_def_gen import iterate_def_template_batch
from generator.completion_test_gen import generate_test_templates_batch as generate_final_tests_batch



@dataclass
class PipelineConfig:
    num_tasks: int
    out_dir: Path
    max_def_retries: int = 5
    max_num_completions: int = 4
    num_solutions: int = 256
    max_actions: int = 20
    model: str = "qwen/qwen-3-32b"
    max_tokens: int = 1024
    task_temperature: float = 1.0
    test_temperature: float = 0.6
    solution_temperature: float = 1.0
    parallel_jobs: int = 1
    verbose: bool = False


def _safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _build_sif(def_path: Path, sif_path: Path) -> bool:
    sif_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        # build_rc = subprocess.run(["apptainer", "build", str(sif_path), str(def_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180).returncode

        rc = subprocess.run(["apptainer", "build", str(sif_path), str(def_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        return rc == 0
    except FileNotFoundError:
        # apptainer not installed / not on PATH
        return False
    except subprocess.TimeoutExpired:
        # SIF build timed out
        return False

def _format_task_dir(base: Path, idx: int, width: int = 6) -> Path:
    suffix = uuid.uuid4().hex[:8]
    return base / f"task_{idx:0{width}d}_{suffix}"

def _save_task_bundle(
    task_dir: Path,
    task_obj: Dict[str, Any],
    initial_test_code: str,
    def_text: str,
    final_test_code: str,
    summary: Dict[str, Any],
) -> Tuple[Path, Path, Path, Path, Path]:
    task_json = task_dir / "task.json"
    init_py = task_dir / "test_initial_state.py"
    final_py = task_dir / "test_final_state.py"
    def_file = task_dir / "container.def"
    sif_file = task_dir / "container.sif"
    sol_dir = task_dir / "solutions"
    sol_dir.mkdir(parents=True, exist_ok=True)

    _safe_write_text(task_json, json.dumps(task_obj, indent=4))
    _safe_write_text(init_py, initial_test_code)
    _safe_write_text(final_py, final_test_code)
    _safe_write_text(def_file, def_text)
    _safe_write_text(sol_dir / "summary.json", json.dumps(summary, indent=4))

    return task_json, init_py, final_py, def_file, sif_file


@dataclass
class AsyncBatchConfig(PipelineConfig):
    batch_size: int = 64
    max_concurrency: int = 64



def _generate_batch(cfg: AsyncBatchConfig, batch_count: int) -> List[Optional[Path]]:
    
    # 1) Task templates
    print(f"Generating {batch_count} task templates with {cfg.max_concurrency} concurrency")
    task_templates = generate_templates_batch(
        batch_count,
        model=cfg.model,
        temperature=cfg.task_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
    )

    if not task_templates:
        print("No task templates generated")
        return []

    descriptions: List[str] = [t.get("description", "").strip() for t in task_templates]
    truths: List[str] = [t.get("truth", "").strip() for t in task_templates]


    # Filter out invalid entries early
    valid_indices = [i for i, (d, tr) in enumerate(zip(descriptions, truths)) if d and tr]
    if not valid_indices:
        print("No valid task templates generated")
        return []


    descriptions = [descriptions[i] for i in valid_indices]
    truths = [truths[i] for i in valid_indices]

    print(f"Task templates generated: {len(descriptions)}")

    # 2) Initial tests (batch)
    print(f"Generating {len(descriptions)} initial tests with {cfg.max_concurrency} concurrency")
    init_tests = generate_initial_tests_batch(
        list(zip(descriptions, truths)),
        model=cfg.model,
        temperature=cfg.test_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
    )

    # get valid indices from init_tests
    valid_indices = [i for i, test in enumerate(init_tests) if test]
    descriptions = [descriptions[i] for i in valid_indices]
    truths = [truths[i] for i in valid_indices]
    init_tests = [init_tests[i] for i in valid_indices]

    print(f"Generated {len(init_tests)} initial tests")

    # 3) Final tests (batch)
    print(f"Generating {len(descriptions)} final tests with {cfg.max_concurrency} concurrency")
    final_tests = generate_final_tests_batch(
        list(zip(descriptions, truths, init_tests)),
        model=cfg.model,
        temperature=cfg.test_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=cfg.max_concurrency,
    )

    print(f"Generated {len(final_tests)} final tests")
    valid_indices = [i for i, test in enumerate(final_tests) if test]
    descriptions = [descriptions[i] for i in valid_indices]
    truths = [truths[i] for i in valid_indices]
    init_tests = [init_tests[i] for i in valid_indices]
    final_tests = [final_tests[i] for i in valid_indices]


    # 4) Apptainer def – single shot per item, then build/test locally
    print(f"Generating {len(descriptions)} defs with {cfg.max_concurrency} concurrency")
    def_candidates = iterate_def_template_batch(
        list(zip(descriptions, truths, init_tests)),
        model=cfg.model,
        temperature=cfg.test_temperature,
        max_tokens=cfg.max_tokens,
        max_concurrency=min(64, cfg.max_concurrency),
    )

    valid_indices = [i for i, def_text in enumerate(def_candidates) if def_text]
    descriptions = [descriptions[i] for i in valid_indices]
    truths = [truths[i] for i in valid_indices]
    init_tests = [init_tests[i] for i in valid_indices]
    final_tests = [final_tests[i] for i in valid_indices]
    def_candidates = [def_candidates[i] for i in valid_indices]

    print(f"Generated {len(def_candidates)} defs")
    # 5) Persist successful items and build SIF + optional upload
    print(f"Saving {len(descriptions)} tasks")
    saved_paths: List[Optional[Path]] = []
    for i in range(len(descriptions)):
        desc = descriptions[i]
        tr = truths[i]
        init_py = init_tests[i]
        def_text = def_candidates[i]
        final_py = final_tests[i]

        if not desc or not tr or not init_py or not def_text or not final_py:
            saved_paths.append(None)
            continue

        task_dir = _format_task_dir(cfg.out_dir, idx=0)  # idx unused in async; name is unique
        task_obj = {"description": desc, "truth": tr, "name": task_dir.name}

        # Save artifacts
        task_json, init_path, final_path, def_path, sif_path = _save_task_bundle(
            task_dir, task_obj, init_py, def_text, final_py, summary={}
        )

        # Build SIF (optional)
        # ok = _build_sif(def_path, sif_path)
        # if not ok:
        #     shutil.rmtree(task_dir, ignore_errors=True)
        #     saved_paths.append(None)
        #     continue

        # Upload if configured
        # if cfg.azure_dest_prefix:
        #     dest = f"{cfg.azure_dest_prefix.rstrip('/')}/{task_dir.name}"
        #     _upload_directory_to_azure(task_dir, dest)

        saved_paths.append(task_dir)

    return saved_paths


def run_pipeline(cfg: AsyncBatchConfig) -> Dict[str, Any]:
    cfg.out_dir.mkdir(parents=True, exist_ok=True)

    # Use batches to fulfill requested tasks. We generate at least num_tasks items,
    # though actual successes may be fewer due to build/test failures.
    requested = cfg.num_tasks
    batch_size = max(1, cfg.batch_size)

    all_saved: List[Optional[Path]] = []
    remaining = requested

    for _ in tqdm(range((requested + batch_size - 1) // batch_size)):
        count = min(batch_size, remaining)
        results = _generate_batch(cfg, count)
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


def parse_args(argv: Optional[List[str]] = None) -> AsyncBatchConfig:
    ap = argparse.ArgumentParser(description="Generate tasks via async-batched LLM calls.")
    ap.add_argument("--num-tasks", type=int, default=100, help="How many tasks to request")
    ap.add_argument("--out-dir", type=Path, default=Path("tasks"), help="Output directory")
    ap.add_argument("--model", type=str, default="gpt-4o")
    ap.add_argument("--task-temperature", type=float, default=1.0)
    ap.add_argument("--test-temperature", type=float, default=0.6)
    ap.add_argument("--solution-temperature", type=float, default=1.0)
    ap.add_argument("--batch-size", type=int, default=100)
    ap.add_argument("--max-concurrency", type=int, default=128)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--quiet", action="store_true")

    args = ap.parse_args(argv)
    verbose = args.verbose and not args.quiet


    return AsyncBatchConfig(
        num_tasks=args.num_tasks,
        out_dir=args.out_dir,
        model=args.model,
        task_temperature=args.task_temperature,
        test_temperature=args.test_temperature,
        solution_temperature=args.solution_temperature,
        parallel_jobs=1,
        verbose=verbose,
        batch_size=max(1, args.batch_size),
        max_concurrency=max(1, args.max_concurrency),
    )


if __name__ == "__main__":
    cfg = parse_args()
    summary = run_pipeline(cfg)
    print(json.dumps(summary, indent=4))


