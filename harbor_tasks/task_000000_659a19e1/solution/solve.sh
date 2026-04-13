#!/bin/bash
# Auto-generated solve script
set -e

mkdir -p /home/user/scripts /home/user/logs
cat > /home/user/scripts/disk_monitor.sh << 'EOF'
#!/bin/bash

# Get disk usage percentage for root filesystem (just the number)
USAGE_PERCENT=$(df / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')

# Get current timestamp in YYYY-MM-DD HH:MM:SS format
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Filesystem mount point
FILESYSTEM="/"

# Determine status based on usage
if [ "$USAGE_PERCENT" -ge 80 ]; then
    STATUS="WARNING"
else
    STATUS="OK"
fi

# Write to log file
echo "${TIMESTAMP}|${FILESYSTEM}|${USAGE_PERCENT}|${STATUS}" > /home/user/logs/disk_status.log
EOF
chmod +x /home/user/scripts/disk_monitor.sh
/home/user/scripts/disk_monitor.sh
cat /home/user/logs/disk_status.log
cat /home/user/scripts/disk_monitor.sh
ls -la /home/user/scripts/disk_monitor.sh
