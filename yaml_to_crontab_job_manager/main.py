from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml
from crontab import CronTab


@dataclass(slots=True)
class CronRule:
    schedule: str
    command: str
    comment: str | None


def load_rules(path: Path) -> List[CronRule]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("rules.yml must contain a list of jobs.")
    rules: List[CronRule] = []
    for entry in data:
        schedule = entry.get("schedule")
        command = entry.get("command")
        if not schedule or not command:
            continue
        rules.append(CronRule(schedule=schedule, command=command, comment=entry.get("comment")))
    return rules


def preview_rules(rules: List[CronRule]) -> None:
    for rule in rules:
        comment = f" # {rule.comment}" if rule.comment else ""
        print(f"{rule.schedule} {rule.command}{comment}")


def apply_rules(rules: List[CronRule], user: str | None) -> None:
    cron = CronTab(user=user)
    for job in list(cron):
        if "yaml-cron" in (job.comment or ""):
            cron.remove(job)
    for rule in rules:
        comment = f"{rule.comment} | yaml-cron" if rule.comment else "yaml-cron"
        job = cron.new(command=rule.command, comment=comment)
        job.setall(rule.schedule)
    cron.write()
    print(f"[OK] Installed {len(rules)} cron job(s).")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert YAML rules to crontab entries.")
    parser.add_argument("--rules", type=Path, default=Path("rules.yml"), help="YAML configuration file.")
    parser.add_argument(
        "--mode",
        choices=["preview", "apply"],
        default="preview",
        help="Preview jobs or apply them to the crontab.",
    )
    parser.add_argument("--user", help="Target user for crontab operations.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rules = load_rules(args.rules.expanduser())
    if args.mode == "preview":
        preview_rules(rules)
    else:
        apply_rules(rules, args.user)


if __name__ == "__main__":
    main()
