FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyinotify

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/logwatch && chmod 0777 /home/user/logwatch
RUN mkdir -p /var/log/apps && chmod 0777 /var/log/apps
RUN mkdir -p /srv/applogs && chmod 0755 /srv/applogs

RUN for i in $(seq 1 247); do \
    name=$(printf "app%03d.log" $i); \
    echo "Initial log entry for $name at $(date)" > /srv/applogs/$name; \
    chmod 0666 /srv/applogs/$name; \
done

RUN cyclic="089 112 134 156 178 189 201 212 223 231 238 245" && \
    for i in $(seq 1 247); do \
    name=$(printf "app%03d.log" $i); \
    num=$(printf "%03d" $i); \
    is_cyclic=0; \
    for c in $cyclic; do \
        if [ "$num" = "$c" ]; then \
            is_cyclic=1; \
            break; \
        fi; \
    done; \
    if [ $is_cyclic -eq 0 ]; then \
        ln -s /srv/applogs/$name /var/log/apps/$name; \
    fi; \
done

RUN ln -s app112.log /var/log/apps/app089.log && \
    ln -s app134.log /var/log/apps/app112.log && \
    ln -s app156.log /var/log/apps/app134.log && \
    ln -s app178.log /var/log/apps/app156.log && \
    ln -s app189.log /var/log/apps/app178.log && \
    ln -s app201.log /var/log/apps/app189.log && \
    ln -s app212.log /var/log/apps/app201.log && \
    ln -s app223.log /var/log/apps/app212.log && \
    ln -s app231.log /var/log/apps/app223.log && \
    ln -s app238.log /var/log/apps/app231.log && \
    ln -s app245.log /var/log/apps/app238.log && \
    ln -s app089.log /var/log/apps/app245.log

RUN cat > /home/user/logwatch/tail_all.py << 'PYEOF'
#!/usr/bin/env python3
"""
Log aggregator that watches /var/log/apps/ and aggregates to unified.log
Uses pyinotify for inotify-based watching.
"""

import os
import sys
import pyinotify

WATCH_DIR = "/var/log/apps"
OUTPUT_FILE = "/home/user/logwatch/unified.log"

class LogHandler(pyinotify.ProcessEvent):
    def __init__(self, file_handles, output_fh):
        self.file_handles = file_handles
        self.output_fh = output_fh
        super().__init__()

    def process_IN_MODIFY(self, event):
        path = event.pathname
        if path in self.file_handles:
            try:
                fh = self.file_handles[path]
                new_data = fh.read()
                if new_data:
                    self.output_fh.write(new_data)
                    self.output_fh.flush()
            except Exception as e:
                pass

def main():
    try:
        file_handles = {}
        file_positions = {}

        # Open output file
        output_fh = open(OUTPUT_FILE, 'a')

        # Iterate through all files in watch directory
        for entry in os.listdir(WATCH_DIR):
            full_path = os.path.join(WATCH_DIR, entry)
            if not os.path.islink(full_path):
                continue

            # Resolve symlink to get real path
            real_path = os.path.realpath(full_path)

            # Open file handle - keyed by realpath to avoid duplicates
            # BUG: For cyclic symlinks, realpath returns the symlink itself
            # Multiple symlinks may map to same key, overwriting handles
            try:
                fh = open(full_path, 'r')
                fh.seek(0, 2)  # Seek to end
                file_handles[full_path] = fh
            except Exception as e:
                continue

        # Set up inotify watcher
        wm = pyinotify.WatchManager()
        handler = LogHandler(file_handles, output_fh)
        notifier = pyinotify.Notifier(wm, handler)

        # Add watches for all files
        for path in file_handles.keys():
            try:
                wm.add_watch(path, pyinotify.IN_MODIFY)
            except Exception:
                pass

        # Also watch the directory for new files
        wm.add_watch(WATCH_DIR, pyinotify.IN_MODIFY)

        # Main loop
        notifier.loop()

    except Exception as e:
        # Clean exit on any error
        sys.exit(0)

if __name__ == "__main__":
    main()
PYEOF

RUN chmod 0755 /home/user/logwatch/tail_all.py

RUN cat > /home/user/logwatch/feeder.sh << 'FEEDEOF'
#!/bin/bash
# Feeder script that appends lines to random log files every 2 seconds

LOG_DIR="/srv/applogs"

while true; do
    # Pick a random file number between 1 and 247
    num=$((RANDOM % 247 + 1))
    filename=$(printf "app%03d.log" $num)
    filepath="$LOG_DIR/$filename"

    # Append a timestamped line
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Log entry for $filename - random data: $RANDOM" >> "$filepath"

    sleep 2
done
FEEDEOF

RUN chmod 0755 /home/user/logwatch/feeder.sh

RUN chown -R nobody:nogroup /home/user/logwatch
RUN chmod -R 0777 /home/user/logwatch
RUN chmod 0777 /var/log/apps
RUN chmod -R 0666 /srv/applogs/*

RUN cat > /entrypoint.sh << 'ENTRYEOF'
#!/bin/bash
# Start the feeder process in background
nohup /home/user/logwatch/feeder.sh > /dev/null 2>&1 &

# Wait a moment for feeder to start
sleep 1

# Execute bash shell
exec /bin/bash
ENTRYEOF

RUN chmod +x /entrypoint.sh

WORKDIR /home/user

ENTRYPOINT ["/entrypoint.sh"]
