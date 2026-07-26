#!/usr/bin/env bash
# Run docker_cleanup.sh every 2.5 minutes in the background.
# Usage: nohup bash scripts/run_docker_cleanup_loop.sh >> harbor_logs/docker_cleanup.log 2>&1 &
SCRIPT="$(dirname "$0")/docker_cleanup.sh"
while true; do
  bash "$SCRIPT"
  sleep 150
done
