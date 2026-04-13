#!/bin/bash
# Auto-generated solve script
set -e

mkdir -p /home/user/backups
tar -czvf /home/user/backups/pipelines_backup.tar.gz -C /home/user ci-pipelines
cd /home/user/backups && sha256sum pipelines_backup.tar.gz > pipelines_backup.sha256
echo -e "BACKUP_DATE=$(date +%Y-%m-%d)\nARCHIVE_FILE=pipelines_backup.tar.gz\nSTATUS=SUCCESS" > /home/user/backups/backup.log
cat /home/user/backups/pipelines_backup.sha256
cat /home/user/backups/backup.log
tar -tzvf /home/user/backups/pipelines_backup.tar.gz
