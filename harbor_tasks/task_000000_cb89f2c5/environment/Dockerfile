FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the k8s-manifests directory structure
RUN mkdir -p /home/user/k8s-manifests/dev \
    && mkdir -p /home/user/k8s-manifests/staging \
    && mkdir -p /home/user/k8s-manifests/prod

# Create dev/app.yaml
RUN cat <<EOF > /home/user/k8s-manifests/dev/app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-svc
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
EOF

# Create dev/database.yaml
RUN cat <<EOF > /home/user/k8s-manifests/dev/database.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-creds
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-svc
EOF

# Create staging/app.yaml
RUN cat <<EOF > /home/user/k8s-manifests/staging/app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-staging
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-staging-svc
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-staging-config
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
EOF

# Create staging/monitoring.yaml
RUN cat <<EOF > /home/user/k8s-manifests/staging/monitoring.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-svc
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
EOF

# Create prod/app.yaml
RUN cat <<EOF > /home/user/k8s-manifests/prod/app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-prod
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-prod-svc
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-prod-config
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-prod-ingress
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
EOF

# Create prod/database.yaml
RUN cat <<EOF > /home/user/k8s-manifests/prod/database.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-prod
---
apiVersion: v1
kind: Secret
metadata:
  name: postgres-prod-creds
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-prod-svc
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
EOF

# Set permissions for all created files and directories
RUN chmod -R 0777 /home/user/k8s-manifests

WORKDIR /home/user
