FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tar \
    gzip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with proper permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the source directory structure
RUN mkdir -p /home/user/app_release_v2.3.1/lib

# Create the deployments directory
RUN mkdir -p /home/user/deployments

# Create main.py
RUN cat <<EOF > /home/user/app_release_v2.3.1/main.py
#!/usr/bin/env python3
# Main application entry point
print("App v2.3.1 starting...")
EOF

# Create config.json
RUN cat <<EOF > /home/user/app_release_v2.3.1/config.json
{"version": "2.3.1", "debug": false, "port": 8080}
EOF

# Create requirements.txt
RUN cat <<EOF > /home/user/app_release_v2.3.1/requirements.txt
flask==2.0.1
requests==2.26.0
EOF

# Create README.md
RUN cat <<EOF > /home/user/app_release_v2.3.1/README.md
# App Release v2.3.1
Deployment package for production servers.
EOF

# Create lib/utils.py
RUN cat <<EOF > /home/user/app_release_v2.3.1/lib/utils.py
# Utility functions
def helper(): pass
EOF

# Create lib/database.py
RUN cat <<EOF > /home/user/app_release_v2.3.1/lib/database.py
# Database connection module
def connect(): pass
EOF

# Set permissions for all created files and directories
RUN chmod -R 0755 /home/user/app_release_v2.3.1 && \
    chmod 0777 /home/user/deployments && \
    chmod 0644 /home/user/app_release_v2.3.1/main.py && \
    chmod 0644 /home/user/app_release_v2.3.1/config.json && \
    chmod 0644 /home/user/app_release_v2.3.1/requirements.txt && \
    chmod 0644 /home/user/app_release_v2.3.1/README.md && \
    chmod 0644 /home/user/app_release_v2.3.1/lib/utils.py && \
    chmod 0644 /home/user/app_release_v2.3.1/lib/database.py

# Set working directory
WORKDIR /home/user
