#!/bin/bash
# Auto-generated solve script
set -e

mkdir -p /home/user/analysis
grep -h " 404 " /home/user/server_logs/*.log > /home/user/analysis/404_errors.txt 2>/dev/null || touch /home/user/analysis/404_errors.txt
cat /home/user/analysis/404_errors.txt
