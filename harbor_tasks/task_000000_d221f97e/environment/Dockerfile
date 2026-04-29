FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/perf && chmod 0777 /home/user/perf

RUN mkdir -p /var/log/gateway && chmod 0755 /var/log/gateway

RUN cat <<'EOF' > /home/user/perf/filter_logs.py
#!/usr/bin/env python3
"""
Filter access logs for slow requests (>500ms response time).
Reads from /var/log/gateway/access.log
Writes matching lines to /home/user/perf/slow.txt
"""

import re

def filter_slow_requests():
    input_file = "/var/log/gateway/access.log"
    output_file = "/home/user/perf/slow.txt"

    # Pattern to match response time
    pattern = r'response_time=(\d+)ms'

    slow_requests = []

    with open(input_file, 'r') as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                response_time = int(match.group(1))
                if response_time > 500:
                    slow_requests.append(line)

    with open(output_file, 'w') as f:
        f.writelines(slow_requests)

    print(f"Found {len(slow_requests)} slow requests (>500ms)")

if __name__ == "__main__":
    filter_slow_requests()
EOF

RUN chmod 0666 /home/user/perf/filter_logs.py

RUN cat <<'EOF' > /home/user/perf/test_access.log
2024-01-15T10:00:01Z GET /api/v1/users/123 200 response_time=150ms client_ip=192.168.1.10
2024-01-15T10:00:02Z POST /api/v1/orders 201 response_time=320ms client_ip=192.168.1.11
2024-01-15T10:00:03Z GET /api/v1/products/456 200 response_time=89ms client_ip=192.168.1.12
2024-01-15T10:00:04Z PUT /api/v1/users/123 200 response_time=245ms client_ip=192.168.1.10
2024-01-15T10:00:05Z GET /api/v1/inventory 200 response_time=567ms client_ip=192.168.1.13
2024-01-15T10:00:06Z DELETE /api/v1/orders/789 204 response_time=178ms client_ip=192.168.1.11
2024-01-15T10:00:07Z GET /api/v1/reports/daily 200 response_time=892ms client_ip=192.168.1.14
2024-01-15T10:00:08Z POST /api/v1/auth/login 200 response_time=134ms client_ip=192.168.1.15
2024-01-15T10:00:09Z GET /api/v1/users/456 200 response_time=98ms client_ip=192.168.1.16
2024-01-15T10:00:10Z GET /api/v1/health 200 response_time=12ms client_ip=192.168.1.17
EOF

RUN chmod 0644 /home/user/perf/test_access.log

RUN cat <<'PYSCRIPT' > /tmp/generate_logs.py
#!/usr/bin/env python3
import random

random.seed(42)

endpoints_v1 = [
    "/api/v1/users/{id}",
    "/api/v1/orders/{id}",
    "/api/v1/products/{id}",
    "/api/v1/inventory",
    "/api/v1/reports/daily",
    "/api/v1/auth/login",
    "/api/v1/health",
    "/api/v1/settings",
    "/api/v1/notifications",
    "/api/v1/search",
]

endpoints_v2 = [
    "/api/v2/users/{id}",
    "/api/v2/orders/{id}",
    "/api/v2/products/{id}",
    "/api/v2/analytics",
    "/api/v2/recommendations",
    "/api/v2/streaming",
    "/api/v2/batch",
    "/api/v2/webhooks",
]

methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
status_codes = [200, 201, 204, 400, 401, 403, 404, 500, 502, 503]

lines = []
slow_count_v1 = 0
slow_count_v2 = 0
target_slow = 187

v1_slow_target = 100
v2_slow_target = 87

for i in range(5000):
    hour = 10 + (i // 500)
    minute = (i % 60)
    second = (i * 7) % 60
    timestamp = f"2024-01-15T{hour:02d}:{minute:02d}:{second:02d}Z"

    client_ip = f"192.168.{random.randint(1,10)}.{random.randint(1,254)}"
    method = random.choice(methods)
    status = random.choice(status_codes)

    use_v2 = random.random() < 0.4

    if use_v2:
        endpoint = random.choice(endpoints_v2).replace("{id}", str(random.randint(100, 9999)))

        if slow_count_v2 < v2_slow_target and random.random() < 0.05:
            response_time = random.randint(501, 2500)
            slow_count_v2 += 1
        else:
            response_time = random.randint(10, 450)

        upstream_time = random.randint(50, 1200)

        line = f"{timestamp} {method} {endpoint} {status} response_time_ms={response_time} upstream_response_time={upstream_time}ms client_ip={client_ip} request_id={random.randint(100000,999999)}"
    else:
        endpoint = random.choice(endpoints_v1).replace("{id}", str(random.randint(100, 9999)))

        if slow_count_v1 < v1_slow_target and random.random() < 0.04:
            response_time = random.randint(501, 3000)
            slow_count_v1 += 1
        else:
            response_time = random.randint(5, 480)

        upstream_time = random.randint(100, 1500)

        line = f"{timestamp} {method} {endpoint} {status} response_time={response_time}ms upstream_response_time={upstream_time}ms client_ip={client_ip} request_id={random.randint(100000,999999)}"

    lines.append(line)

current_slow = slow_count_v1 + slow_count_v2
needed = target_slow - current_slow

if needed > 0:
    indices = random.sample(range(len(lines)), min(needed * 2, len(lines)))
    added = 0
    for idx in indices:
        if added >= needed:
            break
        line = lines[idx]
        if "response_time_ms=" in line and "501" not in line and "502" not in line:
            parts = line.split("response_time_ms=")
            rest = parts[1].split(" ", 1)
            old_time = int(rest[0])
            if old_time <= 500:
                new_time = random.randint(510, 1800)
                lines[idx] = parts[0] + f"response_time_ms={new_time} " + rest[1]
                added += 1
        elif "response_time=" in line and "upstream_response_time" not in line.split("response_time=")[0][-10:]:
            import re
            match = re.search(r'(?<![a-z_])response_time=(\d+)ms', line)
            if match and int(match.group(1)) <= 500:
                old_time = int(match.group(1))
                new_time = random.randint(520, 2000)
                lines[idx] = line.replace(f"response_time={old_time}ms", f"response_time={new_time}ms", 1)
                added += 1

with open("/var/log/gateway/access.log", "w") as f:
    for line in lines:
        f.write(line + "\n")

import re
legacy_pattern = re.compile(r'(?<![a-z_])response_time=(\d+)ms')
new_pattern = re.compile(r'response_time_ms=(\d+)')
final_slow = 0
with open("/var/log/gateway/access.log", "r") as f:
    for line in f:
        legacy_match = legacy_pattern.search(line)
        if legacy_match:
            if int(legacy_match.group(1)) > 500:
                final_slow += 1
                continue
        new_match = new_pattern.search(line)
        if new_match:
            if int(new_match.group(1)) > 500:
                final_slow += 1

print(f"Generated log with {final_slow} slow requests")
PYSCRIPT

RUN python3 /tmp/generate_logs.py

RUN cat <<'PYSCRIPT' > /tmp/adjust_logs.py
#!/usr/bin/env python3
import re
import random

random.seed(123)

legacy_pattern = re.compile(r'(?<![a-z_])response_time=(\d+)ms')
new_pattern = re.compile(r'response_time_ms=(\d+)')

with open("/var/log/gateway/access.log", "r") as f:
    lines = f.readlines()

slow_lines = []
fast_lines = []

for i, line in enumerate(lines):
    is_slow = False
    legacy_match = legacy_pattern.search(line)
    if legacy_match:
        if int(legacy_match.group(1)) > 500:
            is_slow = True
    else:
        new_match = new_pattern.search(line)
        if new_match and int(new_match.group(1)) > 500:
            is_slow = True

    if is_slow:
        slow_lines.append(i)
    else:
        fast_lines.append(i)

current_slow = len(slow_lines)
target = 187

if current_slow > target:
    to_make_fast = current_slow - target
    indices_to_fix = random.sample(slow_lines, to_make_fast)
    for idx in indices_to_fix:
        line = lines[idx]
        legacy_match = legacy_pattern.search(line)
        if legacy_match:
            old_time = int(legacy_match.group(1))
            new_time = random.randint(100, 450)
            lines[idx] = legacy_pattern.sub(f"response_time={new_time}ms", line, count=1)
        else:
            new_match = new_pattern.search(line)
            if new_match:
                old_time = int(new_match.group(1))
                new_time = random.randint(100, 450)
                lines[idx] = new_pattern.sub(f"response_time_ms={new_time}", line, count=1)

elif current_slow < target:
    to_make_slow = target - current_slow
    indices_to_fix = random.sample(fast_lines, to_make_slow)
    for idx in indices_to_fix:
        line = lines[idx]
        legacy_match = legacy_pattern.search(line)
        if legacy_match:
            new_time = random.randint(510, 1500)
            lines[idx] = legacy_pattern.sub(f"response_time={new_time}ms", line, count=1)
        else:
            new_match = new_pattern.search(line)
            if new_match:
                new_time = random.randint(510, 1500)
                lines[idx] = new_pattern.sub(f"response_time_ms={new_time}", line, count=1)

with open("/var/log/gateway/access.log", "w") as f:
    f.writelines(lines)

final_slow = 0
with open("/var/log/gateway/access.log", "r") as f:
    for line in f:
        legacy_match = legacy_pattern.search(line)
        if legacy_match:
            if int(legacy_match.group(1)) > 500:
                final_slow += 1
                continue
        new_match = new_pattern.search(line)
        if new_match:
            if int(new_match.group(1)) > 500:
                final_slow += 1

print(f"Adjusted log now has {final_slow} slow requests")
PYSCRIPT

RUN python3 /tmp/adjust_logs.py

RUN chmod 0644 /var/log/gateway/access.log

RUN rm /tmp/generate_logs.py /tmp/adjust_logs.py

RUN useradd -m -d /home/user -s /bin/bash user

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
