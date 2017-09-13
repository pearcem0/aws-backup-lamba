# aws-backup-lambda
* for reference - lambda scripts to run weekly backup snapshots and additional pruning of old snapshots
* All intended to be used with AWS Lambda

* backup.py (tags new snapshots)
* remove_old_backups.py (requires instances to be tagged approriately)
* remove-old-backups-no-tags.py (removes snapshots older than the specified number of days, regardless of tags)
