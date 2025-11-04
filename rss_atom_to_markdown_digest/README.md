# RSS or Atom to Markdown Digest

## Purpose
Aggregate feed entries into weekly or daily digests rendered as Markdown or HTML.

## Input / Output
- Input: List of RSS or Atom feed URLs.
- Output: `digest.md` files (and optionally HTML or email-ready output).

## Key Dependencies
- `feedparser`
- `jinja2`

## Getting Started
1. Install dependencies: `pip install feedparser jinja2`.
2. Store feed subscriptions and metadata (tags, categories) in a YAML or JSON file.
3. Render digests using Jinja templates for Markdown and HTML variants.

## Implementation Notes
- De-duplicate articles by GUID or URL across multiple feeds.
- Add CLI options for time windows (`--since`, `--until`) and output paths.
- Integrate with schedulers or GitHub Actions for fully automated digests.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
