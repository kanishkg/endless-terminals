FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/backups /home/user/restore

RUN cat <<EOF > /home/user/backups/users_20240115.csv
id,name,email,created_at
1,Alice Chen,alice@example.com,2023-06-12
2,Bob Martinez,bob@example.com,2023-08-24
3,Carol Smith,carol@example.com,2024-01-03
EOF

RUN chmod 0777 /home/user && \
    chmod 0777 /home/user/backups && \
    chmod 0777 /home/user/restore && \
    chmod 0644 /home/user/backups/users_20240115.csv

WORKDIR /home/user

CMD ["/bin/bash"]
