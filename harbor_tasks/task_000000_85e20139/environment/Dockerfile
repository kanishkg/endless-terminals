FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    redis-server \
    procps \
    iproute2 \
    grep \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/services/redis && \
    chmod -R 0777 /home/user

RUN cat > /home/user/services/redis/redis.conf << 'EOF'
# Redis configuration file
bind 127.0.0.1
port 6379
daemonize yes
pidfile /home/user/services/redis/redis.pid
loglevel notice
logfile /home/user/services/redis/redis.log
databases 16
maxmemory-policy lru
maxmemory 100mb
appendonly no
dir /home/user/services/redis
dbfilename dump.rdb
timeout 0
tcp-keepalive 300
EOF

RUN chmod 0666 /home/user/services/redis/redis.conf && \
    chmod 0777 /home/user/services/redis

WORKDIR /home/user

CMD ["/bin/bash"]
