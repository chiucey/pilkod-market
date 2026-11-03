---
name: setup
description: Remotion project initialization, environment config, project structure.
tags: setup, project, init, install, npx
---

# Remotion Project Setup

## Create Project

```bash
# Official scaffold
npx create-video@latest my-remotion-project
cd my-remotion-project

# Manual setup
npm init -y
npm install remotion @remotion/cli three @remotion/player
npm install -D typescript @types/react
```

## Project Structure

```
my-remotion-project/
├── src/
│   ├── Root.tsx              # Entry component
│   ├── Composition.tsx      # Main video component
│   ├── sequences/
│   │   ├── Intro.tsx         # Opening
│   │   ├── MainContent.tsx   # Body
│   │   └── Outro.tsx         # Closing
│   ├── components/
│   │   ├── Title.tsx         # Title animation
│   │   ├── Chart.tsx         # Chart component
│   │   └── Subtitle.tsx      # Subtitle component
│   └── utils/
│       └── interpolate.ts
├── package.json
└── remotion.config.ts        # Config
```

## remotion.config.ts

```typescript
import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setVideoPixelFormat("yuv420p");
Config.setOverwriteOutput(true);

// Dimensions
// Landscape: width=1920, height=1080
// Portrait:  width=1080, height=1920
// Square:    width=1080, height=1080
```

## Preview & Render

```bash
# Preview (hot reload)
npx remotion preview

# Render MP4
npx remotion render out/MyComposition out.mp4

# Render frames
npx remotion render out/MyComposition out/%04d.png --image-format=png

# Specify fps
npx remotion render out/MyComposition out.mp4 --fps=60
```
