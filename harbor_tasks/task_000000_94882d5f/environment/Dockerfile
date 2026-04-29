FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/inventory /home/user/reports && \
    chmod 0777 /home/user && \
    chmod 0777 /home/user/inventory && \
    chmod 0777 /home/user/reports

RUN cat <<'EOF' > /home/user/inventory/hosts.json
[
    {"hostname": "web-prod-01", "cpu_cores": 8, "memory_gb": 32, "datacenter": "us-east"},
    {"hostname": "web-prod-02", "cpu_cores": 8, "memory_gb": 32, "datacenter": "us-east"},
    {"hostname": "db-primary", "cpu_cores": 16, "memory_gb": 128, "datacenter": "us-east"},
    {"hostname": "db-replica", "cpu_cores": 16, "memory_gb": 128, "datacenter": "us-west"},
    {"hostname": "cache-01", "cpu_cores": 4, "memory_gb": 16, "datacenter": "us-west"}
]
EOF

RUN chmod 0644 /home/user/inventory/hosts.json

WORKDIR /home/user

CMD ["/bin/bash"]
