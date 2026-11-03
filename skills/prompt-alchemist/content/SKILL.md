---
name: prompt-alchemist
description: AI painting inspiration parser - reverse engineer any image into professional structured prompts. Use when users upload images and want to generate AI art prompts, analyze image features, extract art styles, or perform style transfer.
---

# Prompt Alchemist - AI Art Inspiration Parser

## Overview

**Prompt Alchemist** is a professional AI painting Prompt reverse engineering tool. It can "dissolve" any image into editable Prompt recipes, supporting complete recreation or style transfer creation.

## Core Features

### 1. Intelligent Image Analysis
Automatically extract six-dimensional features:
- **Subject** - Core visual element identification
- **Composition** - Viewpoint, framing, layout rules
- **Lighting** - Light source type, quality, atmosphere
- **Color Palette** - Extract 5-6 dominant colors
- **Art Style** - Painting style, genre recognition
- **Quality Modifiers** - Professional generation keywords

### 2. Structured Prompt Generation
- Four Prompt templates: Standard, Detailed, English, Minimal
- One-click copy to clipboard
- Export as Markdown format

### 3. Style Transfer
- Extract original image style
- Input new subject description
- Auto-generate combined Prompt
- Original vs New Prompt comparison

## Usage

### Basic Analysis Flow
1. User uploads image (JPG/PNG/WEBP)
2. Click "Start Analysis" button
3. System extracts six-dimensional features
4. Generate structured Prompt
5. User can edit parameters
6. Copy for use or perform style transfer

### Style Transfer Flow
1. Complete basic analysis
2. Enter new subject description in "Style Transfer" area
3. Click "Apply Style" button
4. Get Prompt combining original style with new subject

## Output Format

### Structured Analysis Result
```json
{
  "subject": "Subject description",
  "composition": "Composition method",
  "lighting": "Lighting atmosphere",
  "colorPalette": ["#HEX1", "#HEX2", ...],
  "artStyle": "Art style",
  "qualityModifiers": ["Quality modifier 1", "Quality modifier 2", ...]
}
```

### Recommended Prompt Format
```
[Quality modifiers], [Subject], [Composition], [Lighting], [Colors], [Style] style
```

## Use Cases

| Scenario | Prompt Type |
|----------|-------------|
| Recreate image | Full dimensional Prompt |
| Extract style | Style + Lighting + Colors only |
| Change subject | Style transfer |
| Learning reference | Structured analysis |

## Design Features

- **Dark Lab Theme** - Mysterious tech aesthetic
- **Neon Gradient Effects** - Modern visual design
- **Fully Responsive** - Mobile-friendly
- **Real-time Editing** - Adjustable parameters

## Technical Stack

- React 18 + TypeScript
- Tailwind CSS
- Canvas API color extraction
- AI analysis engine simulation
