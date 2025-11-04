from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import piexif
from PIL import Image

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png"}


@dataclass(slots=True)
class TransformOptions:
    max_width: Optional[int]
    max_height: Optional[int]
    quality: int
    target_format: str
    strip_exif: bool


def discover_images(source: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    for path in sorted(source.glob(pattern)):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path


def resize_image(image: Image.Image, options: TransformOptions) -> Image.Image:
    if not options.max_width and not options.max_height:
        return image
    image = image.copy()
    image.thumbnail(
        (
            options.max_width or image.width,
            options.max_height or image.height,
        ),
        Image.Resampling.LANCZOS,
    )
    return image


def build_target_path(path: Path, output_dir: Path, options: TransformOptions) -> Path:
    relative = path.name if output_dir == path.parent else path.relative_to(path.parent)
    stem = Path(relative).stem
    target_suffix = f".{options.target_format.lower()}"
    return output_dir / f"{stem}{target_suffix}"


def process_image(path: Path, output_dir: Path, options: TransformOptions) -> Path:
    with Image.open(path) as img:
        transformed = resize_image(img, options)
        target = build_target_path(path, output_dir, options)
        target.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {}
        if options.target_format.lower() in {"jpeg", "jpg"}:
            save_kwargs["quality"] = options.quality
            save_kwargs["optimize"] = True
        elif options.target_format.lower() == "webp":
            save_kwargs["quality"] = options.quality
        transformed.save(target, options.target_format.upper(), **save_kwargs)
        if options.strip_exif:
            try:
                piexif.remove(str(target))
            except Exception:
                pass
        return target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resize and optimize image folders.")
    parser.add_argument("source", type=Path, help="Image file or directory.")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("optimized_images"),
        help="Directory to write optimized files.",
    )
    parser.add_argument("--max-width", type=int, help="Maximum width in pixels.")
    parser.add_argument("--max-height", type=int, help="Maximum height in pixels.")
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="Quality level for output (0-100).",
    )
    parser.add_argument(
        "--format",
        choices=["webp", "jpeg", "png"],
        default="webp",
        help="Target image format.",
    )
    parser.add_argument(
        "--strip-exif",
        action="store_true",
        help="Remove EXIF metadata from the output files.",
    )
    parser.add_argument("--recursive", action="store_true", help="Process subdirectories.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.expanduser()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")

    options = TransformOptions(
        max_width=args.max_width,
        max_height=args.max_height,
        quality=args.quality,
        target_format=args.format,
        strip_exif=args.strip_exif,
    )
    if source.is_file():
        processed = process_image(source, args.output_dir, options)
        print(f"[OK] {source} -> {processed}")
        return

    for path in discover_images(source, args.recursive):
        target = process_image(path, args.output_dir, options)
        print(f"[OK] {path} -> {target}")


if __name__ == "__main__":
    main()
