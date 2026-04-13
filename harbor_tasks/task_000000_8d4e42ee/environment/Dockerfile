FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get update && apt-get install -y \
    gnupg \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the api_payload.json file with the required content
RUN cat > /home/user/api_payload.json << 'EOF'
{
  "api_version": "2.1",
  "endpoint": "/v2/transactions",
  "method": "POST",
  "test_id": "TX-20240115-001",
  "payload": {
    "amount": 150.00,
    "currency": "USD",
    "merchant_id": "MERCH-9876"
  }
}
EOF

# Set proper permissions on the payload file
RUN chmod 0666 /home/user/api_payload.json

# Set working directory
WORKDIR /home/user
