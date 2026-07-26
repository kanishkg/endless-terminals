#!/usr/bin/env python3
"""Collect harbor run results into each task's solution/ folder and compute pass@k.

Scans one or more harbor job directories, groups trials by task, copies the
trial directories into ``harbor_tasks/<task>/solution/``, and writes a
``solution.json`` with per-task pass@k metrics.

Usage:
    # Collect from a single job:
    python collect_harbor_results.py --jobs-dir harbor_jobs_aicore/2026-04-14__21-35-22

    # Collect from every job under harbor_jobs_aicore/:
    python collect_harbor_results.py --jobs-dir harbor_jobs_aicore

    # Override the tasks directory (default: reads from each trial's config):
    python collect_harbor_results.py --jobs-dir harbor_jobs_aicore --tasks-dir harbor_tasks
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import defaultdict
from math import comb
from pathlib import Path
from typing import Any


def compute_pass_at_k(n: int, c: int) -> dict[int, float]:
    """Unbiased pass@k estimator (Chen et al., 2021)."""
    results: dict[int, float] = {}
    for k in range(1, n + 1):
        if c == 0:
            results[k] = 0.0
        else:
            results[k] = 1.0 - (comb(n - c, k) / comb(n, k))
    return results


def find_job_dirs(jobs_dir: Path) -> list[Path]:
    """Return a list of job directories (contain result.json + trial folders)."""
    if (jobs_dir / "config.json").exists():
        # jobs_dir is itself a single job directory
        return [jobs_dir]
    # Otherwise, look for subdirectories that are job dirs
    found = []
    for child in sorted(jobs_dir.iterdir()):
        if child.is_dir() and (child / "config.json").exists():
            found.append(child)
    if not found:
        print(f"No job directories found under {jobs_dir}", file=sys.stderr)
    return found


def collect_trials(job_dirs: list[Path]) -> dict[str, list[dict[str, Any]]]:
    """Group trial info by task_name across all job dirs.

    Returns {task_name: [{trial_dir, reward, task_path}, ...]}.
    """
    tasks: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for job_dir in job_dirs:
        for trial_dir in sorted(job_dir.iterdir()):
            result_file = trial_dir / "result.json"
            if not trial_dir.is_dir() or not result_file.exists():
                continue

            try:
                result = json.loads(result_file.read_text())
            except (json.JSONDecodeError, OSError) as e:
                print(f"  Warning: could not read {result_file}: {e}", file=sys.stderr)
                continue

            task_name = result.get("task_name")
            if not task_name:
                continue

            reward = 0.0
            vr = result.get("verifier_result") or {}
            rewards = vr.get("rewards") or {}
            reward = float(rewards.get("reward", 0.0))

            task_path = None
            task_id = result.get("task_id") or {}
            if task_id.get("path"):
                task_path = task_id["path"]

            tasks[task_name].append({
                "trial_dir": trial_dir,
                "trial_name": result.get("trial_name", trial_dir.name),
                "reward": reward,
                "task_path": task_path,
                "result": result,
            })

    return dict(tasks)


def copy_trials_and_write_summary(
    task_name: str,
    trials: list[dict[str, Any]],
    tasks_dir: Path | None,
) -> dict[str, Any] | None:
    """Copy trial dirs into the task's solution/ folder and write solution.json."""

    # Resolve the task directory
    task_dir = None
    if tasks_dir:
        task_dir = tasks_dir / task_name
    else:
        # Infer from the first trial's config
        for t in trials:
            if t["task_path"]:
                task_dir = Path(t["task_path"])
                break

    if task_dir is None or not task_dir.is_dir():
        print(f"  Skipping {task_name}: task directory not found", file=sys.stderr)
        return None

    solution_dir = task_dir / "solution"
    solution_dir.mkdir(parents=True, exist_ok=True)

    # Copy each trial directory into solution/trials/<trial_name>
    trials_dest = solution_dir / "trials"
    trials_dest.mkdir(parents=True, exist_ok=True)

    n = len(trials)
    c = 0
    trial_summaries = []

    for t in trials:
        trial_name = t["trial_name"]
        reward = t["reward"]
        src = t["trial_dir"]

        if reward >= 1.0:
            c += 1

        # Copy trial directory
        dest = trials_dest / trial_name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)

        trial_summaries.append({
            "trial_name": trial_name,
            "reward": reward,
            "success": reward >= 1.0,
        })

    pass_at_k = compute_pass_at_k(n, c)

    summary = {
        "task_name": task_name,
        "num_runs": n,
        "num_success": c,
        "pass_at_k": {str(k): v for k, v in pass_at_k.items()},
        "trials": trial_summaries,
    }

    (solution_dir / "solution.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Collect harbor run results into task solution/ folders with pass@k.",
    )
    parser.add_argument(
        "--jobs-dir", required=True, type=Path,
        help="Path to a job directory or parent of multiple job directories.",
    )
    parser.add_argument(
        "--tasks-dir", type=Path, default=None,
        help="Path to harbor_tasks/ directory. If not set, inferred from trial configs.",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Harbor Results Collector")
    print("=" * 60)

    job_dirs = find_job_dirs(args.jobs_dir)
    if not job_dirs:
        return
    print(f"Found {len(job_dirs)} job dir(s): {[d.name for d in job_dirs]}")

    tasks = collect_trials(job_dirs)
    print(f"Found {sum(len(v) for v in tasks.values())} trials across {len(tasks)} tasks\n")

    all_summaries: list[dict[str, Any]] = []

    for task_name in sorted(tasks):
        trials = tasks[task_name]
        summary = copy_trials_and_write_summary(task_name, trials, args.tasks_dir)
        if summary is None:
            continue
        all_summaries.append(summary)

        p1 = summary["pass_at_k"].get("1", 0)
        print(
            f"  {task_name}: {summary['num_success']}/{summary['num_runs']} passed, "
            f"pass@1={float(p1):.3f}"
        )

    # Aggregate
    print("\n" + "=" * 60)
    print("Aggregate Results")
    print("=" * 60)
    if all_summaries:
        total_tasks = len(all_summaries)
        solved = sum(1 for s in all_summaries if s["num_success"] > 0)
        avg_p1 = sum(float(s["pass_at_k"].get("1", 0)) for s in all_summaries) / total_tasks

        # Compute aggregate pass@k for a few useful values of k
        max_n = min(s["num_runs"] for s in all_summaries)
        print(f"Tasks:           {total_tasks}")
        print(f"Solved (>=1):    {solved}/{total_tasks}")
        print(f"Avg pass@1:      {avg_p1:.3f}")

        for k in [1, 2, 4, 8, 16]:
            if k > max_n:
                break
            avg_pk = sum(float(s["pass_at_k"].get(str(k), 0)) for s in all_summaries) / total_tasks
            print(f"Avg pass@{k:<2}:     {avg_pk:.3f}")

        # Write aggregate summary
        agg_path = args.jobs_dir / "aggregate_pass_at_k.json"
        agg = {
            "total_tasks": total_tasks,
            "solved": solved,
            "avg_pass_at_k": {
                str(k): sum(float(s["pass_at_k"].get(str(k), 0)) for s in all_summaries) / total_tasks
                for k in range(1, max_n + 1)
            },
            "per_task": {
                s["task_name"]: {
                    "num_runs": s["num_runs"],
                    "num_success": s["num_success"],
                    "pass_at_k": s["pass_at_k"],
                }
                for s in all_summaries
            },
        }
        agg_path.write_text(json.dumps(agg, indent=2), encoding="utf-8")
        print(f"\nAggregate results saved to {agg_path}")
    else:
        print("No results collected.")


if __name__ == "__main__":
    main()
