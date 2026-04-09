FROM ubuntu:22.04

# Update and install required packages
RUN apt-get update && \
    apt-get install -y git python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with appropriate permissions
RUN mkdir -p /home/user && \
    chmod 0777 /home/user

# Set working directory
WORKDIR /home/user

# Configure git globally (needed for commits to work)
RUN git config --global user.email "user@example.com" && \
    git config --global user.name "User"
