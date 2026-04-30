FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    procps \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN useradd -m -s /bin/bash -d /home/user user

RUN mkdir -p /home/user/scripts && \
    chmod 0777 /home/user

RUN cat <<'EOF' > /home/user/scripts/syscheck.sh
#!/bin/bash
echo "=== System Check $(date) ===" >> /var/log/syscheck.log
echo "Disk Usage:" >> /var/log/syscheck.log
df -h >> /var/log/syscheck.log
echo "Memory:" >> /var/log/syscheck.log
free -m >> /var/log/syscheck.log
echo "Load Average:" >> /var/log/syscheck.log
uptime >> /var/log/syscheck.log
echo "" >> /var/log/syscheck.log
EOF

RUN chmod 755 /home/user/scripts/syscheck.sh && \
    chown -R user:user /home/user/scripts

RUN touch /var/log/syscheck.log && \
    chown user:user /var/log/syscheck.log && \
    chmod 444 /var/log/syscheck.log

USER user
WORKDIR /home/user
