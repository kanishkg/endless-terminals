#!/bin/bash
# Auto-generated solve script
set -e

cat /home/user/builds/artifact_build.log
grep '\[FAILED\]' /home/user/builds/artifact_build.log | sed 's/.*\[FAILED\] \([^ ]*\) - .*/\1/' | sort > /tmp/failed_components.txt && count=$(wc -l < /tmp/failed_components.txt) && echo "FAILED_COMPONENTS_COUNT: $count" > /home/user/builds/failure_report.txt && echo "" >> /home/user/builds/failure_report.txt && cat /tmp/failed_components.txt >> /home/user/builds/failure_report.txt
cat /home/user/builds/failure_report.txt
