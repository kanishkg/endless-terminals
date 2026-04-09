As a database reliability engineer, I need to create a compressed backup archive of our PostgreSQL configuration files and write a verification log.

Here's what I need you to do:

1. There's a directory at `/home/user/postgres_config` containing several PostgreSQL configuration files. Create a gzipped tar archive of this entire directory and save it as `/home/user/backups/pg_config_backup.tar.gz`.

2. After creating the archive, generate a verification log file at `/home/user/backups/backup_verification.log` that contains:
   - The first line should be exactly: `BACKUP VERIFICATION REPORT`
   - The second line should be the MD5 checksum of the archive file in the format: `MD5: <checksum_value>` (where `<checksum_value>` is the actual 32-character MD5 hash)
   - The third line should show the file count inside the archive in the format: `FILE_COUNT: <number>` (where `<number>` is the actual count of files/directories listed in the archive)

Make sure the backup directory exists before creating the archive. The verification log must follow this exact format for our automated monitoring system to parse it correctly.
