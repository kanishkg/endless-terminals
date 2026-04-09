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

# Create the shared_utils repository
RUN mkdir -p /home/user/shared_utils && chmod 0777 /home/user/shared_utils

# Initialize git repo and create csv_reader.py in shared_utils
WORKDIR /home/user/shared_utils

RUN git init

RUN cat <<'EOF' > csv_reader.py
#!/usr/bin/env python3
import csv
def read_csv(filepath):
    with open(filepath) as f:
        return list(csv.reader(f))
EOF

RUN chmod 644 csv_reader.py

RUN git config user.email "test@test.com" && \
    git config user.name "Test User"

RUN git add csv_reader.py && \
    git commit -m "Initial commit with CSV reader"

# Set proper permissions for the shared_utils directory and all its contents
RUN chmod -R 0777 /home/user/shared_utils

# Set working directory back to /home/user
WORKDIR /home/user
