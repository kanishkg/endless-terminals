#!/usr/bin/env bash
# Run a harbor evaluation job inside a tmux window so it survives SSH disconnects.
#
# Usage:
#   bash scripts/harbor_run.sh --path harbor_tasks_part2_2-2 --job-name 2-2 \
#       --n-attempts 8 --n-concurrent 10
#
# All args are passed through to `harbor run`. Defaults below are Stage 2 standard.
# The job runs in tmux window "harbor" of session "endless" (created if needed).
# Logs go to harbor_logs/harbor_run_<job-name>.log

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SESSION="endless"
LOG_DIR="$REPO/harbor_logs"
mkdir -p "$LOG_DIR"

# Defaults
AGENT="generator.aicore_agent:AICoreTerminus2"
MODEL="claude_4_5"
JOBS_DIR="solution_grace"
N_ATTEMPTS=8
N_CONCURRENT=10
PATH_ARG=""
JOB_NAME=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --path)           PATH_ARG="$2";      shift 2 ;;
        --job-name)       JOB_NAME="$2";      shift 2 ;;
        --n-attempts)     N_ATTEMPTS="$2";    shift 2 ;;
        --n-concurrent)   N_CONCURRENT="$2";  shift 2 ;;
        --model)          MODEL="$2";         shift 2 ;;
        --jobs-dir)       JOBS_DIR="$2";      shift 2 ;;
        --agent)          AGENT="$2";         shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [[ -z "$PATH_ARG" ]]; then
    echo "Error: --path is required"
    exit 1
fi

JOB_NAME="${JOB_NAME:-$(basename "$PATH_ARG")}"
LOG_FILE="$LOG_DIR/harbor_run_${JOB_NAME}.log"

HARBOR_CMD=".venv/bin/harbor run \
  --agent-import-path $AGENT \
  --model $MODEL \
  --path $PATH_ARG \
  --n-attempts $N_ATTEMPTS \
  --jobs-dir $JOBS_DIR \
  --n-concurrent $N_CONCURRENT \
  --job-name $JOB_NAME"

echo "Job:        $JOB_NAME"
echo "Tasks:      $PATH_ARG"
echo "Attempts:   $N_ATTEMPTS  Concurrent: $N_CONCURRENT"
echo "Log:        $LOG_FILE"
echo "Command:    $HARBOR_CMD"
echo ""

# Ensure tmux session exists
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Creating tmux session '$SESSION'..."
    tmux new-session -d -s "$SESSION" -n "main" -c "$REPO"
fi

# Run in a new tmux window named after the job
WINDOW="${SESSION}:harbor-${JOB_NAME}"
tmux new-window -t "$SESSION" -n "harbor-${JOB_NAME}" -c "$REPO"
tmux send-keys -t "$SESSION:harbor-${JOB_NAME}" \
    "cd $REPO && $HARBOR_CMD 2>&1 | tee $LOG_FILE" Enter

echo "Started in tmux window 'harbor-${JOB_NAME}' of session '$SESSION'."
echo ""
echo "  Attach:  tmux attach -t $SESSION"
echo "  Switch:  tmux select-window -t $SESSION:harbor-${JOB_NAME}"
echo "  Logs:    tail -f $LOG_FILE"
