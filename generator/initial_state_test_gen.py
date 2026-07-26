"""Generate pytest *template* for validating the initial OS state."""
from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Optional
import sys

sys.path.insert(0, str(Path().resolve()))
from generator import parse_python_code, check_python_code

SYSTEM_MSG = """
You are a senior Python engineer who writes robust pytest suites.
Write *one* pytest file that validates the operating system / filesystem **before** the student performs the action.
The truth value indicates the answer that the student should get.
You should test for the presence of files, directories, processes, repositories, websites, etc.

Rules:
* The filename should be `test_initial_state.py` (show it in a header comment).
* Use only stdlib + pytest.
* Failures must clearly explain what is missing.
* Ensure that the the state of the OS matches the truth.
* Write the code in a fenced code block that can be parsed to get a single python file.
* When you test for a file or directory, test for the full path to the file or directory, not just relative path.
* DO NOT test for any of the output files or directories.
* The home path is /home/user.
* For service-based tasks, verify that required services/daemons are running and listening.
* For tasks involving processes, verify the expected processes exist.
* Use subprocess calls to check service state when needed (e.g., `ss -tlnp`, `pgrep`, `systemctl`).
"""

USER_TEMPLATE = """The task description is: {task_description}
The truth value is: {truth}
Task difficulty: {difficulty}
Write the code in a fenced code block that can be parsed."""


def generate_test_templates_batch(
    items: list[tuple[str, ...]],
    *,
    model: str = "qwen/Qwen2.5-3B-Instruct",
    temperature: float = 0.6,
    max_tokens: int = 2048,
    max_concurrency: int = 128,
) -> list[Optional[str]]:
    """Batched generation of initial-state pytest templates.

    items: list of (task_description, truth) or
           (task_description, truth, difficulty).
    Returns a list aligned to input, with None for failures.
    """
    from generator import chat_completion_batch

    messages: list[list[dict[str, str]]] = []
    for item in items:
        task_description, truth = item[0], item[1]
        difficulty = item[2] if len(item) > 2 else "medium"
        prompt = USER_TEMPLATE.format(
            task_description=task_description,
            truth=truth,
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

    results: list[Optional[str]] = []
    for resp in responses:
        if resp is None:
            results.append(None)
            continue
        try:
            content = textwrap.dedent(resp.choices[0].message.content)
            parsed = parse_python_code(content)
            if check_python_code(parsed):
                results.append(parsed)
            else:
                results.append(None)
        except Exception:
            results.append(None)
    return results
