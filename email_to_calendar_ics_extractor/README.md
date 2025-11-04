# Email to Calendar Extractor

## Purpose
Scan incoming emails for meeting or event details and export them as calendar files.

## Input / Output
- Input: EML files, Maildir folders, or IMAP mailboxes.
- Output: `.ics` calendar files or CSV digests with extracted events.

## Key Dependencies
- `imaplib`
- `email`
- `ics`

## Getting Started
1. Configure access to the mailbox (credentials, folders, search queries).
2. Install dependencies: `pip install ics`.
3. Build parsers that extract subjects, participants, locations, and date/time ranges.

## Implementation Notes
- Handle timezone conversion consistently across events.
- Prevent duplicates by tracking message IDs and event hashes.
- Add optional notifications once a new calendar file has been generated.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
