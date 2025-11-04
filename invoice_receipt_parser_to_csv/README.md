# Invoice and Receipt Parser to CSV

## Purpose
Extract totals, dates, vendors, and line items from invoices or receipts and write them to structured files.

## Input / Output
- Input: Scanned or digital receipts in PDF or JPG format.
- Output: CSV or JSON documents that describe the captured financial data.

## Key Dependencies
- `pytesseract`
- `regex`
- `pdfplumber`

## Getting Started
1. Install Tesseract OCR and ensure it is available on the system path.
2. Create a virtual environment and install the Python libs: `pip install pytesseract regex pdfplumber`.
3. Build parsers that detect common layouts; keep vendor-specific templates in a `templates/` folder.

## Implementation Notes
- Normalize currencies and date formats before exporting.
- Keep raw OCR text for debugging and traceability.
- Add validation hooks to mark documents that could not be parsed confidently.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
