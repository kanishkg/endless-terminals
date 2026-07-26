#!/usr/bin/env bash
# Prune all Docker artifacts when total disk usage exceeds 3GB.
set -euo pipefail

THRESHOLD_BYTES=$((3 * 1024 * 1024 * 1024))
LOG_PREFIX="[$(date -u +%Y-%m-%dT%H:%M:%SZ)]"

total_bytes=$(docker system df --format '{{.Size}}' \
  | python3 -c "
import sys, re
total = 0
for line in sys.stdin:
    m = re.match(r'([0-9.]+)\s*(GB|MB|kB|B)?', line.strip())
    if m:
        val, unit = float(m.group(1)), m.group(2) or 'B'
        total += val * {'GB': 1073741824, 'MB': 1048576, 'kB': 1024, 'B': 1}[unit]
print(int(total))
")

echo "$LOG_PREFIX Docker usage: $(( total_bytes / 1048576 ))MB (threshold: 5120MB)"

if (( total_bytes > THRESHOLD_BYTES )); then
  echo "$LOG_PREFIX Threshold exceeded — pruning all images, containers, volumes, and build cache..."
  docker system prune -af --volumes
  echo "$LOG_PREFIX Prune complete."
else
  echo "$LOG_PREFIX Under threshold — skipping."
fi
