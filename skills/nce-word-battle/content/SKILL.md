---
name: nce-word-battle
description: New Concept English Book 1 word battle game. An immersive space shooter style vocabulary learning game where players defeat enemy planes by selecting correct Chinese translations. Triggered when users ask to play English word games, word challenges, NCE vocabulary practice, or gamified word learning.
---

# NCE Book 1 Word Battle Game

## Overview

An immersive aircraft battle-style English vocabulary learning game where players control a fighter jet to destroy enemy planes by correctly translating English words into Chinese.

## Core Features

### 1. Lesson Selection System
- Homepage displays lessons 1-72 with grid layout
- Each lesson contains 8 core vocabulary words
- Visual feedback for completed lessons with star indicators

### 2. Space Shooter Game Engine
- **Player Fighter**: Positioned at bottom center, moves with mouse/touch
- **Enemy Planes**: Spawn randomly from top, move downward
- **Word Display**: Each enemy carries an English word to learn
- **Question System**: 4 Chinese options displayed at bottom

### 3. Vocabulary Learning Mechanism
- English word appears on enemy plane
- 4 Chinese translation options shown at screen bottom
- Correct answer destroys enemy with explosion effect
- Wrong answer or timeout - enemy escapes, lose 1 life

### 4. Immersive Interface Design
- Deep space background with animated star particles
- Neon-colored aircraft and bullets
- Explosion effects and score animations
- Smooth 60fps animation experience

## Game Rules

1. 10 words per game session
2. +10 points for correct answer, no penalty for wrong
3. 3 lives total
4. Perfect score: 100 points for all correct
5. Victory screen shows results and star rating

## Technical Implementation

Pure HTML5 Canvas + JavaScript implementation with no external dependencies for optimal performance and compatibility.

### Data Structure

```javascript
// Lesson data structure
{
  lesson: 1,
  words: [
    { english: "excuse", chinese: "原谅", options: ["原谅", "检查", "例子", "练习"] }
  ]
}
```

### Game States

- MENU: Main menu
- PLAYING: Active gameplay
- PAUSED: Game paused
- GAMEOVER: Game over
- VICTORY: Level completed

## Resource Files

- `/workspace/temp-skills/nce-word-battle/index.html`: Complete game file
