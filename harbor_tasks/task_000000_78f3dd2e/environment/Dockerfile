FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    dos2unix \
    coreutils \
    sed \
    gawk \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/backup-check/data/logs \
    && mkdir -p /home/user/backup-check/data/assets

RUN echo '{"app": "backup-system", "version": "2.1.0", "debug": false}' > /home/user/backup-check/data/config.json

RUN echo 'CREATE TABLE users (id INT, name VARCHAR(100));' > /home/user/backup-check/data/database.sql

RUN echo '[2024-01-15 10:30:00] Application started successfully' > /home/user/backup-check/data/logs/app.log

RUN echo '[2024-01-15 11:45:22] ERROR: Connection timeout' > /home/user/backup-check/data/logs/error.log

RUN echo 'FAKE_PNG_BINARY_DATA_FOR_LOGO_IMAGE_12345' > /home/user/backup-check/data/assets/logo.png

RUN printf 'body { margin: 0; padding: 0; }\n.container { width: 100%%; }' > /home/user/backup-check/data/assets/style.css

RUN echo 'Backup System README - Version 2.1' > /home/user/backup-check/data/readme.txt

RUN printf '<?xml version="1.0"?>\n<backup><date>2024-01-15</date></backup>' > /home/user/backup-check/data/backup_meta.xml

RUN cd /home/user/backup-check && \
    h1=$(sha256sum data/config.json | awk '{print $1}') && \
    h2=$(sha256sum data/database.sql | awk '{print $1}') && \
    h3=$(sha256sum data/logs/app.log | awk '{print $1}') && \
    h4=$(sha256sum data/logs/error.log | awk '{print $1}') && \
    h5=$(sha256sum data/assets/logo.png | awk '{print $1}') && \
    h6=$(sha256sum data/assets/style.css | awk '{print $1}') && \
    h7=$(sha256sum data/readme.txt | awk '{print $1}') && \
    h8=$(sha256sum data/backup_meta.xml | awk '{print $1}') && \
    printf '%s  data/config.json\r\n' "$h1" > /home/user/backup-check/manifest.txt && \
    printf '%s  data/database.sql\r\n' "$h2" >> /home/user/backup-check/manifest.txt && \
    printf '%s  data/logs/app.log\r\n' "$h3" >> /home/user/backup-check/manifest.txt && \
    printf '%s  data/logs/error.log\r\n' "$h4" >> /home/user/backup-check/manifest.txt && \
    printf '%s  data/assets/logo.png\r\n' "$h5" >> /home/user/backup-check/manifest.txt && \
    printf '%s  data/assets/style.css\r\n' "$h6" >> /home/user/backup-check/manifest.txt && \
    printf '%s  data/readme.txt\r\n' "$h7" >> /home/user/backup-check/manifest.txt && \
    printf '%s  data/backup_meta.xml\r\n' "$h8" >> /home/user/backup-check/manifest.txt

RUN cat > /home/user/backup-check/verify.sh << 'ENDSCRIPT'
#!/bin/bash

# Backup verification script
# Reads manifest.txt and verifies SHA256 checksums of files

MANIFEST_FILE="/home/user/backup-check/manifest.txt"
BASE_DIR="/home/user/backup-check"
ERRORS=0

echo "Starting backup verification..."
echo "Reading manifest: $MANIFEST_FILE"
echo ""

while IFS= read -r line || [ -n "$line" ]; do
    # Skip empty lines
    if [ -z "$line" ]; then
        continue
    fi

    # Extract expected hash (first 64 characters)
    expected=$(echo "$line" | cut -c1-64)

    # Extract file path (after two spaces following the hash)
    filepath=$(echo "$line" | cut -c67-)

    # Full path to file
    fullpath="$BASE_DIR/$filepath"

    # Check if file exists
    if [ ! -f "$fullpath" ]; then
        echo "MISSING: $filepath"
        ERRORS=$((ERRORS + 1))
        continue
    fi

    # Compute actual hash
    computed=$(sha256sum "$fullpath" | awk '{print $1}')

    # Compare hashes
    if [ "$expected" != "$computed" ]; then
        echo "MISMATCH: $filepath"
        echo "  Expected: $expected"
        echo "  Computed: $computed"
        ERRORS=$((ERRORS + 1))
    else
        echo "OK: $filepath"
    fi
done < "$MANIFEST_FILE"

echo ""
echo "Verification complete."

if [ $ERRORS -gt 0 ]; then
    echo "FAILED: $ERRORS file(s) failed verification."
    exit 1
else
    echo "SUCCESS: All files verified."
    exit 0
fi
ENDSCRIPT

RUN chmod +x /home/user/backup-check/verify.sh

RUN chmod -R 0777 /home/user/backup-check

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
