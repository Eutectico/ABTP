from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

import ffmpeg
from mutagen import File as MutagenFile
from mutagen import id3 as id3_module
from mutagen.id3 import ID3, ID3NoHeaderError

SUPPORTED_SUFFIXES = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


def discover_audio(source: Path, recursive: bool) -> Iterable[Path]:
    if source.is_file():
        yield source
        return
    pattern = "**/*" if recursive else "*"
    for candidate in sorted(source.glob(pattern)):
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES:
            yield candidate


def loudnorm_filter(
    input_stream,
    target_lufs: float,
    true_peak: float,
    loudness_range: float,
):
    return input_stream.filter(
        "loudnorm",
        i=target_lufs,
        tp=true_peak,
        lra=loudness_range,
        dual_mono="true",
    )


def normalize_file(
    source: Path,
    target: Path,
    target_lufs: float,
    true_peak: float,
    loudness_range: float,
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    stream = ffmpeg.input(str(source))
    stream = loudnorm_filter(stream.audio, target_lufs, true_peak, loudness_range)
    output_kwargs = {}
    if target.suffix.lower() == ".mp3":
        output_kwargs["audio_bitrate"] = "192k"
    ffmpeg.output(stream, str(target), **output_kwargs).overwrite_output().run(quiet=True)


def copy_tags(source: Path, target: Path, artist: Optional[str], album: Optional[str]) -> None:
    audio = MutagenFile(str(target), easy=True)
    if audio is None:
        return
    if source != target:
        original = MutagenFile(str(source), easy=True)
        if original:
            for key, value in original.tags.items():
                audio.tags[key] = value
    if artist:
        audio["artist"] = artist
    if album:
        audio["album"] = album
    audio.save()
    if target.suffix.lower() in {".mp3", ".m4a"}:
        try:
            id3_tag = ID3(str(target))
        except ID3NoHeaderError:
            id3_tag = ID3()
        if artist:
            id3_tag.add(id3_module.TPE1(encoding=3, text=artist))
        if album:
            id3_tag.add(id3_module.TALB(encoding=3, text=album))
        id3_tag.save(str(target))


def build_target_path(source: Path, output_dir: Path) -> Path:
    return output_dir / source.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize audio loudness in batch and adjust metadata tags."
    )
    parser.add_argument("source", type=Path, help="File or directory with audio files.")
    parser.add_argument(
        "--output-dir",
        "-o",
        type=Path,
        default=Path("normalized_audio"),
        help="Directory for normalized files.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Process directories recursively.",
    )
    parser.add_argument(
        "--target-lufs",
        type=float,
        default=-14.0,
        help="Integrated loudness target in LUFS.",
    )
    parser.add_argument(
        "--true-peak",
        type=float,
        default=-1.5,
        help="True peak limit in dB.",
    )
    parser.add_argument(
        "--loudness-range",
        type=float,
        default=11.0,
        help="Loudness range constraint.",
    )
    parser.add_argument("--set-artist", help="Override artist tag.")
    parser.add_argument("--set-album", help="Override album tag.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.expanduser()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")

    files = list(discover_audio(source, args.recursive))
    if not files:
        raise SystemExit("No audio files discovered.")

    for file_path in files:
        target = build_target_path(file_path, args.output_dir)
        normalize_file(
            file_path,
            target,
            target_lufs=args.target_lufs,
            true_peak=args.true_peak,
            loudness_range=args.loudness_range,
        )
        copy_tags(file_path, target, args.set_artist, args.set_album)
        print(f"[OK] {file_path} -> {target}")


if __name__ == "__main__":
    main()
