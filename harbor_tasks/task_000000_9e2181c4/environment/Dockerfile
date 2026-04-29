FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

RUN pip3 install pytest pycryptodome

RUN mkdir -p /home/user/rotate && chmod 0777 /home/user && chmod 0777 /home/user/rotate

RUN dd if=/dev/urandom of=/home/user/rotate/old.key bs=32 count=1 2>/dev/null && \
    dd if=/dev/urandom of=/home/user/rotate/new.key bs=32 count=1 2>/dev/null && \
    chmod 644 /home/user/rotate/old.key /home/user/rotate/new.key

RUN python3 << 'PYSCRIPT'
import os
import struct
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

ROTATE_DIR = "/home/user/rotate"
VAULT_DUMP = os.path.join(ROTATE_DIR, "vault_dump.enc")
OLD_KEY_FILE = os.path.join(ROTATE_DIR, "old.key")

with open(OLD_KEY_FILE, "rb") as f:
    old_key = f.read()

key_id = hashlib.sha256(old_key).digest()

entry_count = 80000

with open(VAULT_DUMP, "wb") as f:
    f.write(b"VAULT1")
    f.write(struct.pack("<I", entry_count))
    f.write(key_id)

    for i in range(entry_count):
        plaintext = f"credential_{i:06d}:secret_value_{i:06d}".encode()

        nonce = get_random_bytes(12)
        cipher = AES.new(old_key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        ciphertext_with_tag = ciphertext + tag

        metadata = json.dumps({"id": i, "type": "credential", "created": "2024-01-01"}).encode()

        f.write(nonce)
        f.write(struct.pack("<I", len(ciphertext_with_tag)))
        f.write(ciphertext_with_tag)
        f.write(struct.pack("<H", len(metadata)))
        f.write(metadata)

print(f"Created vault dump with {entry_count} entries")
PYSCRIPT

RUN cat > /home/user/rotate/reencrypt.py << 'REENCRYPT_SCRIPT'
#!/usr/bin/env python3
"""
Re-encryption script for vault credentials.
Decrypts entries with old key and re-encrypts with new key.
"""

import os
import struct
import hashlib
from Crypto.Cipher import AES

ROTATE_DIR = "/home/user/rotate"
VAULT_DUMP = os.path.join(ROTATE_DIR, "vault_dump.enc")
OUTPUT_FILE = os.path.join(ROTATE_DIR, "vault_dump.new.enc")
OLD_KEY_FILE = os.path.join(ROTATE_DIR, "old.key")
NEW_KEY_FILE = os.path.join(ROTATE_DIR, "new.key")


def compute_offset_by_rereading_all_previous_entries(filepath, target_index):
    """
    Compute the byte offset of entry at target_index by reading all previous entries.
    This is intentionally inefficient - reads through all entries before target.
    """
    offset = 0
    with open(filepath, "rb") as f:
        f.seek(42)  # skip header
        for _ in range(target_index):
            nonce = f.read(12)
            if len(nonce) < 12:
                break
            ct_len = struct.unpack("<I", f.read(4))[0]
            f.read(ct_len)  # skip ciphertext
            meta_len = struct.unpack("<H", f.read(2))[0]
            f.read(meta_len)  # skip metadata
            offset = f.tell() - 42
    return offset


def read_one_entry(f):
    """Read a single entry from current file position."""
    nonce = f.read(12)
    if len(nonce) < 12:
        return None
    ct_len = struct.unpack("<I", f.read(4))[0]
    ciphertext_with_tag = f.read(ct_len)
    meta_len = struct.unpack("<H", f.read(2))[0]
    metadata = f.read(meta_len)
    return {
        "nonce": nonce,
        "ciphertext_with_tag": ciphertext_with_tag,
        "metadata": metadata
    }


def decrypt_entry(entry, key):
    """Decrypt an entry using AES-256-GCM."""
    ciphertext = entry["ciphertext_with_tag"][:-16]
    tag = entry["ciphertext_with_tag"][-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=entry["nonce"])
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext


def encrypt_entry(plaintext, metadata, key):
    """Encrypt plaintext and return formatted entry bytes."""
    from Crypto.Random import get_random_bytes
    nonce = get_random_bytes(12)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    ciphertext_with_tag = ciphertext + tag

    entry_bytes = nonce
    entry_bytes += struct.pack("<I", len(ciphertext_with_tag))
    entry_bytes += ciphertext_with_tag
    entry_bytes += struct.pack("<H", len(metadata))
    entry_bytes += metadata
    return entry_bytes


def reencrypt():
    """Main re-encryption function."""
    # Read header to get entry count
    with open(VAULT_DUMP, "rb") as f:
        header = f.read(42)
        magic = header[:6]
        entry_count = struct.unpack("<I", header[6:10])[0]
        old_key_id = header[10:42]

    if magic != b"VAULT1":
        raise ValueError("Invalid vault file magic")

    print(f"Processing {entry_count} entries...")

    # Read new key and compute new key_id for header
    new_key = open(NEW_KEY_FILE, "rb").read()
    new_key_id = hashlib.sha256(new_key).digest()

    # Write header to output file (will be opened fresh each time we append)
    with open(OUTPUT_FILE, "wb") as out:
        out.write(b"VAULT1")
        out.write(struct.pack("<I", entry_count))
        out.write(new_key_id)

    # Process each entry
    for i in range(entry_count):
        # BUG 1: Re-read entire file and seek to find entry position
        with open(VAULT_DUMP, "rb") as f:
            offset = compute_offset_by_rereading_all_previous_entries(VAULT_DUMP, i)
            f.seek(42 + offset)
            entry = read_one_entry(f)

        if entry is None:
            raise ValueError(f"Failed to read entry {i}")

        # BUG 2: Re-read key files for every entry
        old_key = open(OLD_KEY_FILE, "rb").read()
        new_key = open(NEW_KEY_FILE, "rb").read()

        # Decrypt with old key
        plaintext = decrypt_entry(entry, old_key)

        # Re-encrypt with new key
        new_entry_bytes = encrypt_entry(plaintext, entry["metadata"], new_key)

        # BUG 3: Open output file in append mode for every entry
        with open(OUTPUT_FILE, "ab") as out:
            out.write(new_entry_bytes)

        if (i + 1) % 10000 == 0:
            print(f"Processed {i + 1}/{entry_count} entries")

    print(f"Re-encryption complete. Output written to {OUTPUT_FILE}")


if __name__ == "__main__":
    reencrypt()
REENCRYPT_SCRIPT

RUN chmod 755 /home/user/rotate/reencrypt.py

RUN cat > /home/user/rotate/verify.py << 'VERIFY_SCRIPT'
#!/usr/bin/env python3
"""
Verification script for re-encrypted vault.
Decrypts random entries from both files and compares plaintext.
"""

import os
import struct
import hashlib
import sys
from Crypto.Cipher import AES

ROTATE_DIR = "/home/user/rotate"
VAULT_DUMP = os.path.join(ROTATE_DIR, "vault_dump.enc")
OUTPUT_FILE = os.path.join(ROTATE_DIR, "vault_dump.new.enc")
OLD_KEY_FILE = os.path.join(ROTATE_DIR, "old.key")
NEW_KEY_FILE = os.path.join(ROTATE_DIR, "new.key")

TEST_INDICES = [0, 100, 1000, 10000, 50000, 79999]


def read_entry_at_index(filepath, index):
    """Read entry at given index from vault file."""
    with open(filepath, "rb") as f:
        header = f.read(42)
        magic = header[:6]
        entry_count = struct.unpack("<I", header[6:10])[0]
        key_id = header[10:42]

        if magic != b"VAULT1":
            raise ValueError(f"Invalid magic in {filepath}")

        if index >= entry_count:
            raise ValueError(f"Index {index} out of range (count={entry_count})")

        # Seek to entry by reading through previous entries
        for _ in range(index):
            nonce = f.read(12)
            ct_len = struct.unpack("<I", f.read(4))[0]
            f.read(ct_len)
            meta_len = struct.unpack("<H", f.read(2))[0]
            f.read(meta_len)

        # Read target entry
        nonce = f.read(12)
        ct_len = struct.unpack("<I", f.read(4))[0]
        ciphertext_with_tag = f.read(ct_len)
        meta_len = struct.unpack("<H", f.read(2))[0]
        metadata = f.read(meta_len)

        return {
            "nonce": nonce,
            "ciphertext_with_tag": ciphertext_with_tag,
            "metadata": metadata,
            "key_id": key_id
        }


def decrypt_entry(entry, key):
    """Decrypt an entry using AES-256-GCM."""
    ciphertext = entry["ciphertext_with_tag"][:-16]
    tag = entry["ciphertext_with_tag"][-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=entry["nonce"])
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext


def verify():
    """Verify re-encrypted vault matches original."""
    if not os.path.exists(OUTPUT_FILE):
        print(f"ERROR: Output file {OUTPUT_FILE} does not exist")
        return False

    # Load keys
    with open(OLD_KEY_FILE, "rb") as f:
        old_key = f.read()
    with open(NEW_KEY_FILE, "rb") as f:
        new_key = f.read()

    # Verify key_id in output matches new key
    with open(OUTPUT_FILE, "rb") as f:
        header = f.read(42)
        output_key_id = header[10:42]

    expected_key_id = hashlib.sha256(new_key).digest()
    if output_key_id != expected_key_id:
        print("ERROR: Output file key_id does not match new key")
        return False

    # Verify entry count
    with open(VAULT_DUMP, "rb") as f:
        f.read(6)
        orig_count = struct.unpack("<I", f.read(4))[0]

    with open(OUTPUT_FILE, "rb") as f:
        f.read(6)
        new_count = struct.unpack("<I", f.read(4))[0]

    if orig_count != new_count:
        print(f"ERROR: Entry count mismatch: original={orig_count}, output={new_count}")
        return False

    # Verify file sizes are within 1%
    orig_size = os.path.getsize(VAULT_DUMP)
    new_size = os.path.getsize(OUTPUT_FILE)
    size_ratio = new_size / orig_size
    if not (0.99 <= size_ratio <= 1.01):
        print(f"ERROR: File size mismatch: original={orig_size}, output={new_size}, ratio={size_ratio:.4f}")
        return False

    # Verify specific entries
    print(f"Verifying entries at indices: {TEST_INDICES}")
    for idx in TEST_INDICES:
        try:
            orig_entry = read_entry_at_index(VAULT_DUMP, idx)
            new_entry = read_entry_at_index(OUTPUT_FILE, idx)

            orig_plaintext = decrypt_entry(orig_entry, old_key)
            new_plaintext = decrypt_entry(new_entry, new_key)

            if orig_plaintext != new_plaintext:
                print(f"ERROR: Plaintext mismatch at index {idx}")
                print(f"  Original: {orig_plaintext[:50]}...")
                print(f"  New:      {new_plaintext[:50]}...")
                return False

            if orig_entry["metadata"] != new_entry["metadata"]:
                print(f"ERROR: Metadata mismatch at index {idx}")
                return False

            print(f"  Entry {idx}: OK")
        except Exception as e:
            print(f"ERROR: Failed to verify entry {idx}: {e}")
            return False

    print("Verification PASSED")
    return True


if __name__ == "__main__":
    success = verify()
    sys.exit(0 if success else 1)
VERIFY_SCRIPT

RUN chmod 755 /home/user/rotate/verify.py

RUN chmod -R 755 /home/user/rotate && \
    chmod 644 /home/user/rotate/vault_dump.enc && \
    chmod 644 /home/user/rotate/old.key && \
    chmod 644 /home/user/rotate/new.key

WORKDIR /home/user

CMD ["/bin/bash"]
