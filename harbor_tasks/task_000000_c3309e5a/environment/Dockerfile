FROM ubuntu:22.04

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with proper permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create builds directory
RUN mkdir -p /home/user/builds && chmod 0777 /home/user/builds

# Create the artifact_build.log file with the required content
RUN cat <<EOF > /home/user/builds/artifact_build.log
[2024-01-15 09:23:01] [SUCCESS] user-service - Build completed successfully
[2024-01-15 09:23:45] [FAILED] payment-gateway - Missing dependency: libssl
[2024-01-15 09:24:12] [SUCCESS] notification-service - Build completed successfully
[2024-01-15 09:25:33] [FAILED] auth-module - Compilation error in main.cpp
[2024-01-15 09:26:01] [SUCCESS] logging-service - Build completed successfully
[2024-01-15 09:27:15] [FAILED] database-connector - Connection timeout during tests
[2024-01-15 09:28:44] [SUCCESS] cache-manager - Build completed successfully
[2024-01-15 09:29:02] [SUCCESS] api-router - Build completed successfully
EOF

# Set proper permissions on the log file
RUN chmod 0666 /home/user/builds/artifact_build.log

# Set working directory
WORKDIR /home/user
