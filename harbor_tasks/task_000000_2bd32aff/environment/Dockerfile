FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV HOME=/home/user
ENV GNUPGHOME=/home/user/.gnupg

RUN apt-get update && apt-get install -y \
    gnupg \
    tar \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/evidence && chmod 0777 /home/user/evidence

RUN mkdir -p /home/user/.gnupg && chmod 700 /home/user/.gnupg

# Create sample pcap content
RUN mkdir -p /tmp/pcap_data/captures && \
    echo -e '\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00' > /tmp/pcap_data/captures/network_traffic.pcap && \
    echo "Additional packet data for analysis - captured 2024-01-15" >> /tmp/pcap_data/captures/network_traffic.pcap && \
    echo -e '\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\x00\x01\x00\x00\x00' > /tmp/pcap_data/captures/suspicious_activity.pcap && \
    echo "Suspicious traffic patterns detected in this capture" >> /tmp/pcap_data/captures/suspicious_activity.pcap

# Create the tarball
RUN cd /tmp/pcap_data && tar -czvf /tmp/packet_dump.tar.gz captures/

# Generate user key for decryption (no passphrase)
RUN gpg --batch --gen-key <<KEYEOF
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: User Key
Name-Email: user@localhost
Expire-Date: 0
%no-protection
%commit
KEYEOF

# Generate field team signing key (no passphrase)
RUN gpg --batch --gen-key <<KEYEOF2
Key-Type: RSA
Key-Length: 2048
Subkey-Type: RSA
Subkey-Length: 2048
Name-Real: Field Team
Name-Email: fieldteam@localhost
Expire-Date: 0
%no-protection
%commit
KEYEOF2

# Get the user key ID and encrypt the tarball
RUN USER_KEY_ID=$(gpg --list-keys --with-colons user@localhost | grep '^pub' | cut -d':' -f5) && \
    gpg --batch --yes --trust-model always -r "$USER_KEY_ID" --encrypt -o /home/user/evidence/packet_dump.tar.gz.gpg /tmp/packet_dump.tar.gz

# Create detached signature using field team key
RUN FIELD_KEY_ID=$(gpg --list-keys --with-colons fieldteam@localhost | grep '^pub' | cut -d':' -f5) && \
    gpg --batch --yes -u "$FIELD_KEY_ID" --detach-sign -o /home/user/evidence/packet_dump.tar.gz.sig /tmp/packet_dump.tar.gz

# Trust the field team key
RUN FIELD_KEY_FPR=$(gpg --list-keys --with-colons fieldteam@localhost | grep '^fpr' | head -1 | cut -d':' -f10) && \
    echo "$FIELD_KEY_FPR:6:" | gpg --import-ownertrust

# Set proper permissions
RUN chmod 644 /home/user/evidence/packet_dump.tar.gz.gpg && \
    chmod 644 /home/user/evidence/packet_dump.tar.gz.sig && \
    chmod -R 777 /home/user/.gnupg && \
    chmod 0777 /home/user/evidence

# Clean up temporary files
RUN rm -rf /tmp/pcap_data /tmp/packet_dump.tar.gz

# Set ownership for non-root access
RUN chown -R 1000:1000 /home/user

WORKDIR /home/user

CMD ["/bin/bash"]
