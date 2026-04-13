FROM ubuntu:22.04

# Update and install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create the home directory for user with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Set working directory
WORKDIR /home/user
