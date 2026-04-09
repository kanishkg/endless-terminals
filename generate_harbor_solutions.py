"""Generate solutions for Harbor-format tasks using a self-contained agentic loop.

Runs N solution attempts per task in Docker containers, using AICore Claude
Opus 4.5 as the LLM.  Produces a single ``solution.json`` per task (all tries
with full message histories) and a ``solve.sh`` script extracted from the
first successful attempt.

Usage:
    python generate_harbor_solutions.py \
        --tasks-dir harbor_tasks \
        --num-solutions 2 \
        --model claude_opus \
        --max-actions 16 \
        --workers 1
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from math import comb
from pathlib import Path
from typing import Any, Dict, List, Optional

from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aicore_llm_access import get_anthropic_completion, model_aliases


MAX_OUTPUT_LENGTH = 50_000

SYSTEM_MESSAGE = """\
You are a highly capable Linux terminal agent operating strictly via a \
single-shell-command interface.
Goal: Complete the user's task.

Detailed Instructions:
- Output exactly one of the following per turn after you think in the \
<think> </think> tags:
  1) <command>THE_SINGLE_SHELL_COMMAND</command>
  XOR
  2) <action>done</action>
- Don't use interactive commands and confirmations; use non-interactive flags.
- Prefer simple, robust CLI tools; write files explicitly when needed.
- If you believe the task is solved, emit <action>done</action>.
- Run commands interactively to see the output. Don't just pipe commands.
- Only your first command in command tags will be executed.
- Verify your solution once you are done (e.g. use cat to check files).
- Do not just write long bash scripts. Write individual terminal commands.
- Only respond with one of <command>...</command> or <action>done</action> \
after you think in the <think> </think> tags.
- Plan and simulate your actions in <think> </think> tags before responding.\
"""

DONE_RE = re.compile(r"<action>\s*done\s*</action>", flags=re.IGNORECASE)
CMD_RE = re.compile(
    r"<command>\s*(.*?)\s*</command>", flags=re.IGNORECASE | re.DOTALL
)


@dataclass
class SolutionConfig:
    tasks_dir: str = "harbor_tasks"
    num_solutions: int = 2
    max_actions: int = 16
    model: str = "claude_opus"
    temperature: float = 0.8
    max_tokens: int = 4096
    num_tasks: int = 200
    start_at: int = 0
    workers: int = 1
    concurrency: int = 4
    verbose: bool = False


def _extract_action(response: str) -> Dict[str, Optional[str]]:
    """Parse LLM response for <command>...</command> or <action>done</action>."""
    if DONE_RE.search(response):
        return {"type": "done", "command": None}
    matches = CMD_RE.findall(response)
    if matches:
        command = matches[-1].strip()
        if command.lower() == "done":
            return {"type": "done", "command": None}
        return {"type": "command", "command": command}
    return {"type": "invalid", "command": None}


def compute_pass_at_k(n: int, c: int) -> Dict[int, float]:
    pass_at_k: Dict[int, float] = {}
    for k in range(1, n + 1):
        if c == 0:
            p = 0.0
        else:
            p = 1.0 - (comb(n - c, k) / comb(n, k))
        pass_at_k[k] = float(p)
    return pass_at_k


def _extract_solve_script(messages: List[Dict[str, str]]) -> str:
    """Extract shell commands from a successful message history into a script."""
    lines = ["#!/bin/bash", "# Auto-generated solve script", "set -e", ""]
    for msg in messages:
        if msg["role"] == "assistant":
            matches = CMD_RE.findall(msg["content"])
            if matches:
                cmd = matches[-1].strip()
                lines.append(cmd)
    lines.append("")
    return "\n".join(lines)


class DockerContainer:
    """Manages a single Docker container for one solution attempt."""

    def __init__(self, image_tag: str, container_name: str):
        self.image_tag = image_tag
        self.container_name = container_name
        self._started = False

    def start(self) -> bool:
        """Start the container in detached mode."""
        proc = subprocess.run(
            [
                "docker", "run", "-d",
                "--name", self.container_name,
                self.image_tag,
                "sleep", "3600",
            ],
            capture_output=True, text=True, timeout=60,
        )
        self._started = proc.returncode == 0
        return self._started

    def exec(self, command: str, timeout: int = 30) -> tuple[bool, str]:
        """Execute a command inside the container."""
        try:
            proc = subprocess.run(
                ["docker", "exec", self.container_name, "bash", "-c", command],
                capture_output=True, text=True, timeout=timeout,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            return proc.returncode == 0, output
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout}s"

    def run_tests(self, test_final_state_py: str) -> tuple[bool, str]:
        """Copy test file into container and run pytest."""
        # Write test file into container
        subprocess.run(
            ["docker", "exec", self.container_name, "mkdir", "-p", "/tests"],
            capture_output=True, timeout=10,
        )
        # Use docker cp via a temp file
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(test_final_state_py)
            tmp_path = f.name
        try:
            subprocess.run(
                ["docker", "cp", tmp_path,
                 f"{self.container_name}:/tests/test_final_state.py"],
                capture_output=True, timeout=10,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        # Install pytest and run
        self.exec("pip3 install -q pytest 2>/dev/null || pip install -q pytest 2>/dev/null", timeout=60)
        success, output = self.exec(
            "cd /home/user && python3 -m pytest /tests/test_final_state.py -v",
            timeout=120,
        )
        return success, output

    def cleanup(self):
        """Stop and remove the container."""
        if self._started:
            subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                capture_output=True, timeout=30,
            )


def build_docker_image(task_dir: Path) -> str:
    """Build Docker image from task's Dockerfile, return image tag."""
    dockerfile = task_dir / "environment" / "Dockerfile"
    tag = f"harbor-task-{task_dir.name}:{uuid.uuid4().hex[:8]}"
    proc = subprocess.run(
        ["docker", "build", "-t", tag, "-f", str(dockerfile), str(dockerfile.parent)],
        capture_output=True, text=True, timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"Docker build failed for {task_dir.name}:\n{proc.stderr[-500:]}"
        )
    return tag


def discover_tasks(cfg: SolutionConfig) -> List[Path]:
    tasks_dir = Path(cfg.tasks_dir)
    if not tasks_dir.is_dir():
        print(f"Tasks directory not found: {tasks_dir}")
        return []

    task_dirs = []
    for d in sorted(tasks_dir.iterdir()):
        if not d.name.startswith("task_"):
            continue
        required = [
            d / "instruction.md",
            d / "environment" / "Dockerfile",
            d / "tests" / "test_final_state.py",
        ]
        if all(f.exists() for f in required):
            if (d / "solution" / "solution.json").exists():
                if cfg.verbose:
                    print(f"  Skipping {d.name}: solution already exists")
                continue
            task_dirs.append(d)
        elif cfg.verbose:
            missing = [str(f) for f in required if not f.exists()]
            print(f"  Skipping {d.name}: missing {missing}")

    task_dirs = task_dirs[cfg.start_at : cfg.start_at + cfg.num_tasks]
    print(f"Found {len(task_dirs)} valid tasks")
    return task_dirs


def run_task_solutions(task_dir: Path, cfg: SolutionConfig) -> Dict[str, Any]:
    """Run all solution attempts for a single task. Returns summary dict."""
    task_name = task_dir.name
    instruction = (task_dir / "instruction.md").read_text(encoding="utf-8").strip()
    test_py = (task_dir / "tests" / "test_final_state.py").read_text(encoding="utf-8")

    print(f"\n[{task_name}] Building Docker image...")
    image_tag = build_docker_image(task_dir)

    n = cfg.num_solutions
    containers: List[DockerContainer] = []
    messages: List[List[Dict[str, str]]] = []
    results: List[Dict[str, Any]] = []

    try:
        # Start N containers
        print(f"[{task_name}] Starting {n} containers...")
        for i in range(n):
            cname = f"solve-{task_name}-{i}-{uuid.uuid4().hex[:6]}"
            c = DockerContainer(image_tag, cname)
            if not c.start():
                raise RuntimeError(f"Failed to start container {cname}")
            containers.append(c)

        # Initialize message histories
        for _ in range(n):
            messages.append([
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": instruction},
            ])

        # Agentic loop
        is_done = [False] * n
        not_done_idx = list(range(n))

        for step in range(cfg.max_actions):
            if not not_done_idx:
                break

            # Call LLM for all non-done attempts
            responses: List[str] = []
            for idx in not_done_idx:
                try:
                    resp = get_anthropic_completion(
                        messages=messages[idx],
                        model=cfg.model,
                        temperature=cfg.temperature,
                        max_tokens=cfg.max_tokens,
                    )
                except Exception as e:
                    resp = f"<think>Error calling LLM: {e}</think><action>done</action>"
                responses.append(resp)

            # Process responses
            to_mark_done: List[int] = []
            to_exec: List[tuple[int, str]] = []

            for i_resp, idx in enumerate(not_done_idx):
                resp = responses[i_resp]
                act = _extract_action(resp)

                if act["type"] == "done":
                    is_done[idx] = True
                    to_mark_done.append(idx)
                    messages[idx].append({"role": "assistant", "content": resp})
                elif act["type"] == "command":
                    messages[idx].append({"role": "assistant", "content": resp})
                    to_exec.append((idx, act["command"] or ""))
                else:
                    messages[idx].append({"role": "assistant", "content": resp})
                    messages[idx].append({
                        "role": "user",
                        "content": (
                            "Could not parse a single <command>...</command> "
                            "or <action>done</action>. Please respond with "
                            "exactly one of those."
                        ),
                    })

            # Execute commands in parallel
            if to_exec:
                def _exec_one(item: tuple[int, str]) -> tuple[int, bool, str]:
                    idx, cmd = item
                    return (idx, *containers[idx].exec(cmd))

                with ThreadPoolExecutor(max_workers=cfg.concurrency) as pool:
                    exec_results = list(pool.map(_exec_one, to_exec))

                for idx, success, output in exec_results:
                    if len(output) > MAX_OUTPUT_LENGTH:
                        output = output[:MAX_OUTPUT_LENGTH]
                        output += f"\n[Output truncated to {MAX_OUTPUT_LENGTH} chars]"

                    exit_code = 0 if success else 1
                    status = "successfully" if success else "failed"
                    messages[idx].append({
                        "role": "user",
                        "content": (
                            f"Command executed {status}. Output: {output}\n\n"
                            f"(exit_code={exit_code})"
                        ),
                    })

            # Update tracking
            done_set = set(to_mark_done)
            not_done_idx = [i for i in not_done_idx if i not in done_set]

            if cfg.verbose:
                print(
                    f"  [{task_name}] step {step + 1}: "
                    f"{n - len(not_done_idx)}/{n} done"
                )

        # Run final tests
        print(f"[{task_name}] Running tests...")
        num_success = 0

        def _run_test(i: int) -> tuple[bool, str]:
            return containers[i].run_tests(test_py)

        with ThreadPoolExecutor(max_workers=cfg.concurrency) as pool:
            finals = list(pool.map(_run_test, range(n)))

        for i in range(n):
            success, output = finals[i]
            if success:
                num_success += 1
            results.append({
                "success": success,
                "messages": messages[i],
                "output": output,
                "reward": 1 if success else 0,
            })

    finally:
        # Cleanup containers
        for c in containers:
            try:
                c.cleanup()
            except Exception:
                pass
        # Remove image
        subprocess.run(
            ["docker", "rmi", "-f", image_tag],
            capture_output=True, timeout=30,
        )

    pass_at_k = compute_pass_at_k(n, num_success)

    summary = {
        "num_runs": n,
        "num_success": num_success,
        "pass_at_k": pass_at_k,
        "results": results,
    }

    # Save solution.json
    solutions_dir = task_dir / "solution"
    solutions_dir.mkdir(parents=True, exist_ok=True)
    (solutions_dir / "solution.json").write_text(
        json.dumps(summary, indent=4), encoding="utf-8"
    )

    # Save solve.sh from first successful attempt
    for r in results:
        if r["success"]:
            script = _extract_solve_script(r["messages"])
            solve_path = solutions_dir / "solve.sh"
            solve_path.write_text(script, encoding="utf-8")
            solve_path.chmod(0o755)
            break

    print(
        f"  {task_name}: {num_success}/{n} passed, "
        f"pass@1={pass_at_k.get(1, 0):.3f}"
    )
    return summary


def parse_args(argv: Optional[List[str]] = None) -> SolutionConfig:
    ap = argparse.ArgumentParser(
        description="Generate solutions for Harbor tasks using AICore Claude.",
    )
    ap.add_argument("--tasks-dir", type=str, default="harbor_tasks")
    ap.add_argument("--num-solutions", "-k", type=int, default=2)
    ap.add_argument("--max-actions", type=int, default=16)
    ap.add_argument("--model", "-m", type=str, default="claude_opus")
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--num-tasks", type=int, default=200)
    ap.add_argument("--start-at", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)
    return SolutionConfig(**vars(args))


def main():
    cfg = parse_args()

    print("=" * 50)
    print("Harbor Solution Generator")
    print("=" * 50)
    print(f"Tasks Dir:      {cfg.tasks_dir}")
    print(f"Model:          {cfg.model}")
    print(f"Solutions/task:  {cfg.num_solutions}")
    print(f"Max actions:    {cfg.max_actions}")
    print(f"Temperature:    {cfg.temperature}")
    print("=" * 50)

    task_dirs = discover_tasks(cfg)
    if not task_dirs:
        print("No tasks found.")
        return

    all_summaries: Dict[str, Any] = {}

    for task_dir in tqdm(task_dirs, desc="Tasks"):
        try:
            summary = run_task_solutions(task_dir, cfg)
            all_summaries[task_dir.name] = {
                "num_success": summary["num_success"],
                "num_runs": summary["num_runs"],
                "pass_at_1": summary["pass_at_k"].get(1, 0),
            }
        except Exception as e:
            print(f"Error processing {task_dir.name}: {e}")

    # Aggregate
    print("\n" + "=" * 50)
    print("Aggregate Results")
    print("=" * 50)
    total = len(all_summaries)
    if total > 0:
        avg_p1 = sum(s["pass_at_1"] for s in all_summaries.values()) / total
        solved = sum(1 for s in all_summaries.values() if s["num_success"] > 0)
        print(f"Tasks processed: {total}")
        print(f"Tasks solved (>0): {solved}/{total}")
        print(f"Avg pass@1: {avg_p1:.3f}")
    else:
        print("No results collected.")


if __name__ == "__main__":
    main()
