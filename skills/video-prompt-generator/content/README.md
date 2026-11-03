---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d95c1d9c58397d527137c952521975cf
    PropagateID: d95c1d9c58397d527137c952521975cf
    ReservedCode1: 304502203eab48c5a671c550e5500343b5ff9f249f348d2c7319f9d2e588e6b0b465a82c022100e6ea5ade6af678036e28a692fe863bdd40e761b9abd4d683da7ca1d04c6b803e
    ReservedCode2: 304602210087ca63d5102b21bd336a3a55e0090b62f5a1dfa72abf4491a6b25b5c827c79bd0221009e429af89f196e31639ecdca44cf6bc1f1488f674b8dc7c0ef58cf433557232e
---

# Video Prompt Generator Skill

## Overview

This skill generates professional video prompts for e-commerce product showcases, supporting both **Kling** (Chinese) and **Veo** (English JSON) platforms.

## Usage

### Input Required
- **Reference Image(s)**: First frame or first frame + last frame images
- **Camera/Shot Description**: Desired camera movement and scene description

### Output Formats

#### 1. Kling (Chinese Natural Language)
Generates natural Chinese prompts optimized for Kling video generation platform.

#### 2. Veo (English JSON)
Generates structured JSON prompts for Veo platform with:
- Scene description
- Camera movement
- Lighting conditions
- Visual style
- Motion details

## Key Features

- **Professional Terminology**: Maps common descriptions to standard cinematographic terms
- **E-commerce Optimized**: Tailored for product showcase scenarios
- **Quality Control**: Includes negative prompts to avoid common issues
- **Multi-platform**: Supports both Chinese and English output formats

## Common Camera Movements Supported

| Category | Movements |
|----------|-----------|
| Push/Pull | Dolly in, Dolly out, Push to close-up |
| Pan | Pan left/right, Tilt up/down |
| Orbit | Clockwise orbit, Counterclockwise orbit |
| Tracking | Follow shot, Side tracking |
| Complex | Push + Orbit, Pull + Rise |

## Quality Guidelines

### Always Include
- Stable camera movement
- Natural lighting transitions
- Subject structure preservation
- Continuous shot (no cuts)

### Always Avoid
- Screen flicker
- Structural distortion
- Unwanted objects
- Jump cuts
