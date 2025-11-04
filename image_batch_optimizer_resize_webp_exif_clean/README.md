# Image Batch Optimizer (Resize, WebP, EXIF Clean)

## Purpose
Optimize large image collections by resizing, converting to WebP, and stripping sensitive EXIF data.

## Input / Output
- Input: Folders that contain JPG or PNG files.
- Output: Optimized images (WebP or compressed JPG) plus a summary report.

## Key Dependencies
- `Pillow`
- `piexif`

## Getting Started
1. Install dependencies: `pip install Pillow piexif`.
2. Decide on default target sizes, quality levels, and EXIF keep/remove rules.
3. Run the batch processor with options such as `--max-width`, `--format`, or `--report`.

## Implementation Notes
- Preserve originals in an archive directory when possible.
- Use multithreading or multiprocessing to handle large collections efficiently.
- Log every change so photographers know which metadata was removed.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
