---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: a712748bb57f2578d588619857ec8381
    PropagateID: a712748bb57f2578d588619857ec8381
    ReservedCode1: 304502203a2977be774cbf12392b7e0926f6d9296e84caf8dea337837c4345c7de8f8964022100900bcc66209a92b7f478eb76f673695806ee369ab65f4a2abc283d9b534beba3
    ReservedCode2: 3045022100edc32ff76c441ea081cdaf2aa2c6f842db02431139e7559ecba4435dc375f24002205f6ac5b8f884567482d36385be8aa0caf9446923c3b799f51b7ee36f63c2364e
description: Clean and organize video file names with intelligent detection. Use when users ask to clean/rename/organize video files, remove technical suffixes from video titles, convert video naming formats (Part X/Y to numbered format), group video series, or reorganize video folders.
name: video-title-cleaner
---

# Video Title Cleaner

Intelligently clean and organize video file names with smart detection of numbering patterns.

## Quick Start

Run the cleaner on a folder:

```bash
python video_title_cleaner.py "/path/to/video/folder"
```

Preview changes without applying:

```bash
python video_title_cleaner.py "/path/to/video/folder" --preview
```

## Supported Patterns

### Detection Modes

1. **Standalone Topics** → `"N - Title"` format
   - Part X/Y, Topic N, Lesson N, Chapter N
   - Example: `Video Part 1_4 Title` → `1 - Title`

2. **TV Series** → `"S1E1 - Title"` format
   - S1E1, Episode N, Season N patterns
   - Example: `My Series S01E05 Title` → `S1E5 - Title`

3. **Single Topic** → Just `"Title"`
   - Files without numbering detected
   - Example: `My Video Title` → `My Video Title`

4. **Common Themes** → Group into subfolders
   - Files are grouped by detected series and organized into subfolders

## Features

- **Smart Detection**: Automatically distinguishes between standalone topics and TV-style series
- **Title Cleaning**: Removes technical suffixes like `(720p_60fps_H264)`
- **Series Grouping**: Groups related videos and organizes into subfolders
- **Dry Run Mode**: Preview all changes before applying
- **Recursive Scanning**: Scans entire folder trees

## File Types Supported

- `.mp4`, `.mkv`, `.avi`, `.mov`

## Output Format

| Input Pattern | Output Format |
|--------------|---------------|
| `Part 1/4 Title` | `1 - Title` |
| `Lesson 5 Title` | `5 - Title` |
| `S1E3 Title` | `S1E3 - Title` |
| `Episode 2 Title` | `S1E2 - Title` |
| `Single Video` | `Single Video` |

## Examples

### Basic Usage

```bash
# Clean and organize a folder
python video_title_cleaner.py "/Volumes/Videos/Courses"

# Preview what would change
python video_title_cleaner.py "/Volumes/Videos/Courses" --preview
```

### Before and After

```
Before:
  Video Part 1_4 Introduction.mp4
  Video Part 2_4 Basics.mp4
  Video Part 3_4 Advanced.mp4
  S01E05 Special Topic.mp4
  S01E06 Wrap Up.mp4

After:
  1 - Introduction.mp4
  2 - Basics.mp4
  3 - Advanced.mp4
  S1E5 - Special Topic.mp4
  S1E6 - Wrap Up.mp4
```
