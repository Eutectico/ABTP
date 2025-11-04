# Desktop Downloads Auto Cleaner

## Purpose
Organize and archive files that accumulate in Downloads or Desktop folders based on human-readable rules.

## Input / Output
- Input: Watch folders such as Downloads or Desktop.
- Output: Sorted folders, archives, or cleanup logs.

## Key Dependencies
- `pathlib`
- `yaml`

## Getting Started
1. Define cleanup policies in a YAML rules file (patterns, age thresholds, destinations).
2. Install dependencies: `pip install pyyaml`.
3. Run the scheduler or CLI to apply the rules manually or on a timer.

## Implementation Notes
- Provide a preview mode before moving or deleting files.
- Record actions in a log file so users can undo mistakes quickly.
- Include safety checks for large files or items updated recently.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
