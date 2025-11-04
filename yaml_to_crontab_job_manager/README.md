# YAML to Crontab Job Manager

## Purpose
Convert human-friendly YAML schedules into system cron jobs and validate existing rules.

## Input / Output
- Input: `rules.yml` that describes commands, schedules, and metadata.
- Output: Installed cron entries or preview files for review.

## Key Dependencies
- `pyyaml`
- `python-crontab`

## Getting Started
1. Install dependencies: `pip install pyyaml python-crontab`.
2. Define a schema for the YAML file (command, schedule, owner, notifications).
3. Provide commands for `--preview`, `--apply`, and `--validate`.

## Implementation Notes
- Keep backups of the previous crontab before applying changes.
- Detect conflicts or overlapping schedules and warn the user.
- Offer hooks to send notifications after jobs run or fail.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
