FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyyaml

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /var/log/ingest && chmod 0755 /var/log/ingest

RUN mkdir -p /home/user/monitoring/summaries && chmod -R 0777 /home/user/monitoring

RUN python3 << 'PYSCRIPT'
import json
import os
import random
from datetime import datetime, timedelta

random.seed(42)

base_date = datetime(2025, 6, 9, 0, 0, 0)

high_error_hours = {
    (2025, 6, 10, 14): 0.12,
    (2025, 6, 11, 9): 0.08,
}

for hour_offset in range(72):
    current_time = base_date + timedelta(hours=hour_offset)
    year = current_time.year
    month = current_time.month
    day = current_time.day
    hour = current_time.hour

    date_str = f"{year}{month:02d}{day:02d}"
    hour_str = f"{hour:02d}"

    log_filename = f"/var/log/ingest/ingest_{date_str}_{hour_str}.log"

    key = (year, month, day, hour)
    if key in high_error_hours:
        target_error_rate = high_error_hours[key]
    else:
        target_error_rate = random.uniform(0.01, 0.04)

    total_entries = random.randint(80, 120)
    error_count = int(total_entries * target_error_rate)
    ok_count = total_entries - error_count

    entries = []
    for i in range(total_entries):
        ts = current_time + timedelta(seconds=random.randint(0, 3599))
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
        latency = random.randint(10, 500)
        entries.append({
            "ts": ts_str,
            "status": "error" if i < error_count else "ok",
            "latency_ms": latency
        })

    random.shuffle(entries)

    with open(log_filename, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    actual_errors = sum(1 for e in entries if e["status"] == "error")
    actual_total = len(entries)
    actual_error_rate = actual_errors / actual_total if actual_total > 0 else 0

    summary_filename = f"/home/user/monitoring/summaries/summary_{date_str}_{hour_str}.json"
    summary = {
        "hour": f"{date_str}_{hour_str}",
        "total": actual_total,
        "errors": actual_errors,
        "error_rate": f"{actual_error_rate:.4f}"
    }

    with open(summary_filename, 'w') as f:
        json.dump(summary, f)

print("Generated 72 log files and 72 summary files")
PYSCRIPT

RUN cat > /home/user/monitoring/config.yaml << 'EOF'
threshold: 0.05
summary_dir: summaries
alert_log: alerts.log
EOF

RUN cat > /home/user/monitoring/parse_logs.py << 'PYEOF'
#!/usr/bin/env python3
"""
Parser script that reads ingest logs and generates hourly summaries.
Reads from /var/log/ingest/, writes to /home/user/monitoring/summaries/
"""

import json
import os
from pathlib import Path

INGEST_DIR = Path("/var/log/ingest")
SUMMARY_DIR = Path("/home/user/monitoring/summaries")

def parse_log_file(log_path):
    """Parse a single log file and return stats."""
    total = 0
    errors = 0

    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                total += 1
                if entry.get("status") == "error":
                    errors += 1
            except json.JSONDecodeError:
                continue

    return total, errors

def main():
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    for log_file in INGEST_DIR.glob("ingest_*.log"):
        # Extract date/hour from filename: ingest_YYYYMMDD_HH.log
        name_parts = log_file.stem.split("_")
        if len(name_parts) >= 3:
            date_str = name_parts[1]
            hour_str = name_parts[2]
            hour_id = f"{date_str}_{hour_str}"

            total, errors = parse_log_file(log_file)
            error_rate = errors / total if total > 0 else 0

            summary = {
                "hour": hour_id,
                "total": total,
                "errors": errors,
                # BUG: Writing error_rate as string instead of float
                "error_rate": f"{error_rate:.4f}"
            }

            summary_path = SUMMARY_DIR / f"summary_{hour_id}.json"
            with open(summary_path, 'w') as f:
                json.dump(summary, f)

            print(f"Processed {log_file.name} -> {summary_path.name}")

if __name__ == "__main__":
    main()
PYEOF

RUN cat > /home/user/monitoring/alerter.py << 'PYEOF'
#!/usr/bin/env python3
"""
Alerter script that reads summaries and writes alerts when error_rate exceeds threshold.
"""

import json
import os
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def load_config():
    """Load configuration from config.yaml."""
    config_path = SCRIPT_DIR / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    config = load_config()

    # BUG: Typo 'treshold' instead of 'threshold'
    # This silently defaults to 0.5 (50%) instead of 0.05 (5%)
    threshold = config.get('treshold', 0.5)

    summary_dir = SCRIPT_DIR / config.get('summary_dir', 'summaries')
    alert_log = SCRIPT_DIR / config.get('alert_log', 'alerts.log')

    alerts = []

    for summary_file in sorted(summary_dir.glob("summary_*.json")):
        with open(summary_file, 'r') as f:
            summary = json.load(f)

        error_rate = float(summary['error_rate'])

        if error_rate > threshold:
            alert_msg = f"ALERT: Hour {summary['hour']} had error_rate {error_rate:.4f} (threshold: {threshold})"
            alerts.append(alert_msg)

    with open(alert_log, 'a') as f:
        for alert in alerts:
            f.write(alert + "\n")

    if alerts:
        print(f"Wrote {len(alerts)} alerts to {alert_log}")
    else:
        print("No alerts generated")

if __name__ == "__main__":
    main()
PYEOF

RUN chmod +x /home/user/monitoring/parse_logs.py /home/user/monitoring/alerter.py

RUN touch /home/user/monitoring/alerts.log

RUN chmod 0755 /var/log/ingest && \
    chmod 0644 /var/log/ingest/*.log && \
    chown -R root:root /var/log/ingest

RUN chmod -R 0777 /home/user/monitoring

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
