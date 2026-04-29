FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

RUN pip3 install --upgrade pip setuptools wheel pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/myapp/src/myapp

RUN cat > /home/user/myapp/pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "myapp"
version = "0.1.0"
dependencies = [
    "requests>=2.28.0",
    "boto3>=1.26.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "moto>=4.0.0",
    "requests-mock>=1.10.0",
    "urllib3>=2.0.0",
]

[tool.setuptools.packages.find]
where = ["src"]
EOF

RUN cat > /home/user/myapp/src/myapp/__init__.py << 'EOF'
__version__ = "0.1.0"
EOF

RUN cat > /home/user/myapp/src/myapp/core.py << 'EOF'
"""Core functionality for myapp."""

import requests


def main():
    """Main entry point for the application."""
    return "ok"


def fetch_data(url):
    """Fetch data from a URL using requests."""
    response = requests.get(url)
    return response.json()
EOF

RUN touch /home/user/myapp/constraints.txt

RUN echo "-e .[dev]" > /home/user/myapp/requirements-dev.txt

RUN chmod -R 0777 /home/user/myapp

WORKDIR /home/user

CMD ["/bin/bash"]
