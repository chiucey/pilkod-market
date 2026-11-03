---
name: video-subtitle-extractor
description: 提取视频字幕并生成可下载文件。当用户上传视频并要求提取字幕、下载字幕文件、了解视频内容概要时使用。触发短语：提取字幕、下载字幕、视频字幕、视频内容摘要。
---

# Video Subtitle Extractor

Extract subtitles from uploaded video files and generate downloadable subtitle files.

## Capabilities

- **Video Analysis**: Analyze video content using AI to understand speech
- **Subtitle Extraction**: Extract speech content and generate timestamped subtitles
- **Multiple Formats**: Support SRT and TXT export formats
- **Content Summary**: Provide video content overview for quick understanding

## Usage

When user uploads a video and requests:
1. Extract subtitles from the video
2. Download subtitle files
3. Get a summary/overview of video content

## Process

### Step 1: Video Upload & Analysis

Accept video file (MP4, AVI, MOV, MKV supported) and analyze using `videos_understand` tool:

```
Analyze this video and extract all spoken content. Return the complete transcription with timestamps if available.
```

### Step 2: Subtitle Generation

Based on transcription, generate structured subtitles:

1. **Parse transcription** into logical segments
2. **Add timestamps** (estimated based on speaking pace ~3-4 words per second)
3. **Format as SRT** (SubRip format) with sequence numbers, timestamps, and text

### Step 3: File Generation

Create downloadable files:

| Format | Description | File Extension |
|--------|-------------|----------------|
| SRT | SubRip subtitle with timestamps | `.srt` |
| TXT | Plain text transcription | `.txt` |

### Step 4: Content Summary

Generate a brief summary (3-5 sentences) explaining the video's main topics and key points.

## Output Format

Provide user with:
1. **Download Links**: Direct download buttons/links for SRT and TXT files
2. **Preview**: First 5-10 subtitle entries as preview
3. **Summary**: Brief content overview

## Technical Implementation

Use Python with:
- `mcp__matrix__videos_understand` for video content analysis
- File generation with proper encoding (UTF-8)
- Temporary file storage for downloads

## Error Handling

- If video cannot be processed: Inform user and suggest alternative formats
- If no speech detected: Notify user that the video may not contain extractable audio
- For long videos (>30min): Process in segments and combine results
