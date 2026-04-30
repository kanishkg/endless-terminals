FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    iproute2 \
    openssl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest requests flask

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/pipeline/config \
    && mkdir -p /home/user/pipeline/out \
    && chmod -R 0777 /home/user/pipeline

RUN mkdir -p /opt/signing-service/keys \
    && mkdir -p /var/log/signing \
    && chmod 0755 /opt/signing-service \
    && chmod 0755 /opt/signing-service/keys \
    && chmod 0777 /var/log/signing

RUN echo '{"api_key": "sk-mobile-2024-abc123", "api_version": "v2"}' > /home/user/pipeline/config/auth.json \
    && chmod 0644 /home/user/pipeline/config/auth.json

RUN cat > /home/user/pipeline/submit.py << 'SUBMITEOF'
#!/usr/bin/env python3
"""Mobile app submission script - uploads to signing service."""

import json
import sys
import requests
import urllib3

# Disable SSL warnings for self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PATH = "/home/user/pipeline/config/auth.json"
SIGNING_URL = "https://localhost:8443/api/v2/sign"
OUTPUT_PATH = "/home/user/pipeline/out/app-signed.ipa"

def main():
    # Load credentials
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    api_key = config['api_key']
    api_version = config['api_version']

    # Build authorization header
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Submit for signing
    payload = {
        'app_bundle': 'com.example.mobileapp',
        'version': '2.1.0'
    }

    try:
        response = requests.post(
            SIGNING_URL,
            headers=headers,
            json=payload,
            verify=False,
            timeout=30
        )

        if response.status_code == 200:
            print(f"Signed artifact: {OUTPUT_PATH}")
            sys.exit(0)
        else:
            print(f"Signing failed with status {response.status_code}: {response.text}")
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
SUBMITEOF

RUN chmod 0755 /home/user/pipeline/submit.py

RUN cat > /opt/signing-service/server.py << 'SERVEREOF'
#!/usr/bin/env python3
"""Mock signing service for mobile CI pipeline."""

from flask import Flask, request, jsonify
import datetime
import os

app = Flask(__name__)

VALID_KEYS_FILE = "/opt/signing-service/keys/valid_keys.txt"
ACCESS_LOG = "/var/log/signing/access.log"

def log_access(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ACCESS_LOG, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def load_valid_keys():
    with open(VALID_KEYS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

@app.route('/health', methods=['GET'])
def health():
    log_access("GET /health - OK")
    return jsonify({"status": "healthy", "service": "signing-service"})

@app.route('/api/v2/sign', methods=['POST'])
def sign():
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        log_access("POST /api/v2/sign - Auth failed: missing or invalid Authorization header")
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header[7:]  # Remove 'Bearer ' prefix
    valid_keys = load_valid_keys()

    if token not in valid_keys:
        # Check if it's the old format (missing version prefix)
        if any(token in key for key in valid_keys):
            log_access(f"POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix")
        else:
            log_access(f"POST /api/v2/sign - Auth failed: invalid key")
        return jsonify({"error": "Unauthorized", "message": "Invalid API key"}), 401

    log_access(f"POST /api/v2/sign - Auth success, signing artifact")
    return jsonify({
        "status": "success",
        "artifact": "/home/user/pipeline/out/app-signed.ipa",
        "signature": "sha256:abc123def456"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, ssl_context='adhoc')
SERVEREOF

RUN chmod 0444 /opt/signing-service/server.py

RUN echo "v2:sk-mobile-2024-abc123" > /opt/signing-service/keys/valid_keys.txt \
    && chmod 0444 /opt/signing-service/keys/valid_keys.txt

RUN cat > /var/log/signing/access.log << 'LOGEOF'
[2024-01-15 02:14:33] POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix
[2024-01-15 02:14:35] POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix
[2024-01-15 02:15:01] GET /health - OK
[2024-01-15 02:15:45] POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix
[2024-01-15 02:16:22] POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix
[2024-01-15 03:00:00] GET /health - OK
[2024-01-15 03:14:33] POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix
LOGEOF

RUN chmod 0666 /var/log/signing/access.log

RUN cat > /var/log/signing/changelog.txt << 'CHANGELOGEOF'
Signing Service Changelog
=========================

2024-01-14: Updated auth format - keys must now include version prefix (e.g., "v2:sk-xxx")
            This ensures API version compatibility and prevents cross-version key usage.
            All existing keys in valid_keys.txt have been updated to the new format.

2024-01-10: Added rate limiting to /api/v2/sign endpoint (100 req/min)

2024-01-05: Initial deployment of v2 API
CHANGELOGEOF

RUN chmod 0644 /var/log/signing/changelog.txt

RUN openssl req -x509 -newkey rsa:2048 -keyout /opt/signing-service/key.pem \
    -out /opt/signing-service/cert.pem -days 365 -nodes \
    -subj "/CN=localhost" 2>/dev/null \
    && chmod 0444 /opt/signing-service/key.pem /opt/signing-service/cert.pem

RUN cat > /opt/signing-service/run_server.py << 'RUNSERVEREOF'
#!/usr/bin/env python3
"""Wrapper to run the signing service with proper SSL."""

from flask import Flask, request, jsonify
import datetime
import os
import ssl

app = Flask(__name__)

VALID_KEYS_FILE = "/opt/signing-service/keys/valid_keys.txt"
ACCESS_LOG = "/var/log/signing/access.log"

def log_access(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ACCESS_LOG, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def load_valid_keys():
    with open(VALID_KEYS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

@app.route('/health', methods=['GET'])
def health():
    log_access("GET /health - OK")
    return jsonify({"status": "healthy", "service": "signing-service"})

@app.route('/api/v2/sign', methods=['POST'])
def sign():
    auth_header = request.headers.get('Authorization', '')

    if not auth_header.startswith('Bearer '):
        log_access("POST /api/v2/sign - Auth failed: missing or invalid Authorization header")
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header[7:]  # Remove 'Bearer ' prefix
    valid_keys = load_valid_keys()

    if token not in valid_keys:
        # Check if it's the old format (missing version prefix)
        if any(token in key for key in valid_keys):
            log_access(f"POST /api/v2/sign - Auth failed: key format mismatch, expected 'v2:' prefix")
        else:
            log_access(f"POST /api/v2/sign - Auth failed: invalid key")
        return jsonify({"error": "Unauthorized", "message": "Invalid API key"}), 401

    log_access(f"POST /api/v2/sign - Auth success, signing artifact")
    return jsonify({
        "status": "success",
        "artifact": "/home/user/pipeline/out/app-signed.ipa",
        "signature": "sha256:abc123def456"
    }), 200

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('/opt/signing-service/cert.pem', '/opt/signing-service/key.pem')
    app.run(host='0.0.0.0', port=8443, ssl_context=context)
RUNSERVEREOF

RUN chmod 0555 /opt/signing-service/run_server.py

RUN cat > /entrypoint.sh << 'ENTRYPOINTEOF'
#!/bin/bash
# Start the signing service in the background
cd /opt/signing-service
python3 /opt/signing-service/run_server.py &

# Wait for service to be ready
for i in {1..30}; do
    if curl -sk https://localhost:8443/health >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Execute the provided command or start bash
exec "$@"
ENTRYPOINTEOF

RUN chmod 0755 /entrypoint.sh

WORKDIR /home/user

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/bin/bash"]
