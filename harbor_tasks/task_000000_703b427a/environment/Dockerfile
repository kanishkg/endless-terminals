FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gawk \
    sed \
    grep \
    perl \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/scripts && \
    mkdir -p /var/log/httpd && \
    chmod 0777 /home/user && \
    chmod 0777 /home/user/scripts && \
    chmod 0755 /var/log/httpd

RUN cat > /home/user/scripts/top_ips.sh << 'EOF'
#!/bin/bash
LOGDIR="/var/log/httpd"
YESTERDAY=$(date -d "yesterday" +%Y%m%d)
LOGFILE="$LOGDIR/access_$YESTERDAY.log"

cat "$LOGFILE" | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -10
EOF

RUN chmod +x /home/user/scripts/top_ips.sh

RUN cat > /tmp/generate_logs.py << 'PYEOF'
import random
from datetime import datetime, timedelta

# Define IPs with their expected counts for the final day (20250125)
# Total should be 8847 lines
ip_weights = {
    "192.168.44.12": 847,
    "10.0.0.55": 723,
    "172.16.8.99": 691,
    "192.168.44.8": 584,
    "10.0.0.71": 512,
    "172.16.8.102": 445,
    "192.168.1.15": 398,
    "10.0.0.12": 367,
    "172.16.8.44": 289,
    "192.168.44.200": 256,
}

# Additional IPs to fill up to 8847
other_ips = [
    "192.168.1.100", "10.0.0.100", "172.16.8.1", "192.168.44.50",
    "10.0.0.200", "172.16.8.200", "192.168.1.50", "10.0.0.150",
    "172.16.8.150", "192.168.44.150", "192.168.1.200", "10.0.0.75",
    "172.16.8.75", "192.168.44.75", "192.168.1.75"
]

proxy_ips = ["10.255.0.1", "10.255.0.2", "10.255.0.3"]

methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
paths = ["/", "/index.html", "/api/users", "/api/data", "/images/logo.png", 
         "/css/style.css", "/js/app.js", "/login", "/logout", "/dashboard"]
statuses = ["200", "200", "200", "200", "301", "302", "404", "500"]
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "curl/7.68.0",
    "python-requests/2.28.0"
]

def generate_log_line(ip, timestamp, use_xff=False):
    method = random.choice(methods)
    path = random.choice(paths)
    status = random.choice(statuses)
    size = random.randint(100, 50000)
    referer = "-"
    ua = random.choice(user_agents)
    ts_str = timestamp.strftime("%d/%b/%Y:%H:%M:%S +0000")

    if use_xff:
        proxy_ip = random.choice(proxy_ips)
        return f'X-Forwarded-For: {ip} - {proxy_ip} - - [{ts_str}] "{method} {path} HTTP/1.1" {status} {size} "{referer}" "{ua}"'
    else:
        return f'{ip} - - [{ts_str}] "{method} {path} HTTP/1.1" {status} {size} "{referer}" "{ua}"'

def generate_day_logs(date_str, total_lines, use_xff_ratio=0.0):
    lines = []
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    base_date = datetime(year, month, day)

    # Calculate IP distribution
    main_ip_total = sum(ip_weights.values())

    if date_str == "20250125":
        # Use exact counts for the target day
        ip_counts = dict(ip_weights)
        remaining = total_lines - main_ip_total
        for ip in other_ips:
            count = remaining // len(other_ips)
            ip_counts[ip] = count
        # Adjust to hit exact total
        current_total = sum(ip_counts.values())
        diff = total_lines - current_total
        if diff > 0:
            ip_counts[other_ips[0]] += diff
    else:
        # Proportional distribution for other days
        scale = total_lines / 8847.0
        ip_counts = {}
        for ip, count in ip_weights.items():
            ip_counts[ip] = int(count * scale)
        remaining = total_lines - sum(ip_counts.values())
        for ip in other_ips:
            count = remaining // len(other_ips)
            ip_counts[ip] = count
        current_total = sum(ip_counts.values())
        diff = total_lines - current_total
        if diff > 0:
            ip_counts[other_ips[0]] += diff

    # Generate lines
    for ip, count in ip_counts.items():
        for _ in range(count):
            ts = base_date + timedelta(seconds=random.randint(0, 86399))
            use_xff = random.random() < use_xff_ratio
            lines.append((ts, generate_log_line(ip, ts, use_xff)))

    # Sort by timestamp
    lines.sort(key=lambda x: x[0])
    return [line[1] for line in lines]

# Generate log files
log_configs = [
    ("20250120", 5000, 0.0),   # No XFF
    ("20250121", 5500, 0.0),   # No XFF
    ("20250122", 6000, 0.66),  # ~2/3 XFF (load balancer added)
    ("20250123", 7000, 0.66),
    ("20250124", 8000, 0.66),
    ("20250125", 8847, 0.66),  # Yesterday - exact counts needed
]

for date_str, total_lines, xff_ratio in log_configs:
    lines = generate_day_logs(date_str, total_lines, xff_ratio)
    with open(f"/var/log/httpd/access_{date_str}.log", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Generated access_{date_str}.log with {len(lines)} lines")

PYEOF

RUN python3 /tmp/generate_logs.py && rm /tmp/generate_logs.py

RUN chmod 644 /var/log/httpd/*.log

RUN useradd -m -d /home/user -s /bin/bash user && \
    chown -R user:user /home/user

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set fake date so "yesterday" resolves to 20250125
RUN apt-get update && apt-get install -y faketime && rm -rf /var/lib/apt/lists/*

ENV FAKETIME="2025-01-26 12:00:00"
ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketime.so.1

WORKDIR /home/user
USER user

CMD ["/bin/bash"]
