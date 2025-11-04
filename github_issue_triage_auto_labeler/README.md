# GitHub Issue Triage Auto Labeler

## Purpose
Label and group incoming GitHub issues automatically by looking at keywords, duplicates, and owners.

## Input / Output
- Input: Issues fetched from a GitHub repository.
- Output: Updated labels, duplicate suggestions, and summary reports.

## Key Dependencies
- `PyGithub`
- `regex`

## Getting Started
1. Create a personal access token with `repo` scope and store it securely.
2. Install dependencies: `pip install PyGithub`.
3. Build a triage ruleset (regex patterns, label mappings, component owners).
4. Run the bot manually or on a schedule using GitHub Actions or cron.

## Implementation Notes
- Avoid relabeling issues explicitly set by humans; respect manual overrides.
- Log all actions for transparency and future tuning.
- Consider a dry-run mode that only prints proposed label changes.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
