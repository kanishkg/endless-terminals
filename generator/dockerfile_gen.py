"""Generate a Dockerfile for task environment setup and validate via Docker build + test."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

from tqdm import tqdm

from generator import chat_completion_batch

SYSTEM_MSG = """You are an expert in Docker.
You are given a task description and will be tested so that the initial state of the container is set up in a way that an agent can be tested on the task.
Make sure that the container is set up in a way that an agent can be tested on the task.
Basically ensure that the task is valid when the container is built: Clone a repository, create a file, create a directory, create a process, etc.

Key rules:
- Always use `FROM ubuntu:22.04` as the base image.
- Install pytest via pip3.
- Create /home/user directory with appropriate permissions (chmod 0777 /home/user).
- The agent will not have root access. So make sure that the right permissions are set for the files and directories.
- Don't include the tests in the Dockerfile (no COPY of test files).
- Don't add any of the output files or directories that the agent will create.
- Don't create / touch empty files for the agent.
- The home path is /home/user.
- For tasks that require running services/daemons (e.g. web servers, databases, redis), set up an entrypoint script or use CMD to start them. Services started in RUN steps won't persist — use a wrapper script that starts services then exec's into a shell.
- NO Docker-in-Docker, Kubernetes, kind, minikube, or container orchestration tools — they cannot work inside this container.
- NO systemd or init systems. Start services directly as processes (e.g. `postgres -D /data &` not `systemctl start postgresql`).
- NO nftables/iptables rules — the container has no NET_ADMIN capability.
- For PostgreSQL: initialize with `initdb`, then start with `pg_ctl start` or `postgres -D <datadir> &` in an entrypoint script. Do NOT use `apt install postgresql` and expect the service to auto-start.
- For any service that must be running when the agent connects: use a CMD/ENTRYPOINT wrapper script that starts the service in the background, waits for it to be ready, then exec's into bash.

Heredoc and multiline command rules (IMPORTANT):
- Every shell command must be inside a `RUN` instruction. Do NOT leave lines like `PermitRootLogin yes` or similar outside of a `RUN`; otherwise Docker will treat them as invalid instructions.
- When using heredoc blocks (e.g. `cat <<EOF ... EOF`):
  - Keep the entire heredoc inside a single `RUN` instruction.
  - The line with `<<EOF` (or `<< 'EOF'`) must be the last thing on that line (no trailing `&&` etc.).
  - The heredoc body must start on the next line and be left as plain text.
  - The terminating `EOF` must be alone on its own line with nothing after it.
  - If needed, you may place any follow-up commands (e.g. `chmod ...`) in a separate `RUN` instruction after the heredoc.
- Do NOT wrap a heredoc block inside a single-quoted string like `sh -c 'cat <<EOF ... EOF'`.

CRITICAL: Your response must start with `FROM ubuntu:22.04` on the very first line. Do NOT include any explanation, commentary, thinking, or markdown fences. Output ONLY valid Dockerfile instructions — nothing else."""


BASE_USER_TEMPLATE = """
Using the task description template and pytest tests below, output a complete
Dockerfile that sets up the initial environment for the task.

Task difficulty: {difficulty}

Question description given to the agent:
{task_description}

Here is some ground truth data that might be useful to you:
{truth}

Here are the tests that will be run on the container to verify the initial state:
{test_py}

Previous failures (may be empty):
{failures}

Make sure that you create the right files and directories for the task.
Eg: for a csv task you will have to create a csv file. For a process cleanup task you will have to create processes.
Don't include the tests in the Dockerfile or copy a test file.
Don't add any of the output files or directories that the student will create.
Don't create / touch empty files for the agent.
Remember to install pytest in the container.
The home path is /home/user.

IMPORTANT: Output ONLY the Dockerfile starting with `FROM ubuntu:22.04`. No explanation, no markdown fences, no thinking — just the raw Dockerfile content.
"""


def parse_dockerfile(raw: str) -> str:
    """Extract Dockerfile content from LLM response, stripping markdown fences and preamble."""
    content = raw.strip()

    # Remove markdown code block markers if present
    if "```dockerfile" in content.lower():
        parts = content.split("```")
        for i, part in enumerate(parts):
            if "dockerfile" in part.lower() and i + 1 < len(parts):
                content = parts[i + 1].strip()
                break
    elif "```" in content:
        parts = content.split("```")
        for i, part in enumerate(parts):
            if "FROM" in part and i > 0:
                content = part.strip()
                break
        else:
            lines = content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)

    content = textwrap.dedent(content).strip()

    # If the LLM prefixed the output with a bare "dockerfile" or "Dockerfile"
    # language tag (no fences), strip it so Docker doesn't choke on it.
    first_line = content.split("\n", 1)[0].strip().lower()
    if first_line in ("dockerfile", "docker"):
        content = content.split("\n", 1)[1].strip()

    # Strip any preamble text before the first FROM instruction.
    # LLMs sometimes output thinking/explanation before the actual Dockerfile.
    from_match = re.search(r"^FROM\s", content, re.MULTILINE)
    if from_match and from_match.start() > 0:
        content = content[from_match.start():]

    return content


def _create_dockerignore(context_dir: Path) -> None:
    """Create a .dockerignore to minimize build context transfer."""
    ignore_path = context_dir / ".dockerignore"
    if not ignore_path.exists():
        ignore_path.write_text(
            "*.sif\n*.tar\n*.tar.gz\n*.zip\nsolutions/\n__pycache__/\n*.pyc\n.git/\n"
        )


def build_and_test_docker(
    dockerfile_text: str,
    test_py: str,
    final_test_py: Optional[str] = None,
    memory_limit: str = "8g",
    build_timeout: int = 600,
    test_timeout: int = 300,
) -> Tuple[bool, str]:
    """Build a Docker image from a Dockerfile, run initial tests, and verify final tests fail.

    Returns (success, output_message).
    """
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)

        # Write Dockerfile and test file
        dockerfile_path = td_path / "Dockerfile"
        dockerfile_path.write_text(dockerfile_text)

        test_file = td_path / "test_initial_state.py"
        test_file.write_text(test_py)

        _create_dockerignore(td_path)

        # Build the Docker image
        image_tag = f"harbor-gen-test-{os.getpid()}-{id(dockerfile_text):x}"
        build_cmd = [
            "docker", "build",
            "--memory", memory_limit,
            "--memory-swap", memory_limit,
            "--network", "host",
            "--progress=plain",
            "-t", image_tag,
            "-f", str(dockerfile_path),
            str(td_path),
        ]
        try:
            build_proc = subprocess.run(
                build_cmd,
                capture_output=True,
                text=True,
                timeout=build_timeout,
            )
            if build_proc.returncode != 0:
                return False, f"Docker build failed:\n{build_proc.stdout}\n{build_proc.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Docker build timed out"
        except FileNotFoundError:
            return False, "Docker not found on PATH"

        # Run initial tests inside the container
        test_cmd = [
            "docker", "run", "--rm",
            "--memory", "4g",
            "--memory-swap", "4g",
            "-v", f"{td_path}:/mnt",
            image_tag,
            "bash", "-c",
            "cp /mnt/test_initial_state.py /home/user/ && cd /home/user && pytest -v test_initial_state.py",
        ]
        try:
            test_proc = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=test_timeout,
            )
        except subprocess.TimeoutExpired:
            _cleanup_image(image_tag)
            return False, "Test execution timed out"

        if test_proc.returncode != 0:
            _cleanup_image(image_tag)
            return False, test_proc.stdout + test_proc.stderr

        # Verify final tests FAIL in initial state (task is not trivially solved)
        if final_test_py:
            final_test_file = td_path / "test_final_state.py"
            final_test_file.write_text(final_test_py)

            final_test_cmd = [
                "docker", "run", "--rm",
                "--memory", "4g",
                "--memory-swap", "4g",
                "-v", f"{td_path}:/mnt:ro",
                image_tag,
                "bash", "-c",
                "cp /mnt/test_final_state.py /home/user/ && cd /home/user && pytest -v test_final_state.py",
            ]
            try:
                final_proc = subprocess.run(
                    final_test_cmd,
                    capture_output=True,
                    text=True,
                    timeout=test_timeout,
                )
            except subprocess.TimeoutExpired:
                _cleanup_image(image_tag)
                return False, "Final test execution timed out"

            if final_proc.returncode == 0:
                _cleanup_image(image_tag)
                return False, "Final tests pass in initial state - task is trivially solved"

        _cleanup_image(image_tag)
        return True, test_proc.stdout + test_proc.stderr


def _cleanup_image(image_tag: str) -> None:
    """Remove a Docker image, ignoring errors."""
    try:
        subprocess.run(
            ["docker", "rmi", "-f", image_tag],
            capture_output=True,
            timeout=30,
        )
    except Exception:
        pass


def generate_dockerfiles_batch(
    items: List[Tuple[str, ...]],
    *,
    model: str = "claude_opus",
    temperature: float = 0.6,
    max_tokens: int = 4096,
    max_concurrency: int = 4,
    build_containers: bool = True,
) -> List[Optional[str]]:
    """Batched Dockerfile generation followed by optional parallel build/test.

    items: list of (task_description, truth, test_py) or
           (task_description, truth, test_py, difficulty).
    Returns list aligned with input: passing Dockerfile text, or None on failure.
    """
    messages: list[list[dict[str, str]]] = []
    for item in items:
        task_description, truth, test_py = item[0], item[1], item[2]
        difficulty = item[3] if len(item) > 3 else "medium"
        prompt = BASE_USER_TEMPLATE.format(
            task_description=task_description,
            truth=truth,
            test_py=test_py,
            failures="None yet",
            difficulty=difficulty,
        )
        messages.append([
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user", "content": prompt},
        ])

    responses = chat_completion_batch(
        messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        num_completions=1,
        max_concurrency=max_concurrency,
    )

    results: List[Optional[str]] = [None] * len(items)

    if not build_containers:
        # Skip build/test -- just parse Dockerfiles
        for idx, resp in enumerate(responses):
            if resp is None:
                continue
            try:
                content = resp.choices[0].message.content
                results[idx] = parse_dockerfile(content)
            except Exception:
                pass
        return results

    # Build and test in parallel
    def worker(index: int, item: Tuple[str, ...], resp_obj) -> Tuple[int, Optional[str]]:
        try:
            if resp_obj is None:
                return index, None
            content = resp_obj.choices[0].message.content
            dockerfile_text = parse_dockerfile(content)
            _task_description, _truth, test_py = item[0], item[1], item[2]
            final_test_py = item[4] if len(item) > 4 else None
            import logging
            _log = logging.getLogger(__name__)
            _log.warning(
                "Parsed Dockerfile for task %d (first 500 chars):\n%s", index, dockerfile_text[:500]
            )
            ok, err_msg = build_and_test_docker(dockerfile_text, test_py, final_test_py=final_test_py)
            if not ok:
                _log.warning(
                    "Docker build/test FAILED for task %d:\n%s", index, err_msg[:2000]
                )
            return index, (dockerfile_text if ok else None)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "Docker worker exception for task %d: %s", index, exc
            )
            return index, None

    futures = []
    with ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as executor:
        for idx, (item, resp) in enumerate(zip(items, responses)):
            futures.append(executor.submit(worker, idx, item, resp))

        for fut in tqdm(as_completed(futures), total=len(futures), desc="Docker build/test"):
            idx, value = fut.result()
            results[idx] = value

    return results
