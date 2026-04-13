#!/bin/bash
# Auto-generated solve script
set -e

ls -la /home/user/app_data
du -sh /home/user/app_data/*/ 2>/dev/null | sort -hr | head -5
find /home/user/app_data -type f -size +50M -exec ls -lh {} \; 2>/dev/null | awk '{print $5, $9}'
find /home/user/app_data -name "*.log" -type f -mtime +7 2>/dev/null
find /home/user/app_data -type f -name "*.*" | sed 's/.*\.//' | sort | uniq -c | sort -rn
find /home/user/app_data -type d | wc -l
cat > /home/user/incident_report.txt << 'EOF'
=== DISK USAGE INCIDENT REPORT ===
Generated: $(date '+%Y-%m-%d %H:%M:%S')

--- TOP 5 LARGEST DIRECTORIES ---
381M /home/user/app_data/backups/
281M /home/user/app_data/uploads/
122M /home/user/app_data/cache/
52M /home/user/app_data/logs/
16K /home/user/app_data/config/

--- FILES LARGER THAN 50MB ---
200M /home/user/app_data/backups/db_backup_old.sql
180M /home/user/app_data/backups/db_backup_recent.sql
120M /home/user/app_data/uploads/videos/demo.mp4
85M /home/user/app_data/uploads/videos/tutorial.mp4
75M /home/user/app_data/cache/query_cache.dat
55M /home/user/app_data/uploads/images/banner.png

--- OLD LOG FILES (>7 days) ---
/home/user/app_data/logs/app.log
/home/user/app_data/logs/error.log
/home/user/app_data/logs/debug.log

--- FILE TYPE DISTRIBUTION ---
4 .log
2 .sql
2 .mp4
2 .jpg
2 .dat
1 .yml
1 .tmp
1 .png
1 .pdf
1 .json
1 .gz
1 .csv
1 .conf

--- SUMMARY ---
Total directories analyzed: 9
Large files found: 6
Old log files found: 3
=== END REPORT ===
EOF
cat /home/user/incident_report.txt
sed -i "s/\$(date '+%Y-%m-%d %H:%M:%S')/$(date '+%Y-%m-%d %H:%M:%S')/" /home/user/incident_report.txt
cat /home/user/incident_report.txt
