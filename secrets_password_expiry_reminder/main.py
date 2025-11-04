from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

import schedule
import time

try:
    from cryptography.fernet import Fernet
except ImportError:  # pragma: no cover - optional dependency
    Fernet = None  # type: ignore

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


class SecretRecord:
    def __init__(self, name: str, owner: str, expires: datetime) -> None:
        self.name = name
        self.owner = owner
        self.expires = expires

    def days_until_expiry(self) -> int:
        return (self.expires.date() - datetime.utcnow().date()).days


def decrypt_file(path: Path, key_file: Optional[Path]) -> bytes:
    data = path.read_bytes()
    if not key_file:
        return data
    if Fernet is None:
        raise SystemExit("cryptography is required to decrypt the inventory.")
    key = key_file.read_bytes()
    fernet = Fernet(key)
    return fernet.decrypt(data)


def load_records(path: Path, key_file: Optional[Path]) -> List[SecretRecord]:
    payload = decrypt_file(path, key_file)
    if path.suffix.lower() in {".yml", ".yaml"}:
        if yaml is None:
            raise SystemExit("PyYAML is required to load YAML inventory files.")
        data = yaml.safe_load(payload.decode("utf-8"))
    elif path.suffix.lower() == ".json":
        data = json.loads(payload.decode("utf-8"))
    else:
        reader = csv.DictReader(payload.decode("utf-8").splitlines())
        data = list(reader)
    records: List[SecretRecord] = []
    for item in data:
        name = item.get("name")
        owner = item.get("owner", "unknown")
        exp = item.get("expires")
        if not name or not exp:
            continue
        expires = datetime.fromisoformat(exp)
        records.append(SecretRecord(name, owner, expires))
    return records


def notify(record: SecretRecord, lead_time: int) -> None:
    days_left = record.days_until_expiry()
    if days_left <= lead_time:
        print(
            f"[ALERT] {record.name} owned by {record.owner} expires in {days_left} day(s) "
            f"on {record.expires.date()}"
        )


def check_inventory(records: Iterable[SecretRecord], lead_time: int) -> None:
    for record in records:
        notify(record, lead_time)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remind owners about expiring secrets/passwords.")
    parser.add_argument("--inventory", type=Path, required=True, help="CSV/JSON/YAML inventory file.")
    parser.add_argument("--key-file", type=Path, help="Fernet key file to decrypt the inventory.")
    parser.add_argument("--lead-time", type=int, default=14, help="Days before expiry to alert.")
    parser.add_argument("--interval", type=int, default=1440, help="Check interval in minutes.")
    parser.add_argument("--run-once", action="store_true", help="Run a single check and exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_records(args.inventory.expanduser(), args.key_file.expanduser() if args.key_file else None)
    if args.run_once:
        check_inventory(records, args.lead_time)
        return
    schedule.every(args.interval).minutes.do(check_inventory, records=records, lead_time=args.lead_time)
    print(f"[INFO] Scheduler started. Checking every {args.interval} minutes.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped reminders.")


if __name__ == "__main__":
    main()
