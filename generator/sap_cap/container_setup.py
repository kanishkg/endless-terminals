"""
SAP CAP container setup and Apptainer definition generation.
"""
from __future__ import annotations


# Base Apptainer definition for SAP CAP environment
CAP_CONTAINER_DEF_TEMPLATE = """Bootstrap: docker
From: ubuntu:22.04

%post
    # Update and install essential tools
    apt-get update
    apt-get install -y curl wget git sqlite3 build-essential python3 python3-pip

    # Install Node.js 20 LTS
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs

    # Install SAP CDS Development Kit
    npm install -g @sap/cds-dk

    # Create user
    useradd -m -s /bin/bash user
    chown -R user:user /home/user

    # Verify installations
    node --version
    npm --version
    cds version

    # Clean up
    apt-get clean
    rm -rf /var/lib/apt/lists/*

%environment
    export HOME=/home/user
    export PATH=/usr/local/bin:$PATH

%runscript
    cd /home/user
    exec "$@"
"""


def get_cap_container_def() -> str:
    """
    Get the Apptainer definition file content for SAP CAP environment.

    Returns:
        String containing the complete Apptainer definition
    """
    return CAP_CONTAINER_DEF_TEMPLATE


def get_cap_dockerfile() -> str:
    """
    Get Dockerfile for SAP CAP environment (alternative to Apptainer).

    Returns:
        String containing the complete Dockerfile
    """
    return """FROM ubuntu:22.04

# Install essential tools
RUN apt-get update && apt-get install -y \\
    curl \\
    wget \\
    git \\
    sqlite3 \\
    build-essential \\
    python3 \\
    python3-pip \\
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \\
    apt-get install -y nodejs

# Install SAP CDS Development Kit
RUN npm install -g @sap/cds-dk

# Create user
RUN useradd -m -s /bin/bash user

# Set working directory
WORKDIR /home/user

# Set user
USER user

# Verify installations
RUN node --version && npm --version && cds version

# Default command
CMD ["/bin/bash"]
"""