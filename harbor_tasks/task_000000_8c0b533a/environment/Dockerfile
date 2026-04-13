FROM ubuntu:22.04

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the data directory
RUN mkdir -p /home/user/data && chmod 0755 /home/user/data

# Create the users.json file with the required content
RUN cat <<EOF > /home/user/data/users.json
[
  {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "signup_date": "2024-01-15"},
  {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "signup_date": "2024-02-20"},
  {"id": 3, "name": "Carol Davis", "email": "carol@example.com", "signup_date": "2024-03-10"}
]
EOF

# Set permissions on the JSON file to be readable
RUN chmod 0644 /home/user/data/users.json

# Set working directory
WORKDIR /home/user
