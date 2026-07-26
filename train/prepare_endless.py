import subprocess
import sys
import pathlib
import argparse
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import datasets
import json
from pathlib import Path

sys.path.insert(0, str(pathlib.Path().resolve()))
from generator.sample_solutions import _extract_action, SYSTEM_MESSAGE, USER_TEMPLATE


def build_container_for_task(task_dir_name, task_dir, verbose=True):
    """Build Docker image for a single task. Returns (task_dir_name, success)."""
    dockerfile = Path(task_dir) / task_dir_name / "environment" / "Dockerfile"

    if not dockerfile.exists():
        print(f"Dockerfile not found for {task_dir_name}")
        return task_dir_name, False

    tag = f"harbor-task-{task_dir_name}:latest"
    try:
        proc = subprocess.run(
            ["docker", "build", "-t", tag, "-f", str(dockerfile), str(dockerfile.parent)],
            capture_output=True, text=True, timeout=300,
        )
        if proc.returncode != 0:
            if verbose:
                print(f"Docker build failed for {task_dir_name}: {proc.stderr[-200:]}")
            return task_dir_name, False
        return task_dir_name, True
    except Exception as e:
        print(f"Error building Docker image for {task_dir_name}: {e}")
        return task_dir_name, False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="./data")
    parser.add_argument("--task-dir", default="./tasks")
    parser.add_argument("--difficulty", default="none")
    parser.add_argument("--max-time", default=300)
    parser.add_argument("--eval-count", type=int, default=100)
    parser.add_argument("--build-docker", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-workers", type=int, default=20, help="Number of parallel workers for building containers")
    parser.add_argument(
        "--source", choices=["stage1", "stage2"], default=None,
        help=(
            "Task filtering mode. 'stage1': filter by solutions/o3_summary.json pass@16>0 "
            "(vLLM/Apptainer tasks). 'stage2': filter by solution/solution.json num_success>0 "
            "(Harbor/Docker tasks). Auto-detected if not set."
        ),
    )

    args = parser.parse_args()
    random.seed(args.seed)
    task_dir_names = [f for f in os.listdir(args.task_dir) if "task" in f]
    # check if task dir has solution
    task_dir_names = [f for f in task_dir_names if (Path(args.task_dir) / f / "solution" / "solution.json").exists()]
    # check if solution pass @16 is greater than 0
    task_dir_names = [f for f in task_dir_names if any(v > 0 for v in json.load(open(Path(args.task_dir) / f / "solution" / "solution.json"))["pass_at_k"].values())]
    task_dir_names = list(sorted(task_dir_names))
    random.shuffle(task_dir_names)
    task_descriptions = [json.load(open(Path(args.task_dir) / f / "environment" / "task.json"))["description"] for f in task_dir_names]

    # Build containers in parallel if requested
    failed_tasks = set()
    if args.build_docker:
        print(f"Building containers in parallel with {args.max_workers} workers...")
        completed = 0
        total = len(task_dir_names)
        progress_lock = Lock()
        
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            # Submit all build tasks with verbose=False
            future_to_task = {
                executor.submit(build_container_for_task, task_dir_name, args.task_dir, verbose=False): task_dir_name
                for task_dir_name in task_dir_names
            }
            
            # Process results as they complete
            for future in as_completed(future_to_task):
                task_name, success = future.result()
                if not success:
                    failed_tasks.add(task_name)
                
                with progress_lock:
                    completed += 1
                    print(f"\rProgress: {completed}/{total} ({len(failed_tasks)} failed)", end='', flush=True)
        
        print()  # New line after progress
        print(f"Container building complete. Failed: {len(failed_tasks)}/{len(task_dir_names)}")

    # Prepare datasets
    train_dataset, val_dataset = [], []
    for t, task_dir_name in enumerate(task_dir_names):
        # Skip failed tasks
        if task_dir_name in failed_tasks:
            continue
            
        row = {}
        row["description"] = task_descriptions[t]
        row["task_dir"] = task_dir_name
        initial_test_path = Path(args.task_dir) / task_dir_name / "environment" / "test_initial_state.py"
        
        
        
        if t < len(task_dir_names) - args.eval_count:
            train_dataset.append(row)
        else:
            val_dataset.append(row)
    
    # convert to hf dataset
    train_dataset = datasets.Dataset.from_list(train_dataset)
    val_dataset = datasets.Dataset.from_list(val_dataset)


    # add a row to each data item that represents a unique id
    def make_map_fn(split):
        def process_fn(example, idx):
            system_prompt = SYSTEM_MESSAGE
            question = USER_TEMPLATE.format(task_description=example["description"])

            data = {
                "data_source": "endless",
                "prompt": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
                "env_class": "endless",
                "reward_spec": {
                    "method": "rule",
                    "ground_truth": os.path.join(args.task_dir, example["task_dir"]),
                },
                "extra_info": {
                    "task_dir": os.path.join(args.task_dir, example["task_dir"]),
                    "max_time": args.max_time,
                },
            }
            return data

        return process_fn

    train_dataset = train_dataset.map(function=make_map_fn("train"), with_indices=True)
    val_dataset = val_dataset.map(function=make_map_fn("val"), with_indices=True)

    print(f"Train dataset size: {len(train_dataset)}")
    print(f"Val dataset size: {len(val_dataset)}")
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    train_dataset.to_parquet(os.path.join(output_dir, "train.parquet"))
    val_dataset.to_parquet(os.path.join(output_dir, "validation.parquet"))