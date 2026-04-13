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

# Create logs directory
RUN mkdir -p /home/user/logs && chmod 0777 /home/user/logs

# Create the access.log file with Apache Combined Log Format entries
RUN cat <<EOF > /home/user/logs/access.log
192.168.1.100 - - [15/Jan/2024:10:15:32 +0000] "GET /index.html HTTP/1.1" 200 1542 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:15:45 +0000] "GET /style.css HTTP/1.1" 200 892 "-" "Mozilla/5.0"
10.0.0.55 - - [15/Jan/2024:10:16:01 +0000] "GET /api/users HTTP/1.1" 200 2048 "-" "curl/7.68.0"
192.168.1.100 - - [15/Jan/2024:10:17:22 +0000] "GET /admin/login HTTP/1.1" 403 512 "-" "Mozilla/5.0"
10.0.0.55 - - [15/Jan/2024:10:18:05 +0000] "POST /api/users HTTP/1.1" 201 256 "-" "curl/7.68.0"
172.16.0.25 - - [15/Jan/2024:10:19:33 +0000] "GET /products HTTP/1.1" 200 4096 "-" "Mozilla/5.0"
172.16.0.25 - - [15/Jan/2024:10:20:12 +0000] "GET /products?id=5 HTTP/1.1" 200 1024 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:21:45 +0000] "GET /index.html HTTP/1.1" 200 1542 "-" "Mozilla/5.0"
10.0.0.55 - - [15/Jan/2024:10:22:18 +0000] "GET /api/missing HTTP/1.1" 404 128 "-" "curl/7.68.0"
203.0.113.50 - - [15/Jan/2024:10:23:55 +0000] "GET /index.html HTTP/1.1" 200 1542 "-" "Mozilla/5.0"
203.0.113.50 - - [15/Jan/2024:10:24:30 +0000] "GET /broken HTTP/1.1" 500 256 "-" "Mozilla/5.0"
172.16.0.25 - - [15/Jan/2024:10:25:00 +0000] "GET /products HTTP/1.1" 200 4096 "-" "Mozilla/5.0"
192.168.1.100 - - [15/Jan/2024:10:26:15 +0000] "DELETE /api/admin HTTP/1.1" 403 512 "-" "Mozilla/5.0"
10.0.0.55 - - [15/Jan/2024:10:27:00 +0000] "GET /api/users HTTP/1.1" 200 2048 "-" "curl/7.68.0"
203.0.113.50 - - [15/Jan/2024:10:28:45 +0000] "GET /style.css HTTP/1.1" 200 892 "-" "Mozilla/5.0"
EOF

# Set permissions on the log file
RUN chmod 0644 /home/user/logs/access.log

# Set working directory
WORKDIR /home/user
