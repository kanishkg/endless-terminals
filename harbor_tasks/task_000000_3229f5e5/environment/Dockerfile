FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/metrics && chmod 0777 /home/user && chmod 0777 /home/user/metrics

RUN python3 << 'PYEOF'
import json
import random

# We need exactly 200 entries with sum of latency_p99 = 4827.6
# Generate 199 random values and calculate the last one to hit exact sum

services = [
    "auth-service", "api-gateway", "user-service", "payment-service",
    "order-service", "inventory-service", "notification-service",
    "search-service", "recommendation-service", "analytics-service",
    "logging-service", "cache-service", "queue-service", "storage-service",
    "email-service", "sms-service", "push-service", "scheduler-service",
    "config-service", "discovery-service", "gateway-service", "proxy-service",
    "load-balancer", "rate-limiter", "circuit-breaker", "health-checker",
    "metrics-collector", "trace-aggregator", "log-shipper", "event-bus",
    "message-broker", "task-runner", "job-scheduler", "workflow-engine",
    "data-pipeline", "etl-service", "sync-service", "backup-service",
    "restore-service", "migration-service", "audit-service", "compliance-service",
    "security-scanner", "vulnerability-checker", "access-control", "identity-provider",
    "token-service", "session-manager", "permission-service", "role-manager"
]

random.seed(42)
entries = []
target_sum = 4827.6

# Generate 199 entries with random latency values
running_sum = 0.0
for i in range(199):
    service_name = f"{random.choice(services)}-{i:03d}"
    latency = round(random.uniform(5.0, 50.0), 1)
    running_sum += latency
    entries.append({
        "service": service_name,
        "latency_p99": latency,
        "requests": random.randint(10000, 200000)
    })

# Calculate the last value to hit exact target
last_latency = round(target_sum - running_sum, 1)
entries.append({
    "service": "final-service-199",
    "latency_p99": last_latency,
    "requests": random.randint(10000, 200000)
})

# Verify the sum
actual_sum = sum(e["latency_p99"] for e in entries)
print(f"Generated {len(entries)} entries with sum {actual_sum}")

# Write to file
with open("/home/user/metrics/traces.json", "w") as f:
    json.dump(entries, f, indent=2)
PYEOF

RUN chmod 0644 /home/user/metrics/traces.json

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

USER user
WORKDIR /home/user

CMD ["/bin/bash"]
