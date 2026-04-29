FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/user

RUN apt-get update && apt-get install -y \
    openssh-client \
    rsync \
    python3 \
    python3-pip \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/.ssh && chmod 0700 /home/user/.ssh

RUN ssh-keygen -t rsa -b 2048 -f /home/user/.ssh/etl_warehouse -N "" -q

RUN chmod 0644 /home/user/.ssh/etl_warehouse

RUN cat > /home/user/.ssh/config << 'EOF'
Host warehouse
    HostName 10.0.50.12
    User etl_service
    IdentityFile ~/.ssh/etl_warehouse
    StrictHostKeyChecking no
EOF

RUN chmod 0644 /home/user/.ssh/config

RUN mkdir -p /home/user/etl/staging

RUN cat > /home/user/etl/sync_to_warehouse.sh << 'EOF'
#!/bin/bash
set -e
rsync -avz -e "ssh -i ~/.ssh/etl_warehouse" /home/user/etl/staging/ warehouse:/data/incoming/
EOF

RUN chmod +x /home/user/etl/sync_to_warehouse.sh

RUN echo "order_id,customer_id,amount,date" > /home/user/etl/staging/orders_20240115.csv && \
    echo "1001,C001,150.00,2024-01-15" >> /home/user/etl/staging/orders_20240115.csv && \
    echo "1002,C002,275.50,2024-01-15" >> /home/user/etl/staging/orders_20240115.csv

RUN echo "order_id,customer_id,amount,date" > /home/user/etl/staging/orders_20240116.csv && \
    echo "1003,C003,89.99,2024-01-16" >> /home/user/etl/staging/orders_20240116.csv && \
    echo "1004,C001,320.00,2024-01-16" >> /home/user/etl/staging/orders_20240116.csv

RUN echo "order_id,customer_id,amount,date" > /home/user/etl/staging/orders_20240117.csv && \
    echo "1005,C004,199.99,2024-01-17" >> /home/user/etl/staging/orders_20240117.csv && \
    echo "1006,C002,450.00,2024-01-17" >> /home/user/etl/staging/orders_20240117.csv

RUN cat > /usr/local/bin/ssh-permission-check << 'EOF'
#!/bin/bash
# Simulates SSH private key permission validation
KEY="$HOME/.ssh/etl_warehouse"
PERMS=$(stat -c %a "$KEY" 2>/dev/null)
if [[ "$PERMS" =~ ^[0-7]00$ ]]; then
    echo "Key permissions OK"
    exit 0
else
    echo "Permissions $PERMS for '$KEY' are too open."
    echo "It is required that your private key files are NOT accessible by others."
    exit 1
fi
EOF

RUN chmod +x /usr/local/bin/ssh-permission-check

RUN cat > /home/user/etl/test_ssh.sh << 'EOF'
#!/bin/bash
/usr/local/bin/ssh-permission-check
EOF

RUN chmod +x /home/user/etl/test_ssh.sh

RUN mv /usr/bin/ssh /usr/bin/ssh.real

RUN cat > /usr/bin/ssh << 'EOFWRAPPER'
#!/bin/bash
# SSH wrapper that checks key permissions before proceeding

# Parse arguments to find -i option
KEY_FILE=""
ARGS=("$@")
for ((i=0; i<${#ARGS[@]}; i++)); do
    if [[ "${ARGS[i]}" == "-i" ]]; then
        KEY_FILE="${ARGS[i+1]}"
        # Expand ~ to $HOME
        KEY_FILE="${KEY_FILE/#\~/$HOME}"
        break
    fi
done

# If no -i specified, check default identity files
if [[ -z "$KEY_FILE" ]]; then
    for default_key in "$HOME/.ssh/id_rsa" "$HOME/.ssh/id_dsa" "$HOME/.ssh/id_ecdsa" "$HOME/.ssh/id_ed25519"; do
        if [[ -f "$default_key" ]]; then
            KEY_FILE="$default_key"
            break
        fi
    done
fi

# Check key permissions if key file exists
if [[ -n "$KEY_FILE" && -f "$KEY_FILE" ]]; then
    PERMS=$(stat -c %a "$KEY_FILE" 2>/dev/null)
    if [[ ! "$PERMS" =~ ^[0-7]00$ ]]; then
        echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
        echo "@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @"
        echo "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
        echo "Permissions 0$PERMS for '$KEY_FILE' are too open."
        echo "It is required that your private key files are NOT accessible by others."
        echo "This private key will be ignored."
        echo "Load key \"$KEY_FILE\": bad permissions"
        exit 255
    fi
fi

# Call real ssh
exec /usr/bin/ssh.real "$@"
EOFWRAPPER

RUN chmod +x /usr/bin/ssh

RUN chown -R 1000:1000 /home/user && \
    chmod 0777 /home/user && \
    chmod 0755 /home/user/.ssh && \
    chmod 0644 /home/user/.ssh/etl_warehouse && \
    chmod 0644 /home/user/.ssh/etl_warehouse.pub && \
    chmod 0644 /home/user/.ssh/config && \
    chmod -R 0755 /home/user/etl

USER 1000

WORKDIR /home/user

CMD ["/bin/bash"]
