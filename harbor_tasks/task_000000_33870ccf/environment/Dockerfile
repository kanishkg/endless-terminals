FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    coreutils \
    findutils \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user && chmod 0777 /home/user

RUN mkdir -p /home/user/app_data/logs \
    && mkdir -p /home/user/app_data/uploads/images \
    && mkdir -p /home/user/app_data/uploads/videos \
    && mkdir -p /home/user/app_data/uploads/documents \
    && mkdir -p /home/user/app_data/cache \
    && mkdir -p /home/user/app_data/backups \
    && mkdir -p /home/user/app_data/config

# Create log files with sizes
RUN truncate -s 15M /home/user/app_data/logs/app.log \
    && truncate -s 8M /home/user/app_data/logs/error.log \
    && truncate -s 25M /home/user/app_data/logs/access.log \
    && truncate -s 3M /home/user/app_data/logs/debug.log

# Create upload files
RUN truncate -s 2M /home/user/app_data/uploads/images/photo1.jpg \
    && truncate -s 3M /home/user/app_data/uploads/images/photo2.jpg \
    && truncate -s 55M /home/user/app_data/uploads/images/banner.png \
    && truncate -s 120M /home/user/app_data/uploads/videos/demo.mp4 \
    && truncate -s 85M /home/user/app_data/uploads/videos/tutorial.mp4 \
    && truncate -s 5M /home/user/app_data/uploads/documents/report.pdf \
    && truncate -s 10M /home/user/app_data/uploads/documents/data.csv

# Create cache files
RUN truncate -s 45M /home/user/app_data/cache/session_cache.dat \
    && truncate -s 75M /home/user/app_data/cache/query_cache.dat \
    && truncate -s 1M /home/user/app_data/cache/temp.tmp

# Create backup files
RUN truncate -s 200M /home/user/app_data/backups/db_backup_old.sql \
    && truncate -s 180M /home/user/app_data/backups/db_backup_recent.sql \
    && truncate -s 500K /home/user/app_data/backups/config_backup.tar.gz

# Create config files
RUN truncate -s 2K /home/user/app_data/config/app.conf \
    && truncate -s 1K /home/user/app_data/config/database.yml \
    && truncate -s 3K /home/user/app_data/config/settings.json

# Set old modification times for specific files
RUN touch -d "10 days ago" /home/user/app_data/logs/app.log \
    && touch -d "15 days ago" /home/user/app_data/logs/error.log \
    && touch -d "20 days ago" /home/user/app_data/logs/debug.log \
    && touch -d "2 days ago" /home/user/app_data/logs/access.log \
    && touch -d "30 days ago" /home/user/app_data/backups/db_backup_old.sql \
    && touch -d "1 day ago" /home/user/app_data/backups/db_backup_recent.sql

# Set permissions for all files and directories
RUN chmod -R 0777 /home/user

WORKDIR /home/user
