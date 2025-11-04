from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import pdfplumber
import pytesseract
from PIL import Image
from pypdf import PdfReader, PdfWriter


@dataclass(slots=True)
class MergeConfig:
    inputs: List[Path]
    output: Path


@dataclass(slots=True)
class SplitConfig:
    source: Path
    output_dir: Path


@dataclass(slots=True)
class OcrConfig:
    source: Path
    output: Path
    include_layout: bool


def merge_pdfs(config: MergeConfig) -> None:
    writer = PdfWriter()
    for pdf_path in config.inputs:
        reader = PdfReader(str(pdf_path))
        for page in reader.pages:
            writer.add_page(page)
    config.output.parent.mkdir(parents=True, exist_ok=True)
    with config.output.open("wb") as handle:
        writer.write(handle)


def split_pdf(config: SplitConfig) -> None:
    reader = PdfReader(str(config.source))
    config.output_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        target = config.output_dir / f"{config.source.stem}_page{index:03d}.pdf"
        with target.open("wb") as handle:
            writer.write(handle)


def _extract_text_from_page(page: pdfplumber.page.Page, include_layout: bool) -> str:
    text = page.extract_text(layout=include_layout) or ""
    if text.strip():
        return text
    with page.to_image(resolution=300).original.convert("RGB") as image:
        return pytesseract.image_to_string(image)


def ocr_pdf(config: OcrConfig) -> None:
    records = []
    with pdfplumber.open(str(config.source)) as pdf_doc:
        for index, page in enumerate(pdf_doc.pages, start=1):
            content = _extract_text_from_page(page, config.include_layout)
            records.append(
                {
                    "page": index,
                    "text": content,
                }
            )
    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PDF merge/split/ocr helper")
    sub = parser.add_subparsers(dest="command", required=True)

    merge = sub.add_parser("merge", help="Merge multiple PDFs into a single file")
    merge.add_argument("inputs", nargs="+", type=Path, help="PDF files ordered as merged")
    merge.add_argument("--output", "-o", required=True, type=Path, help="Target PDF path")

    split = sub.add_parser("split", help="Split a PDF into one file per page")
    split.add_argument("source", type=Path, help="PDF file to split")
    split.add_argument(
        "--output-dir",
        "-d",
        type=Path,
        default=Path("split_output"),
        help="Directory for split PDFs",
    )

    ocr = sub.add_parser("ocr", help="Extract text via OCR and emit JSON")
    ocr.add_argument("source", type=Path, help="PDF file to process")
    ocr.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("ocr_output.json"),
        help="Destination JSON file",
    )
    ocr.add_argument(
        "--layout",
        action="store_true",
        help="Preserve layout information where possible",
    )

    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    if args.command == "merge":
        config = MergeConfig(inputs=[Path(p) for p in args.inputs], output=Path(args.output))
        merge_pdfs(config)
    elif args.command == "split":
        config = SplitConfig(source=Path(args.source), output_dir=Path(args.output_dir))
        split_pdf(config)
    elif args.command == "ocr":
        config = OcrConfig(
            source=Path(args.source), output=Path(args.output), include_layout=args.layout
        )
        ocr_pdf(config)
    else:
        raise ValueError(f"Unrecognized command: {args.command}")


if __name__ == "__main__":
    main()
