FROM ubuntu:22.04

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create server_logs directory
RUN mkdir -p /home/user/server_logs && chmod 0777 /home/user/server_logs

# Create access_2024_01_15.log
RUN cat <<EOF > /home/user/server_logs/access_2024_01_15.log
192.168.1.100 - - [15/Jan/2024:10:15:32 +0000] "GET /index.html HTTP/1.1" 200 1234
192.168.1.101 - - [15/Jan/2024:10:16:45 +0000] "GET /missing-page.html HTTP/1.1" 404 512
192.168.1.102 - - [15/Jan/2024:10:17:22 +0000] "GET /about.html HTTP/1.1" 200 2048
192.168.1.103 - - [15/Jan/2024:10:18:01 +0000] "GET /old-link.html HTTP/1.1" 404 512
EOF

# Create access_2024_01_16.log
RUN cat <<EOF > /home/user/server_logs/access_2024_01_16.log
10.0.0.50 - - [16/Jan/2024:08:30:11 +0000] "GET /products HTTP/1.1" 200 4096
10.0.0.51 - - [16/Jan/2024:08:31:22 +0000] "GET /nonexistent HTTP/1.1" 404 512
10.0.0.52 - - [16/Jan/2024:08:32:15 +0000] "POST /api/login HTTP/1.1" 500 256
10.0.0.53 - - [16/Jan/2024:08:33:44 +0000] "GET /styles.css HTTP/1.1" 200 1024
EOF

# Create access_2024_01_17.log
RUN cat <<EOF > /home/user/server_logs/access_2024_01_17.log
172.16.0.25 - - [17/Jan/2024:14:20:00 +0000] "GET /dashboard HTTP/1.1" 200 8192
172.16.0.26 - - [17/Jan/2024:14:21:30 +0000] "GET /deleted-resource HTTP/1.1" 404 512
172.16.0.27 - - [17/Jan/2024:14:22:45 +0000] "GET /favicon.ico HTTP/1.1" 200 512
EOF

# Create notes.txt (non-.log file that should be ignored)
RUN cat <<EOF > /home/user/server_logs/notes.txt
Remember to check 404 errors weekly.
EOF

# Set permissions on all created files
RUN chmod 0666 /home/user/server_logs/*.log && chmod 0666 /home/user/server_logs/notes.txt

WORKDIR /home/user
