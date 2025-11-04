from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import regex
from github import Github


@dataclass(slots=True)
class Rule:
    pattern: regex.Pattern[str]
    labels: List[str]


def load_rules(path: Path) -> List[Rule]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rules: List[Rule] = []
    for entry in data:
        labels = entry.get("labels", [])
        if not labels:
            continue
        pattern = regex.compile(entry["pattern"], regex.IGNORECASE | regex.MULTILINE)
        rules.append(Rule(pattern=pattern, labels=labels))
    return rules


def apply_rules_to_issue(issue, rules: Iterable[Rule]) -> List[str]:
    body = f"{issue.title}\n{issue.body or ''}"
    resulting: List[str] = []
    for rule in rules:
        if rule.pattern.search(body):
            resulting.extend(rule.labels)
    return list(sorted(set(resulting)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automatically label GitHub issues based on keyword rules.")
    parser.add_argument("--repo", required=True, help="Repository in the form owner/name.")
    parser.add_argument("--rules", type=Path, required=True, help="JSON file with pattern/labels definitions.")
    parser.add_argument("--token", help="GitHub token (falls back to GITHUB_TOKEN env var).")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying issues.")
    parser.add_argument("--state", choices=["open", "closed", "all"], default="open", help="Which issues to process.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GitHub token missing. Pass --token or set GITHUB_TOKEN.")

    rules = load_rules(args.rules.expanduser())
    gh = Github(token)
    repo = gh.get_repo(args.repo)
    issues = repo.get_issues(state=args.state)
    for issue in issues:
        proposed = apply_rules_to_issue(issue, rules)
        if not proposed:
            continue
        current_labels = {label.name for label in issue.labels}
        missing = [label for label in proposed if label not in current_labels]
        if not missing:
            continue
        if args.dry_run:
            print(f"[DRY] Would apply labels {missing} to issue #{issue.number}")
        else:
            issue.add_to_labels(*missing)
            print(f"[OK] Applied labels {missing} to issue #{issue.number}")


if __name__ == "__main__":
    main()
