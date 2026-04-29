FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user
RUN mkdir -p /var/log/suricata && chmod 0755 /var/log/suricata

RUN cat > /home/user/correlate.py << 'ENDSCRIPT'
#!/usr/bin/env python3
import json
from collections import defaultdict
from datetime import datetime, timedelta

INTERNAL_PREFIX = "10."
WINDOW_MINUTES = 5
THRESHOLD = 3

def is_internal(ip):
    return ip.startswith(INTERNAL_PREFIX)

def parse_timestamp(ts):
    # Bug 1: Suricata timestamps have microseconds and timezone, this format string is wrong
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

def main():
    connections = []
    with open("/var/log/suricata/eve.json") as f:
        for line in f:
            event = json.loads(line)
            # Bug 2: Only looks at event_type == "flow", but Suricata marks 
            # completed flows as "flow" with flow.state == "closed" or "new".
            # The script checks for "netflow" which doesn't exist in standard eve.json
            if event.get("event_type") != "netflow":
                continue
            src = event.get("src_ip", "")
            dst = event.get("dest_ip", "")  # Bug 3: Suricata uses "dest_ip", not "dst_ip" - this is actually correct but see below
            # Bug 4: script uses "dst_ip" in the variable name but reads "dest_ip" - 
            # Actually the real bug is the event_type check above means this never runs
            if is_internal(src) and is_internal(dst) and src != dst:
                ts = parse_timestamp(event.get("timestamp", ""))
                connections.append((ts, src, dst))

    # Window-based grouping
    connections.sort()
    flagged = set()
    for i, (ts, src, dst) in enumerate(connections):
        window_end = ts + timedelta(minutes=WINDOW_MINUTES)
        dsts_in_window = set()
        for j in range(i, len(connections)):
            if connections[j][0] > window_end:
                break
            if connections[j][1] == src:
                dsts_in_window.add(connections[j][2])
        if len(dsts_in_window) > THRESHOLD:
            flagged.add(src)

    for host in sorted(flagged):
        print(f"LATERAL_MOVEMENT_CANDIDATE: {host}")

if __name__ == "__main__":
    main()
ENDSCRIPT

RUN chmod 0755 /home/user/correlate.py

RUN python3 << 'PYSCRIPT'
import json
import random
from datetime import datetime, timedelta

random.seed(42)

base_time = datetime(2024, 1, 10, 0, 0, 0)
events = []

event_id = 0

def make_timestamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "+0000"

def random_internal_ip():
    return f"10.{random.randint(0,255)}.{random.randint(1,254)}.{random.randint(1,254)}"

def random_external_ip():
    first = random.choice([8, 17, 23, 52, 93, 104, 142, 172, 185, 192, 198, 203, 216])
    if first == 172:
        second = random.choice([0, 1, 2, 64, 65, 128, 200])
    elif first == 192:
        second = random.choice([0, 1, 100, 200])
    else:
        second = random.randint(0, 255)
    return f"{first}.{second}.{random.randint(0,255)}.{random.randint(1,254)}"

internal_hosts = [f"10.1.{i}.{j}" for i in range(1, 10) for j in range(1, 30)]
scanner_ip = "10.1.5.23"
scanner_targets = [f"10.1.{i}.{j}" for i in range(1, 12) for j in range(1, 20) if f"10.1.{i}.{j}" != scanner_ip][:47]

for day in range(7):
    day_start = base_time + timedelta(days=day)

    for hour in range(24):
        hour_start = day_start + timedelta(hours=hour)

        for _ in range(random.randint(200, 400)):
            ts = hour_start + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))
            src = random.choice(internal_hosts)
            dst = random_external_ip()
            event = {
                "timestamp": make_timestamp(ts),
                "flow_id": random.randint(1000000000, 9999999999),
                "event_type": "flow",
                "src_ip": src,
                "src_port": random.randint(32768, 65535),
                "dest_ip": dst,
                "dest_port": random.choice([80, 443, 8080, 8443]),
                "proto": "TCP",
                "flow": {
                    "pkts_toserver": random.randint(5, 100),
                    "pkts_toclient": random.randint(5, 100),
                    "bytes_toserver": random.randint(500, 50000),
                    "bytes_toclient": random.randint(500, 500000),
                    "start": make_timestamp(ts - timedelta(seconds=random.randint(1, 60))),
                    "end": make_timestamp(ts),
                    "state": "closed"
                }
            }
            events.append((ts, event))

        for _ in range(random.randint(50, 100)):
            ts = hour_start + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))
            src = random.choice(internal_hosts)
            dst = random.choice([h for h in internal_hosts if h != src])
            event = {
                "timestamp": make_timestamp(ts),
                "flow_id": random.randint(1000000000, 9999999999),
                "event_type": "flow",
                "src_ip": src,
                "src_port": random.randint(32768, 65535),
                "dest_ip": dst,
                "dest_port": random.choice([22, 445, 3389, 5985, 139]),
                "proto": "TCP",
                "flow": {
                    "pkts_toserver": random.randint(2, 20),
                    "pkts_toclient": random.randint(2, 20),
                    "bytes_toserver": random.randint(100, 5000),
                    "bytes_toclient": random.randint(100, 5000),
                    "start": make_timestamp(ts - timedelta(seconds=random.randint(1, 30))),
                    "end": make_timestamp(ts),
                    "state": "closed"
                }
            }
            events.append((ts, event))

        for _ in range(random.randint(30, 60)):
            ts = hour_start + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))
            src = random.choice(internal_hosts)
            event = {
                "timestamp": make_timestamp(ts),
                "event_type": "dns",
                "src_ip": src,
                "src_port": random.randint(32768, 65535),
                "dest_ip": "10.1.1.1",
                "dest_port": 53,
                "proto": "UDP",
                "dns": {
                    "type": "query",
                    "rrname": random.choice(["google.com", "microsoft.com", "amazon.com", "github.com", "example.com"]),
                    "rrtype": "A"
                }
            }
            events.append((ts, event))

        for _ in range(random.randint(10, 30)):
            ts = hour_start + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))
            src = random.choice(internal_hosts)
            dst = random_external_ip()
            event = {
                "timestamp": make_timestamp(ts),
                "event_type": "http",
                "src_ip": src,
                "src_port": random.randint(32768, 65535),
                "dest_ip": dst,
                "dest_port": 80,
                "proto": "TCP",
                "http": {
                    "hostname": random.choice(["www.example.com", "api.service.com", "cdn.provider.net"]),
                    "http_method": random.choice(["GET", "POST"]),
                    "url": "/",
                    "status": 200
                }
            }
            events.append((ts, event))

        for _ in range(random.randint(5, 15)):
            ts = hour_start + timedelta(minutes=random.randint(0, 59), seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))
            src = random.choice(internal_hosts)
            dst = random_external_ip()
            event = {
                "timestamp": make_timestamp(ts),
                "event_type": "tls",
                "src_ip": src,
                "src_port": random.randint(32768, 65535),
                "dest_ip": dst,
                "dest_port": 443,
                "proto": "TCP",
                "tls": {
                    "sni": random.choice(["www.google.com", "api.microsoft.com", "github.com"]),
                    "version": "TLS 1.3"
                }
            }
            events.append((ts, event))

        if random.random() < 0.1:
            ts = hour_start + timedelta(minutes=random.randint(0, 59))
            event = {
                "timestamp": make_timestamp(ts),
                "event_type": "alert",
                "src_ip": random.choice(internal_hosts),
                "src_port": random.randint(32768, 65535),
                "dest_ip": random_external_ip(),
                "dest_port": random.choice([80, 443, 4444, 8080]),
                "proto": "TCP",
                "alert": {
                    "signature_id": random.randint(2000000, 2999999),
                    "signature": random.choice([
                        "ET MALWARE Generic Trojan",
                        "ET POLICY Suspicious User-Agent",
                        "ET SCAN Potential SSH Scan"
                    ]),
                    "category": random.choice(["Malware", "Policy Violation", "Attempted Recon"]),
                    "severity": random.randint(1, 3)
                }
            }
            events.append((ts, event))

scan_windows = [
    (base_time + timedelta(days=1, hours=2, minutes=15), 12),
    (base_time + timedelta(days=2, hours=14, minutes=30), 10),
    (base_time + timedelta(days=3, hours=8, minutes=45), 8),
    (base_time + timedelta(days=4, hours=22, minutes=10), 11),
    (base_time + timedelta(days=5, hours=16, minutes=20), 9),
    (base_time + timedelta(days=6, hours=4, minutes=5), 7),
]

targets_used = set()
for window_start, num_targets in scan_windows:
    available_targets = [t for t in scanner_targets if t not in targets_used]
    if len(available_targets) < num_targets:
        available_targets = scanner_targets

    targets_for_window = random.sample(available_targets, min(num_targets, len(available_targets)))
    targets_used.update(targets_for_window)

    for i, target in enumerate(targets_for_window):
        ts = window_start + timedelta(seconds=i * random.randint(5, 25), microseconds=random.randint(0, 999999))
        event = {
            "timestamp": make_timestamp(ts),
            "flow_id": random.randint(1000000000, 9999999999),
            "event_type": "flow",
            "src_ip": scanner_ip,
            "src_port": random.randint(32768, 65535),
            "dest_ip": target,
            "dest_port": random.choice([22, 445, 3389, 5985, 139, 135]),
            "proto": "TCP",
            "flow": {
                "pkts_toserver": random.randint(3, 10),
                "pkts_toclient": random.randint(0, 5),
                "bytes_toserver": random.randint(100, 1000),
                "bytes_toclient": random.randint(0, 500),
                "start": make_timestamp(ts - timedelta(seconds=random.randint(1, 5))),
                "end": make_timestamp(ts),
                "state": "closed"
            }
        }
        events.append((ts, event))

for day in range(7):
    day_start = base_time + timedelta(days=day)
    ts = day_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
    event = {
        "timestamp": make_timestamp(ts),
        "event_type": "stats",
        "stats": {
            "uptime": day * 86400 + random.randint(0, 86400),
            "capture": {
                "kernel_packets": random.randint(1000000, 10000000),
                "kernel_drops": random.randint(0, 1000)
            }
        }
    }
    events.append((ts, event))

events.sort(key=lambda x: x[0])

with open("/var/log/suricata/eve.json", "w") as f:
    for ts, event in events:
        f.write(json.dumps(event) + "\n")

print(f"Generated {len(events)} events")
PYSCRIPT

RUN chmod 0644 /var/log/suricata/eve.json

WORKDIR /home/user

CMD ["/bin/bash"]
