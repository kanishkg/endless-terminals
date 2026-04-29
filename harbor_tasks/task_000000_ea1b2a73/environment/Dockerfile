FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/backup-tools && chmod 0777 /home/user && chmod 0777 /home/user/backup-tools

RUN cat <<'EOF' > /home/user/backup-tools/requirements.txt
boto3==1.34.0
PyYAML==6.0.1
EOF

RUN chmod 644 /home/user/backup-tools/requirements.txt

RUN cat <<'EOF' > /home/user/backup-tools/sync_backups.py
#!/usr/bin/env python3
"""
Backup synchronization script.
Requires boto3 and PyYAML to be installed.
"""

import boto3
import yaml


def load_config(config_path):
    """Load configuration from a YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def sync_backups(config):
    """Sync backups to S3 based on configuration."""
    s3_client = boto3.client('s3')
    # Implementation would go here
    print("Backup sync initialized")
    return True


if __name__ == "__main__":
    print("Backup sync script ready")
EOF

RUN chmod 644 /home/user/backup-tools/sync_backups.py

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

USER user
WORKDIR /home/user

CMD ["/bin/bash"]
