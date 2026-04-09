I need help creating a simple disk space monitoring script for our storage management workflow.

Please create a shell script at /home/user/scripts/disk_monitor.sh that does the following:

1. Gets the disk usage percentage for the root filesystem (/)
2. Writes a status report to /home/user/logs/disk_status.log

The log file should contain exactly one line in this specific format:
```
TIMESTAMP|FILESYSTEM|USAGE_PERCENT|STATUS
```

Where:
- TIMESTAMP is the current date and time in format: YYYY-MM-DD HH:MM:SS
- FILESYSTEM is the mount point (which should be /)
- USAGE_PERCENT is just the number (no % sign), representing the percentage of disk used
- STATUS should be "OK" if usage is below 80%, or "WARNING" if 80% or above

For example, a valid log entry would look like:
```
2024-01-15 14:30:22|/|45|OK
```

Make sure:
- The script is executable
- The /home/user/scripts directory exists
- The /home/user/logs directory exists
- After creating the script, run it once so the log file is populated

The script should use basic commands like df, date, and standard shell constructs. Keep it simple and straightforward.
