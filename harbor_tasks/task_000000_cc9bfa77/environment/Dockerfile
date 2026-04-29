FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    lsb-release \
    python3 \
    python3-pip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-15 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

ENV PATH="/usr/lib/postgresql/15/bin:$PATH"

RUN mkdir -p /home/user/wal_recovery/primary_wal \
    && mkdir -p /home/user/wal_recovery/replica_wal \
    && chmod -R 0777 /home/user/wal_recovery

RUN mkdir -p /tmp/pgdata_init \
    && chown postgres:postgres /tmp/pgdata_init \
    && su - postgres -c "/usr/lib/postgresql/15/bin/initdb -D /tmp/pgdata_init" \
    && rm -rf /tmp/pgdata_init/pg_wal/*

RUN cd /tmp/pgdata_init \
    && tar -czvf /home/user/wal_recovery/base_backup.tar.gz . \
    && rm -rf /tmp/pgdata_init

RUN dd if=/dev/urandom of=/home/user/wal_recovery/primary_wal/000000010000000000000003 bs=1M count=16

RUN cp /home/user/wal_recovery/primary_wal/000000010000000000000003 /home/user/wal_recovery/replica_wal/000000010000000000000003

RUN dd if=/dev/urandom of=/home/user/wal_recovery/replica_wal/000000010000000000000004 bs=1M count=16

RUN cp /home/user/wal_recovery/replica_wal/000000010000000000000004 /home/user/wal_recovery/primary_wal/000000010000000000000004 \
    && dd if=/dev/zero of=/home/user/wal_recovery/primary_wal/000000010000000000000004 bs=1 count=512 seek=8192 conv=notrunc

RUN dd if=/dev/urandom of=/home/user/wal_recovery/primary_wal/000000010000000000000005 bs=1M count=16

RUN cp /home/user/wal_recovery/primary_wal/000000010000000000000005 /home/user/wal_recovery/replica_wal/000000010000000000000005 \
    && dd if=/home/user/wal_recovery/replica_wal/000000010000000000000004 of=/home/user/wal_recovery/replica_wal/000000010000000000000005 bs=1 count=512 conv=notrunc

RUN dd if=/dev/urandom of=/home/user/wal_recovery/primary_wal/000000010000000000000006 bs=1M count=8

RUN cat > /home/user/wal_recovery/manifest.json << 'EOFMANIFEST'
{"base_backup_lsn": "0/3000000", "crash_time": "2024-01-09T14:32:17Z", "primary_last_lsn": "0/6A00000", "replica_last_received_lsn": "0/5FFFFFF"}
EOFMANIFEST

RUN chmod -R 0777 /home/user/wal_recovery

RUN useradd -m -d /home/user -s /bin/bash user || true \
    && chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
