---
name: transitions
description: Scene transitions in Remotion: fade, slide, zoom, dissolve.
tags: transition, fade, slide, dissolve, wipe
---

# Scene Transitions

## Fade to Black
const opacity = interpolate(frame,[fadeStart,fadeStart+30],[1,0]);
<div style={{opacity,background:"black",position:"absolute"}} />

## Slide Transition
<div style={{transform:translateX(interpolate(frame,[0,30],[-1920,0]))}} />

## Cross-dissolve
opacity from 1 to 0 over 15-30 frames between scenes

## Scale Zoom
scale from 1.0 to 1.1 with opacity fade
