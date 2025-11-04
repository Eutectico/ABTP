from __future__ import annotations

import argparse
import difflib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import requests
import schedule


@dataclass(slots=True)
class Target:
    url: str
    expected_status: int
    save_content: bool


def load_targets(path: Path) -> list[Target]:
    data = json.loads(path.read_text(encoding="utf-8"))
    targets: list[Target] = []
    for entry in data:
        targets.append(
            Target(
                url=entry["url"],
                expected_status=int(entry.get("expected_status", 200)),
                save_content=bool(entry.get("content_diff", True)),
            )
        )
    return targets


def check_target(target: Target, state_dir: Path) -> None:
    try:
        response = requests.get(target.url, timeout=10)
    except requests.RequestException as exc:
        print(f"[FAIL] {target.url} unreachable: {exc}")
        return
    if response.status_code != target.expected_status:
        print(f"[WARN] {target.url} returned {response.status_code}, expected {target.expected_status}")
    else:
        print(f"[OK] {target.url} status {response.status_code}")
    if target.save_content and response.ok:
        state_dir.mkdir(parents=True, exist_ok=True)
        slug = target.url.replace("://", "_").replace("/", "_")
        content_path = state_dir / f"{slug}.txt"
        new_content = response.text
        if content_path.exists():
            old_content = content_path.read_text(encoding="utf-8")
            if old_content != new_content:
                diff = difflib.unified_diff(
                    old_content.splitlines(), new_content.splitlines(), lineterm="", fromfile="old", tofile="new"
                )
                print(f"[DIFF] Changes detected for {target.url}")
                for line in list(diff)[:50]:
                    print(line)
        content_path.write_text(new_content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monitor website/API uptime and content changes.")
    parser.add_argument("--config", type=Path, required=True, help="JSON config with url definitions.")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in minutes.")
    parser.add_argument("--state-dir", type=Path, default=Path(".monitor-state"), help="Directory to store snapshots.")
    parser.add_argument("--run-once", action="store_true", help="Execute a single check and exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    targets = load_targets(args.config.expanduser())
    if args.run_once:
        for target in targets:
            check_target(target, args.state_dir.expanduser())
        return
    schedule.every(args.interval).minutes.do(
        lambda: [check_target(target, args.state_dir.expanduser()) for target in targets]
    )
    print(f"[INFO] Monitoring {len(targets)} targets every {args.interval} minutes.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Monitor stopped.")


if __name__ == "__main__":
    main()
