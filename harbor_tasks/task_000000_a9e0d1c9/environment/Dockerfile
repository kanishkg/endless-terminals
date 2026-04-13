FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install required packages
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (LTS version) from NodeSource
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install pytest via pip3
RUN pip3 install pytest

# Install additional dependencies that Puppeteer/Playwright might need
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Set working directory
WORKDIR /home/user

# Create a non-root user for testing (optional but good practice)
RUN useradd -m -d /home/user -s /bin/bash user || true

# Ensure /home/user has correct permissions
RUN chown -R user:user /home/user 2>/dev/null || chmod -R 0777 /home/user

# Set environment variables for npm to work without root
ENV NPM_CONFIG_PREFIX=/home/user/.npm-global
ENV PATH=/home/user/.npm-global/bin:$PATH

# Make sure the npm global directory can be created
RUN mkdir -p /home/user/.npm-global && chmod 0777 /home/user/.npm-global

# Ensure npm cache directory is writable
RUN mkdir -p /home/user/.npm && chmod 0777 /home/user/.npm
