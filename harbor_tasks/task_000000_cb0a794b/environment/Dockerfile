FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/pipeline && chmod 0777 /home/user && chmod 0777 /home/user/pipeline

RUN cat > /home/user/pipeline/requirements.txt << 'EOF'
flask==2.2.3
requests>=2.20
pyyaml~=6.0
celery[redis]>=5.2,<6.0
EOF

RUN chmod 0666 /home/user/pipeline/requirements.txt

WORKDIR /home/user
