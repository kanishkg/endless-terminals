FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    patch \
    diffutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/audit && chmod 0777 /home/user && chmod 0777 /home/user/audit

RUN python3 << 'PYSCRIPT'
import random
import hashlib

random.seed(42)

components = ['auth', 'network', 'storage', 'compute', 'scheduler', 'monitor', 'gateway', 'cache', 'queue', 'database']
levels = ['INFO', 'DEBUG', 'WARN', 'ERROR']
level_weights = [60, 20, 15, 5]

messages = [
    "Connection established from {ip}",
    "User {user} logged in successfully",
    "Request processed in {ms}ms",
    "Cache hit ratio: {pct}%",
    "Memory usage at {pct}%",
    "CPU load average: {load}",
    "Disk I/O: {io} ops/sec",
    "Network throughput: {throughput} MB/s",
    "Session {session} created",
    "Query executed in {ms}ms",
    "Background job {job} completed",
    "Configuration reloaded",
    "Health check passed",
    "Metrics exported successfully",
    "Rate limit applied to {ip}",
    "Connection pool size: {pool}",
    "Thread count: {threads}",
    "Garbage collection completed in {ms}ms",
    "Index rebuild started",
    "Backup snapshot created",
]

def gen_ip():
    return f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"

def gen_user():
    return random.choice(['alice', 'bob', 'charlie', 'david', 'eve', 'frank', 'grace', 'henry'])

def gen_session():
    return hashlib.md5(str(random.randint(0,999999)).encode()).hexdigest()[:12]

def gen_job():
    return f"job_{random.randint(1000,9999)}"

def gen_msg():
    template = random.choice(messages)
    return template.format(
        ip=gen_ip(),
        user=gen_user(),
        ms=random.randint(1, 500),
        pct=random.randint(10, 95),
        load=round(random.uniform(0.1, 4.0), 2),
        io=random.randint(100, 5000),
        throughput=round(random.uniform(1.0, 100.0), 1),
        session=gen_session(),
        job=gen_job(),
        pool=random.randint(5, 50),
        threads=random.randint(10, 200),
    )

def gen_timestamp(line_num):
    base_hour = 9
    base_min = 0
    total_seconds = line_num * 3
    hours = base_hour + total_seconds // 3600
    mins = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours >= 24:
        hours = hours % 24
    return f"2024-01-15 {hours:02d}:{mins:02d}:{secs:02d}"

baseline_lines = []
for i in range(1200):
    ts = gen_timestamp(i)
    level = random.choices(levels, weights=level_weights)[0]
    comp = random.choice(components)
    msg = gen_msg()
    line = f"[{ts}] [{level}] [{comp}] {msg}"
    baseline_lines.append(line)

with open('/home/user/audit/baseline.log', 'w') as f:
    for line in baseline_lines:
        f.write(line + '\n')

patched_lines = baseline_lines.copy()

patched_lines[49] = "[2024-01-15 09:02:27] [WARN] [auth] Authentication attempt failed for user mallory from 10.0.0.99"
patched_lines.insert(50, "[2024-01-15 09:02:28] [ERROR] [auth] Brute force detection triggered for IP 10.0.0.99")

patched_lines[201] = "[2024-01-15 09:10:03] [ERROR] [network] Connection timeout to upstream server 10.1.1.1"
patched_lines[202] = "[2024-01-15 09:10:06] [WARN] [network] Retrying connection attempt 1/3"
patched_lines.insert(203, "[2024-01-15 09:10:09] [INFO] [network] Connection restored to upstream server")

patched_lines[401] = "[2024-01-15 09:20:03] [WARN] [storage] Disk usage exceeded 80% threshold on /dev/sda1"

patched_lines[502] = "[2024-01-15 09:25:06] [ERROR] [database] Query timeout after 30000ms"
patched_lines[503] = "[2024-01-15 09:25:09] [WARN] [database] Connection pool exhausted, queuing requests"
patched_lines.insert(504, "[2024-01-15 09:25:10] [INFO] [database] Emergency pool expansion initiated")
patched_lines.insert(505, "[2024-01-15 09:25:11] [INFO] [database] Pool size increased from 20 to 40")

for idx in range(850, 856):
    if idx < len(patched_lines):
        patched_lines[idx] = f"[2024-01-15 09:42:{15+idx-850:02d}] [INFO] [monitor] System health check iteration {idx-849} completed"

patched_lines.insert(856, "[2024-01-15 09:42:21] [WARN] [monitor] Elevated memory pressure detected")
patched_lines.insert(857, "[2024-01-15 09:42:22] [INFO] [monitor] Initiating memory optimization routine")

del patched_lines[860]

patched_lines[1002] = "[2024-01-15 09:50:06] [INFO] [scheduler] Maintenance window started"
patched_lines.insert(1003, "[2024-01-15 09:50:07] [INFO] [scheduler] Non-critical jobs paused")

with open('/home/user/audit/patched_correct.log', 'w') as f:
    for line in patched_lines:
        f.write(line + '\n')

reference_lines = patched_lines[846:901]
with open('/home/user/audit/reference_fragment.txt', 'w') as f:
    for line in reference_lines:
        f.write(line + '\n')

import subprocess
result = subprocess.run(
    ['diff', '-u', '/home/user/audit/baseline.log', '/home/user/audit/patched_correct.log'],
    capture_output=True,
    text=True
)
correct_patch = result.stdout

patch_lines = correct_patch.split('\n')

corrupted_lines = []
hunk_num = 0
in_hunk = False
hunk_line_count = 0

i = 0
while i < len(patch_lines):
    line = patch_lines[i]

    if line.startswith('@@'):
        hunk_num += 1
        in_hunk = True
        hunk_line_count = 0

        if hunk_num == 2:
            corrupted_lines.append(line)
            i += 1
            ctx_corrupted = 0
            while i < len(patch_lines) and not patch_lines[i].startswith('@@'):
                curr = patch_lines[i]
                if curr.startswith(' ') and ctx_corrupted < 3:
                    if '[2024-01-15 09:' in curr:
                        curr = curr.replace('[2024-01-15 09:', '[2024-01-')
                        ctx_corrupted += 1
                corrupted_lines.append(curr)
                i += 1
            continue

        elif hunk_num == 4:
            corrupted_lines.append('@@ -498,7 +498,9 @@')
            i += 1
            continue

        elif hunk_num == 5:
            corrupted_lines.append(line)
            i += 1
            added_truncated = 0
            removal_seen = False
            removal_line = None
            while i < len(patch_lines) and not patch_lines[i].startswith('@@'):
                curr = patch_lines[i]
                if curr.startswith('+') and not curr.startswith('+++'):
                    if added_truncated < 2 and len(curr) > 45:
                        curr = curr[:40]
                        added_truncated += 1
                if curr.startswith('-') and not curr.startswith('---'):
                    if not removal_seen:
                        removal_seen = True
                        removal_line = curr
                        corrupted_lines.append(curr)
                        corrupted_lines.append(curr)
                        i += 1
                        continue
                corrupted_lines.append(curr)
                i += 1
            continue
        else:
            corrupted_lines.append(line)
    else:
        corrupted_lines.append(line)
    i += 1

with open('/home/user/audit/changes.patch', 'w') as f:
    f.write('\n'.join(corrupted_lines))

import os
os.remove('/home/user/audit/patched_correct.log')

PYSCRIPT

RUN chmod 644 /home/user/audit/baseline.log && \
    chmod 644 /home/user/audit/changes.patch && \
    chmod 644 /home/user/audit/reference_fragment.txt

CMD ["/bin/bash"]
