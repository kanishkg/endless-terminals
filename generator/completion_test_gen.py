# generator/completion_test_gen.py
"""Generate a pytest *template* that validates the **final** state after the task
is completed.

This script consumes the task-template JSON produced by ``task_template_gen.py``
(which contains the description template, parameter schema and a privileged
``truth`` section).  It samples concrete values for each placeholder, renders a
full *task description* and then asks the LLM to create a single pytest file
(`test_final_state.py`) that passes **only if** the task has been solved
correctly.  The privileged ``truth`` data is forwarded to the LLM so the tests
can assert the exact expected end state.
"""
from __future__ import annotations

import textwrap
from pathlib import Path
import sys
from typing import Optional

# Ensure the project root is on ``sys.path`` so ``generator.chat_completion`` can
# be imported when this script is executed from arbitrary working directories.
sys.path.insert(0, str(Path().resolve()))
from generator import  parse_python_code, check_python_code, chat_completion_batch

# ---------------------------------------------------------------------------
# LLM prompt scaffolding
# ---------------------------------------------------------------------------

SYSTEM_MSG = """You are a senior Python engineer who writes robust pytest suites.
Write a robust pytest suite that validates the **FINAL** state of the operating-system / container **after** the student has
completed the task described.
Use the privileged *truth* data to assert the exact expected end state for the task to be completed.

Rules:
* The filename must be ``test_final_state.py`` (show it in a header comment).
* Use **only** the Python standard library and ``pytest`` (no third-party libs).
* Failures must clearly explain **what is still wrong**.
* When you check for files or directories, always use their *absolute* paths exactly as given (no relative paths).
* Ensure that the the state of the OS matches the truth after the task is completed.
* Write the code in a fenced code block that can be parsed to get a single python file.

Evaluation approach guidelines:
* Prefer semantic validation over exact string matching. For example:
  - Parse JSON/YAML and check keys/values instead of comparing raw strings.
  - Use `in` or regex to check for required content instead of exact line matching.
  - Check numeric values with tolerance (abs(actual - expected) < epsilon) instead of string comparison.
* For service-based tasks, test that services respond correctly:
  - Use subprocess to curl/wget endpoints and check response codes and content.
  - Check that ports are listening (socket connect or ss/netstat).
  - Verify processes are running (subprocess: pgrep, ps).
* For command-output tasks, run the command and check its exit code and stdout.
* For file tasks, validate structure and key content, not exact byte-for-byte match.
* Never check exact whitespace, trailing newlines, or formatting that the task didn't explicitly specify.
* For easy tasks, tests should check simple outcomes (file exists, content contains expected value).
* For hard tasks, tests can check complex multi-faceted state but should still validate semantics over exact formatting."""

USER_TEMPLATE = """The task description is: {task_description}
The truth value is: {truth}
Task difficulty: {difficulty}
The tests to check the initial container state, before the task is completed, are:
{initial_test_py}
Write the code in a fenced code block that can be parsed."""

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def generate_test_templates_batch(
    items: list[tuple[str, ...]],
    *,
    model: str = "qwen/Qwen2.5-3B-Instruct",
    temperature: float = 0.6,
    max_tokens: int = 2048,
    max_concurrency: int = 128,
) -> list[Optional[str]]:
    """Batched generation of final-state pytest templates.

    items: list of (task_description, truth, initial_test_py) or
           (task_description, truth, initial_test_py, difficulty).
    Returns aligned list with None on failure.
    """

    messages: list[list[dict[str, str]]] = []
    for item in items:
        task_description, truth, initial_test_py = item[0], item[1], item[2]
        difficulty = item[3] if len(item) > 3 else "medium"
        prompt = USER_TEMPLATE.format(
            task_description=task_description,
            truth=truth,
            initial_test_py=initial_test_py,
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


