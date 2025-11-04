# Screenshot to Text Pipeline (OCR to Markdown)

## Purpose
Turn screenshots into searchable Markdown notes by running OCR and formatting the recognized text.

## Input / Output
- Input: PNG or JPG screenshots.
- Output: Markdown files that store the extracted text alongside metadata.

## Key Dependencies
- `pytesseract`
- `Pillow`

## Getting Started
1. Install Tesseract OCR and add it to the system path.
2. Install Python dependencies: `pip install pytesseract Pillow`.
3. Define naming conventions for output files and optional tagging.

## Implementation Notes
- Store the raw OCR text before cleanup for auditing.
- Use language packs that match the expected screenshot language.
- Combine OCR output with metadata (timestamp, source app) to enrich the Markdown file.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
