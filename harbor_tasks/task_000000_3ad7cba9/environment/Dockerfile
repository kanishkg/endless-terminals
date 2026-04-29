FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    openssl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/certs /home/user/report && \
    chmod 0777 /home/user && \
    chmod 0777 /home/user/certs && \
    chmod 0777 /home/user/report

RUN openssl req -x509 -newkey rsa:2048 -keyout /tmp/webapp.key -out /home/user/certs/webapp.pem \
    -days 365 -nodes -subj "/CN=webapp.example.com" \
    -set_serial 1 2>/dev/null || true

RUN rm -f /home/user/certs/webapp.pem

RUN cat > /tmp/gen_cert.sh << 'SCRIPT'
#!/bin/bash
openssl genrsa -out /tmp/webapp.key 2048 2>/dev/null

cat > /tmp/openssl.cnf << 'CNFEOF'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = webapp.example.com

[v3_ca]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
CNFEOF

# Create certificate with specific expiry date: Mar 15 09:30:45 2025 GMT
# We need to use faketime or set dates manually
# Using openssl with specific start and end dates

openssl req -new -key /tmp/webapp.key -out /tmp/webapp.csr -config /tmp/openssl.cnf 2>/dev/null

# Create a self-signed cert with specific validity
# notAfter = Mar 15 09:30:45 2025 GMT
openssl x509 -req -in /tmp/webapp.csr -signkey /tmp/webapp.key \
    -out /home/user/certs/webapp.pem \
    -days 3650 \
    -set_serial 1 2>/dev/null
SCRIPT
RUN chmod +x /tmp/gen_cert.sh && /tmp/gen_cert.sh

RUN rm -f /home/user/certs/webapp.pem

RUN apt-get update && apt-get install -y faketime && rm -rf /var/lib/apt/lists/*

RUN openssl genrsa -out /tmp/webapp.key 2048 2>/dev/null

RUN cat > /tmp/openssl.cnf << 'EOF'
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[req_distinguished_name]
CN = webapp.example.com

[v3_ca]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
EOF

RUN faketime "2024-03-15 09:30:45" openssl req -x509 -new -key /tmp/webapp.key \
    -out /home/user/certs/webapp.pem \
    -days 365 \
    -config /tmp/openssl.cnf \
    -set_serial 1 2>/dev/null

RUN chmod 0644 /home/user/certs/webapp.pem

RUN rm -f /tmp/webapp.key /tmp/webapp.csr /tmp/openssl.cnf /tmp/gen_cert.sh

RUN useradd -m -d /home/user -s /bin/bash user || true

RUN chown -R user:user /home/user

WORKDIR /home/user

USER user

CMD ["/bin/bash"]
