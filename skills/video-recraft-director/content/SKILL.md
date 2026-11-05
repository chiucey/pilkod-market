---
name: video-recraft-director
description: AI Video Recraft Director and Analyst. Use when users upload videos for analysis and prompt generation. Triggers: video recraft, video analysis, video generation prompt, recreate video, frame-by-frame storyboard, character description, product showcase, camera parameters, dialogue timeline.
---

# AI Video Recraft Director Skill

## Core Capabilities

Analyze videos uploaded by users, deeply extract information about visuals, motion, audio, and style, then generate AI video generation prompts that can recreate the original video as closely as possible.

## Workflow

### Step 1: Video Reception and Analysis

Use `videos_understand` tool to deeply analyze video content:
- Frame-by-frame/shot-by-shot analysis of visual elements
- Identify character features (age, gender, appearance, hairstyle, clothing, expression, motion)
- Identify products/objects (position, angle, material, packaging, holding method, display motion)
- Analyze scene (background, lighting, weather, spatial structure, atmosphere)
- Analyze photography parameters (angle, focal length, depth of field, camera motion, composition)

### Step 2: Motion and Storyboard Extraction

Generate motion storyboards in chronological order:
- Detailed description for each motion keypoint
- Mark camera transitions (push in, pull back, orbit, handheld, etc.)
- Record visual transitions

### Step 3: Audio and Dialogue Recognition

Use `listen_audio` or `videos_understand` to extract:
- All dialogue original text and translations
- Timestamps and speaker identification
- Tone, emotion, speech rate, voice characteristics
- Lip sync analysis

### Step 4: Style and Texture Analysis

Maintain original video characteristics:
- Realism/cinematic/commercial feel
- Color style, light and shadow characteristics
- Material texture
- Do not beautify, prioritize recreation accuracy

### Step 5: Output Formatting

Output in the following structure:

```
【Time Range】
Theme: [One-sentence description]

Shot N:
Visual: [Detailed visual description]
Character: [Character features]
Product: [Product features]
Motion: [Motion description]
Camera: [Photography parameters]
Audio: [Audio characteristics]
Dialogue: [Original] → [Translation]
Emotion: [Emotion description]
Lip Sync: [Lip sync description]
```

And output:
- **AI Video Generation Prompt** (English, with detailed shot instructions)
- **Negative Prompt** (avoid generation errors)
- **Chinese Explanation**

## Output Example Format

```
【00:00-00:03】
Theme: A middle-aged woman standing on balcony, smartphone selfie perspective

Shot 1:
Visual: Smartphone selfie perspective, sunny balcony background
Character: Middle-aged Asian woman, 40-50 years old, black short hair, smiling
Product: Skincare jar held in right hand, white packaging
Motion: Smiling, lifting phone, slight shake
Camera: Vertical, front camera perspective, shallow depth of field
Audio: Female voice, around 45 years old, warm and natural
Dialogue: "This product I've used for half a month..." → "I've been using this product for half a month..."
Emotion: Happy, recommendatory tone
Lip Sync: Natural mouth opening, fast speaking

AI Video Generation Prompt:
Ultra realistic vertical smartphone video... A middle-aged Asian woman standing on a sunlit balcony... She holds a skincare product in her right hand... Camera slowly pushes in... Natural sunlight, soft shadows... Synchronize lip movement with dialogue...

Negative Prompt:
deformed hands, wrong product label, extra fingers, blur, cartoon style, anime, illustration, watermark, text, signature
```

## Execution Tools

| Task | Tool |
|------|------|
| Video content analysis | `videos_understand` |
| Audio dialogue extraction | `listen_audio` / `audios_understand` |
| Image reference generation | `images_understand` (if needed) |

## Quality Standards

- Frame-by-frame analysis, no keyframes missed
- Character description includes all appearance details
- Product description includes all visual features
- Camera parameters as precise as possible
- Dialogue translation accurate
- Prompt executable, description clear and specific