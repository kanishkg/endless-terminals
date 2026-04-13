FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest

# Create /home/user directory with appropriate permissions
RUN mkdir -p /home/user && chmod 0777 /home/user

# Create the pentest directory
RUN mkdir -p /home/user/pentest && chmod 0777 /home/user/pentest

# Create the scan_results.log file
RUN cat <<EOF > /home/user/pentest/scan_results.log
[2024-01-15 09:23:45] [INFO] [192.168.1.10] [SCAN-001] - Scan initiated on target host
[2024-01-15 09:23:47] [LOW] [192.168.1.10] [CVE-2023-1234] - Outdated SSH banner detected
[2024-01-15 09:23:52] [CRITICAL] [192.168.1.10] [CVE-2024-0012] - Remote code execution in web application
[2024-01-15 09:24:01] [MEDIUM] [192.168.1.10] [CVE-2023-5678] - SSL certificate expires in 30 days
[2024-01-15 09:24:15] [HIGH] [192.168.1.10] [CVE-2024-1086] - SQL injection vulnerability in login form
[2024-01-15 09:24:23] [INFO] [192.168.1.10] [SCAN-002] - Port scan completed
[2024-01-15 09:24:45] [CRITICAL] [192.168.1.15] [CVE-2024-21887] - Authentication bypass in admin panel
[2024-01-15 09:25:02] [LOW] [192.168.1.15] [CVE-2022-9999] - Information disclosure in error pages
[2024-01-15 09:25:18] [HIGH] [192.168.1.15] [CVE-2024-20931] - Privilege escalation via misconfigured sudo
[2024-01-15 09:25:34] [MEDIUM] [192.168.1.15] [CVE-2023-4567] - Cross-site scripting in search function
[2024-01-15 09:25:50] [HIGH] [192.168.1.20] [CVE-2024-23897] - Arbitrary file read vulnerability
[2024-01-15 09:26:05] [INFO] [192.168.1.20] [SCAN-003] - Service enumeration completed
[2024-01-15 09:26:22] [CRITICAL] [192.168.1.20] [CVE-2024-3400] - Command injection in firewall management
EOF

# Set permissions on the log file
RUN chmod 0644 /home/user/pentest/scan_results.log

# Set working directory
WORKDIR /home/user
