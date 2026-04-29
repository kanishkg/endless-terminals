FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    sqlite3 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/fleet && chmod 0777 /home/user && chmod 0777 /home/user/fleet

RUN sqlite3 /home/user/fleet/telemetry.db "CREATE TABLE devices (id INTEGER PRIMARY KEY, device_id TEXT NOT NULL, firmware_version TEXT, last_ping INTEGER);" && \
    for i in $(seq 1 200); do \
        sqlite3 /home/user/fleet/telemetry.db "INSERT INTO devices (id, device_id, firmware_version, last_ping) VALUES ($i, 'DEV-$(printf '%05d' $i)', '1.$((i % 10)).$((i % 100))', $((1700000000 + i * 100)));"; \
    done && \
    chmod 0666 /home/user/fleet/telemetry.db

WORKDIR /home/user
