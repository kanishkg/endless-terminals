# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Endless Terminals** is a pipeline for procedurally generating terminal-use tasks and training RL agents on them — without human annotation. Tasks are generated, containerized, solved, and used as training data.

The project was developed in two stages:

- **Stage 1** (`generator/`, `train/`): vLLM-based task generation pipeline and SkyRL RL training. Uses Apptainer containers and a local vLLM server.
- **Stage 2** (top-level `*.py` scripts, `app/`, `aicore_*.py`): AICore/Claude-based generation and evaluation via the Harbor framework. Uses Docker containers. Scripts in `scripts/` are mixed — some belong to Stage 1, some to Stage 2.

## Environment Setup

```bash
uv sync                        # Install all dependencies
uv sync --extra harbor         # Include harbor + aicore deps
uv sync --extra train          # Include ray/hydra for training
```

Always run Harbor via the repo venv to ensure correct dependencies:
```bash
source .venv/bin/activate
# or directly:
.venv/bin/harbor run ...
```

## Key Commands

**Stage 2 — Task generation (AICore/Claude):**
```bash
python generate_harbor_tasks.py --num-tasks 10 --out-dir harbor_tasks --model claude_opus
```

**Stage 2 — Harbor evaluation run:**
```bash
.venv/bin/harbor run \
  --agent-import-path aicore_agent:AICoreTerminus2 \
  --model claude_4_5 \
  --path harbor_tasks_part2_2-1 \
  --n-attempts 8 \
  --jobs-dir solution_grace \
  --n-concurrent 10 \
  --job-name harbor_tasks_part2_2-1
```

```bash
uv run python -m app.server --port 5050   # http://127.0.0.1:5050
```

**Tests:**
```bash
pytest                                    # all tests
pytest -m unit                            # unit tests only
pytest -m "not slow"                      # skip slow tests
pytest tests/test_foo.py::test_bar -v     # single test
```

**Lint:**
```bash
ruff check .
ruff format .
```

## Architecture

### Stage 1 — vLLM-based Pipeline (`generator/`, `train/`)

Multi-stage LLM pipeline using a local vLLM server and Apptainer containers:

Multi-stage LLM pipeline — each stage calls Claude (or vLLM) and validates output:

Multi-stage LLM pipeline using a local vLLM server and Apptainer containers:

1. `generator/task_template_gen.py` — generates task description + category
2. `generator/initial_state_test_gen.py` — generates pytest to validate container setup
3. `generator/completion_test_gen.py` — generates pytest to verify task completion
4. `generator/dockerfile_gen.py` — generates Ubuntu 22.04 Dockerfile for the environment
5. `generator/apptainer_def_gen.py` — generates Apptainer definition (alternative to Docker)

**RL Training** (`train/`):
- `train/prepare_endless.py` — converts task trajectories to HuggingFace dataset format
- `train/main_endless.py` — Hydra entry point, launches SkyRL PPO trainer
- `train/sky_endless.py` — gym environment wrapper for task containers
- `train/confs/` — YAML configs (base, qwen, t4 variants)

### Stage 2 — AICore/Claude + Harbor (top-level scripts, `app/`, `aicore_*.py`)

Stage 2 upgrades the full pipeline to use Harbor for orchestration and Docker for containerization. Apptainer is dropped — Docker is now the sole container runtime. The generator stages from Stage 1 are reused but LLM calls are routed through AICore instead of a local vLLM server.


**Task generation & evaluation via AICore:**
- `generate_harbor_tasks.py` — generates Harbor-format tasks using Claude via AICore
- `generate_harbor_solutions.py` — runs solution attempts using Claude via AICore
- `collect_harbor_results.py` — aggregates Harbor trial results

**AICore LLM backend** (`aicore_*.py`) — three-layer stack routing calls through SAP AICore:
- `aicore_llm_access.py` — low-level: `ClaudeModels` enum with deployment IDs, `get_anthropic_completion()`
- `aicore_llm.py` — mid-level: `AICoreAnthropicLLM` implementing Harbor's `BaseLLM` via Bedrock converse API
- `aicore_agent.py` — top-level: `AICoreTerminus2` subclasses Harbor's `Terminus2`, swaps LiteLLM backend
- `generator/aicore_batch.py` — drop-in replacement for vLLM `chat_completion_batch` in generator modules

Models: `claude_opus` and `claude_4_5`. Deployment IDs configured in `aicore_llm_access.py`.

**Harbor evaluation** (`endless_harbor/`, `aicore_agent.py`):
- Harbor orchestrates agent runs in Docker containers and scores via pytest verifiers
- `endless_harbor/endless_agent.py` — Harbor `BaseAgent` for the vLLM-based agent (Stage 1 bridge)
- Results land in `solution_grace/<job-name>/` — every trial saved regardless of pass/fail


**Known issue in generated Dockerfiles**: `generator/dockerfile_gen.py` produces `RUN cat > file << 'EOF'` heredoc syntax which Docker's parser rejects (~97% of `harbor_tasks_part2_2-*` tasks affected). Fix: prepend `# syntax=docker/dockerfile:1` to enable BuildKit heredoc support.

## Infrastructure Monitoring Tools

- **Docker cleanup loop** must be manually restarted after reboots: `nohup bash scripts/run_docker_cleanup_loop.sh >> harbor_logs/docker_cleanup.log 2>&1 &`
- **Resource monitoring**: `bash scripts/check_resources.sh`
- Harbor runs log to `harbor_logs/harbor_run_<name>.log`
- Results summarized in `output/` as markdown files


Behavioral guidelines to reduce common LLM coding mistakes. Merge
with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For
 trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick sil
ently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated
?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.
When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused
.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's r
equest.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make th
em pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
