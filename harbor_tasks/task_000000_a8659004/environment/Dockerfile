FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    gawk \
    cron \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/scripts && chmod 0777 /home/user/scripts

RUN mkdir -p /var/log/nginx && chmod 0755 /var/log/nginx

RUN mkdir -p /var/log/reports && chmod 0777 /var/log/reports

RUN cat > /home/user/scripts/aggregate_logs.sh << 'SCRIPT_EOF'
#!/bin/bash
LOG_DIR="/var/log/nginx"
OUTPUT="/var/log/reports/top_paths.txt"
YESTERDAY=$(date -d "yesterday" +%Y%m%d)

cat $LOG_DIR/access.$YESTERDAY.log | \
    awk '{print $7}' | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10 > $OUTPUT
SCRIPT_EOF

RUN chmod 0755 /home/user/scripts/aggregate_logs.sh && chown -R 1000:1000 /home/user/scripts

RUN cat > /etc/cron.d/logstats << 'CRON_EOF'
0 * * * * user /home/user/scripts/aggregate_logs.sh
CRON_EOF

RUN chmod 0644 /etc/cron.d/logstats

RUN python3 << 'GENLOG_EOF'
import random

paths = [
    ("/api/health", 203),
    ("/api/users", 156),
    ("/static/app.js", 98),
    ("/api/orders", 87),
    ("/", 72),
    ("/static/style.css", 68),
    ("/api/products", 54),
    ("/login", 43),
    ("/api/auth", 38),
    ("/favicon.ico", 28),
]

total = sum(count for _, count in paths)
# total = 847

log_entries = []
ips = ["192.168.1.50", "10.0.0.25", "172.16.0.100", "192.168.2.75", "10.1.1.50"]
methods = ["GET", "GET", "GET", "POST", "PUT"]
statuses = [200, 200, 200, 200, 201, 304, 404]
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "curl/7.68.0",
    "python-requests/2.25.1",
]

for path, count in paths:
    for _ in range(count):
        ip = random.choice(ips)
        method = random.choice(methods)
        status = random.choice(statuses)
        size = random.randint(100, 5000)
        ua = random.choice(user_agents)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamp = f"15/Jan/2025:{hour:02d}:{minute:02d}:{second:02d} +0000"
        log_line = f'{ip} - - [{timestamp}] "{method} {path} HTTP/1.1" {status} {size} "-" "{ua}"'
        log_entries.append(log_line)

random.shuffle(log_entries)

with open("/var/log/nginx/access.log.1", "w") as f:
    for entry in log_entries:
        f.write(entry + "\n")
GENLOG_EOF

RUN python3 << 'GENTODAY_EOF'
import random

paths = ["/api/health", "/api/users", "/static/app.js", "/api/orders", "/"]
ips = ["192.168.1.50", "10.0.0.25"]
user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"]

with open("/var/log/nginx/access.log", "w") as f:
    for i in range(50):
        ip = random.choice(ips)
        path = random.choice(paths)
        ua = random.choice(user_agents)
        hour = random.randint(0, 12)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamp = f"16/Jan/2025:{hour:02d}:{minute:02d}:{second:02d} +0000"
        log_line = f'{ip} - - [{timestamp}] "GET {path} HTTP/1.1" 200 1234 "-" "{ua}"'
        f.write(log_line + "\n")
GENTODAY_EOF

RUN chmod 0644 /var/log/nginx/access.log /var/log/nginx/access.log.1

RUN touch /var/log/reports/top_paths.txt && \
    touch -d "7 days ago" /var/log/reports/top_paths.txt && \
    chmod 0666 /var/log/reports/top_paths.txt

RUN useradd -u 1000 -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
