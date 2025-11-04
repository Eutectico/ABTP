# Duplicate and Similar Image Finder

## Purpose
Identify duplicate or nearly identical photos to help declutter large image libraries.

## Input / Output
- Input: Directories filled with images to compare.
- Output: Reports (CSV, JSON, or HTML) that list duplicates or safe delete suggestions.

## Key Dependencies
- `imagehash`
- `Pillow`

## Getting Started
1. Install dependencies: `pip install imagehash Pillow`.
2. Generate perceptual hashes for each image and store them in a cache or database.
3. Provide thresholds for what counts as an exact match versus a similar picture.

## Implementation Notes
- Offer actions like hardlinking or moving duplicates to a quarantine folder.
- Visualize matches with side-by-side comparisons to help manual review.
- Track ignored pairs so users can keep intentional near-duplicates.

---

<a href="https://www.buymeacoffee.com/Eutectico" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
