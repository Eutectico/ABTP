from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable

import pandas as pd

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover - optional
    gTTS = None  # type: ignore


def load_markdown_table(path: Path) -> pd.DataFrame:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if not table_lines:
        raise ValueError("No Markdown table detected.")
    # Remove the header separator row
    table_lines = [line for line in table_lines if set(line.replace("|", "").strip()) - {"-"}]
    reader = csv.reader(table_lines, delimiter="|")
    rows = [list(filter(None, [col.strip() for col in row])) for row in reader]
    headers = rows[0]
    records = rows[1:]
    return pd.DataFrame(records, columns=headers)


def load_vocab(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".md":
        return load_markdown_table(path)
    return pd.read_csv(path)


def generate_audio(text: str, language: str, destination: Path) -> None:
    if gTTS is None:
        raise SystemExit("gTTS is required for audio generation. Install gTTS or disable audio output.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    gTTS(text=text, lang=language).save(str(destination))


def export_cards(frame: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Anki-friendly CSV and audio from vocabulary lists.")
    parser.add_argument("source", type=Path, help="CSV or Markdown file with vocabulary entries.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("cards.csv"),
        help="Destination CSV for Anki import.",
    )
    parser.add_argument("--audio-dir", type=Path, help="Directory to store generated audio files.")
    parser.add_argument("--audio-language", default="ru", help="Language code for TTS.")
    parser.add_argument(
        "--fields",
        nargs=3,
        metavar=("WORD", "TRANSLATION", "EXAMPLE"),
        default=["word", "translation", "example"],
        help="Column names (in source file) used to build flashcards.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame = load_vocab(args.source.expanduser())
    word_col, translation_col, example_col = args.fields
    missing = [col for col in [word_col, translation_col, example_col] if col not in frame.columns]
    if missing:
        raise SystemExit(f"Missing columns: {missing}")
    export = frame[[word_col, translation_col, example_col]].rename(
        columns={
            word_col: "Front",
            translation_col: "Back",
            example_col: "Example",
        }
    )
    output_path = args.output.expanduser()
    export_cards(export, output_path)
    if args.audio_dir:
        audio_dir = args.audio_dir.expanduser()
        for word in export["Front"]:
            audio_path = audio_dir / f"{word}.mp3"
            generate_audio(str(word), args.audio_language, audio_path)
    print(f"[OK] Generated {len(export)} flashcards.")


if __name__ == "__main__":
    main()
