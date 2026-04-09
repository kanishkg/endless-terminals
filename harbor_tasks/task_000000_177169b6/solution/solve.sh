#!/bin/bash
# Auto-generated solve script
set -e

cat /home/user/pentest/scan_results.log
grep -E '\[CRITICAL\]|\[HIGH\]' /home/user/pentest/scan_results.log > /home/user/pentest/critical_high_vulns.txt
cat /home/user/pentest/critical_high_vulns.txt
critical_count=$(grep -c '\[CRITICAL\]' /home/user/pentest/scan_results.log) && high_count=$(grep -c '\[HIGH\]' /home/user/pentest/scan_results.log) && printf "CRITICAL: %s\nHIGH: %s\n" "$critical_count" "$high_count" > /home/user/pentest/vuln_summary.txt
cat /home/user/pentest/vuln_summary.txt
wc -l /home/user/pentest/vuln_summary.txt && cat -A /home/user/pentest/vuln_summary.txt
