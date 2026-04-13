# Endless Terminals

**Scaling RL Environments for Terminal Agents**

[![Paper](https://img.shields.io/badge/Paper-arXiv-red)](https://arxiv.org/abs/2601.16443)
[![Dataset](https://img.shields.io/badge/Dataset-HuggingFace-yellow)](https://huggingface.co/collections/obiwan96/endless-terminals)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

Endless Terminals is a fully autonomous pipeline that procedurally generates terminal-use tasks without human annotation for training terminal agents with reinforcement learning.

## Installation

**Prerequisites:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
# Install Apptainer
./scripts/install_apptainer.sh

# Install dependencies
uv sync

# Download base container
./scripts/get_ubuntu_sif.sh
```

## Task Generation

Start a vLLM server locally before running task generation:

```bash
./scripts/launch_vllm_server.sh
```

Then generate tasks:

```bash
python generate_tasks.py --num-tasks 100 --out-dir ./tasks --model Qwen/Qwen3-32B --jobs 8
```

Each task generates: `task.json`, `test_initial_state.py`, `test_final_state.py`, `container.def`, and `container.sif`.

## Running Solutions

```bash
python generate_solutions.py --tasks-dir ./tasks --num-solutions 16 --model Qwen/Qwen3-32B
```

## Training

```bash
# Prepare dataset
python train/prepare_endless.py --task-dir ./tasks --output-dir ./data --build-sif

# Install SkyRL
./scripts/install_sky.sh

# Run training
ray start --head
python train/main_endless.py --config-dir train/confs --config-name base
```

Configs: `base.yaml` (Llama-3.2-3B), `base_qwen.yaml` (Qwen2.5-7B), `base_qwen3_otak8.yaml` (Qwen3-8B)

## Evaluation with Harbor

```bash
# Install Harbor
./scripts/setup.sh

# Run evaluation
./scripts/parallel_harbor.sh --model path/to/model --parallel 8
```

## Citation

```bibtex
@article{gandhi2025endless,
    title={Endless Terminals: Scaling RL Environments for Terminal Agents},
    author={Gandhi, Kanishk and Garg, Shivam and Goodman, Noah D. and Papailiopoulos, Dimitris},
    journal={arXiv preprint arXiv:2601.16443},
    year={2025}
}
```

## Harbor Task Generation

The pipeline can generate tasks in [Harbor](https://www.harborframework.com/) format, using Claude Opus 4.5 as the LLM backend instead of a local vLLM server.

**Prerequisites:** Docker, access to AICore Claude API (configured via `aicore_llm_access.py`)

The AICore integration is split across three modules:

- **`aicore_llm_access.py`** — Model registry and low-level completion function. Defines a `get_anthropic_completion()` helper used by the task and solution generators.
- **`aicore_llm.py`** — Harbor-compatible LLM backend. Implements Harbor's `BaseLLM` interface (`AICoreAnthropicLLM`) so that Harbor agents can call Claude through AICore's Bedrock-compatible API instead of LiteLLM.
- **`aicore_agent.py`** — Custom Harbor agent. Subclasses Harbor's `Terminus2` agent and swaps in `AICoreAnthropicLLM` as the LLM backend, for use with `harbor run --agent-import-path aicore_agent:AICoreTerminus2`.

### Generating Tasks

```bash
python generate_harbor_tasks.py --num-tasks 10 --out-dir harbor_tasks --model claude_opus
```

This runs a 5-stage pipeline:
1. **Task templates** — generates task descriptions and ground-truth solutions
2. **Initial-state tests** — generates pytest tests that verify the container starts in the correct state
3. **Final-state tests** — generates pytest tests that verify the task was completed correctly
4. **Dockerfiles** — generates Dockerfiles and optionally builds/tests them
5. **Save** — writes each task as a Harbor-compatible directory

Each task produces:

```
task_{id}_{hash}/
├── instruction.md              # Task prompt shown to the agent
├── task.toml                   # Harbor metadata (difficulty, timeouts, resources)
├── environment/
│   ├── Dockerfile              # Container environment definition
│   ├── task.json               # Task description + ground truth
│   └── test_initial_state.py   # Validates the initial container state
├── solution/
│   ├── solve.sh                # Reference solution script (if available)
│   └── solution.json           # Full solution attempt data
└── tests/
    ├── test.sh                 # Harbor verifier — runs pytest and writes reward
    └── test_final_state.py     # Validates task completion
```

`--skip-build` to skip Docker image building during generation, `--batch-size` to control how many are processed per LLM call.

### Generating Solutions

```bash
python generate_harbor_solutions.py \
    --tasks-dir harbor_tasks \
    --num-solutions 2 \
    --model claude_opus \
    --max-actions 16
```

For each task, this:
1. Builds the task's Docker image
2. Starts N containers (one per solution attempt)
3. Runs an agentic loop — the LLM reads the instruction, issues shell commands, and observes outputs
4. Runs the final-state tests inside each container
5. Saves `solution.json` (all attempts with message histories) and `solve.sh` (commands from the first passing attempt) to `solution/`

Tasks that already have a `solution/solution.json` are skipped automatically. Use `--workers` to process multiple tasks in parallel and `--max-actions` to cap the number of commands per attempt.

## License

Apache License 2.0 - see [LICENSE](LICENSE).
