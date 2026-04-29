FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest pyyaml

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/deploy/manifests && \
    mkdir -p /home/user/.kube-state && \
    chmod -R 0777 /home/user

RUN cat > /home/user/deploy/manifests/deployment.yaml << 'EOF'
# Deployment for web application
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: default
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: nginx:1.21
        ports:
        - containerPort: 80
EOF

RUN cat > /home/user/deploy/manifests/service.yaml << 'EOF'
# Service for web application
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
  namespace: default
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF

RUN cat > /home/user/deploy/manifests/configmap.yaml << 'EOF'
# ConfigMap for application settings
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  LOG_LEVEL: info
  MAX_CONNECTIONS: "100"
  ENABLE_CACHE: "true"
EOF

RUN cat > /home/user/deploy/manifests/ingress.yaml << 'EOF'
# Ingress for web application
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 80
EOF

RUN cat > /home/user/.kube-state/deployment.yaml << 'EOF'
# Deployment for web application
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: default
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: nginx:1.21
        ports:
        - containerPort: 80
EOF

RUN cat > /home/user/.kube-state/service.yaml << 'EOF'
# Service for web application
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
  namespace: default
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF

RUN cat > /home/user/.kube-state/configmap.yaml << 'EOF'
# ConfigMap for application settings
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  LOG_LEVEL: info
  MAX_CONNECTIONS: "100"
  ENABLE_CACHE: "true"
EOF

RUN cat > /home/user/.kube-state/ingress.yaml << 'EOF'
# Ingress for web application
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-app-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-service
            port:
              number: 80
EOF

RUN cat > /usr/local/bin/kubectl << 'KUBECTLEOF'
#!/bin/bash

KUBE_STATE_DIR="/home/user/.kube-state"

get_normalized_name() {
    local filepath="$1"
    basename "$filepath"
}

normalize_yaml() {
    python3 -c "import yaml, sys; yaml.dump(yaml.safe_load(sys.stdin), sys.stdout, default_flow_style=False, sort_keys=True)"
}

cmd_apply() {
    local filepath=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f)
                filepath="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$filepath" ]]; then
        echo "error: must specify -f" >&2
        exit 1
    fi

    if [[ ! -f "$filepath" ]]; then
        echo "error: file not found: $filepath" >&2
        exit 1
    fi

    local name
    name=$(get_normalized_name "$filepath")
    cp "$filepath" "$KUBE_STATE_DIR/$name"
    echo "deployment.apps/web-app configured"
    exit 0
}

cmd_diff() {
    local filepath=""
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -f)
                filepath="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ -z "$filepath" ]]; then
        echo "error: must specify -f" >&2
        exit 1
    fi

    if [[ ! -f "$filepath" ]]; then
        echo "error: file not found: $filepath" >&2
        exit 1
    fi

    local name
    name=$(get_normalized_name "$filepath")
    local stored_path="$KUBE_STATE_DIR/$name"

    if [[ ! -f "$stored_path" ]]; then
        echo "diff: file does not exist in cluster state"
        exit 1
    fi

    # BUG: Only normalize the new file, not the stored one
    local new_normalized
    new_normalized=$(cat "$filepath" | normalize_yaml)

    local stored_content
    stored_content=$(cat "$stored_path")

    if [[ "$new_normalized" == "$stored_content" ]]; then
        exit 0
    else
        echo "diff detected between local and cluster state"
        exit 1
    fi
}

case "$1" in
    apply)
        shift
        cmd_apply "$@"
        ;;
    diff)
        shift
        cmd_diff "$@"
        ;;
    *)
        echo "fake kubectl: unknown command '$1'" >&2
        exit 1
        ;;
esac
KUBECTLEOF

RUN chmod 0777 /usr/local/bin/kubectl

RUN cat > /home/user/deploy/sync-manifests.sh << 'SYNCEOF'
#!/bin/bash

MANIFESTS_DIR="/home/user/deploy/manifests"
changed_count=0
applied_count=0

echo "Starting manifest sync..."

for manifest in "$MANIFESTS_DIR"/*.yaml; do
    if [[ ! -f "$manifest" ]]; then
        continue
    fi

    filename=$(basename "$manifest")
    echo "Checking $filename..."

    kubectl diff -f "$manifest" > /dev/null 2>&1
    diff_exit=$?

    if [[ $diff_exit -ne 0 ]]; then
        echo "  Changes detected in $filename, applying..."
        kubectl apply -f "$manifest"
        ((changed_count++))
        ((applied_count++))
    else
        echo "  No changes in $filename, skipping."
    fi
done

echo ""
echo "$changed_count manifests changed"
echo "Sync complete. Applied $applied_count manifests."
SYNCEOF

RUN chmod 0755 /home/user/deploy/sync-manifests.sh

RUN cat > /home/user/deploy/test-sync.sh << 'TESTEOF'
#!/bin/bash

set -e

SCRIPT_DIR="/home/user/deploy"
SYNC_SCRIPT="$SCRIPT_DIR/sync-manifests.sh"

echo "=== Test: Sync manifests idempotency ==="
echo ""

# First run - establish baseline (may apply everything)
echo "--- First run (establishing baseline) ---"
"$SYNC_SCRIPT"
echo ""

# Second run - should detect no changes
echo "--- Second run (should detect no changes) ---"
output=$("$SYNC_SCRIPT" 2>&1)
echo "$output"
echo ""

# Check that second run reports 0 changes
if echo "$output" | grep -q "0 manifests changed"; then
    echo "SUCCESS: Second run correctly reported 0 manifests changed"
    exit 0
else
    echo "FAILURE: Second run should have reported '0 manifests changed'"
    echo "This indicates the diff logic is not working correctly."
    exit 1
fi
TESTEOF

RUN chmod 0755 /home/user/deploy/test-sync.sh

RUN chmod -R 0777 /home/user
