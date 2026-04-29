FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    bash \
    tar \
    gzip \
    coreutils \
    diffutils \
    locales \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN locale-gen en_US.UTF-8 && \
    locale-gen C.UTF-8 && \
    update-locale

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/scripts && chmod 0777 /home/user/scripts

RUN mkdir -p /home/user/test_payload && chmod 0777 /home/user/test_payload

RUN cat > /home/user/scripts/archive.sh << 'EOF'
#!/bin/bash
set -e
INPUT_DIR="$1"
OUTPUT_DIR="$2"
mkdir -p "$OUTPUT_DIR"
tar cf - "$INPUT_DIR" | gzip -9 | split -b 50M - "$OUTPUT_DIR/chunk_"
EOF

RUN chmod +x /home/user/scripts/archive.sh

RUN cat > /home/user/scripts/restore.sh << 'EOF'
#!/bin/bash
set -e
CHUNKS_DIR="$1"
OUTPUT_DIR="$2"
mkdir -p "$OUTPUT_DIR"
cat "$CHUNKS_DIR"/chunk_* | gunzip | tar xf - -C "$OUTPUT_DIR"
EOF

RUN chmod +x /home/user/scripts/restore.sh

RUN cp /usr/bin/ls /home/user/test_payload/binary_ls && \
    cp /usr/bin/cat /home/user/test_payload/binary_cat && \
    cp /usr/bin/grep /home/user/test_payload/binary_grep && \
    cp /usr/bin/sed /home/user/test_payload/binary_sed && \
    cp /usr/bin/awk /home/user/test_payload/binary_awk && \
    cp /usr/bin/sort /home/user/test_payload/binary_sort && \
    cp /usr/bin/tar /home/user/test_payload/binary_tar && \
    cp /usr/bin/gzip /home/user/test_payload/binary_gzip && \
    cp /usr/bin/bash /home/user/test_payload/binary_bash && \
    cp /usr/bin/diff /home/user/test_payload/binary_diff

RUN dd if=/dev/urandom of=/home/user/test_payload/random_data_1.bin bs=1M count=30 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/random_data_2.bin bs=1M count=30 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/random_data_3.bin bs=1M count=30 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/random_data_4.bin bs=1M count=30 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/random_data_5.bin bs=1M count=30 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/random_data_6.bin bs=1M count=30 2>/dev/null

RUN for i in $(seq 1 10); do \
        echo "=== Log file $i ===" > /home/user/test_payload/log_$i.txt && \
        for j in $(seq 1 1000); do \
            echo "$(date) - Log entry $j - Random data: $(head -c 100 /dev/urandom | base64)" >> /home/user/test_payload/log_$i.txt; \
        done; \
    done

RUN cat > /home/user/test_payload/sample_image.png << 'PNGEOF'
PNG fake image data for testing purposes
This is not a real PNG but simulates binary content
PNGEOF

RUN dd if=/dev/urandom of=/home/user/test_payload/image_data_1.png bs=1K count=500 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/image_data_2.png bs=1K count=500 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/test_payload/image_data_3.png bs=1K count=500 2>/dev/null

RUN echo "C" > /home/user/.collate_setting && chmod 0666 /home/user/.collate_setting

RUN echo "0" > /home/user/.collate_counter && chmod 0666 /home/user/.collate_counter

RUN cat > /home/user/.bashrc << 'BASHRCEOF'
# Locale rotation mechanism for testing
COUNTER_FILE="/home/user/.collate_counter"
SETTING_FILE="/home/user/.collate_setting"

if [ -f "$COUNTER_FILE" ]; then
    COUNT=$(cat "$COUNTER_FILE" 2>/dev/null || echo "0")
    COUNT=$((COUNT + 1))
    echo "$COUNT" > "$COUNTER_FILE" 2>/dev/null || true

    if [ $((COUNT % 2)) -eq 0 ]; then
        echo "C" > "$SETTING_FILE" 2>/dev/null || true
        export LC_COLLATE="C"
    else
        echo "en_US.UTF-8" > "$SETTING_FILE" 2>/dev/null || true
        export LC_COLLATE="en_US.UTF-8"
    fi
else
    echo "1" > "$COUNTER_FILE" 2>/dev/null || true
    echo "en_US.UTF-8" > "$SETTING_FILE" 2>/dev/null || true
    export LC_COLLATE="en_US.UTF-8"
fi
BASHRCEOF

RUN chmod 0666 /home/user/.bashrc

RUN chmod -R 0777 /home/user/test_payload && \
    chmod -R 0777 /home/user/scripts

WORKDIR /home/user

CMD ["/bin/bash"]
