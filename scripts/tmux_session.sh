#!/usr/bin/env bash
# Start or attach to the standard endless-terminals tmux session.
#
# Layout:
#   window 0 "main"    — full pane, general work
#   window 1 "harbor"  — left: harbor run | right: logs tail
#   window 2 "monitor" — left: check_resources loop | right: docker stats

SESSION="endless"
REPO="$(cd "$(dirname "$0")/.." && pwd)"

# Attach if session already exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Attaching to existing session '$SESSION'..."
    tmux attach-session -t "$SESSION"
    exit 0
fi

# Create session with window 0: main
tmux new-session -d -s "$SESSION" -n "main" -c "$REPO"

# Window 1: harbor — left pane for running harbor, right pane for log tail
tmux new-window -t "$SESSION:1" -n "harbor" -c "$REPO"
tmux split-window -t "$SESSION:1" -h -c "$REPO"
tmux send-keys -t "$SESSION:1.0" "# harbor run commands go here" Enter
tmux send-keys -t "$SESSION:1.1" "# tail -f harbor_logs/harbor_run_<name>.log" Enter

# Window 2: monitor — left pane loops resource check, right pane docker stats
tmux new-window -t "$SESSION:2" -n "monitor" -c "$REPO"
tmux split-window -t "$SESSION:2" -h -c "$REPO"
tmux send-keys -t "$SESSION:2.0" "watch -n 10 bash scripts/check_resources.sh" Enter
tmux send-keys -t "$SESSION:2.1" "docker stats --no-trunc 2>/dev/null || echo 'No containers running'" Enter

# Focus main window on attach
tmux select-window -t "$SESSION:0"

echo "Created session '$SESSION'. Attaching..."
tmux attach-session -t "$SESSION"
