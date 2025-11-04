from __future__ import annotations

import argparse
import queue
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


@dataclass(slots=True)
class AlertConfig:
    pattern: re.Pattern[str]
    webhook: Optional[str]
    slack_token: Optional[str]
    slack_channel: Optional[str]


class Tailer(FileSystemEventHandler):
    def __init__(self, path: Path, config: AlertConfig) -> None:
        self.path = path
        self.config = config
        self.position = 0
        self._queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._process_queue, daemon=True)
        self._thread.start()

    def on_modified(self, event) -> None:  # type: ignore[override]
        if Path(event.src_path) != self.path:
            return
        self._read_new_lines()

    def on_created(self, event) -> None:  # type: ignore[override]
        if Path(event.src_path) == self.path:
            self.position = 0
            self._read_new_lines()

    def start(self) -> None:
        self._read_new_lines()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=2)

    def _read_new_lines(self) -> None:
        with self.path.open("r", encoding="utf-8", errors="ignore") as handle:
            handle.seek(self.position)
            for line in handle:
                line = line.rstrip("\n")
                if self.config.pattern.search(line):
                    self._queue.put(line)
            self.position = handle.tell()

    def _process_queue(self) -> None:
        while not self._stop_event.is_set():
            try:
                line = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            send_alert(line, self.config)
            self._queue.task_done()


def send_alert(message: str, config: AlertConfig) -> None:
    payload = {"text": message}
    if config.webhook:
        try:
            response = requests.post(config.webhook, json=payload, timeout=5)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - best effort
            print(f"[WARN] Failed to deliver webhook: {exc}")
    if config.slack_token and config.slack_channel:
        headers = {"Authorization": f"Bearer {config.slack_token}"}
        data = {"channel": config.slack_channel, "text": message}
        try:
            response = requests.post(
                "https://slack.com/api/chat.postMessage", headers=headers, data=data, timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover
            print(f"[WARN] Failed to send Slack alert: {exc}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Watch logfiles and raise alerts on regex matches.")
    parser.add_argument("path", type=Path, help="Log file to watch.")
    parser.add_argument(
        "--pattern",
        "-p",
        default=r"ERROR|CRITICAL",
        help="Regular expression that triggers alerts.",
    )
    parser.add_argument("--webhook", help="Webhook endpoint that receives alert payload.")
    parser.add_argument("--slack-token", help="Slack API token for chat.postMessage.")
    parser.add_argument("--slack-channel", help="Slack channel ID for alerts.")
    parser.add_argument(
        "--debounce",
        type=float,
        default=1.0,
        help="Minimum seconds between filesystem polls to reduce noise.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = args.path.expanduser()
    if not path.exists():
        raise SystemExit(f"Log file not found: {path}")

    config = AlertConfig(
        pattern=re.compile(args.pattern),
        webhook=args.webhook,
        slack_token=args.slack_token,
        slack_channel=args.slack_channel,
    )
    tailer = Tailer(path, config)
    observer = Observer(timeout=args.debounce)
    observer.schedule(tailer, path=path.parent, recursive=False)
    observer.start()
    tailer.start()

    print(f"[INFO] Watching {path} for pattern {config.pattern.pattern!r}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Stopping watcher...")
    finally:
        observer.stop()
        observer.join(timeout=2)
        tailer.stop()


if __name__ == "__main__":
    main()
