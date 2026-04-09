FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gzip \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create home directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the postgres_config directory
RUN mkdir -p /home/user/postgres_config && chmod 0777 /home/user/postgres_config

# Create the backups directory (empty, for the agent to use)
RUN mkdir -p /home/user/backups && chmod 0777 /home/user/backups

# Create postgresql.conf with content
RUN echo "max_connections = 100" > /home/user/postgres_config/postgresql.conf

# Create pg_hba.conf with content
RUN echo "host all all 0.0.0.0/0 md5" > /home/user/postgres_config/pg_hba.conf

# Create recovery.conf with content
RUN echo "standby_mode = 'on'" > /home/user/postgres_config/recovery.conf

# Set permissions on all created files
RUN chmod 0666 /home/user/postgres_config/postgresql.conf && \
    chmod 0666 /home/user/postgres_config/pg_hba.conf && \
    chmod 0666 /home/user/postgres_config/recovery.conf

# Set working directory
WORKDIR /home/user
