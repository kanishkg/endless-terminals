FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sudo \
    tar \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN groupadd -g 1001 backupd && \
    useradd -u 1001 -g 1001 -m -s /bin/bash backupd

RUN groupadd -f backup

RUN useradd -u 1000 -m -s /bin/bash user && \
    usermod -aG backup user && \
    usermod -aG backupd user

RUN mkdir -p /home/user/backup && \
    chown user:user /home/user && \
    chmod 0777 /home/user

RUN cat > /home/user/backup/verify_restore.sh << 'SCRIPTEOF'
#!/bin/bash
set -e
STAGING=/srv/backup-staging
RESTORE_DIR=/tmp/restore-verify
LOGFILE=/var/log/backup/verify.log

echo "[$(date)] Starting restore verification" >> "$LOGFILE"

mkdir -p "$RESTORE_DIR"

for archive in "$STAGING"/*.tar.gz; do
    [ -e "$archive" ] || continue
    name=$(basename "$archive" .tar.gz)
    echo "[$(date)] Verifying $name" >> "$LOGFILE"
    tar -tzf "$archive" > /dev/null
    tar -xzf "$archive" -C "$RESTORE_DIR"
    # Simulated integrity check
    if [ -f "$RESTORE_DIR/$name/manifest.sha256" ]; then
        cd "$RESTORE_DIR/$name"
        sha256sum -c manifest.sha256 >> "$LOGFILE" 2>&1
        cd - > /dev/null
    fi
done

rm -rf "$RESTORE_DIR"
echo "[$(date)] Restore verification complete" >> "$LOGFILE"
SCRIPTEOF

RUN chown user:backup /home/user/backup/verify_restore.sh && \
    chmod 750 /home/user/backup/verify_restore.sh

RUN chown user:backup /home/user/backup && \
    chmod 755 /home/user/backup

RUN mkdir -p /srv/backup-staging && \
    chown root:backup /srv/backup-staging && \
    chmod 2750 /srv/backup-staging

RUN mkdir -p /tmp/daily-build/daily-2024-01-15 && \
    echo "data file 1 content" > /tmp/daily-build/daily-2024-01-15/data1.txt && \
    echo "data file 2 content" > /tmp/daily-build/daily-2024-01-15/data2.txt && \
    cd /tmp/daily-build/daily-2024-01-15 && \
    sha256sum data1.txt data2.txt > manifest.sha256 && \
    cd /tmp/daily-build && \
    tar -czf /srv/backup-staging/daily-2024-01-15.tar.gz daily-2024-01-15 && \
    rm -rf /tmp/daily-build

RUN mkdir -p /tmp/weekly-build/weekly-2024-01-14 && \
    echo "weekly data file 1" > /tmp/weekly-build/weekly-2024-01-14/weekly1.txt && \
    echo "weekly data file 2" > /tmp/weekly-build/weekly-2024-01-14/weekly2.txt && \
    cd /tmp/weekly-build/weekly-2024-01-14 && \
    sha256sum weekly1.txt weekly2.txt > manifest.sha256 && \
    cd /tmp/weekly-build && \
    tar -czf /srv/backup-staging/weekly-2024-01-14.tar.gz weekly-2024-01-14 && \
    rm -rf /tmp/weekly-build

RUN chown root:backup /srv/backup-staging/*.tar.gz && \
    chmod 640 /srv/backup-staging/*.tar.gz

RUN mkdir -p /var/log/backup && \
    chown root:backup /var/log/backup && \
    chmod 2770 /var/log/backup

RUN touch /var/log/backup/verify.log && \
    chown user:backup /var/log/backup/verify.log && \
    chmod 660 /var/log/backup/verify.log

RUN echo "user ALL=(root) NOPASSWD: /usr/sbin/usermod, /usr/sbin/groupmod" > /etc/sudoers.d/backup-admin && \
    chmod 440 /etc/sudoers.d/backup-admin

RUN echo "user ALL=(backupd) NOPASSWD: ALL" >> /etc/sudoers.d/backup-admin

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
