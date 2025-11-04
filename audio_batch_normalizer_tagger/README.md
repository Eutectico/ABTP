# Audio Batch Normalizer and Tagger

## Purpose
Normalize loudness across large sets of audio files and update metadata tags in one pass.

## Input / Output
- Input: WAV, MP3, or other audio formats that need consistent volume.
- Output: Normalized audio files plus updated tag metadata.

## Key Dependencies
- `ffmpeg-python`
- `mutagen`

## Getting Started
1. Install FFmpeg binaries and ensure they are accessible on the system path.
2. Create a virtual environment and install Python dependencies: `pip install ffmpeg-python mutagen`.
3. Design CLI options for target LUFS, album gain, and tag updates.

## Implementation Notes
- Write peak and loudness measurements to a report for quality control.
- Support dry runs that only print intended gain adjustments.
- Preserve original files in a backup folder until the workflow is proven stable.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
