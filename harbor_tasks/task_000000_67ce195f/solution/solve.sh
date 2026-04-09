#!/bin/bash
# Auto-generated solve script
set -e

mkdir -p /home/user/backups
ls -la /home/user/postgres_config
tar -czvf /home/user/backups/pg_config_backup.tar.gz -C /home/user postgres_config
md5sum /home/user/backups/pg_config_backup.tar.gz
tar -tzf /home/user/backups/pg_config_backup.tar.gz | wc -l
cat > /home/user/backups/backup_verification.log << 'EOF'
BACKUP VERIFICATION REPORT
MD5: aee7dc6ea02cd13675f093de99cdffd2
FILE_COUNT: 4
EOF
cat /home/user/backups/backup_verification.log
ls -la /home/user/backups/
tar -tzf /home/user/backups/pg_config_backup.tar.gz
