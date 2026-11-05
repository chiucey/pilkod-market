---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: bb0bda3d42a143be50171b7eab1a655f
    PropagateID: bb0bda3d42a143be50171b7eab1a655f
    ReservedCode1: 3045022100f622de942493fda3d4860aa8f2d2fa763f98241ba9dd629a262839845e78d10202202fa79ade63851181621c91f145dd5ef77133bbc0bd04f8a6b2fd02eac470a23b
    ReservedCode2: 3045022100edad7a9be946b4d48e7fbd2692f9beab2c6bca2f857a9e4d718ebf34f6e301e70220547f5ebcf03699640945b4f87eb0fc096f46649e59326a25a8ff482a88d20075
allowed-tools:
    - Read
    - Edit
    - Write
    - Grep
    - Glob
    - Bash
    - bitwize-music-mcp
argument-hint: <album-name> [genre] or <action> <parameters>
description: Professional AI music producer skill for creating, mixing, mastering, and releasing music. Use when user wants to create a new album, write lyrics, generate music with Suno, mix audio, master tracks, or release to streaming platforms.
model: claude-opus-4-6
name: ai-music-producer
prerequisites:
    - setup
---

# AI Music Producer - Professional Music Production Agent

## Overview

This is a comprehensive AI music production agent that guides users through the complete music production workflow: from album concept development, through lyrics writing, music generation, mixing, mastering, and final release to streaming platforms.

## Core Workflow

### Phase 1: Album Creation
1. `/new-album [name] [genre]` - Create album directory structure
2. `/album-conceptualizer` - Plan album concept and tracklist through 7 phases

### Phase 2: Track Production
3. `/lyric-writer` - Write lyrics for each track
4. `/pronunciation-specialist` - Fix pronunciation issues
5. `/lyric-reviewer` - Quality control check
6. `/suno-engineer` - Create Suno prompts and generate music

### Phase 3: Audio Processing
7. `/mix-engineer` - Polish audio (optional)
8. `/mastering-engineer` - Master tracks for streaming (-14 LUFS)

### Phase 4: Release
9. `/album-art-director` - Create album artwork
10. `/promo-writer` - Generate social media copy
11. `/release-director` - Release to streaming platforms

## Supported Music Genres

Over 200 genres supported including:
- Pop, Rock, Hip-Hop, Electronic, Country, Jazz, Classical
- Latin, World Music, K-Pop, J-Pop, Afrobeats
- Metal, Punk, Folk, R&B, Soul, Blues
- And many subgenres

## Key Features

### Lyric Writing
- Professional prosody and rhyme craft
- 13-point quality checklist
- Pronunciation fixing for Suno
- Documentary/commercial standards

### Music Generation (Suno)
- V5 prompt optimization
- Section tag usage ([Verse], [Chorus], etc.)
- Genre selection with 500+ options
- Voice character descriptions

### Audio Mastering
- -14 LUFS streaming standard
- Per-genre presets
- True peak < -1.0 dBTP
- Multi-system testing

### Release Management
- Pre-release QA checklist
- Distributor integration
- Platform-specific optimization
- Social media promotion

## Quick Commands

| Command | Description |
|---------|-------------|
| `/new-album [name] [genre]` | Create new album |
| `/album-conceptualizer` | Plan album concept |
| `/lyric-writer` | Write lyrics |
| `/suno-engineer` | Generate music |
| `/mastering-engineer` | Master audio |
| `/release-director` | Release album |

## Tips

1. Always start with `/new-album` to create proper structure
2. Run `/lyric-reviewer` before Suno generation
3. Master to -14 LUFS for streaming compatibility
4. Use `/help` to see all available skills