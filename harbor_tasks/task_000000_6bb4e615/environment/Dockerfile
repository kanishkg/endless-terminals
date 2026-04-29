FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    xxd \
    file \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/audit/data && chmod 0777 /home/user && chmod 0777 /home/user/audit && chmod 0777 /home/user/audit/data

RUN cd /home/user/audit/data && \
    echo "Regular text file content line 1" > file1.txt && \
    echo "More text content here" >> file1.txt && \
    echo "Binary looking data" > file2.bin && \
    dd if=/dev/urandom bs=256 count=1 2>/dev/null >> file2.bin && \
    echo "name,value,count" > data1.csv && \
    echo "alpha,100,5" >> data1.csv && \
    echo "beta,200,10" >> data1.csv && \
    echo '{"key": "value", "number": 42}' > settings.json && \
    echo "Another text file" > readme.txt && \
    dd if=/dev/urandom bs=512 count=1 2>/dev/null > random1.bin && \
    dd if=/dev/urandom bs=512 count=1 2>/dev/null > random2.bin && \
    echo "Log entry 1" > log1.txt && \
    echo "Log entry 2" >> log1.txt && \
    echo "id,name,score" > scores.csv && \
    echo "1,Alice,95" >> scores.csv && \
    echo "2,Bob,87" >> scores.csv && \
    echo '{"config": true, "debug": false}' > app.json && \
    echo "Documentation content" > docs.txt && \
    dd if=/dev/urandom bs=128 count=1 2>/dev/null > data.bin && \
    echo "timestamp,event" > events.csv && \
    echo "2024-01-01,start" >> events.csv && \
    echo '{"version": "1.0"}' > meta.json && \
    echo "Notes about the project" > project_notes.txt && \
    dd if=/dev/urandom bs=64 count=1 2>/dev/null > small.bin && \
    echo "x,y,z" > coords.csv && \
    echo "1,2,3" >> coords.csv && \
    echo '{"enabled": true}' > flags.json && \
    echo "Sample text data" > sample.txt && \
    dd if=/dev/urandom bs=256 count=1 2>/dev/null > chunk1.bin && \
    dd if=/dev/urandom bs=256 count=1 2>/dev/null > chunk2.bin && \
    echo "Header info" > header.txt && \
    echo "a,b,c,d" > matrix.csv && \
    echo "1,2,3,4" >> matrix.csv && \
    echo '{"items": [1,2,3]}' > list.json && \
    echo "Footer content" > footer.txt && \
    dd if=/dev/urandom bs=100 count=1 2>/dev/null > blob.bin && \
    echo "key,val" > pairs.csv && \
    echo "foo,bar" >> pairs.csv && \
    echo '{"status": "ok"}' > status.json && \
    echo "Misc text" > misc.txt && \
    dd if=/dev/urandom bs=200 count=1 2>/dev/null > payload.bin && \
    echo "col1,col2" > table.csv && \
    echo "x,y" >> table.csv && \
    echo '{"type": "data"}' > info.json && \
    echo "Archive notes" > archive.txt && \
    dd if=/dev/urandom bs=150 count=1 2>/dev/null > extra.bin && \
    echo "Final text" > final.txt

RUN printf 'date,revenue,expenses,profit\r\n2024-01-15,50000,35000,15000\r\n2024-02-15,55000,38000,17000\r\n2024-03-15,48000,32000,16000\r\n' > /home/user/audit/data/report_2024q1.csv

RUN printf '{\r\n  "database": {\r\n    "host": "localhost",\r\n    "port": 5432,\r\n    "name": "production"\r\n  },\r\n  "cache": {\r\n    "enabled": true,\r\n    "ttl": 3600\r\n  }\r\n}\r\n' > /home/user/audit/data/config.json

RUN printf 'Meeting Notes - Q1 Review\r\n==========================\r\n\r\nAttendees: Alice, Bob, Charlie\r\nDate: 2024-03-20\r\n\r\nAction items:\r\n- Review budget allocations\r\n- Update project timeline\r\n- Schedule follow-up meeting\r\n' > /home/user/audit/data/notes.txt

RUN cd /home/user/audit && sha256sum data/* > manifest.sha256

WORKDIR /home/user/audit

RUN cat << 'PYSCRIPT' > /home/user/audit/check_integrity.py
#!/usr/bin/env python3
"""
Integrity checker script for audit verification.
Reads manifest.sha256 and verifies each file's hash.
"""

import hashlib
import os
import sys

MANIFEST_FILE = "manifest.sha256"

def compute_hash(filepath):
    """Compute SHA256 hash of a file. 
    # handles encoding properly
    """
    hasher = hashlib.sha256()
    with open(filepath, 'r') as f:
        content = f.read()
        hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()

def load_manifest(manifest_path):
    """Load the manifest file and return a dict of path -> expected_hash."""
    manifest = {}
    with open(manifest_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Format: <hash>  <path> (two spaces)
            parts = line.split('  ', 1)
            if len(parts) == 2:
                expected_hash, filepath = parts
                manifest[filepath] = expected_hash.lower()
    return manifest

def verify_integrity():
    """Main verification routine."""
    if not os.path.exists(MANIFEST_FILE):
        print(f"ERROR: Manifest file '{MANIFEST_FILE}' not found")
        return False

    manifest = load_manifest(MANIFEST_FILE)

    if not manifest:
        print("ERROR: Manifest is empty")
        return False

    print(f"Verifying {len(manifest)} files...")
    print("-" * 50)

    failures = []
    successes = 0

    for filepath, expected_hash in sorted(manifest.items()):
        if not os.path.exists(filepath):
            print(f"FAIL: {filepath} - file not found")
            failures.append(filepath)
            continue

        try:
            actual_hash = compute_hash(filepath)
            if actual_hash == expected_hash:
                print(f"OK: {filepath}")
                successes += 1
            else:
                print(f"FAIL: {filepath} - hash mismatch")
                print(f"      expected: {expected_hash}")
                print(f"      actual:   {actual_hash}")
                failures.append(filepath)
        except Exception as e:
            print(f"FAIL: {filepath} - error: {e}")
            failures.append(filepath)

    print("-" * 50)
    print(f"Results: {successes} passed, {len(failures)} failed")

    if failures:
        print("\nFailed files:")
        for f in failures:
            print(f"  - {f}")
        return False

    print("\nAll files verified successfully!")
    return True

if __name__ == "__main__":
    success = verify_integrity()
    sys.exit(0 if success else 1)
PYSCRIPT

RUN chmod 0666 /home/user/audit/check_integrity.py && \
    chmod 0666 /home/user/audit/manifest.sha256 && \
    chmod 0666 /home/user/audit/data/*

WORKDIR /home/user

CMD ["/bin/bash"]
