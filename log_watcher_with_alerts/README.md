# Log Watcher with Alerts

## Purpose
Monitor application or system logs in real time and send notifications when error patterns appear.

## Input / Output
- Input: Log files, journalctl streams, or stdout pipelines.
- Output: Alerts delivered via email, Slack, webhook, or other channels.

## Key Dependencies
- `watchdog`
- `re`
- `requests`

## Getting Started
1. Install dependencies: `pip install watchdog requests`.
2. Define regex patterns or severity filters to watch for.
3. Configure alert transports (SMTP, Slack webhook, etc.) in a settings file.

## Implementation Notes
- Debounce repeated alerts to avoid noise during outages.
- Persist the last processed position so the watcher survives restarts.
- Consider adding a health endpoint that confirms the watcher is running.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
