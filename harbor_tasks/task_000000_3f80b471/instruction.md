I need to create a backup of our CI/CD pipeline configuration files before we do a major upgrade this weekend.

Here's what I need you to do:

1. There's a directory at `/home/user/ci-pipelines` containing our pipeline configuration files. Create a compressed tar archive of this entire directory and save it to `/home/user/backups/` with the filename `pipelines_backup.tar.gz`.

2. After creating the archive, generate a SHA256 checksum of the backup file and save it to `/home/user/backups/pipelines_backup.sha256`. The checksum file should contain only the hash value followed by two spaces and then the filename (just `pipelines_backup.tar.gz`, not the full path) - this is the standard format produced by sha256sum.

3. Create a simple backup log file at `/home/user/backups/backup.log` that contains exactly three lines:
   - Line 1: The text `BACKUP_DATE=` followed by today's date in YYYY-MM-DD format
   - Line 2: The text `ARCHIVE_FILE=pipelines_backup.tar.gz`
   - Line 3: The text `STATUS=SUCCESS`

Make sure the `/home/user/backups/` directory exists before creating files in it.
