from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

import boto3


@dataclass(slots=True)
class FileRecord:
    path: Path
    relative: str
    digest: str
    size: int


def iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def compute_digest(path: Path, chunk_size: int = 1 << 20) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            sha.update(chunk)
    return sha.hexdigest()


def load_manifest(path: Path) -> Dict[str, Dict[str, str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def store_manifest(path: Path, data: Dict[str, Dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_records(root: Path) -> Dict[str, FileRecord]:
    records: Dict[str, FileRecord] = {}
    for file_path in iter_files(root):
        relative = file_path.relative_to(root).as_posix()
        digest = compute_digest(file_path)
        size = file_path.stat().st_size
        records[relative] = FileRecord(path=file_path, relative=relative, digest=digest, size=size)
    return records


def upload_changed(
    records: Dict[str, FileRecord],
    previous: Dict[str, Dict[str, str]],
    client,
    bucket: str,
    prefix: str,
) -> int:
    uploaded = 0
    for key, record in records.items():
        previous_digest = previous.get(key, {}).get("digest")
        if record.digest == previous_digest:
            continue
        s3_key = f"{prefix.rstrip('/')}/{key}" if prefix else key
        client.upload_file(str(record.path), bucket, s3_key)
        uploaded += 1
        print(f"[UPLOAD] {record.path} -> s3://{bucket}/{s3_key}")
    return uploaded


def main() -> None:
    parser = argparse.ArgumentParser(description="Incremental backup to S3 or MinIO.")
    parser.add_argument("source", type=Path, help="Directory to sync.")
    parser.add_argument("--bucket", required=True, help="Destination bucket.")
    parser.add_argument("--prefix", default="", help="Key prefix within the bucket.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path(".backup-manifest.json"),
        help="Local manifest path to track file hashes.",
    )
    parser.add_argument(
        "--endpoint",
        help="Optional custom endpoint URL for MinIO or S3-compatible storage.",
    )
    parser.add_argument(
        "--profile",
        help="AWS credential profile to use.",
    )
    args = parser.parse_args()

    source = args.source.expanduser()
    if not source.is_dir():
        raise SystemExit(f"Source directory not found: {source}")

    session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
    client = session.client(
        "s3",
        endpoint_url=args.endpoint,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    previous = load_manifest(args.manifest)
    records = build_records(source)
    uploaded = upload_changed(records, previous, client, args.bucket, args.prefix)
    snapshot = {
        key: {"digest": record.digest, "size": record.size, "timestamp": datetime.utcnow().isoformat()}
        for key, record in records.items()
    }
    store_manifest(args.manifest, snapshot)
    print(f"[INFO] Uploaded {uploaded} changed files.")


if __name__ == "__main__":
    main()
