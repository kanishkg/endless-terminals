Customer's rsync backup job at /home/user/backup/sync.sh has been silently succeeding but not actually transferring anything for about a week — runs nightly via cron, exits 0, logs look clean, but the destination dir /home/user/backup/dest is nearly empty while /home/user/backup/source has ~200 files. They swear nothing changed but "maybe IT updated something on the box last Tuesday?"

Need to figure out why it's not syncing and get it working. Customer wants the dest to mirror source after the script runs. Probably something dumb but I've stared at it for 20 min and I'm not seeing it.
