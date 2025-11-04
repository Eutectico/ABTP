# Vocabulary Flashcard Generator (Anki Friendly)

## Purpose
Convert vocabulary lists into Anki-ready CSV files and optionally generate audio pronunciations.

## Input / Output
- Input: Markdown or CSV word lists with translations and notes.
- Output: `cards.csv` plus MP3 files suitable for Anki import.

## Key Dependencies
- `gTTS` or `pyttsx3`
- `pandas`

## Getting Started
1. Install dependencies: `pip install gTTS pandas` (or `pyttsx3` for offline TTS).
2. Normalize your vocabulary source (columns for word, meaning, example).
3. Emit CSV columns in the order expected by your Anki note type.

## Implementation Notes
- Cache generated audio so repeated exports remain fast.
- Provide hooks for language-specific transliteration or stress markers.
- Add a QA step that flags missing translations or audio failures.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
