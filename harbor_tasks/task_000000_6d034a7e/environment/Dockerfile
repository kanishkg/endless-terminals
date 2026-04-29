FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/ingest/packages && chmod -R 0777 /home/user/ingest

RUN echo "alpha package content version 1.2" > /tmp/alpha-content.txt && \
    tar -czf /home/user/ingest/packages/alpha-1.2.tar.gz -C /tmp alpha-content.txt && \
    rm /tmp/alpha-content.txt

RUN echo "beta package content version 3.0" > /tmp/beta-content.txt && \
    tar -czf /home/user/ingest/packages/beta-3.0.tar.gz -C /tmp beta-content.txt && \
    rm /tmp/beta-content.txt

RUN echo "gamma package content version 2.1" > /tmp/gamma-content.txt && \
    tar -czf /home/user/ingest/packages/gamma-2.1.tar.gz -C /tmp gamma-content.txt && \
    rm /tmp/gamma-content.txt

RUN echo "delta package content version 0.9" > /tmp/delta-content.txt && \
    tar -czf /home/user/ingest/packages/delta-0.9.tar.gz -C /tmp delta-content.txt && \
    rm /tmp/delta-content.txt

RUN echo "epsilon package content version 1.0" > /tmp/epsilon-content.txt && \
    tar -czf /home/user/ingest/packages/epsilon-1.0.tar.gz -C /tmp epsilon-content.txt && \
    rm /tmp/epsilon-content.txt

RUN cd /home/user/ingest/packages && \
    ALPHA_HASH=$(sha256sum alpha-1.2.tar.gz | cut -d' ' -f1) && \
    BETA_HASH=$(sha256sum beta-3.0.tar.gz | cut -d' ' -f1) && \
    GAMMA_HASH=$(sha256sum gamma-2.1.tar.gz | cut -d' ' -f1) && \
    DELTA_HASH=$(sha256sum delta-0.9.tar.gz | cut -d' ' -f1) && \
    EPSILON_HASH=$(sha256sum epsilon-1.0.tar.gz | cut -d' ' -f1) && \
    echo "${ALPHA_HASH}  alpha-1.2.tar.gz" > /home/user/ingest/checksums.sha256 && \
    echo "${BETA_HASH}  Beta-3.0.tar.gz" >> /home/user/ingest/checksums.sha256 && \
    echo "${GAMMA_HASH}  gamma-2.1.tar.gz" >> /home/user/ingest/checksums.sha256 && \
    echo "${DELTA_HASH}  Delta-0.9.tar.gz" >> /home/user/ingest/checksums.sha256 && \
    echo "${EPSILON_HASH}  Epsilon-1.0.tar.gz" >> /home/user/ingest/checksums.sha256

RUN cat <<'EOF' > /home/user/ingest/verify.sh
#!/bin/bash
cd /home/user/ingest/packages
if sha256sum -c ../checksums.sha256 > /dev/null 2>&1; then
    echo "all checksums valid"
    exit 0
else
    echo "checksum mismatch"
    exit 1
fi
EOF

RUN chmod +x /home/user/ingest/verify.sh

RUN chmod -R 0777 /home/user/ingest
