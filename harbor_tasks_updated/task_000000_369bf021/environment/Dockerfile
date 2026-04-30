FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    coreutils \
    findutils \
    gawk \
    grep \
    sed \
    tar \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/admin && chmod 0777 /home/user/admin

RUN mkdir -p /var/userdata && chmod 0777 /var/userdata

RUN mkdir -p /home/users && chmod 0777 /home/users

RUN mkdir -p /backup/archived && chmod 0777 /backup/archived

RUN cat <<'EOF' > /home/user/admin/cleanup.sh
#!/bin/bash
THRESHOLD=90
find /var/userdata -name "last-login" -mtime +$THRESHOLD -print0 | \
    xargs -0 -I{} bash -c '
        user=$(basename $(dirname "{}"))
        tar -czf /backup/archived/${user}.tar.gz /home/users/${user}
        rm -rf /home/users/${user}
    '
EOF

RUN chmod 0755 /home/user/admin/cleanup.sh

RUN for user in alice bob carol dan eve frank grace henry ivan judy kim larry; do \
    mkdir -p /var/userdata/$user && chmod 0777 /var/userdata/$user; \
done

RUN echo "2025-01-28T10:15:00" > /var/userdata/alice/last-login && \
    echo "2024-09-15T14:00:00" > /var/userdata/bob/last-login && \
    echo "2025-01-15T14:30:00" > /var/userdata/carol/last-login && \
    echo "2024-12-20T09:00:00" > /var/userdata/dan/last-login && \
    echo "2024-08-20T11:30:00" > /var/userdata/eve/last-login && \
    echo "2025-01-30T16:45:00" > /var/userdata/frank/last-login && \
    echo "2024-11-25T11:00:00" > /var/userdata/grace/last-login && \
    echo "2024-10-01T08:45:00" > /var/userdata/henry/last-login && \
    echo "2025-01-10T13:20:00" > /var/userdata/ivan/last-login && \
    echo "2024-12-05T08:30:00" > /var/userdata/judy/last-login && \
    echo "2024-07-05T16:20:00" > /var/userdata/kim/last-login && \
    echo "2025-01-20T17:00:00" > /var/userdata/larry/last-login

RUN for user in alice bob carol dan eve frank grace henry ivan judy kim larry; do \
    chmod 0666 /var/userdata/$user/last-login; \
done

RUN touch -d "2024-09-25" /var/userdata/alice/last-login && \
    touch -d "2024-09-25" /var/userdata/bob/last-login && \
    touch -d "2024-09-25" /var/userdata/carol/last-login && \
    touch -d "2024-09-25" /var/userdata/dan/last-login && \
    touch -d "2024-09-25" /var/userdata/eve/last-login && \
    touch -d "2024-09-25" /var/userdata/frank/last-login && \
    touch -d "2024-09-25" /var/userdata/grace/last-login && \
    touch -d "2024-09-25" /var/userdata/henry/last-login && \
    touch -d "2024-09-25" /var/userdata/ivan/last-login && \
    touch -d "2024-09-25" /var/userdata/judy/last-login && \
    touch -d "2024-09-25" /var/userdata/kim/last-login && \
    touch -d "2024-09-25" /var/userdata/larry/last-login

RUN for user in alice bob carol dan eve frank grace henry ivan judy kim larry; do \
    mkdir -p /home/users/$user && \
    echo "Profile for $user" > /home/users/$user/.profile && \
    echo "Bashrc for $user" > /home/users/$user/.bashrc && \
    mkdir -p /home/users/$user/documents && \
    echo "Document 1 for $user" > /home/users/$user/documents/doc1.txt && \
    echo "Document 2 for $user" > /home/users/$user/documents/doc2.txt && \
    mkdir -p /home/users/$user/config && \
    echo "Config for $user" > /home/users/$user/config/settings.conf && \
    chmod -R 0755 /home/users/$user; \
done

RUN for user in alice bob carol dan eve frank grace henry ivan judy kim larry; do \
    tar -czf /backup/archived/${user}.tar.gz -C / home/users/${user}; \
done

RUN chmod 0666 /backup/archived/*.tar.gz

RUN rm -rf /home/users/*

WORKDIR /home/user

CMD ["/bin/bash"]
