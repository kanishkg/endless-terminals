FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Set up the monitoring-project git repository
WORKDIR /home/user/monitoring-project

RUN git init && \
    git config user.email "test@example.com" && \
    git config user.name "Test User"

# Create README.md and make initial commit
RUN echo "# Monitoring Project" > README.md && \
    git add README.md && \
    git commit -m "Initial commit"

# Ensure proper permissions for the entire project directory
RUN chmod -R 0777 /home/user/monitoring-project

# Set working directory back to home
WORKDIR /home/user
