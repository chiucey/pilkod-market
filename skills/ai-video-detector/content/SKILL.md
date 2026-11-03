---
name: ai-video-detector
description: AI video/image detection tool based on browser-side heuristics. Use when users ask to analyze videos/images for AI generation characteristics, detect deepfakes, assess media provenance risk, or identify synthetic content. Also triggers for requests about Sora, Runway, Pika, Kling video analysis, or checking if content is AI-generated.
---

# AI Video Detector Skill

A comprehensive tool for analyzing videos and images to assess media provenance risk and detect potential AI-generated characteristics.

## Core Capabilities

### 1. Video Analysis
- **Frame sampling**: Extract 8 evenly-spaced frames from video
- **Visual features**: Mean luma, edge density, saturation analysis
- **Temporal features**: Frame delta variance, frozen frame detection
- **Audio analysis**: Spectral flatness, RMS variance, zero-crossing rate
- **Provenance scanning**: Byte-level scan for C2PA, Content Credentials, XMP markers

### 2. Image Analysis (via video mode)
- Single frame analysis with visual feature extraction
- Edge density and saturation profiling
- Provenance metadata scanning

### 3. Media Metadata Extraction
- Resolution, duration, frame rate detection
- File size and MIME type identification
- Audio track presence detection

## Supported AI Video Models (Detection Database)

| Model | Max Resolution | Max Duration |
|-------|---------------|--------------|
| Sora | 1920x1080 | 60s |
| Runway Gen-3 | 1368x768 | 10s |
| Pika 2.0 | 1280x720 | 10s |
| Kling 1.5 | 1920x1080 | 5s |
| Veo 2 | 1920x1080 | 8s |
| HunyuanVideo | 1280x720 | 15s |
| Seedance 2 | 2048x2048 | 10s |

## Risk Scoring System

### Score Ranges
- **0-39**: Low risk - No significant anomalies detected
- **40-59**: Medium risk - Multiple anomalies present
- **60-100**: High risk - Anomalies concentrated

### Detection Categories
1. **Provenance** (权重: 0.8): C2PA/XMP metadata markers
2. **Visual** (权重: 0.9): Edge density outliers, saturation anomalies
3. **Temporal** (权重: 1.0): Frozen frames, low variation
4. **Audio** (权重: 0.7): Noise-like spectrum, flat envelope
5. **Metadata** (权重: 0.8): Unusual frame rates

## Usage Workflow

### Step 1: Input Media
```
Accept video formats: MP4, WebM, MOV, AVI
Accept audio formats: MP3, WAV, M4A, OGG
Max file size: 500MB
```

### Step 2: Analysis Process
1. Load media metadata
2. Sample frames/waveform
3. Extract visual/temporal/audio features
4. Scan for provenance markers
5. Generate risk assessment

### Step 3: Interpretation
```
Output includes:
- Overall risk score (0-100)
- Evidence items with titles and observations
- Confidence level (High/Medium/Low)
- Limitations disclaimer
```

## Key Limitations

**Important**: This tool uses browser-side heuristics only:
- Cannot establish authorship or provenance definitively
- Results should be used for initial triage only
- Pair with source verification and forensic review for critical decisions
- Compression, editing, and screen recording can trigger anomalies

## Implementation Files

- `src/App.tsx`: Main React component
- `src/lib/analysis.ts`: Feature extraction and scoring
- `src/lib/media.ts`: Media handling utilities
- `src/lib/translations.ts`: i18n support (Chinese/English)
- `src/types/analysis.ts`: TypeScript type definitions

## Language Support

- Chinese (zh) - Default
- English (en)

Toggle via language switcher in UI.

## Example Triggers

- "分析这个视频是否AI生成"
- "Check if this image is fake"
- "检测deepfake"
- "Is this video from Sora?"
- "Assess media provenance risk"
- "Check for AI generation artifacts"
- "分析视频真实性"
