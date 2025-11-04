from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import chardet
import pandas as pd
from dateutil import parser as dateparser


def detect_encoding(path: Path, sample_size: int = 4096) -> str:
    with path.open("rb") as handle:
        raw = handle.read(sample_size)
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def detect_delimiter(path: Path, encoding: str) -> str:
    with path.open("r", encoding=encoding, errors="ignore") as handle:
        sample = "".join(handle.readline() for _ in range(5))
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=";,|\t")
        return dialect.delimiter
    except csv.Error:
        return ","


def normalize_dates(frame: pd.DataFrame, columns: Iterable[str]) -> None:
    for column in columns:
        if column not in frame.columns:
            continue
        try:
            frame[column] = frame[column].apply(
                lambda value: dateparser.parse(str(value)).date().isoformat()
                if pd.notna(value) and str(value).strip()
                else value
            )
        except (ValueError, TypeError):
            continue


def clean_csv(source: Path, output: Path, date_columns: list[str], force_delimiter: str | None) -> None:
    encoding = detect_encoding(source)
    delimiter = force_delimiter or detect_delimiter(source, encoding)
    frame = pd.read_csv(source, encoding=encoding, sep=delimiter, engine="python", dtype=str)
    frame.columns = [col.strip() for col in frame.columns]
    normalize_dates(frame, date_columns)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean CSV files (encoding, delimiter, dates).")
    parser.add_argument("source", type=Path, help="CSV file to clean.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("clean.csv"),
        help="Destination CSV path.",
    )
    parser.add_argument(
        "--date-columns",
        nargs="*",
        default=["date", "created_at"],
        help="Columns to treat as dates.",
    )
    parser.add_argument(
        "--delimiter",
        help="Override detected delimiter.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    clean_csv(args.source.expanduser(), args.output.expanduser(), args.date_columns, args.delimiter)
    print(f"[OK] Wrote cleaned CSV to {args.output}")


if __name__ == "__main__":
    main()
