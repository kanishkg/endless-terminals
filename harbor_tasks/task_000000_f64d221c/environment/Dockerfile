FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/ci && chmod 0777 /home/user && chmod 0777 /home/user/ci

RUN cat > /home/user/ci/build.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting build..."
docker build -t myapp:latest .
docker tag myapp:latest registry.internal/myapp:latest
echo "Build complete"
EOF

RUN chmod +x /home/user/ci/build.sh && chmod 0777 /home/user/ci/build.sh

WORKDIR /home/user
