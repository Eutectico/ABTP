from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import click


@dataclass(slots=True)
class RenamePlan:
    source: Path
    target: Path


def discover_files(source: Path, recursive: bool) -> Iterable[Path]:
    if not source.exists():
        raise click.BadParameter(f"Source path does not exist: {source}")
    if source.is_file():
        yield source
        return
    pattern = "**/*" if recursive else "*"
    for item in sorted(source.glob(pattern)):
        if item.is_file():
            yield item


def load_tag_mapping(tag_file: Optional[Path]) -> dict[str, str]:
    if not tag_file:
        return {}
    if tag_file.suffix.lower() == ".json":
        return json.loads(tag_file.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    with tag_file.open("r", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = row.get("pattern")
            value = row.get("replacement")
            if key and value:
                mapping[key] = value
    return mapping


def build_plan(
    files: Iterable[Path],
    pattern: Optional[re.Pattern[str]],
    replace: str,
    tag_map: dict[str, str],
) -> list[RenamePlan]:
    plan: list[RenamePlan] = []
    for file_path in files:
        stem = file_path.stem
        replacement = None
        if pattern:
            replacement = pattern.sub(replace, stem)
        if not replacement or replacement == stem:
            for tag_pattern, tag_replacement in tag_map.items():
                if re.search(tag_pattern, stem):
                    replacement = re.sub(tag_pattern, tag_replacement, stem)
                    break
        if not replacement or replacement == stem:
            continue
        target = file_path.with_name(f"{replacement}{file_path.suffix}")
        if target.exists() and target != file_path:
            raise click.ClickException(
                f"Target file already exists: {target} (for source {file_path})"
            )
        plan.append(RenamePlan(source=file_path, target=target))
    return plan


def apply_plan(plan: Iterable[RenamePlan], dry_run: bool, log_file: Optional[Path]) -> None:
    rows = []
    for item in plan:
        click.echo(f"{'[DRY]' if dry_run else '[REN]'} {item.source} -> {item.target}")
        rows.append((str(item.source), str(item.target)))
        if not dry_run:
            item.source.rename(item.target)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["source", "target"])
            writer.writerows(rows)


@click.command()
@click.option(
    "--source",
    "-s",
    type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=True),
    default=".",
    help="File or directory to rename.",
)
@click.option("--pattern", "-p", help="Regular expression applied to the filename stem.")
@click.option("--replace", "-r", default="", help="Replacement string for regex matches.")
@click.option(
    "--tag-file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    help="Optional CSV/JSON mapping with 'pattern' and 'replacement' columns.",
)
@click.option("--recursive/--no-recursive", default=False, help="Walk subdirectories.")
@click.option("--dry-run/--no-dry-run", default=True, help="Preview changes without touching files.")
@click.option(
    "--log-file",
    type=click.Path(path_type=Path, dir_okay=False),
    help="Write rename actions to a CSV log.",
)
def main(
    source: Path,
    pattern: Optional[str],
    replace: str,
    tag_file: Optional[Path],
    recursive: bool,
    dry_run: bool,
    log_file: Optional[Path],
) -> None:
    """Bulk rename helper that combines regex rules with optional tag mappings."""
    compiled = re.compile(pattern) if pattern else None
    tag_map = load_tag_mapping(tag_file)
    files = list(discover_files(source, recursive))
    plan = build_plan(files, compiled, replace, tag_map)
    if not plan:
        click.echo("No files matched the provided rules.")
        return
    apply_plan(plan, dry_run, log_file)


if __name__ == "__main__":
    main()
