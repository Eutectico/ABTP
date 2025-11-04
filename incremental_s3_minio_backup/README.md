# Incremental S3 or MinIO Backup

## Purpose
Synchronize local folders to object storage with incremental uploads and retention policies.

## Input / Output
- Input: One or more directories that should be protected.
- Output: Versioned snapshots stored in an S3 or MinIO bucket.

## Key Dependencies
- `boto3`
- `hashlib`
- (optional) `rclone` wrapper or CLI

## Getting Started
1. Export credentials via environment variables or a config file (`AWS_ACCESS_KEY_ID`, etc.).
2. Install Python dependencies: `pip install boto3`.
3. Decide how to track file state (hashes, manifest database, etags).
4. Implement the CLI, for example: `python main.py --source <path> --bucket <name> --prefix <folder>`.

## Implementation Notes
- Store manifests locally to detect changed or deleted files quickly.
- Rotate old backups based on retention rules (keep-daily, weekly, monthly).
- Encrypt sensitive archives before uploading if compliance requires it.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
