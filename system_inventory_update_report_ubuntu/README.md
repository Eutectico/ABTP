# System Inventory and Update Report (Ubuntu)

## Purpose
Collect package, kernel, and service information from Ubuntu hosts and highlight pending updates.

## Input / Output
- Input: Commands executed on the target system (`dpkg`, `apt`, `systemctl`, etc.).
- Output: JSON or HTML reports that summarize system state and update recommendations.

## Key Dependencies
- `subprocess`
- `jinja2`

## Getting Started
1. Plan the data collectors (apt list, snap list, kernel info, service status).
2. Install templating dependency: `pip install jinja2`.
3. Render the results into HTML or Markdown via Jinja templates.

## Implementation Notes
- Cache inventories to compare against previous runs and detect drift.
- Support SSH execution for remote hosts via Paramiko or native tools.
- Include security advisories by parsing `ubuntu-security-status` or the CVE tracker.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
