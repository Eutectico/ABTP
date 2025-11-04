# CSV Cleaner and Standardizer

## Purpose
Normalize messy CSV files by fixing delimiters, encodings, headers, and date formats.

## Input / Output
- Input: CSV files in inconsistent encodings or schemas.
- Output: Clean CSV files plus an optional quality report.

## Key Dependencies
- `pandas`
- `chardet`
- `dateutil`

## Getting Started
1. Install dependencies: `pip install pandas chardet python-dateutil`.
2. Detect encoding and delimiter automatically, then validate results with sample rows.
3. Provide CLI options to enforce schemas, rename columns, or coerce data types.

## Implementation Notes
- Produce a summary of detected issues (missing columns, malformed dates, etc.).
- Keep backups of the original files alongside the cleaned output.
- Add unit tests that cover the most common CSV quirks you encounter.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
