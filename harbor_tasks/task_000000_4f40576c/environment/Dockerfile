FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tar \
    zstd \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/archive_pipeline && chmod 0777 /home/user/archive_pipeline

RUN cat > /home/user/archive_pipeline/carch_format.md << 'EOF'
# CARCH Archive Format

The `.carch` format is a custom archive bundle that combines metadata with a compressed tar archive.

## Format Structure

```
[4 bytes]           magic: "CARC" (ASCII)
[4 bytes]           header_len: uint32 little-endian, length of JSON metadata
[header_len bytes]  JSON metadata
[remaining bytes]   tar+zstd compressed payload
```

## Field Details

### Magic (4 bytes)
- Fixed ASCII string: `CARC`
- Used to identify valid .carch files

### Header Length (4 bytes)
- Unsigned 32-bit integer in little-endian format
- Specifies the length of the JSON metadata section in bytes

### JSON Metadata (variable length)
- UTF-8 encoded JSON object
- Contains:
  - `source_path`: Original path that was archived
  - `timestamp`: Unix timestamp when archive was created
  - `file_count`: Number of files in the archive
  - `total_size`: Total uncompressed size in bytes

### Payload (remaining bytes)
- tar archive compressed with zstd
- Contains the directory tree from source_path
- Starts at offset: 4 (magic) + 4 (header_len) + header_len (metadata) = 8 + header_len

## Example

For a metadata JSON of 150 bytes:
- Bytes 0-3: "CARC"
- Bytes 4-7: 0x96 0x00 0x00 0x00 (150 in little-endian)
- Bytes 8-157: JSON metadata
- Bytes 158+: zstd-compressed tar data
EOF

RUN cat > /home/user/archive_pipeline/create.py << 'EOF'
#!/usr/bin/env python3
"""
create.py - Create a .carch archive bundle

Usage: python3 create.py <source_dir> <output.carch>
"""

import sys
import os
import json
import struct
import subprocess
import time


def count_files_and_size(directory):
    """Count files and total size in directory tree."""
    file_count = 0
    total_size = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            filepath = os.path.join(root, f)
            if os.path.isfile(filepath):
                file_count += 1
                total_size += os.path.getsize(filepath)
    return file_count, total_size


def create_archive(source_dir, output_path):
    """Create a .carch archive from source directory."""
    if not os.path.isdir(source_dir):
        raise ValueError(f"Source directory does not exist: {source_dir}")

    # Build metadata
    file_count, total_size = count_files_and_size(source_dir)
    metadata = {
        "source_path": os.path.abspath(source_dir),
        "timestamp": int(time.time()),
        "file_count": file_count,
        "total_size": total_size
    }

    metadata_bytes = json.dumps(metadata).encode('utf-8')
    header_len = len(metadata_bytes)

    with open(output_path, 'wb') as out:
        # Write magic
        out.write(b'CARC')

        # Write header length (uint32 little-endian)
        out.write(struct.pack('<I', header_len))

        # Write metadata
        out.write(metadata_bytes)

        # Create tar+zstd compressed payload and append
        # Use tar to archive, pipe through zstd
        tar_proc = subprocess.Popen(
            ['tar', '-c', '-C', source_dir, '.'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        zstd_proc = subprocess.Popen(
            ['zstd', '-c', '-'],
            stdin=tar_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        tar_proc.stdout.close()

        # Read compressed data and write to output
        compressed_data, zstd_err = zstd_proc.communicate()
        tar_proc.wait()

        if tar_proc.returncode != 0:
            raise RuntimeError(f"tar failed")
        if zstd_proc.returncode != 0:
            raise RuntimeError(f"zstd failed: {zstd_err.decode()}")

        out.write(compressed_data)

    print(f"Created archive: {output_path}")
    print(f"  Files: {file_count}")
    print(f"  Original size: {total_size} bytes")
    print(f"  Archive size: {os.path.getsize(output_path)} bytes")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <source_dir> <output.carch>")
        sys.exit(1)

    create_archive(sys.argv[1], sys.argv[2])
EOF

RUN cat > /home/user/archive_pipeline/extract.py << 'EOF'
#!/usr/bin/env python3
"""
extract.py - Extract a .carch archive bundle

Usage: python3 extract.py <archive.carch> <dest_dir>
"""

import sys
import os
import json
import struct
import subprocess


def extract_archive(carch_path, dest_dir):
    """Extract a .carch archive to destination directory."""
    if not os.path.isfile(carch_path):
        raise ValueError(f"Archive does not exist: {carch_path}")

    # Create destination directory if needed
    os.makedirs(dest_dir, exist_ok=True)

    with open(carch_path, 'rb') as f:
        # Read and verify magic
        magic = f.read(4)
        if magic != b'CARC':
            raise ValueError(f"Invalid archive: bad magic bytes")

        # Read header length
        header_len = struct.unpack('<I', f.read(4))[0]

        # Read and parse metadata
        metadata_bytes = f.read(header_len)
        metadata = json.loads(metadata_bytes.decode('utf-8'))

        print(f"Extracting archive...")
        print(f"  Source: {metadata.get('source_path', 'unknown')}")
        print(f"  Files: {metadata.get('file_count', 'unknown')}")
        print(f"  Original size: {metadata.get('total_size', 'unknown')} bytes")

        # Calculate payload offset and seek to it
        # The payload starts after magic + header_len field + metadata
        payload_offset = header_len
        f.seek(payload_offset)

        # Read the compressed payload
        payload = f.read()

        # Decompress with zstd and extract with tar
        zstd_proc = subprocess.Popen(
            ['zstd', '-d', '-c'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        tar_proc = subprocess.Popen(
            ['tar', '-x', '-C', dest_dir],
            stdin=zstd_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        zstd_proc.stdout.close()

        # Send payload to zstd
        zstd_proc.stdin.write(payload)
        zstd_proc.stdin.close()

        # Wait for processes to complete
        tar_out, tar_err = tar_proc.communicate()
        zstd_proc.wait()

        # Note: We don't strictly check return codes because zstd/tar
        # can sometimes return non-zero even on partial success

        print(f"Extracted to: {dest_dir}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <archive.carch> <dest_dir>")
        sys.exit(1)

    extract_archive(sys.argv[1], sys.argv[2])
EOF

RUN cat > /home/user/archive_pipeline/run_test.sh << 'EOFSCRIPT'
#!/bin/bash
set -e

TEST_SRC="/tmp/test_src"
TEST_DST="/tmp/test_dst"
TEST_ARCHIVE="/tmp/test.carch"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Clean up any previous test artifacts
rm -rf "$TEST_SRC" "$TEST_DST" "$TEST_ARCHIVE"

echo "=== Creating test source tree ==="
mkdir -p "$TEST_SRC"

# Create various subdirectories
mkdir -p "$TEST_SRC/subdir1/nested"
mkdir -p "$TEST_SRC/subdir2"
mkdir -p "$TEST_SRC/empty_dir"
mkdir -p "$TEST_SRC/deep/path/to/files"

# Create files with random content of varying sizes
# Small files
for i in $(seq 1 10); do
    dd if=/dev/urandom bs=100 count=1 2>/dev/null | base64 > "$TEST_SRC/small_$i.txt"
done

# Medium files
for i in $(seq 1 15); do
    dd if=/dev/urandom bs=1024 count=$((RANDOM % 50 + 10)) 2>/dev/null > "$TEST_SRC/subdir1/medium_$i.bin"
done

# Larger files
for i in $(seq 1 5); do
    dd if=/dev/urandom bs=1024 count=$((RANDOM % 500 + 500)) 2>/dev/null > "$TEST_SRC/subdir2/large_$i.dat"
done

# Files in nested directories
for i in $(seq 1 10); do
    dd if=/dev/urandom bs=512 count=$((RANDOM % 100 + 1)) 2>/dev/null > "$TEST_SRC/subdir1/nested/nested_$i.bin"
done

# Files in deep path
for i in $(seq 1 8); do
    dd if=/dev/urandom bs=2048 count=$((RANDOM % 200 + 50)) 2>/dev/null > "$TEST_SRC/deep/path/to/files/deep_$i.dat"
done

# Some empty files
touch "$TEST_SRC/empty1.txt"
touch "$TEST_SRC/subdir1/empty2.txt"

# Text files with specific content
echo "This is a test file with known content" > "$TEST_SRC/known_content.txt"
for i in $(seq 1 100); do
    echo "Line $i: $(dd if=/dev/urandom bs=50 count=1 2>/dev/null | base64)" >> "$TEST_SRC/multiline.txt"
done

FILE_COUNT=$(find "$TEST_SRC" -type f | wc -l)
echo "Created $FILE_COUNT files in test source"

echo ""
echo "=== Computing source checksums ==="
SRC_CHECKSUMS=$(cd "$TEST_SRC" && find . -type f -exec sha256sum {} \; | sort)

echo ""
echo "=== Creating archive ==="
python3 "$SCRIPT_DIR/create.py" "$TEST_SRC" "$TEST_ARCHIVE"

echo ""
echo "=== Extracting archive ==="
python3 "$SCRIPT_DIR/extract.py" "$TEST_ARCHIVE" "$TEST_DST"

echo ""
echo "=== Computing destination checksums ==="
DST_CHECKSUMS=$(cd "$TEST_DST" && find . -type f -exec sha256sum {} \; | sort)

echo ""
echo "=== Comparing checksums ==="

# Compare checksums
if [ "$SRC_CHECKSUMS" = "$DST_CHECKSUMS" ]; then
    echo "SUCCESS: All file checksums match!"
    EXTRACTED_COUNT=$(find "$TEST_DST" -type f | wc -l)
    echo "Verified $EXTRACTED_COUNT files"
    exit 0
else
    echo "FAILURE: Checksum mismatch detected!"
    echo ""
    echo "Source checksums:"
    echo "$SRC_CHECKSUMS" | head -20
    echo "..."
    echo ""
    echo "Destination checksums:"
    echo "$DST_CHECKSUMS" | head -20
    echo "..."
    echo ""

    # Show specific differences
    echo "Differences:"
    diff <(echo "$SRC_CHECKSUMS") <(echo "$DST_CHECKSUMS") | head -30 || true

    exit 1
fi
EOFSCRIPT

RUN chmod +x /home/user/archive_pipeline/run_test.sh && \
    chmod +x /home/user/archive_pipeline/create.py && \
    chmod +x /home/user/archive_pipeline/extract.py && \
    chmod 0666 /home/user/archive_pipeline/extract.py && \
    chmod 0644 /home/user/archive_pipeline/carch_format.md

RUN chmod -R 0777 /home/user/archive_pipeline

RUN useradd -m -s /bin/bash -d /home/user user || true

RUN chown -R user:user /home/user

USER user
WORKDIR /home/user
