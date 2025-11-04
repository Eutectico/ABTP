from __future__ import annotations

import argparse
import csv
import imaplib
import os
from email import message_from_bytes
from email.message import Message
from pathlib import Path
from typing import Iterable, List

from dateutil import parser as dateparser
from ics import Calendar, Event


def load_eml_files(source: Path, recursive: bool) -> Iterable[bytes]:
    if source.is_file():
        yield source.read_bytes()
        return
    pattern = "**/*.eml" if recursive else "*.eml"
    for eml_path in sorted(source.glob(pattern)):
        yield eml_path.read_bytes()


def fetch_imap_messages(
    host: str,
    username: str,
    password: str,
    mailbox: str,
    criteria: str,
) -> Iterable[bytes]:
    with imaplib.IMAP4_SSL(host) as client:
        client.login(username, password)
        client.select(mailbox)
        status, data = client.search(None, criteria)
        if status != "OK":
            raise SystemExit(f"IMAP search failed: {status}")
        for msg_id in data[0].split():
            status, payload = client.fetch(msg_id, "(RFC822)")
            if status == "OK":
                yield payload[0][1]


def events_from_attachment(payload: bytes) -> List[Event]:
    calendar = Calendar(payload.decode("utf-8", errors="ignore"))
    return list(calendar.events)


def heuristics_from_body(message: Message) -> List[Event]:
    text = message.get_body(preferencelist=("plain", "html"))
    if not text:
        return []
    content = text.get_content()
    try:
        start = dateparser.parse(content, fuzzy=True)
    except (ValueError, OverflowError):
        return []
    summary = message.get("Subject", "Mail Event")
    event = Event(name=summary, begin=start)
    return [event]


def extract_events(message_bytes: bytes) -> List[Event]:
    msg = message_from_bytes(message_bytes)
    events: List[Event] = []
    for part in msg.walk():
        if part.get_content_type() == "text/calendar":
            payload = part.get_payload(decode=True)
            if payload:
                events.extend(events_from_attachment(payload))
    if not events:
        events.extend(heuristics_from_body(msg))
    return events


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract calendar events from emails.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path, help="EML file or directory.")
    group.add_argument("--imap-host", help="IMAP host to fetch emails from.")
    parser.add_argument("--imap-user", help="IMAP username.")
    parser.add_argument("--imap-password", help="IMAP password (or use IMAP_PASSWORD env var).")
    parser.add_argument("--imap-mailbox", default="INBOX", help="Mailbox folder.")
    parser.add_argument("--imap-criteria", default="UNSEEN", help="IMAP search criteria.")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories recursively.")
    parser.add_argument("--ics-output", type=Path, default=Path("events.ics"), help="ICS output file.")
    parser.add_argument("--csv-output", type=Path, help="Optional CSV output file.")
    return parser.parse_args()


def write_outputs(events: List[Event], ics_path: Path, csv_path: Path | None) -> None:
    calendar = Calendar()
    for event in events:
        calendar.events.add(event)
    ics_path.write_text(str(calendar), encoding="utf-8")
    if csv_path:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["name", "start", "end", "location"])
            for event in events:
                writer.writerow(
                    [
                        event.name or "",
                        event.begin.isoformat() if event.begin else "",
                        event.end.isoformat() if event.end else "",
                        event.location or "",
                    ]
                )


def main() -> None:
    args = parse_args()
    events: List[Event] = []
    if args.source:
        for message_bytes in load_eml_files(args.source.expanduser(), args.recursive):
            events.extend(extract_events(message_bytes))
    else:
        password = args.imap_password or os.getenv("IMAP_PASSWORD")
        if not password or not args.imap_user:
            raise SystemExit("IMAP credentials missing (user/password).")
        for message_bytes in fetch_imap_messages(
            args.imap_host,
            args.imap_user,
            password,
            args.imap_mailbox,
            args.imap_criteria,
        ):
            events.extend(extract_events(message_bytes))
    if not events:
        print("[INFO] No events discovered.")
        return
    write_outputs(events, args.ics_output.expanduser(), args.csv_output.expanduser() if args.csv_output else None)
    print(f"[OK] Extracted {len(events)} events.")


if __name__ == "__main__":
    main()
