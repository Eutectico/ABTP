from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

import mutagen
from mutagen.easyid3 import EasyID3
from yt_dlp import YoutubeDL


def build_ydl_opts(
    output_template: str,
    audio_only: bool,
    metadata_json: Optional[Path],
) -> Dict[str, Any]:
    postprocessors = [{"key": "FFmpegMetadata"}]
    if audio_only:
        postprocessors.insert(0, {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"})
    return {
        "outtmpl": output_template,
        "writethumbnail": True,
        "writeinfojson": True if metadata_json else False,
        "postprocessors": postprocessors,
    }


def enrich_metadata(media_path: Path, info: Dict[str, Any], cover_path: Optional[Path]) -> None:
    if media_path.suffix.lower() == ".mp3":
        audio = EasyID3(str(media_path))
        audio["title"] = info.get("title") or media_path.stem
        if info.get("uploader"):
            audio["artist"] = info["uploader"]
        if info.get("album"):
            audio["album"] = info["album"]
        audio.save()
    if cover_path and cover_path.exists() and media_path.suffix.lower() == ".mp3":
        audio_file = mutagen.File(str(media_path))
        if audio_file:
            with cover_path.open("rb") as handle:
                image_data = handle.read()
            audio_file.tags.add(  # type: ignore[attr-defined]
                mutagen.id3.APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=mutagen.id3.PictureType.COVER_FRONT,
                    desc="Cover",
                    data=image_data,
                )
            )
            audio_file.save()


def download(url: str, output_dir: Path, audio_only: bool, metadata_json: Optional[Path]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(uploader)s/%(playlist_title)s/%(title)s.%(ext)s")
    ydl_opts = build_ydl_opts(template, audio_only, metadata_json)
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if metadata_json:
            metadata_json.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
        downloaded_path = Path(ydl.prepare_filename(info))
        cover_path = downloaded_path.with_suffix(".jpg")
        enrich_metadata(downloaded_path, info, cover_path if cover_path.exists() else None)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download YouTube or podcast content with metadata.")
    parser.add_argument("url", help="Video, playlist, or feed URL.")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("downloads"),
        help="Base directory for downloaded files.",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Extract audio as MP3 instead of full video.",
    )
    parser.add_argument(
        "--metadata-json",
        type=Path,
        help="Optional path to write full metadata JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    download(args.url, args.output_dir.expanduser(), args.audio_only, args.metadata_json)


if __name__ == "__main__":
    main()
