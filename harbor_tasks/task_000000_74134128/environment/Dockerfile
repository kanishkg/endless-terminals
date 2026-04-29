FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tzdata \
    curl \
    faketime \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pytz python-dateutil

RUN mkdir -p /home/user/monitor && chmod 0777 /home/user && chmod 0777 /home/user/monitor

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo "America/New_York" > /etc/timezone

RUN cat > /home/user/monitor/check_uptime.py << 'ENDSCRIPT'
#!/usr/bin/env python3
"""
Synthetic monitoring script that checks uptime of internal services.
Runs every 5 minutes, logs timestamps, alerts if any service was down
for more than 15 minutes in the past hour.
"""

import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

# Configuration
SERVICES = [
    ("service1", "http://localhost:8001/"),
    ("service2", "http://localhost:8002/"),
    ("service3", "http://localhost:8003/"),
]
LOG_FILE = "/home/user/monitor/uptime.log"
ALERT_FILE = "/home/user/monitor/alerts.log"
CHECK_INTERVAL_MINUTES = 5
ALERT_THRESHOLD_MINUTES = 15
LOOKBACK_HOURS = 1


def check_service(url, timeout=5):
    """Check if a service is up by making an HTTP request."""
    try:
        response = urllib.request.urlopen(url, timeout=timeout)
        return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError, Exception):
        return False


def get_current_time():
    """Get the current time."""
    return datetime.now()


def parse_timestamp(ts_str):
    """Parse a timestamp string from the log file."""
    return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")


def format_timestamp(dt):
    """Format a datetime for logging."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def read_log_entries():
    """Read all entries from the uptime log."""
    entries = []
    if not os.path.exists(LOG_FILE):
        return entries

    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                # Format: timestamp|service_name|status
                parts = line.split('|')
                if len(parts) >= 3:
                    ts = parse_timestamp(parts[0])
                    service = parts[1]
                    status = parts[2] == 'UP'
                    entries.append((ts, service, status))
            except (ValueError, IndexError):
                continue
    return entries


def get_entries_last_hour():
    """Get log entries from the last hour."""
    now = get_current_time()
    one_hour_ago = now - timedelta(hours=LOOKBACK_HOURS)

    all_entries = read_log_entries()
    recent_entries = []

    for ts, service, status in all_entries:
        if ts >= one_hour_ago and ts <= now:
            recent_entries.append((ts, service, status))

    return recent_entries


def calculate_downtime(entries, service_name):
    """
    Calculate total downtime for a service in minutes.
    Assumes checks happen every CHECK_INTERVAL_MINUTES.
    Each DOWN entry represents CHECK_INTERVAL_MINUTES of downtime.
    """
    downtime_minutes = 0
    for ts, service, status in entries:
        if service == service_name and not status:
            downtime_minutes += CHECK_INTERVAL_MINUTES
    return downtime_minutes


def write_log_entry(service_name, is_up):
    """Append a log entry for a service check."""
    now = get_current_time()
    status = "UP" if is_up else "DOWN"
    entry = f"{format_timestamp(now)}|{service_name}|{status}\n"

    with open(LOG_FILE, 'a') as f:
        f.write(entry)


def write_alert(message):
    """Write an alert to the alerts log."""
    now = get_current_time()
    alert_entry = f"{format_timestamp(now)}|ALERT|{message}\n"

    with open(ALERT_FILE, 'a') as f:
        f.write(alert_entry)

    print(f"ALERT: {message}", file=sys.stderr)


def run_checks():
    """Run health checks on all services."""
    results = {}
    for service_name, url in SERVICES:
        is_up = check_service(url)
        write_log_entry(service_name, is_up)
        results[service_name] = is_up
    return results


def check_for_alerts():
    """Check if any service has exceeded the downtime threshold."""
    entries = get_entries_last_hour()
    alerts_triggered = False

    for service_name, _ in SERVICES:
        downtime = calculate_downtime(entries, service_name)
        if downtime > ALERT_THRESHOLD_MINUTES:
            write_alert(
                f"{service_name} was down for {downtime} minutes "
                f"in the last hour (threshold: {ALERT_THRESHOLD_MINUTES} minutes)"
            )
            alerts_triggered = True

    return alerts_triggered


def main():
    """Main entry point."""
    # Run health checks
    results = run_checks()

    # Check for alerts based on historical data
    alerts = check_for_alerts()

    # Print current status
    now = get_current_time()
    print(f"[{format_timestamp(now)}] Health check completed:")
    for service_name, is_up in results.items():
        status = "UP" if is_up else "DOWN"
        print(f"  {service_name}: {status}")

    if alerts:
        print("ALERTS TRIGGERED - check alerts.log")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
ENDSCRIPT

RUN chmod 755 /home/user/monitor/check_uptime.py

RUN cat > /home/user/monitor/uptime.log << 'ENDLOG'
2024-03-10 01:00:00|service1|UP
2024-03-10 01:00:00|service2|UP
2024-03-10 01:00:00|service3|UP
2024-03-10 01:05:00|service1|UP
2024-03-10 01:05:00|service2|UP
2024-03-10 01:05:00|service3|UP
2024-03-10 01:10:00|service1|UP
2024-03-10 01:10:00|service2|UP
2024-03-10 01:10:00|service3|UP
2024-03-10 01:15:00|service1|UP
2024-03-10 01:15:00|service2|UP
2024-03-10 01:15:00|service3|UP
2024-03-10 01:20:00|service1|UP
2024-03-10 01:20:00|service2|UP
2024-03-10 01:20:00|service3|UP
2024-03-10 01:25:00|service1|UP
2024-03-10 01:25:00|service2|UP
2024-03-10 01:25:00|service3|UP
2024-03-10 01:30:00|service1|UP
2024-03-10 01:30:00|service2|UP
2024-03-10 01:30:00|service3|UP
2024-03-10 01:35:00|service1|UP
2024-03-10 01:35:00|service2|UP
2024-03-10 01:35:00|service3|UP
2024-03-10 01:40:00|service1|UP
2024-03-10 01:40:00|service2|UP
2024-03-10 01:40:00|service3|UP
2024-03-10 01:45:00|service1|UP
2024-03-10 01:45:00|service2|UP
2024-03-10 01:45:00|service3|UP
2024-03-10 01:50:00|service1|UP
2024-03-10 01:50:00|service2|UP
2024-03-10 01:50:00|service3|UP
2024-03-10 01:55:00|service1|UP
2024-03-10 01:55:00|service2|UP
2024-03-10 01:55:00|service3|UP
2024-03-10 03:00:00|service1|UP
2024-03-10 03:00:00|service2|UP
2024-03-10 03:00:00|service3|UP
2024-11-03 00:30:00|service1|UP
2024-11-03 00:30:00|service2|UP
2024-11-03 00:30:00|service3|UP
2024-11-03 00:35:00|service1|UP
2024-11-03 00:35:00|service2|UP
2024-11-03 00:35:00|service3|UP
2024-11-03 00:40:00|service1|UP
2024-11-03 00:40:00|service2|UP
2024-11-03 00:40:00|service3|UP
2024-11-03 00:45:00|service1|UP
2024-11-03 00:45:00|service2|UP
2024-11-03 00:45:00|service3|UP
2024-11-03 00:50:00|service1|UP
2024-11-03 00:50:00|service2|UP
2024-11-03 00:50:00|service3|UP
2024-11-03 00:55:00|service1|UP
2024-11-03 00:55:00|service2|UP
2024-11-03 00:55:00|service3|UP
2024-11-03 01:00:00|service1|UP
2024-11-03 01:00:00|service2|UP
2024-11-03 01:00:00|service3|UP
2024-11-03 01:05:00|service1|UP
2024-11-03 01:05:00|service2|UP
2024-11-03 01:05:00|service3|UP
2024-11-03 01:10:00|service1|UP
2024-11-03 01:10:00|service2|UP
2024-11-03 01:10:00|service3|UP
2024-11-03 01:15:00|service1|UP
2024-11-03 01:15:00|service2|UP
2024-11-03 01:15:00|service3|UP
2024-11-03 01:20:00|service1|UP
2024-11-03 01:20:00|service2|UP
2024-11-03 01:20:00|service3|UP
2024-11-03 01:25:00|service1|UP
2024-11-03 01:25:00|service2|UP
2024-11-03 01:25:00|service3|UP
ENDLOG

RUN chmod 666 /home/user/monitor/uptime.log

RUN cat > /home/user/monitor/mock_server.py << 'ENDSERVER'
#!/usr/bin/env python3
"""Simple mock HTTP server that always returns 200 OK."""

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        pass  # Suppress logging


def run_server(port):
    server = HTTPServer(('localhost', port), SimpleHandler)
    server.serve_forever()


if __name__ == "__main__":
    ports = [8001, 8002, 8003]
    threads = []

    for port in ports:
        t = threading.Thread(target=run_server, args=(port,), daemon=True)
        t.start()
        threads.append(t)
        print(f"Mock server started on port {port}")

    # Keep main thread alive
    import time
    while True:
        time.sleep(3600)
ENDSERVER

RUN chmod 755 /home/user/monitor/mock_server.py

RUN cat > /entrypoint.sh << 'ENTRYPOINT'
#!/bin/bash
# Start mock servers in background
python3 /home/user/monitor/mock_server.py &

# Wait for servers to be ready
sleep 2

# Execute shell
exec /bin/bash
ENTRYPOINT

RUN chmod 755 /entrypoint.sh

RUN chown -R 1000:1000 /home/user

WORKDIR /home/user

ENTRYPOINT ["/entrypoint.sh"]
