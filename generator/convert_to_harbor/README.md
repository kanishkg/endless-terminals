# Harbor Integration for Endless Terminals

This directory contains utilities to convert Endless Terminals tasks to Harbor format for evaluation and training.

## Overview

Harbor is a standardized agent evaluation framework that provides:
- Sandbox management (Daytona, Modal)
- Agent execution loop
- Reward computation and verification

This integration allows you to:
1. Convert Endless Terminals tasks → Harbor format
2. Evaluate agents using Harbor's infrastructure
3. Use converted tasks for SkyRL RL training

## Quick Start

```bash
# Run complete workflow
./scripts/harbor_quickstart.sh \
  --num-tasks 10 \
  --model Qwen/Qwen3-32B \
  --workers 4
```

## Step-by-Step Usage

### 1. Convert Tasks to Harbor Format

```bash
python generator/convert_to_harbor/convert_tasks.py \
  --tasks-dir ./tasks \
  --output-dir ./harbor_tasks \
  --model Qwen/Qwen3-32B \
  --provider openai \
  --workers 4
```

**What it does:**
- Reads Endless Terminals tasks from `--tasks-dir`
- Converts to Harbor format:
  - `task.json` → `instruction.md`
  - `container.def` → `environment/Dockerfile`
  - `test_final_state.py` → `tests/test_final_state.py`
  - Creates `tests/test.sh` with reward generation
- Outputs Harbor-compatible tasks to `--output-dir`

### 2. Validate Conversion

```bash
python generator/convert_to_harbor/validate_harbor.py \
  --harbor-dir ./harbor_tasks \
  --results-file harbor_conversion_results.json \
  --output validation_results.json
```

**Checks:**
- ✅ All required files exist
- ✅ Dockerfile syntax is valid
- ✅ test.sh writes to `/logs/verifier/reward.txt`
- ✅ Test files are executable

### 3. Run Harbor Evaluation

```bash
# Install Harbor
uv tool install harbor

# Set environment credentials
export DAYTONA_API_KEY=your_key
# OR
export MODAL_TOKEN_ID=your_id
export MODAL_TOKEN_SECRET=your_secret

# Run evaluation
./scripts/parallel_harbor.sh \
  --tasks-dir ./harbor_tasks \
  --agent endless_harbor.EndlessAgent \
  --model Qwen/Qwen2.5-7B-Instruct \
  --parallel 4 \
  --env daytona
```

## Harbor Task Format

```
task_000001_abcd1234/
  instruction.md              # Task description
  environment/
    Dockerfile                # Container setup
  tests/
    test_final_state.py       # Pytest verification
    test.sh                   # Shell script that runs pytest and writes reward
```

## Scripts

- **`convert_tasks.py`** - Convert Endless Terminals → Harbor format
- **`validate_harbor.py`** - Validate Harbor task structure
- **`harbor_quickstart.sh`** - End-to-end workflow script
- **`parallel_harbor.sh`** - Run Harbor evaluation in parallel

## Configuration Options

### convert_tasks.py

| Option | Default | Description |
|--------|---------|-------------|
| `--tasks-dir` | Required | Endless Terminals tasks directory |
| `--output-dir` | Required | Harbor output directory |
| `--model` | `Qwen/Qwen3-32B` | LLM for Dockerfile conversion |
| `--provider` | `openai` | LLM provider: openai or anthropic |
| `--workers` | 1 | Parallel workers |
| `--reuse-dockerfile` | False | Skip LLM if Dockerfile exists |
| `--start-at` | 0 | Start at task N |
| `--num-tasks` | All | Number of tasks to convert |

### parallel_harbor.sh

| Option | Default | Description |
|--------|---------|-------------|
| `--tasks-dir` | `./harbor_tasks` | Harbor tasks directory |
| `--agent` | `endless_harbor.EndlessAgent` | Agent import path |
| `--model` | `Qwen/Qwen2.5-7B-Instruct` | Model for agent |
| `--parallel` | 8 | Concurrent jobs |
| `--env` | `daytona` | Environment: daytona or modal |
| `--dataset` | Empty | Harbor dataset (empty = local) |

## Integration with SkyRL

Harbor tasks can be used directly with SkyRL for RL training:

```python
from skyrl.generators import HarborGenerator

generator = HarborGenerator(
    task_dir="./harbor_tasks",
    agent_class="endless_harbor.EndlessAgent",
    model="Qwen/Qwen2.5-7B-Instruct",
)

# Use in SkyRL training loop
```

See [skyrl-harbor.md](../../skyrl-harbor.md) for details.

## Troubleshooting

### Conversion fails with "Failed to generate Dockerfile"

- Check OpenAI/Anthropic API key is set
- Verify vLLM server is running (if using local model)
- Try different `--provider` or `--model`

### Validation errors: "test.sh does not write to /logs/verifier/reward.txt"

- The test.sh template should include reward writing
- Check if custom template was used during conversion
- Re-run conversion without `--reuse-dockerfile`

### Harbor evaluation hangs or times out

- Check environment credentials (DAYTONA_API_KEY, etc.)
- Verify Harbor is installed: `harbor --version`
- Check Docker/container runtime is working
- Review logs in `--log-dir` for specific errors

### Rate limiting during conversion

- Reduce `--workers` to limit API concurrency
- Use `--reuse-dockerfile` to skip re-conversion
- Switch to local vLLM server if using cloud APIs

## Related Files

- `endless_harbor/endless_agent.py` - Harbor agent implementation
- `convert_sif_docker.py` - Apptainer → Docker conversion
- `add_reward_file.py` - Legacy reward file utility

## References

- [Harbor Documentation](https://harborframework.com/)
- [Harbor GitHub](https://github.com/laude-institute/harbor)
- [SkyRL Documentation](https://docs.skyrl.ai/docs/harbor)
- [Terminal-Bench](https://terminalbench.com/)