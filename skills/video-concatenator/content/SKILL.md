---
name: video-concatenator
description: AI video concatenation tool that automatically sorts and merges multiple video clips by sequence number. Use when users need to merge video segments, create short dramas, concatenate video chapters, or batch combine videos.
---

# Video Concatenator

AI-powered video concatenation tool that automatically sorts and merges multiple video clips by sequence number.

## Features

- **Sequence Sorting**: Automatically identifies sequence numbers in filenames (e.g., scene_01.mp4, scene_02.mp4)
- **Flexible Input**: Supports directory input or file list
- **Format Compatibility**: Supports MP4, MKV, AVI, MOV and other common formats
- **Quality Control**: Configurable output video quality
- **Progress Display**: Real-time concatenation progress

## Usage

### Basic Usage

```bash
python video_concatenator.py --input-dir /path/to/videos --output output.mp4
```

### Advanced Usage

```bash
python video_concatenator.py \
  --input-dir /path/to/videos \
  --output final_video.mp4 \
  --pattern "*.mp4" \
  --quality high
```

### Specify File List

```bash
python video_concatenator.py \
  --files video1.mp4 video2.mp4 video3.mp4 \
  --output final_video.mp4
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--input-dir` | Video directory | - |
| `--files` | Video file list | - |
| `--output` | Output file path | concatenated.mp4 |
| `--pattern` | File matching pattern | *.mp4 |
| `--quality` | Output quality: low/medium/high | high |
| `--delete-input` | Delete source files after concatenation | False |

## Sequence Detection Rules

The tool extracts sequence numbers from filenames using these patterns:
- `scene_01.mp4` → 1
- `video_001.mp4` → 1
- `episode_1.mp4` → 1
- `clip(001).mp4` → 1
- `video001.mp4` → 1
