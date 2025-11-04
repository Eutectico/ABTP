# YouTube and Podcast Downloader with Metadata

## Purpose
Archive playlists or podcast feeds locally while preserving metadata such as chapters, thumbnails, and tags.

## Input / Output
- Input: Playlist URLs, channel URLs, or individual media links.
- Output: MP3 or MP4 files plus JSON sidecars that store metadata.

## Key Dependencies
- `yt-dlp`
- `mutagen`

## Getting Started
1. Install dependencies: `pip install yt-dlp mutagen`.
2. Configure default output templates (e.g. `{uploader}/{playlist}/{title}.{ext}`).
3. Provide CLI switches for audio-only extraction, chapter JSON export, and cover art downloads.

## Implementation Notes
- Respect rate limits by adding retry and throttle logic.
- Cache downloads to avoid re-fetching unchanged items.
- Keep a manifest of downloaded IDs to prevent duplicates.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
