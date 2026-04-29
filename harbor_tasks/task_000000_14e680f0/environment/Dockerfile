FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    bc \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/buildbot && chmod 0777 /home/user && chmod 0777 /home/user/buildbot

RUN cat > /home/user/buildbot/config.ini << 'EOF'
[buildbot]
# Configuration for the build agent
worker_name = android-ndk-builder
max_concurrent_builds = 1

[heartbeat]
# Heartbeat interval in seconds
interval = 5
# Watchdog timeout in seconds
timeout = 30

[validation]
# Build artifact validation settings
# NOTE: file_lock is used for concurrent access protection when writing
# heartbeat file and validating artifacts. Do not remove the lock.
enabled = true
chunk_size = 50000

[logging]
level = INFO
file = /tmp/buildbot.log
EOF

RUN cat > /home/user/buildbot/mock_build.sh << 'EOFMOCK'
#!/bin/bash
# Mock build script that simulates Android NDK build timing
# Compressed from 50 minutes to ~60 seconds, same pattern

echo "=== Starting mock Android NDK build ==="
echo "Phase 1: Configuring build environment..."

# Phase 1: Configuration (small output, 10 seconds)
for i in $(seq 1 10); do
    echo "Checking dependency $i/10..."
    sleep 1
done

echo "Phase 2: Compiling source files..."

# Phase 2: Compilation (small output, 25 seconds)
for i in $(seq 1 25); do
    echo "Compiling module $i/25..."
    sleep 1
done

echo "Phase 3: Linking..."

# Phase 3: Linking - this is where the large output happens
# Simulates the linker dumping lots of symbol information
# This triggers the bug - large output causes validation to run long

for i in $(seq 1 200); do
    # Each iteration outputs ~1KB of "linker" data
    echo "ld: linking symbol_table_entry_$i with references:"
    for j in $(seq 1 20); do
        echo "    -> _ZN7android${i}_${j}internal_symbol_name_that_is_quite_long_to_simulate_real_linker_outputEPKcS1_S1_S1_"
    done
done

echo "Phase 4: Finalizing..."

# Phase 4: Finalization (small output, 20 seconds)
for i in $(seq 1 20); do
    echo "Finalizing artifact $i/20..."
    sleep 1
done

echo "=== Build completed successfully ==="
exit 0
EOFMOCK

RUN chmod +x /home/user/buildbot/mock_build.sh

RUN cat > /home/user/buildbot/watchdog.sh << 'EOFWATCH'
#!/bin/bash
# Watchdog script - monitors worker heartbeat and kills if stale
WORKER_PID=$1

if [ -z "$WORKER_PID" ]; then
    echo "Watchdog: No worker PID provided"
    exit 1
fi

echo "Watchdog: Monitoring worker PID $WORKER_PID"

while kill -0 $WORKER_PID 2>/dev/null; do
    sleep 10
    if [ -f /tmp/buildbot_heartbeat ]; then
        LAST=$(cat /tmp/buildbot_heartbeat 2>/dev/null)
        if [ -n "$LAST" ]; then
            NOW=$(date +%s.%N)
            AGE=$(echo "$NOW - $LAST" | bc 2>/dev/null)
            if [ -n "$AGE" ]; then
                STALE=$(echo "$AGE > 30" | bc -l 2>/dev/null)
                if [ "$STALE" = "1" ]; then
                    echo "Watchdog: heartbeat stale by ${AGE}s, killing worker"
                    kill -9 $WORKER_PID 2>/dev/null
                    exit 1
                fi
            fi
        fi
    else
        echo "Watchdog: heartbeat file not found yet, waiting..."
    fi
done

echo "Watchdog: Worker $WORKER_PID exited normally"
exit 0
EOFWATCH

RUN chmod +x /home/user/buildbot/watchdog.sh

RUN cat > /home/user/buildbot/worker.py << 'EOFWORKER'
#!/usr/bin/env python3
"""
Buildbot worker script
Runs builds and maintains heartbeat for watchdog monitoring
"""

import threading
import subprocess
import time
import os
import sys

# Lock for file operations - used by both heartbeat and validation
# NOTE: This lock exists for concurrent access protection. See config.ini.
file_lock = threading.Lock()

# Global flag for heartbeat thread
_running = True


def write_heartbeat():
    """Write current timestamp to heartbeat file. Called every 5 seconds."""
    global _running
    if not _running:
        return

    with file_lock:
        try:
            with open('/tmp/buildbot_heartbeat', 'w') as f:
                f.write(str(time.time()))
        except Exception as e:
            print(f"Heartbeat write error: {e}", file=sys.stderr)

    # Schedule next heartbeat
    if _running:
        t = threading.Timer(5.0, write_heartbeat)
        t.daemon = True
        t.start()


def validate_build_artifacts(output_chunk):
    """
    Validate build output for correctness.
    This function processes linker output to check for common errors.

    NOTE: Acquires file_lock during processing for safe file access
    if validation needs to write temporary data.
    """
    with file_lock:  # BUG: holds lock during long CPU-bound processing
        # Simulates validation of linker output
        # This becomes very slow when processing large linker output
        total = 0
        lines = output_chunk.split('\n')
        for line in lines:
            # Simulate per-line validation processing
            for char in line:
                total += ord(char)
            # Small delay per line to simulate real validation work
            time.sleep(0.001)
        return total


def run_build(script):
    """Run a build script and monitor its output."""
    global _running

    print(f"Worker: Starting build with script {script}")

    proc = subprocess.Popen(
        ['bash', script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    # Start heartbeat timer chain
    write_heartbeat()

    output = b''
    try:
        while True:
            chunk = proc.stdout.read(4096)
            if not chunk:
                break
            output += chunk

            # Print output for logging
            try:
                print(chunk.decode('utf-8', errors='replace'), end='')
            except:
                pass

            # Every ~50KB, run validation on accumulated output
            if len(output) > 50000:
                print("\nWorker: Validating build artifacts...", file=sys.stderr)
                validate_build_artifacts(output.decode('utf-8', errors='replace'))
                print("Worker: Validation complete", file=sys.stderr)
                output = b''

        # Final validation if there's remaining output
        if output:
            validate_build_artifacts(output.decode('utf-8', errors='replace'))

        proc.wait()
        return proc.returncode

    finally:
        _running = False


if __name__ == '__main__':
    print("Worker started")
    sys.stdout.flush()

    exit_code = run_build('/home/user/buildbot/mock_build.sh')

    print(f"Worker: Build finished with exit code {exit_code}")
    sys.exit(exit_code)
EOFWORKER

RUN chmod +x /home/user/buildbot/worker.py

RUN cat > /home/user/buildbot/run_agent.sh << 'EOFAGENT'
#!/bin/bash
# Build agent wrapper script
# Launches worker and watchdog, manages lifecycle

cd /home/user/buildbot

# Clean up any stale heartbeat file
rm -f /tmp/buildbot_heartbeat

echo "Agent: Starting worker..."

# Start worker in background
python3 worker.py &
WORKER_PID=$!

echo "Agent: Worker started with PID $WORKER_PID"
echo "Agent: Starting watchdog..."

# Start watchdog in background
bash watchdog.sh $WORKER_PID &
WATCHDOG_PID=$!

echo "Agent: Watchdog started with PID $WATCHDOG_PID"

# Wait for worker to complete
wait $WORKER_PID
EXIT_CODE=$?

echo "Agent: Worker exited with code $EXIT_CODE"

# Clean up watchdog
kill $WATCHDOG_PID 2>/dev/null
pkill -f "watchdog.sh $WORKER_PID" 2>/dev/null

# Clean up heartbeat file
rm -f /tmp/buildbot_heartbeat

exit $EXIT_CODE
EOFAGENT

RUN chmod +x /home/user/buildbot/run_agent.sh

RUN chmod -R 0777 /home/user/buildbot

RUN chown -R nobody:nogroup /home/user

WORKDIR /home/user

CMD ["/bin/bash"]
