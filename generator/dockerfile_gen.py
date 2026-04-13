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

Heredoc and multiline command rules (IMPORTANT):
- Every shell command must be inside a `RUN` instruction. Do NOT leave lines like `PermitRootLogin yes` or similar outside of a `RUN`; otherwise Docker will treat them as invalid instructions.
- When using heredoc blocks (e.g. `cat <<EOF ... EOF`):
  - Keep the entire heredoc inside a single `RUN` instruction.
  - The line with `<<EOF` (or `<< 'EOF'`) must be the last thing on that line (no trailing `&&` etc.).
  - The heredoc body must start on the next line and be left as plain text.
  - The terminating `EOF` must be alone on its own line with nothing after it.
  - If needed, you may place any follow-up commands (e.g. `chmod ...`) in a separate `RUN` instruction after the heredoc.
- Do NOT wrap a heredoc block inside a single-quoted string like `sh -c 'cat <<EOF ... EOF'`.

Output only the Dockerfile content, no explanations or markdown code blocks."""


BASE_USER_TEMPLATE = """
Using the task description template and pytest tests below, output a complete
Dockerfile that sets up the initial environment for the task.

Question description given to the agent:
{task_description}

Here is some ground truth data that might be useful to you:
{truth}

Here are the tests that will be run on the container to verify the initial state:
{test_py}

Previous failures (may be empty):
{failures}

Respond with the Dockerfile only. You should think step by step and then write the file. The file should be valid and buildable.
Make sure that you create the right files and directories for the task.
Eg: for a csv task you will have to create a csv file. For a process cleanup task you will have to create processes.
Don't include the tests in the Dockerfile or copy a test file.
Don't add any of the output files or directories that the student will create.
Don't create / touch empty files for the agent.
Remember to install pytest in the container.
The home path is /home/user.
"""


def parse_dockerfile(raw: str) -> str:
    """Extract Dockerfile content from LLM response, stripping markdown fences."""
    content = raw.strip()

    # Remove markdown code block markers if present
    if "```dockerfile" in content.lower():
        parts = content.split("```")
        for i, part in enumerate(parts):
            if "dockerfile" in part.lower() and i + 1 < len(parts):
                content = parts[i + 1].strip()
                break
    elif content.startswith("```"):
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
    memory_limit: str = "8g",
    build_timeout: int = 600,
    test_timeout: int = 300,
) -> Tuple[bool, str]:
    """Build a Docker image from a Dockerfile and run initial tests inside it.

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

        # Clean up Docker image
        _cleanup_image(image_tag)

        return test_proc.returncode == 0, test_proc.stdout + test_proc.stderr


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
    items: List[Tuple[str, str, str]],
    *,
    model: str = "claude_opus",
    temperature: float = 0.6,
    max_tokens: int = 4096,
    max_concurrency: int = 4,
    build_containers: bool = True,
) -> List[Optional[str]]:
    """Batched Dockerfile generation followed by optional parallel build/test.

    items: list of (task_description, truth, test_py)
    Returns list aligned with input: passing Dockerfile text, or None on failure.
    """
    messages: list[list[dict[str, str]]] = []
    for task_description, truth, test_py in items:
        prompt = BASE_USER_TEMPLATE.format(
            task_description=task_description,
            truth=truth,
            test_py=test_py,
            failures="None yet",
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
    def worker(index: int, item: Tuple[str, str, str], resp_obj) -> Tuple[int, Optional[str]]:
        try:
            if resp_obj is None:
                return index, None
            content = resp_obj.choices[0].message.content
            dockerfile_text = parse_dockerfile(content)
            _task_description, _truth, test_py = item
            ok, _ = build_and_test_docker(dockerfile_text, test_py)
            return index, (dockerfile_text if ok else None)
        except Exception:
            return index, None

    futures = []
    with ThreadPoolExecutor(max_workers=max(1, max_concurrency)) as executor:
        for idx, (item, resp) in enumerate(zip(items, responses)):
            futures.append(executor.submit(worker, idx, item, resp))

        for fut in tqdm(as_completed(futures), total=len(futures), desc="Docker build/test"):
            idx, value = fut.result()
            results[idx] = value

    return results
