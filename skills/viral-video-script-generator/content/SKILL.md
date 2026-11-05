---
name: viral-video-script-generator
description: 分析短视频爆火原因并生成类似套路的脚本。当用户发送爆火短视频链接，要求分析视频内容、归纳爆火原因、生成类似脚本或制作Word文档时使用。
---

# Viral Video Script Generator Skill

## Overview

This skill helps users analyze why viral short videos succeed and generates three original story scripts following similar patterns, delivered as a Word document.

## Workflow

### Step 1: Receive Video Link
- Accept short video links from users (supports platforms like Douyin, Kuaishou, Xiaohongshu, Bilibili, etc.)
- Confirm link validity

### Step 2: Extract Video Content
- Use `videos_understand` tool to analyze video content
- Extract core information: theme, characters, scenes, dialogue/narration, key plot points

### Step 3: Viral Success Analysis
Analyze the following dimensions:
- **Emotional Triggers**: Elements that resonate with viewers
- **Hook Design**: How the opening captures attention and stops scrolling
- **Pacing Control**: Video rhythm and duration management
- **Content Pattern**: Narrative patterns or creative formulas used
- **Visual/Audio Elements**: Music, effects, visual style
- **Viral Factors**: Elements that drive sharing behavior

### Step 4: Generate Similar Scripts
Based on viral success factors, generate three different but pattern-following original story scripts:
- **Script 1**: Keep core pattern, change setting
- **Script 2**: Keep core pattern, change character relationships
- **Script 3**: Keep core pattern, change plot direction

Each script must include:
- Title
- Recommended video duration
- Shot descriptions
- Dialogue/narration
- Background music suggestions
- Key visual requirements

### Step 5: Generate Word Document
Use `minimax-docx` skill to create a professional Word document containing:
- Video analysis report
- Three original scripts
- Usage instructions and filming tips

## Output Format

Generate a complete Word document with the following sections:

```
1. Video Analysis Report
   - Basic video information
   - In-depth viral success analysis
   - Key success factors summary

2. Original Script One
   - Title and overview
   - Detailed script content
   - Filming points

3. Original Script Two
   - Same structure

4. Original Script Three
   - Same structure

5. Appendix: Filming Tips and Precautions
```

## Trigger Conditions

- User sends a short video link
- User asks to "analyze why the video went viral"
- User asks to "generate similar scripts"
- User asks to "create a Word document"
- User asks to "analyze the short video"

## Limitations and Notes

- Only analyze videos that users actively provide
- Ensure generated scripts are original, not direct copies of original video content
- Respect originality - only borrow viral patterns, not copy specific content
- If video is inaccessible, prompt user to provide alternative links or video files
