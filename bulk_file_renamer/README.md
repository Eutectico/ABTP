# Bulk File Renamer (Regex + Tags)

## Purpose
Batch rename large numbers of files using regex patterns or metadata tags.

## Input / Output
- Input: Directory that contains the files to rename.
- Output: Same directory with renamed files plus an optional rename log.

## Key Dependencies
- `pathlib`
- `re`
- `click`

## Getting Started
1. Create and activate a virtual environment.
2. Install the CLI dependency: `pip install click`.
3. Prepare your rename rules (regex search/replace or tag mappings).
4. Run the tool, for example: `python main.py --source <folder> --pattern "<regex>" --replace "<string>"`.

## Implementation Notes
- Always expose a `--dry-run` flag so users can preview changes safely.
- Write rename results to CSV or JSON to keep an audit trail and enable rollbacks.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
