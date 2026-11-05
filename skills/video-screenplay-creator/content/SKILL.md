---
name: video-screenplay-creator
description: Video analysis and screenplay creation skill. Use when users provide video files (mp4/mov/avi) and request video frame analysis, short drama screenplay creation, or storyboard script制作. Triggers: analyze video, create screenplay, make storyboard, short drama script, video to screenplay, 视频分析, 剧本创作.
---

# Video Screenplay Creator Skill

## Workflow

### Step 1: Video Analysis

Use `videos_understand` tool to analyze video, strictly following time sequence:

1. **Scene Content**: Describe each shot specifically
2. **Dialogue**: Complete transcription of all dialogue (distinguish: dialogue, OS inner monologue, OV voiceover)
3. **Actions & Expressions**: Character movements, expression changes
4. **Scene Transitions**: Time markers
5. **Special Effects**: Breaking fourth wall, OS monologue, etc.

**Important**: Only record content that actually exists in the video. Do not add any speculation or content not in the source.

### Step 2: Screenplay Creation

Create screenplay following this format:

```
### Scene Number Time IN/OUT Location

**Characters:** Character List

△Action description (starts with △ symbol)

**Character**：（tone/state）：Dialogue
```

**Dialogue Type Guidelines**:
- Normal Dialogue: `**Character**：（tone）：Line`
- Inner Monologue: `**CharacterOS**：Line`
- Voiceover: `**Character**（OV）：Line`
- Breaking Fourth Wall: `**Character**（breaking fourth wall）：Line`

### Step 3: Storyboard Creation

Create storyboard table with:

| Shot # | Duration | Shot Type | Description | Dialogue/Voiceover | Notes |
|--------|----------|-----------|-------------|-------------------|-------|
| 1 | 3s | Close-up | Character expression | "Line..." | - |

### Step 4: Output Documents

Generate:
- `episode_X_screenplay.md` - Complete screenplay
- `episode_X_storyboard.md` - Storyboard script
- `episode_X_combined.docx` - Word combined version (optional)

## Reference Format

See `references/screenplay_format.md`
