---
name: ai-drama-director
description: AI Drama Director - end-to-end automated short drama generation. Use when users request creating AI short dramas, generating short videos, visualizing screenplays, converting scripts to videos, producing story videos, or inputting plot/shot scripts. Supports one-click generation of complete AI short dramas from text scripts. Applicable for short video creation, story visualization, screenplay demonstration, and similar scenarios.
---

# AI Drama Director Skill

## Trigger Conditions

Activate this skill when user requests:
- Create AI short drama / Generate AI video drama
- Script visualization / Storyboard-to-video
- Input plot to generate video
- Auto-generate short video
- Story video production
- Input script to output complete short drama

## Core Workflow

### Step 1: Script Analysis

1. **Parse Input**
   - Extract scene descriptions, character list, dialogues
   - Identify scene types (indoor/outdoor/VFX scenes)
   - Mark emotional tone (warm/tense/suspenseful/cheerful)

2. **Storyboard Design**
   - Break script into independent shots
   - Define per shot: framing, angle, movement, duration
   - Output shot list

### Step 2: Image Generation

1. **Character Consistency**
   - Use reference images for consistent character appearance
   - Record each character's appearance (clothing/hair/features)

2. **Shot Image Generation**
   - Call `image_synthesize` tool
   - Generate each shot per storyboard
   - Save generated images to `assets/shots/` directory

### Step 3: Video Generation & Editing

1. **Shot-level Video Generation**
   - Call `batch_image_to_video` tool
   - Generate video clip for each shot image

2. **Video Assembly**
   - Stitch all clips in storyboard order
   - Add transitions (fade in/out/cross dissolve)
   - Add background music (match emotional tone)

3. **Export Final Video**
   - Output complete AI short drama video

## Tool Usage Specification

| Tool | Purpose | Parameters |
|------|---------|------------|
| `image_synthesize` | Generate single shot frame | prompt, output_file |
| `batch_image_to_video` | Batch image-to-video | image_file_list, prompt_list |
| `batch_text_to_music` | Generate background music | prompt_list, lyrics_list |
| `gen_videos` | Generate pure AI video | prompt, output_file |

## Output Artifacts

- **Shot List**: `docs/shot_list.md`
- **Shot Images**: `assets/shots/shot_001.png` ...
- **Video Clips**: `assets/videos/shot_001.mp4` ...
- **Background Music**: `assets/audio/bgm.mp3`
- **Final Drama**: `output/final_drama.mp4`

## Example Input

```yaml
# Example Script Input
title: "Stellar Drift"
genre: "Sci-Fi/Suspense"
scenes:
  - scene: "Spaceship Cockpit"
    characters: ["Captain Li Ming", "AI Assistant Xiao Zhi"]
    dialogues:
      - speaker: "Li Ming"
        text: "Course anomaly detected, we've deviated from the planned trajectory."
      - speaker: "Xiao Zhi"
        text: "Unknown signal source detected, identification impossible."

# Emotional Tone: tense, suspenseful
```

## Quality Checkpoints

1. **Character Consistency**: Verify character appearance remains consistent
2. **Scene Coherence**: Confirm scene transitions make logical sense
3. **Audio Sync**: Ensure BGM matches video pacing
4. **Duration Control**: Total duration fits short video platform requirements (recommended 60 sec - 5 min)
