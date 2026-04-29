FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN useradd -m -d /home/user -s /bin/bash user

WORKDIR /home/user

RUN mkdir -p /home/user/infra-configs && \
    cd /home/user/infra-configs && \
    git init && \
    git config user.email "admin@internal" && \
    git config user.name "Admin"

RUN cd /home/user/infra-configs && \
    echo "# Infrastructure Configs" > README.md && \
    git add README.md && \
    git commit -m "Initial commit"

RUN cat > /home/user/infra-configs/.git/hooks/pre-commit << 'HOOKEOF'
#!/bin/bash
# Pre-commit hook to block world-readable private keys

# Get list of staged files
staged_files=$(git diff --cached --name-only --diff-filter=ACM)

exit_code=0

for file in $staged_files; do
    # Check if file matches *.pem or *.key
    if [[ "$file" == *.pem ]] || [[ "$file" == *.key ]]; then
        # Check if file exists in working tree
        if [ -f "$file" ]; then
            # Get file permissions
            perms=$(stat -c "%a" "$file")
            # Check if world-readable (mode 0644 or looser)
            # 0644 = 644, check if group or other have read permissions beyond owner
            other_read=$((perms % 10))
            group_read=$(((perms / 10) % 10))

            # If other has read (4, 5, 6, 7) or group has read (4, 5, 6, 7)
            # and the overall mode is 644 or looser
            if [ "$perms" -ge 644 ]; then
                if [ $((other_read & 4)) -ne 0 ] || [ $((group_read & 4)) -ne 0 ]; then
                    echo "ERROR: $file has world-readable permissions ($perms). Private keys must not be world-readable."
                    exit_code=1
                fi
            fi
        fi
    fi
done

exit $exit_code
HOOKEOF

RUN chmod 755 /home/user/infra-configs/.git/hooks/pre-commit

RUN cd /home/user/infra-configs && \
    mkdir -p secrets && \
    echo "-----BEGIN RSA PRIVATE KEY-----" > secrets/deploy.key && \
    echo "MIIEpAIBAAKCAQEA0Z3VS5JJcds3xfn/ygWyF8PbnGy0AHB7MmjJH" >> secrets/deploy.key && \
    echo "-----END RSA PRIVATE KEY-----" >> secrets/deploy.key && \
    chmod 644 secrets/deploy.key && \
    git add secrets/deploy.key && \
    GIT_AUTHOR_NAME="jenkins-bot" GIT_AUTHOR_EMAIL="jenkins@internal" \
    GIT_COMMITTER_NAME="jenkins-bot" GIT_COMMITTER_EMAIL="jenkins@internal" \
    GIT_AUTHOR_DATE="$(date -d '3 days ago' --rfc-2822)" \
    GIT_COMMITTER_DATE="$(date -d '3 days ago' --rfc-2822)" \
    git commit --no-verify -m "auto-update keys"

RUN cd /home/user/infra-configs && \
    echo "# More config" >> README.md && \
    git add README.md && \
    git commit -m "Update readme"

RUN mkdir -p /home/user/jenkins-workspace

RUN cat > /home/user/jenkins-workspace/deploy.sh << 'SCRIPTEOF'
#!/bin/bash
# Jenkins deployment script
# This script auto-updates keys from the key management system

set -e

cd /home/user/infra-configs

# Fetch latest keys from key management
# (simulated - in real scenario this pulls from vault)
echo "Fetching keys..."

# Stage any key changes
git add -A secrets/

# Commit with --no-verify to skip slow pre-commit checks
# The CI pipeline validates separately
git commit --no-verify -m "auto-update keys" || true

echo "Keys updated successfully"
SCRIPTEOF

RUN chmod 444 /home/user/jenkins-workspace/deploy.sh && \
    chown root:root /home/user/jenkins-workspace/deploy.sh

RUN chown -R user:user /home/user/infra-configs && \
    chmod -R u+rwX /home/user/infra-configs

RUN chown user:user /home/user/jenkins-workspace && \
    chmod 755 /home/user/jenkins-workspace

USER user
WORKDIR /home/user
