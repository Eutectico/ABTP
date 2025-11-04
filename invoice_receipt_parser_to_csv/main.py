from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pdfplumber
import pytesseract
import regex
from PIL import Image

AMOUNT_PATTERN = regex.compile(r"(?<!\d)(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2}))\s?(?:€|EUR)", regex.IGNORECASE)
DATE_PATTERN = regex.compile(r"(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})")
VENDOR_PATTERN = re.compile(r"^[A-ZÄÖÜß][\w\s&.,-]{3,}$", re.MULTILINE)


@dataclass(slots=True)
class ParsedReceipt:
    path: Path
    vendor: Optional[str]
    amount: Optional[str]
    date: Optional[str]
    raw_text: str


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        with pdfplumber.open(str(path)) as pdf_doc:
            return "\n".join(page.extract_text() or "" for page in pdf_doc.pages)
    with Image.open(path) as image:
        return pytesseract.image_to_string(image)


def parse_receipt(path: Path) -> ParsedReceipt:
    text = extract_text(path)
    amount_match = AMOUNT_PATTERN.search(text)
    date_match = DATE_PATTERN.search(text)
    vendor_match = VENDOR_PATTERN.search(text)
    vendor = vendor_match.group(0).strip() if vendor_match else None
    amount = amount_match.group(1).replace(".", "").replace(",", ".") if amount_match else None
    date = date_match.group(1) if date_match else None
    return ParsedReceipt(path=path, vendor=vendor, amount=amount, date=date, raw_text=text)


def discover_documents(source: Path, recursive: bool) -> Iterable[Path]:
    suffixes = {".pdf", ".jpg", ".jpeg", ".png"}
    if source.is_file():
        yield source
        return
    pattern = "**/*" if recursive else "*"
    for candidate in sorted(source.glob(pattern)):
        if candidate.is_file() and candidate.suffix.lower() in suffixes:
            yield candidate


def write_outputs(records: Iterable[ParsedReceipt], csv_path: Path, json_path: Optional[Path]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "vendor", "amount_eur", "date"])
        for record in records:
            writer.writerow(
                [
                    str(record.path),
                    record.vendor or "",
                    record.amount or "",
                    record.date or "",
                ]
            )
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(
                [
                    {
                        "path": str(item.path),
                        "vendor": item.vendor,
                        "amount_eur": item.amount,
                        "date": item.date,
                        "raw_text": item.raw_text,
                    }
                    for item in records
                ],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parse receipts into CSV/JSON structures.")
    parser.add_argument("source", type=Path, help="File or directory with receipts (PDF/JPG/PNG).")
    parser.add_argument("--recursive", action="store_true", help="Search subdirectories.")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("receipts.csv"),
        help="Output CSV file.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        help="Optional JSON file capturing parsed results and raw text.",
    )
    args = parser.parse_args()

    documents = list(discover_documents(args.source, args.recursive))
    if not documents:
        raise SystemExit("No receipts found.")

    parsed = [parse_receipt(path) for path in documents]
    write_outputs(parsed, args.csv, args.json)


if __name__ == "__main__":
    main()
