from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import pytesseract
from PIL import Image

SUPPORTED = {".png", ".jpg", ".jpeg"}


def ocr_image(path: Path, language: str) -> str:
    with Image.open(path) as image:
        return pytesseract.image_to_string(image, lang=language)


def write_markdown(text: str, target: Path, source: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    header = f"# OCR Result for {source.name}\n\n"
    metadata = f"_Generated: {datetime.utcnow().isoformat()}Z_\n\n"
    target.write_text(header + metadata + text.strip() + "\n", encoding="utf-8")


def process(path: Path, output_dir: Path, language: str) -> None:
    text = ocr_image(path, language)
    target = output_dir / f"{path.stem}.md"
    write_markdown(text, target, path)
    print(f"[OK] {path} -> {target}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OCR screenshots into Markdown notes.")
    parser.add_argument("source", type=Path, help="Image file or directory.")
    parser.add_argument("--output-dir", type=Path, default=Path("ocr_notes"), help="Directory for Markdown output.")
    parser.add_argument("--language", default="eng", help="Tesseract language code.")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.expanduser()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")
    if source.is_file():
        process(source, args.output_dir, args.language)
        return
    pattern = "**/*" if args.recursive else "*"
    for image_path in sorted(source.glob(pattern)):
        if image_path.is_file() and image_path.suffix.lower() in SUPPORTED:
            process(image_path, args.output_dir, args.language)


if __name__ == "__main__":
    main()
