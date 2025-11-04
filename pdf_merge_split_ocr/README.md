# PDF Merger and Splitter (with OCR)

## Purpose
Combine and split PDF documents, and optionally extract searchable text through OCR.

## Input / Output
- Input: One or more PDF files, optionally a queue for OCR.
- Output: Merged or split PDF files plus optional text or JSON sidecars.

## Key Dependencies
- `pypdf`
- `pdfplumber`
- `pytesseract`

## Getting Started
1. Install system packages for Tesseract OCR (required by `pytesseract`).
2. Create a virtual environment and install Python libs: `pip install pypdf pdfplumber pytesseract`.
3. Implement CLI switches such as `--merge`, `--split`, `--ocr`, and `--output`.

## Implementation Notes
- Provide progress feedback for large document batches.
- Store OCR output separately so users can diff or archive extracted text.
- Consider a config file that lists merge or split recipes to automate routine jobs.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
