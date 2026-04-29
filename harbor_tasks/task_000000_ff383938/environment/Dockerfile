FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user
RUN mkdir -p /home/user/tools && chmod 0777 /home/user/tools
RUN mkdir -p /home/user/reports && chmod 0777 /home/user/reports
RUN mkdir -p /var/log/batch && chmod 0755 /var/log/batch
RUN mkdir -p /var/spool/cron/crontabs && chmod 0755 /var/spool/cron/crontabs

RUN cat <<'EOF' > /var/spool/cron/crontabs/user
0 1 * * * /opt/batch/etl_main.sh
0 2 * * * /opt/batch/backup.sh
30 2 * * * /opt/batch/cleanup.sh
0 3 * * * /opt/batch/db_vacuum.sh
0 4 * * * /opt/batch/reports.sh
0 6 * * * /opt/batch/health_check.sh
EOF

RUN chmod 0644 /var/spool/cron/crontabs/user

RUN cat <<'EOF' > /var/log/batch/etl_main.log
Job: etl_main.sh
START 2024-01-15 01:00:03
Processing data files...
Loading stage 1...
Loading stage 2...
Transforming records...
Writing output...
END 2024-01-15 02:47:19
EOF

RUN cat <<'EOF' > /var/log/batch/backup.log
Job: backup.sh
START 2024-01-15 02:00:01
Initializing backup...
Backing up database...
Backing up files...
Compressing archive...
Uploading to remote...
END 2024-01-15 03:12:44
EOF

RUN cat <<'EOF' > /var/log/batch/cleanup.log
Job: cleanup.sh
START 2024-01-15 02:30:02
Scanning temp directories...
Removing old files...
Clearing caches...
END 2024-01-15 02:58:31
EOF

RUN cat <<'EOF' > /var/log/batch/db_vacuum.log
Job: db_vacuum.sh
START 2024-01-15 03:00:04
Connecting to database...
Running VACUUM ANALYZE...
Updating statistics...
END 2024-01-15 03:45:22
EOF

RUN cat <<'EOF' > /var/log/batch/reports.log
Job: reports.sh
START 2024-01-15 04:00:01
Generating daily reports...
Sending notifications...
END 2024-01-15 04:22:17
EOF

RUN cat <<'EOF' > /var/log/batch/health_check.log
Job: health_check.sh
START 2024-01-15 06:00:02
Checking services...
All systems operational.
END 2024-01-15 06:03:41
EOF

RUN chmod 0644 /var/log/batch/*.log

RUN cat <<'PYEOF' > /home/user/tools/capacity_report.py
#!/usr/bin/env python3
"""
Capacity Report Generator

Parses crontab entries and batch job logs to identify:
1. Hours where jobs overlapped (one started before another finished)
2. Hours that were genuinely idle (no jobs scheduled or running)

Output: /home/user/reports/windows.json
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path


CRONTAB_PATH = "/var/spool/cron/crontabs/user"
LOG_DIR = "/var/log/batch"
OUTPUT_PATH = "/home/user/reports/windows.json"


class Job:
    def __init__(self, name, scheduled_hour, start_time=None, end_time=None):
        self.name = name
        self.scheduled_hour = scheduled_hour  # Bug 1: Only stores hour, loses minute
        self.start_time = start_time
        self.end_time = end_time

    @property
    def start_hour(self):
        if self.start_time:
            return self.start_time.hour
        return self.scheduled_hour

    @property
    def end_hour(self):
        if self.end_time:
            return self.end_time.hour
        return self.scheduled_hour


def parse_crontab():
    """Parse crontab file and extract job schedules."""
    jobs = []

    with open(CRONTAB_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if len(parts) >= 6:
                minute = parts[0]
                hour = parts[1]
                command = parts[5]

                # Bug 1: We only store the hour, ignoring minute field
                # This means "30 2 * * *" is treated same as "0 2 * * *"
                job_name = os.path.basename(command)
                scheduled_hour = int(hour)

                jobs.append(Job(job_name, scheduled_hour))

    return jobs


def parse_log_file(log_path):
    """Parse a log file to extract start and end timestamps."""
    start_time = None
    end_time = None

    with open(log_path, 'r') as f:
        content = f.read()

    # Match START timestamp
    start_match = re.search(r'START\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', content)
    if start_match:
        start_time = datetime.strptime(start_match.group(1), '%Y-%m-%d %H:%M:%S')

    # Match END timestamp
    end_match = re.search(r'END\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', content)
    if end_match:
        end_time = datetime.strptime(end_match.group(1), '%Y-%m-%d %H:%M:%S')

    return start_time, end_time


def load_job_runtimes(jobs):
    """Load actual runtime data from log files into job objects."""
    log_dir = Path(LOG_DIR)

    for job in jobs:
        # Find corresponding log file
        log_name = job.name.replace('.sh', '.log')
        log_path = log_dir / log_name

        if log_path.exists():
            start_time, end_time = parse_log_file(log_path)
            job.start_time = start_time
            job.end_time = end_time

    return jobs


def find_overlapping_hours(jobs):
    """Find hours where jobs overlapped."""
    overlapping = set()

    for i, job1 in enumerate(jobs):
        for job2 in jobs[i+1:]:
            if job1.start_time is None or job1.end_time is None:
                continue
            if job2.start_time is None or job2.end_time is None:
                continue

            # Bug 3: Using integer hour comparison instead of actual timestamps
            # This misses overlaps within the same hour and boundary conditions
            # Comparing end_hour > start_hour misses when they're equal
            if job1.end_hour > job2.start_hour and job1.start_hour < job2.end_hour:
                # Add the hours where overlap occurs
                for h in range(job2.start_hour, job1.end_hour + 1):
                    overlapping.add(h)
            elif job2.end_hour > job1.start_hour and job2.start_hour < job1.end_hour:
                for h in range(job1.start_hour, job2.end_hour + 1):
                    overlapping.add(h)

    return sorted(list(overlapping))


def find_idle_hours(jobs):
    """Find hours that were genuinely idle."""
    idle = []

    for hour in range(24):
        is_idle = True

        # Bug 2: Only checking if a job is SCHEDULED to start in this hour
        # Not checking if a job from a previous hour is still running
        for job in jobs:
            if job.scheduled_hour == hour:
                is_idle = False
                break

        if is_idle:
            idle.append(hour)

    return idle


def main():
    # Parse crontab to get scheduled jobs
    jobs = parse_crontab()

    # Load actual runtime data from logs
    jobs = load_job_runtimes(jobs)

    # Find overlapping and idle hours
    overlapping_hours = find_overlapping_hours(jobs)
    idle_hours = find_idle_hours(jobs)

    # Write output
    result = {
        "overlapping_hours": overlapping_hours,
        "idle_hours": idle_hours
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Report written to {OUTPUT_PATH}")
    print(f"Overlapping hours: {overlapping_hours}")
    print(f"Idle hours: {idle_hours}")


if __name__ == "__main__":
    main()
PYEOF

RUN chmod 0755 /home/user/tools/capacity_report.py

RUN useradd -m -d /home/user -s /bin/bash user || true
RUN chown -R user:user /home/user
RUN chmod 0777 /home/user/tools
RUN chmod 0777 /home/user/reports
RUN chmod 0666 /home/user/tools/capacity_report.py

USER user
WORKDIR /home/user

CMD ["/bin/bash"]
