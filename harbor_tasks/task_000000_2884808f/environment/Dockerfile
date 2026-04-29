FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN curl -LO "https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/manifests/base/services \
    && mkdir -p /home/user/manifests/base/config \
    && mkdir -p /home/user/manifests/envs/staging \
    && mkdir -p /home/user/manifests/envs/prod

RUN cat <<'EOF' > /home/user/manifests/base/services/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  labels:
    app: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
      - name: api
        image: nginx:1.21
        ports:
        - containerPort: 80
EOF

RUN cat <<'EOF' > /home/user/manifests/base/services/api-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  selector:
    app: api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: ClusterIP
EOF

RUN cat <<'EOF' > /home/user/manifests/base/config/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  LOG_LEVEL: "info"
  API_TIMEOUT: "30"
EOF

RUN cat <<'EOF' > /home/user/manifests/envs/staging/staging-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: staging-ingress
spec:
  rules:
  - host: staging.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
EOF

RUN cat <<'EOF' > /home/user/manifests/envs/prod/prod-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: prod-ingress
spec:
  rules:
  - host: prod.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 80
EOF

WORKDIR /home/user/manifests/envs/staging
RUN ln -s ../../base/services/api-deployment.yaml deployment.yaml
RUN ln -s ../../base/api-service.yaml service.yaml
RUN ln -s ../../base/configmaps/configmap.yaml configmap.yaml

WORKDIR /home/user/manifests/envs/prod
RUN ln -s ../../base/services/api-deployment.yaml deployment.yaml
RUN ln -s ../../base/api-service.yaml service.yaml
RUN ln -s ../../base/configmaps/configmap.yaml configmap.yaml

RUN chmod -R 0777 /home/user/manifests

WORKDIR /home/user

CMD ["/bin/bash"]
