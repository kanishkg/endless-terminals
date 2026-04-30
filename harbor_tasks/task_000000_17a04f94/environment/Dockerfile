FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    gawk \
    grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /var/log/backup && chmod 0755 /var/log/backup

RUN python3 << 'PYSCRIPT'
import random

job_configs = [
    ("db-prod", 23),
    ("db-staging", 18),
    ("web-assets", 15),
    ("user-uploads", 12),
    ("config-backup", 7),
    ("logs-archive", 5)
]

total_failed = sum(c for _, c in job_configs)  # 80
total_success = 500 - total_failed  # 420

all_jobs = ["db-prod", "db-staging", "web-assets", "user-uploads", "config-backup", "logs-archive", "mail-backup", "analytics-dump", "cache-snapshot"]

messages_success = [
    "Backup completed successfully",
    "All files transferred",
    "Snapshot created",
    "Backup verified OK",
    "Transfer complete"
]

messages_failed = [
    "Connection timeout",
    "Disk quota exceeded",
    "Permission denied",
    "Network unreachable",
    "Checksum mismatch"
]

lines = []

for job, count in job_configs:
    for _ in range(count):
        day = random.randint(1, 31)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        date_str = f"2024-03-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        msg = random.choice(messages_failed)
        line = f"{date_str} {time_str} {job} FAILED {msg}"
        lines.append(line)

success_jobs = ["db-prod", "db-staging", "web-assets", "user-uploads", "config-backup", "logs-archive", "mail-backup", "analytics-dump", "cache-snapshot"]
for _ in range(total_success):
    job = random.choice(success_jobs)
    day = random.randint(1, 31)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    date_str = f"2024-03-{day:02d}"
    time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
    msg = random.choice(messages_success)
    line = f"{date_str} {time_str} {job} SUCCESS {msg}"
    lines.append(line)

random.shuffle(lines)

with open("/var/log/backup/march.log", "w") as f:
    for line in lines:
        f.write(line + "\n")
PYSCRIPT

RUN chmod 0644 /var/log/backup/march.log

RUN useradd -m -d /home/user -s /bin/bash user

RUN chown user:user /home/user && chmod 0777 /home/user

USER user
WORKDIR /home/user

CMD ["/bin/bash"]
