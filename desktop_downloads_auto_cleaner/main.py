from __future__ import annotations

import argparse
import fnmatch
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import yaml


def load_rules(path: Path) -> list[Dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Rules file must contain a top-level list.")
    return data


def matches(rule: Dict[str, Any], path: Path) -> bool:
    pattern = rule.get("pattern", "*")
    if not fnmatch.fnmatch(path.name, pattern):
        return False
    age_days = rule.get("age_days")
    if age_days is not None:
        cutoff = datetime.now() - timedelta(days=int(age_days))
        if datetime.fromtimestamp(path.stat().st_mtime) > cutoff:
            return False
    max_size_mb = rule.get("max_size_mb")
    if max_size_mb is not None and path.stat().st_size > int(max_size_mb) * 1024 * 1024:
        return False
    return True


def apply_rule(rule: Dict[str, Any], path: Path, dry_run: bool) -> Optional[str]:
    action = rule.get("action", "move")
    if action == "delete":
        if dry_run:
            return f"[DRY] Delete {path}"
        path.unlink()
        return f"[DEL] {path}"
    destination = Path(rule.get("destination", path.parent))
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / path.name
    if dry_run:
        return f"[DRY] Move {path} -> {target}"
    shutil.move(str(path), str(target))
    return f"[MOVE] {path} -> {target}"


def process_directory(source: Path, rules: Iterable[Dict[str, Any]], dry_run: bool, recursive: bool) -> None:
    pattern = "**/*" if recursive else "*"
    for file_path in sorted(source.glob(pattern)):
        if not file_path.is_file():
            continue
        for rule in rules:
            if matches(rule, file_path):
                result = apply_rule(rule, file_path, dry_run)
                if result:
                    print(result)
                break


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean Downloads/Desktop folders using YAML rules.")
    parser.add_argument("source", type=Path, help="Directory to tidy.")
    parser.add_argument("--rules", type=Path, required=True, help="YAML file with cleanup rules.")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without changing files.")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.expanduser()
    if not source.is_dir():
        raise SystemExit(f"Source directory not found: {source}")
    rules = load_rules(args.rules.expanduser())
    process_directory(source, rules, args.dry_run, args.recursive)


if __name__ == "__main__":
    main()
