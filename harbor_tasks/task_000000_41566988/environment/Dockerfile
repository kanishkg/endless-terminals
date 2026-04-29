FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    bash \
    make \
    iproute2 \
    coreutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/diagnostics/src && \
    mkdir -p /home/user/diagnostics/out && \
    chmod -R 0777 /home/user/diagnostics

RUN cat > /home/user/diagnostics/Makefile << 'MAKEFILEEOF'
.PHONY: collect clean

collect: out/report.txt

out/report.txt: out/sysinfo.raw out/netstat.parsed out/disk.raw
	python3 src/combine.py

out/sysinfo.raw:
	bash src/sysinfo.sh

out/netstat.parsed: out/netstat.raw
	python3 src/netstat_parser.py

out/netstat.raw:
	ss -tuln > out/netstat.raw

out/disk.raw:
	bash src/diskcheck.sh

clean:
	rm -f out/*
MAKEFILEEOF

RUN cat > /home/user/diagnostics/src/sysinfo.sh << 'SYSINFOOF'
#!/bin/bash
# Gather system information
echo "Hostname: $(hostname)" > out/sysinfo.raw
echo "Kernel: $(uname -r)" >> out/sysinfo.raw
echo "Uptime: $(uptime -p 2>/dev/null || echo 'unknown')" >> out/sysinfo.raw
echo "Date: $(date)" >> out/sysinfo.raw
SYSINFOOF

RUN cat > /home/user/diagnostics/src/netstat_parser.py << 'NETSTATEOF'
#!/usr/bin/env python3
"""
Parse netstat/ss output and produce a formatted summary.
"""
import os

# Debug code - forgot to remove this after testing
os.chdir('/tmp')

def parse_netstat():
    # Read from absolute path
    input_path = '/home/user/diagnostics/out/netstat.raw'
    output_path = 'out/netstat.parsed'  # relative path - will go to /tmp/out/

    with open(input_path, 'r') as f:
        lines = f.readlines()

    parsed_lines = []
    parsed_lines.append("Parsed Network Connections:")
    parsed_lines.append("-" * 40)

    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) >= 5:
            proto = parts[0]
            local_addr = parts[4]
            parsed_lines.append(f"  {proto}: {local_addr}")

    if len(parsed_lines) == 2:
        parsed_lines.append("  No active connections found")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        f.write('\n'.join(parsed_lines) + '\n')

if __name__ == '__main__':
    parse_netstat()
NETSTATEOF

RUN cat > /home/user/diagnostics/src/diskcheck.sh << 'DISKCHECKEOF'
#!/bin/bash
# Gather disk information

# Source environment configuration
source "$(dirname "$0")/../.env"

# Set default disk target (note: missing colon in parameter expansion)
DIAG_DISK_TARGET=${DIAG_DISK_TARGET-"/"}

# Get disk info for target
df -h $DIAG_DISK_TARGET | head -2 > out/disk.raw
DISKCHECKEOF

RUN cat > /home/user/diagnostics/src/combine.py << 'COMBINEEOF'
#!/usr/bin/env python3
"""
Combine all diagnostic outputs into a single report.
"""
import os
import sys

OUT_DIR = 'out'
REPORT_FILE = 'out/report.txt'

def read_file(filepath):
    """Read and return file contents."""
    with open(filepath, 'r') as f:
        return f.read().strip()

def validate_disk_raw(content):
    """Validate disk.raw has expected format (header + single fs line)."""
    lines = content.strip().split('\n')
    if len(lines) != 2:
        raise ValueError(f"disk.raw expected 2 lines (header + 1 filesystem), got {len(lines)} lines")
    return content

def main():
    report_sections = []

    # System Info Section
    sysinfo_path = os.path.join(OUT_DIR, 'sysinfo.raw')
    if os.path.exists(sysinfo_path):
        content = read_file(sysinfo_path)
        report_sections.append("=== SYSTEM INFO ===")
        report_sections.append(content)
        report_sections.append("")
    else:
        print(f"Warning: {sysinfo_path} not found", file=sys.stderr)

    # Network Section
    netstat_path = os.path.join(OUT_DIR, 'netstat.parsed')
    if os.path.exists(netstat_path):
        content = read_file(netstat_path)
        report_sections.append("=== NETWORK ===")
        report_sections.append(content)
        report_sections.append("")
    else:
        print(f"Warning: {netstat_path} not found", file=sys.stderr)

    # Disk Section
    disk_path = os.path.join(OUT_DIR, 'disk.raw')
    if os.path.exists(disk_path):
        content = read_file(disk_path)
        # Validate format
        validate_disk_raw(content)
        report_sections.append("=== DISK ===")
        report_sections.append(content)
        report_sections.append("")
    else:
        print(f"Warning: {disk_path} not found", file=sys.stderr)

    # Write final report
    with open(REPORT_FILE, 'w') as f:
        f.write('\n'.join(report_sections))

    print(f"Report generated: {REPORT_FILE}")

if __name__ == '__main__':
    main()
COMBINEEOF

RUN cat > /home/user/diagnostics/.env << 'ENVEOF'
# Diagnostic configuration
DIAG_DISK_TARGET=""
DIAG_VERBOSE=0
ENVEOF

RUN chmod +x /home/user/diagnostics/src/sysinfo.sh && \
    chmod +x /home/user/diagnostics/src/diskcheck.sh && \
    chmod +x /home/user/diagnostics/src/netstat_parser.py && \
    chmod +x /home/user/diagnostics/src/combine.py && \
    chmod 0666 /home/user/diagnostics/Makefile && \
    chmod 0666 /home/user/diagnostics/.env && \
    chmod 0666 /home/user/diagnostics/src/*.py && \
    chmod 0666 /home/user/diagnostics/src/*.sh && \
    chmod 0777 /home/user/diagnostics/out && \
    chmod 0777 /home/user/diagnostics/src && \
    chmod 0777 /home/user/diagnostics && \
    chown -R 1000:1000 /home/user

RUN mkdir -p /tmp/out && chmod 0777 /tmp/out

WORKDIR /home/user

USER 1000

CMD ["/bin/bash"]
