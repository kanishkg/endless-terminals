FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    rsync \
    bash \
    grep \
    diffutils \
    coreutils \
    findutils \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/backup/source /home/user/backup/dest

RUN for i in $(seq 1 60); do \
        echo "Log entry $i - $(date -d "-$((i % 30)) days" +%Y-%m-%d) - System status normal" > /home/user/backup/source/log_$i.txt; \
    done && \
    for i in $(seq 1 50); do \
        echo "Data record $i,value_$((i * 7)),$(date -d "-$((i % 25)) days" +%Y-%m-%d),active" > /home/user/backup/source/data_$i.log; \
    done && \
    for i in $(seq 1 55); do \
        dd if=/dev/urandom bs=1024 count=$((i % 20 + 1)) 2>/dev/null | base64 > /home/user/backup/source/binary_$i.dat; \
    done && \
    for i in $(seq 1 52); do \
        echo "id,name,value,timestamp" > /home/user/backup/source/report_$i.csv; \
        for j in $(seq 1 10); do \
            echo "$j,item_$j,$((j * i)),$(date -d "-$((i % 20)) days" +%Y-%m-%d)" >> /home/user/backup/source/report_$i.csv; \
        done; \
    done

RUN echo "Old file 1 content" > /home/user/backup/dest/old_file1.txt && \
    echo "Old file 2 content" > /home/user/backup/dest/old_file2.txt && \
    echo "Old file 3 content" > /home/user/backup/dest/old_file3.txt

RUN cat > /home/user/backup/sync.sh << 'EOF'
#!/bin/bash
LOGFILE="/home/user/backup/sync.log"
rsync -av --exclude-from=/home/user/backup/exclude.lst /home/user/backup/source/ /home/user/backup/dest/ >> "$LOGFILE" 2>&1
exit 0
EOF

RUN chmod +x /home/user/backup/sync.sh

RUN cat > /home/user/backup/exclude.lst << 'EOF'
# Updated patterns 2024-01-09
*
!.gitkeep
EOF

RUN cat > /home/user/backup/sync.log << 'EOF'
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
sending incremental file list

sent 43 bytes  received 12 bytes  110.00 bytes/sec
total size is 0  speedup is 0.00
EOF

RUN chown -R 1000:1000 /home/user/backup && \
    chmod -R 0755 /home/user/backup && \
    chmod 0666 /home/user/backup/sync.log && \
    chmod 0666 /home/user/backup/exclude.lst && \
    chmod 0777 /home/user/backup/source && \
    chmod 0777 /home/user/backup/dest && \
    chmod 0755 /home/user/backup/sync.sh

RUN useradd -u 1000 -d /home/user -s /bin/bash user || true

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
