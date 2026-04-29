FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    echo "Asia/Tokyo" > /etc/timezone

RUN mkdir -p /home/user/scheduler /home/user/reports && \
    chmod 0777 /home/user && \
    chmod 0777 /home/user/scheduler && \
    chmod 0777 /home/user/reports

RUN cat > /home/user/scheduler/gen_report.py << 'EOF'
#!/usr/bin/env python3
import datetime
import os

def get_configured_tz():
    """Read timezone from /etc/timezone like a proper system citizen"""
    with open('/etc/timezone', 'r') as f:
        tz_name = f.read().strip()
    # Set it in environment for good measure
    os.environ['TZ'] = tz_name
    return tz_name

def generate_report():
    tz_name = get_configured_tz()

    # Get current time - should respect TZ now
    now = datetime.datetime.now()

    timestamp = now.strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'/home/user/reports/report_{timestamp}.txt'

    with open(filename, 'w') as f:
        f.write(f"Daily Report\n")
        f.write(f"Generated: {now.isoformat()}\n")
        f.write(f"Timezone: {tz_name}\n")
        f.write(f"---\n")
        f.write(f"[Report content would go here]\n")

    print(f"Report written to {filename}")
    return filename

if __name__ == '__main__':
    generate_report()
EOF

RUN chmod 0755 /home/user/scheduler/gen_report.py

WORKDIR /home/user

CMD ["/bin/bash"]
