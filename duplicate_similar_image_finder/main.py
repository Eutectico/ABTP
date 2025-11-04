from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

import imagehash
from PIL import Image


def discover_images(source: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    for candidate in sorted(source.glob(pattern)):
        if candidate.is_file() and candidate.suffix.lower() in {".jpg", ".jpeg", ".png"}:
            yield candidate


def compute_hash(path: Path, hash_size: int) -> imagehash.ImageHash:
    with Image.open(path) as image:
        return imagehash.phash(image, hash_size=hash_size)


def group_images(source: Path, recursive: bool, hash_size: int) -> Dict[str, imagehash.ImageHash]:
    result: Dict[str, imagehash.ImageHash] = {}
    for image_path in discover_images(source, recursive):
        result[str(image_path)] = compute_hash(image_path, hash_size)
    return result


def find_duplicates(hashes: Dict[str, imagehash.ImageHash], threshold: int) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = defaultdict(list)
    paths = list(hashes.keys())
    for idx, path in enumerate(paths):
        base_hash = hashes[path]
        for other in paths[idx + 1 :]:
            if base_hash - hashes[other] <= threshold:
                groups[path].append(other)
    return {key: value for key, value in groups.items() if value}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find duplicate or similar images using perceptual hash.")
    parser.add_argument("source", type=Path, help="Directory to scan.")
    parser.add_argument("--recursive", action="store_true", help="Scan subdirectories.")
    parser.add_argument(
        "--hash-size",
        type=int,
        default=16,
        help="Hash size (larger values increase sensitivity).",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=5,
        help="Maximum Hamming distance to treat images as similar.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.source.is_dir():
        raise SystemExit(f"Source directory not found: {args.source}")
    hashes = group_images(args.source, args.recursive, args.hash_size)
    duplicates = find_duplicates(hashes, args.threshold)
    if not duplicates:
        print("[INFO] No duplicates detected.")
        return
    for base, dupes in duplicates.items():
        print(f"[DUP] {base}")
        for other in dupes:
            print(f"      -> {other}")


if __name__ == "__main__":
    main()
