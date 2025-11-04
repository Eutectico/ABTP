from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment


def run_command(command: List[str]) -> str:
    try:
        result = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.CalledProcessError):
        return ""
    return result.strip()


def collect_inventory() -> Dict[str, Any]:
    inventory: Dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "hostname": run_command(["hostname"]),
        "kernel": run_command(["uname", "-r"]),
        "packages": [],
        "services": [],
        "upgrades": run_command(["apt", "list", "--upgradable"]),
    }
    dpkg_output = run_command(["dpkg-query", "-W", "-f=${Package}\t${Version}\n"])
    if dpkg_output:
        inventory["packages"] = [
            {"name": name, "version": version}
            for line in dpkg_output.splitlines()
            if (parts := line.split("\t")) and len(parts) == 2
            for name, version in [parts]
        ]
    systemctl_output = run_command(["systemctl", "list-units", "--type=service", "--state=running"])
    if systemctl_output:
        inventory["services"] = [line.split()[0] for line in systemctl_output.splitlines() if line.endswith("running")]
    return inventory


def render_html(inventory: Dict[str, Any], template_path: Path | None) -> str:
    env = Environment()
    if template_path and template_path.exists():
        template = env.from_string(template_path.read_text(encoding="utf-8"))
    else:
        template = env.from_string(
            """<!doctype html>
<html><head><meta charset="utf-8"><title>System Report</title></head>
<body>
  <h1>System Inventory</h1>
  <p>Generated: {{ data.generated_at }}</p>
  <p>Hostname: {{ data.hostname }}</p>
  <p>Kernel: {{ data.kernel }}</p>
  <h2>Running Services</h2>
  <ul>
    {% for service in data.services %}
    <li>{{ service }}</li>
    {% endfor %}
  </ul>
  <h2>Upgradeable Packages</h2>
  <pre>{{ data.upgrades }}</pre>
  <h2>Installed Packages (first 50)</h2>
  <ul>
    {% for package in data.packages[:50] %}
    <li>{{ package.name }} {{ package.version }}</li>
    {% endfor %}
  </ul>
</body></html>"""
        )
    return template.render(data=inventory)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Ubuntu inventory/update reports.")
    parser.add_argument("--html", type=Path, default=Path("system-report.html"), help="HTML output path.")
    parser.add_argument("--json", type=Path, default=Path("system-report.json"), help="JSON output path.")
    parser.add_argument("--template", type=Path, help="Optional custom Jinja2 template for HTML.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inventory = collect_inventory()
    args.json.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    html = render_html(inventory, args.template)
    args.html.write_text(html, encoding="utf-8")
    print(f"[OK] Wrote {args.json} and {args.html}")


if __name__ == "__main__":
    main()
