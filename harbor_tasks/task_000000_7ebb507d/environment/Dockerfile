FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest requests pyyaml flask

RUN mkdir -p /home/user/netcheck && chmod 0777 /home/user && chmod 0777 /home/user/netcheck

RUN cat > /home/user/netcheck/endpoints.yaml << 'EOF'
endpoints:
  - name: auth-service
    url: http://127.0.0.1:5001/health
    timeout: 5
  - name: data-service
    url: http://127.0.0.1:5002/health
    timeout: 5
  - name: cache-service
    url: http://127.0.0.1:5003/health
    timeout: 5
EOF

RUN chmod 644 /home/user/netcheck/endpoints.yaml

RUN cat > /home/user/netcheck/config.py << 'EOF'
# Configuration module added during project reorganization
# TODO: Integrate these constants into the main checker

DEFAULT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Service categories for future use
SERVICE_CATEGORIES = {
    'auth': ['auth-service'],
    'data': ['data-service'],
    'cache': ['cache-service'],
}
EOF

RUN chmod 644 /home/user/netcheck/config.py

RUN cat > /home/user/netcheck/checker.py << 'EOF'
#!/usr/bin/env python3
"""
Health checker script - checks configured endpoints and writes results.
Reads endpoint configuration from endpoints.yaml and outputs to results.json.
"""

import json
import os
import yaml
import requests
from datetime import datetime

# Import from config module (added during reorganization)
from config import DEFAULT_TIMEOUT


def load_config(config_path):
    """Load endpoint configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def check_endpoint(endpoint, config):
    """
    Check a single endpoint and return its status.

    Args:
        endpoint: dict with 'name', 'url', and 'timeout' keys
        config: the full configuration dict

    Returns:
        dict with check results
    """
    name = endpoint.get('name', 'unknown')
    url = endpoint.get('url')
    timeout_val = endpoint.get('timeout', 5)

    result = {
        'name': name,
        'url': url,
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'unknown',
        'response_time_ms': None,
        'error': None
    }

    try:
        start_time = datetime.utcnow()
        # Make the request with configured timeout
        # Note: Using global_timeout from config for consistency across all endpoints
        resp = requests.get(url, timeout=config.get('global_timeout'))
        end_time = datetime.utcnow()

        response_time = (end_time - start_time).total_seconds() * 1000
        result['response_time_ms'] = round(response_time, 2)

        if resp.status_code == 200:
            result['status'] = 'healthy'
        else:
            result['status'] = 'unhealthy'
            result['error'] = f'HTTP {resp.status_code}'

    except requests.exceptions.Timeout:
        result['status'] = 'timeout'
        result['error'] = 'Request timed out'
    except requests.exceptions.ConnectionError as e:
        result['status'] = 'unreachable'
        result['error'] = str(e)
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)

    return result


def run_health_checks(config_path, output_path):
    """
    Run health checks on all configured endpoints.

    Args:
        config_path: path to endpoints.yaml
        output_path: path to write results.json
    """
    config = load_config(config_path)
    endpoints = config.get('endpoints', [])

    results = {
        'check_time': datetime.utcnow().isoformat(),
        'total_endpoints': len(endpoints),
        'results': []
    }

    for endpoint in endpoints:
        print(f"Checking {endpoint.get('name', 'unknown')}...")
        check_result = check_endpoint(endpoint, config)
        results['results'].append(check_result)
        print(f"  Status: {check_result['status']}")

    # Calculate summary
    healthy_count = sum(1 for r in results['results'] if r['status'] == 'healthy')
    results['healthy_count'] = healthy_count
    results['unhealthy_count'] = len(endpoints) - healthy_count

    # Write results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {output_path}")
    return results


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'endpoints.yaml')
    output_path = os.path.join(script_dir, 'results.json')

    run_health_checks(config_path, output_path)
EOF

RUN chmod 755 /home/user/netcheck/checker.py

RUN cat > /home/user/netcheck/mock_services.py << 'EOF'
#!/usr/bin/env python3
"""
Mock Flask services for testing the health checker.
Runs three simple health endpoints on ports 5001, 5002, 5003.
"""

import multiprocessing
import time
from flask import Flask, jsonify


def create_app(service_name):
    """Create a Flask app for a mock service."""
    app = Flask(service_name)

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok', 'service': service_name})

    @app.route('/')
    def index():
        return jsonify({'service': service_name, 'endpoints': ['/health']})

    return app


def run_service(name, port):
    """Run a Flask service on the specified port."""
    app = create_app(name)
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)


def start_all_services():
    """Start all mock services as separate processes."""
    services = [
        ('auth-service', 5001),
        ('data-service', 5002),
        ('cache-service', 5003),
    ]

    processes = []
    for name, port in services:
        p = multiprocessing.Process(target=run_service, args=(name, port))
        p.daemon = True
        p.start()
        processes.append(p)
        print(f"Started {name} on port {port}")

    return processes


if __name__ == '__main__':
    processes = start_all_services()
    print("All services started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
EOF

RUN chmod 755 /home/user/netcheck/mock_services.py

RUN cat > /entrypoint.sh << 'ENTRYEOF'
#!/bin/bash

# Start the mock Flask services in the background
cd /home/user/netcheck

# Start auth-service on port 5001
python3 -c "
from flask import Flask, jsonify
app = Flask('auth-service')
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'auth-service'})
app.run(host='127.0.0.1', port=5001, debug=False)
" &

# Start data-service on port 5002
python3 -c "
from flask import Flask, jsonify
app = Flask('data-service')
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'data-service'})
app.run(host='127.0.0.1', port=5002, debug=False)
" &

# Start cache-service on port 5003
python3 -c "
from flask import Flask, jsonify
app = Flask('cache-service')
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'service': 'cache-service'})
app.run(host='127.0.0.1', port=5003, debug=False)
" &

# Wait for services to be ready
sleep 2

# Verify services are up
for port in 5001 5002 5003; do
    for i in {1..10}; do
        if curl -s http://127.0.0.1:$port/health > /dev/null 2>&1; then
            echo "Service on port $port is ready"
            break
        fi
        sleep 0.5
    done
done

exec "$@"
ENTRYEOF

RUN chmod +x /entrypoint.sh

RUN chown -R 1000:1000 /home/user

WORKDIR /home/user

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
