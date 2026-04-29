FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    iproute2 \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest requests flask

RUN mkdir -p /home/user/monitor && chmod 0777 /home/user && chmod 0777 /home/user/monitor

RUN mkdir -p /home/user/services

RUN cat > /home/user/services/inventory_service.py << 'PYEOF'
from flask import Flask, jsonify, make_response
app = Flask(__name__)

@app.route('/health')
def health():
    response = make_response(jsonify({"status": "ok"}))
    response.headers['X-Service-Ready'] = 'true'
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)
PYEOF

RUN cat > /home/user/services/pricing_service.py << 'PYEOF'
from flask import Flask, jsonify, make_response
app = Flask(__name__)

@app.route('/health')
def health():
    response = make_response(jsonify({"status": "ok"}))
    response.headers['X-Service-Ready'] = 'true'
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8082)
PYEOF

RUN cat > /home/user/services/fulfillment_service.py << 'PYEOF'
from flask import Flask, jsonify, make_response
app = Flask(__name__)

@app.route('/health')
def health():
    response = make_response(jsonify({"status": "ok"}))
    response.headers['X-Service-Ready'] = 'true'
    return response

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8083)
PYEOF

RUN cat > /home/user/monitor/check_all.py << 'PYEOF'
#!/usr/bin/env python3
"""
Health check dashboard script.
Polls internal services and writes status report to status.json.
"""

import json
import requests
from datetime import datetime

# Service configuration
SERVICES = {
    "inventory": "http://127.0.0.1:8081/health",
    "pricing": "http://127.0.0.1:8082/health",
    "fulfillment": "http://127.0.0.1:8083/health",
}

# Timeout for requests (bumped to 30s to rule out timeout issues)
REQUEST_TIMEOUT = 30


def check_service(name, url):
    """
    Check a single service's health endpoint.
    Returns dict with status information.
    """
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        # TODO: also check X-Service-Ready header
        if response.status_code == 200:
            data = response.json()
            # Check if service reports healthy state
            if data.get("state") == "ok":
                return {"status": "healthy", "response_time_ms": response.elapsed.total_seconds() * 1000}
        return {"status": "degraded", "reason": "unhealthy response"}
    except requests.exceptions.Timeout:
        return {"status": "degraded", "reason": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"status": "degraded", "reason": "connection_failed"}
    except Exception as e:
        return {"status": "degraded", "reason": str(e)}


def main():
    """Main entry point - check all services and write report."""
    results = {}
    all_healthy = True

    for name, url in SERVICES.items():
        result = check_service(name, url)
        results[name] = result
        if result["status"] != "healthy":
            all_healthy = False

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": results,
        "healthy": all_healthy,
    }

    with open("/home/user/monitor/status.json", "w") as f:
        json.dump(report, f, indent=2)

    return 0 if all_healthy else 1


if __name__ == "__main__":
    exit(main())
PYEOF

RUN chmod +x /home/user/monitor/check_all.py

RUN chmod -R 0777 /home/user/services && chmod -R 0777 /home/user/monitor

RUN cat > /entrypoint.sh << 'ENTRYEOF'
#!/bin/bash

# Start the three Flask services in the background
cd /home/user/services
python3 inventory_service.py &
python3 pricing_service.py &
python3 fulfillment_service.py &

# Wait for services to be ready
sleep 3

# Verify services are up
for port in 8081 8082 8083; do
    for i in {1..10}; do
        if curl -s http://127.0.0.1:$port/health > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done
done

# Run the buggy check_all.py to create initial status.json with degraded state
cd /home/user/monitor
python3 check_all.py

# Execute the provided command or start bash
exec "$@"
ENTRYEOF

RUN chmod +x /entrypoint.sh

WORKDIR /home/user

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
