---
name: video-soundtrack
description: 为视频创作者提供智能配乐服务。当用户上传视频并选择情绪、气氛或场景类型时使用。支持悬疑、温馨、史诗、欢快、悲伤、浪漫、紧张、励志等多种情绪风格，自动在视频的关键节点插入节奏匹配的背景音乐。触发词：配乐、视频配乐、背景音乐、BGM、音乐添加。
---

# Video Soundtrack Generator

Generate mood-matched background music for videos using MiniMax Music 2.6 model.

## Workflow

### Step 1: Video Analysis
- Accept video file (MP4, MOV, AVI, WebM)
- Analyze video content: scene types, pacing, visual mood
- Identify key moments for music transitions

### Step 2: Mood Selection
User provides one or more of:
- Primary emotion (required): suspenseful, warm, epic, cheerful, melancholic, romantic, tense, inspirational
- Atmosphere: cinematic, documentary, commercial, social_media
- Tempo preference: slow, medium, fast, dynamic

### Step 3: Music Generation
Use MiniMax Music 2.6 to generate tracks matching:
- Selected mood and atmosphere
- Video duration and pacing
- Transition points detected in analysis

### Step 4: Music Placement
- Insert music at identified key moments
- Apply fade in/out at transitions
- Match music intensity to video energy levels

### Step 5: Output
- Export video with embedded soundtrack
- Provide separate audio track option
- Include music metadata (tempo, key, duration)

## Supported Moods

| Emotion | Description | Best For |
|---------|-------------|----------|
| Suspenseful | Tension-building, mysterious | Thriller, horror, drama |
| Warm | Cozy, heartwarming | Family, lifestyle, testimonials |
| Epic | Grand, powerful | Action, trailer, documentary |
| Cheerful | Upbeat, happy | Vlogs, ads, tutorials |
| Melancholic | Sad, reflective | Drama, memorial, poetry |
| Romantic | Love, tender | Weddings, couples, proposals |
| Tense | High anxiety, urgent | Action, sports, breaking news |
| Inspirational | Uplifting, motivational | Presentations, sports clips |

## Example Usage

```
User: "为我的旅游视频添加配乐，选择温馨浪漫的风格"
Agent: [Analyze video] → [Generate warm romantic track] → [Insert at key moments] → [Export final video]
```

## Technical Notes

- Video format: MP4 (H.264/H.265), MOV, AVI, WebM
- Max video duration: 30 minutes
- Audio output: AAC 320kbps
- Music generation: MiniMax Music 2.6 API
