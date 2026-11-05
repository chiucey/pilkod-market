---
name: voice-clone
description: Clone and replicate human voices for text-to-speech synthesis. Use when users ask to clone a voice, replicate speech patterns, create voice overs, generate audio with a specific person's voice, or convert text to speech using a custom voice model.
---

# Voice Clone Skill

## Overview

This skill enables voice cloning and text-to-speech synthesis, allowing users to replicate human voices from audio samples and generate speech with the cloned voice.

## Core Capabilities

- **Voice Sample Analysis**: Process audio samples to extract voice characteristics
- **Voice Model Training**: Create a voice model from reference audio
- **Text-to-Speech**: Generate speech with cloned voice from text input
- **Multi-language Support**: Support for Chinese, English, and other languages

## Usage Workflow

### Step 1: Voice Sample Collection

Collect high-quality voice samples:
- Minimum 30 seconds of clear speech
- Multiple sentences preferred
- Background noise should be minimal
- File format: MP3, WAV, or FLAC

### Step 2: Audio Processing

Process the voice sample:
1. Use `audios_understand` to analyze voice characteristics
2. Validate audio quality and duration
3. Extract voice embedding features

### Step 3: Voice Cloning

Generate speech with the cloned voice:
1. Prepare text input
2. Configure voice parameters (speed, pitch)
3. Generate audio using voice synthesis
4. Output as MP3 format

## Supported Input Methods

| Method | Description |
|--------|-------------|
| File Upload | Upload audio file directly |
| URL | Provide audio URL |
| Recording | Real-time audio recording |

## Output Specifications

- **Format**: MP3 (default)
- **Sample Rate**: 44.1kHz
- **Channels**: Mono/Stereo selectable

## Best Practices

1. Use clear, high-quality voice samples
2. Avoid samples with heavy background noise
3. Include diverse phonetic patterns in reference audio
4. Test with short phrases first before full synthesis

## Examples

### Basic Voice Cloning
```
User: Clone this voice and say "Hello, how are you?"
Action: Process voice sample → Generate speech with cloned voice
```

### Voice Profile Creation
```
User: Create a voice model from my audio file
Action: Analyze audio → Extract voice features → Create voice profile
```

### Multi-language Synthesis
```
User: Read this Chinese text with my cloned voice
Action: Load voice model → Process text → Generate audio
```

## Error Handling

- **Low Quality Audio**: Request better quality samples
- **Insufficient Duration**: Require minimum 30 seconds
- **Processing Failure**: Retry with alternative audio source
