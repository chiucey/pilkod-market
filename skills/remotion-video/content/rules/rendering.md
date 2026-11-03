---
name: rendering
description: FFmpeg rendering parameters, Remotion CLI render commands, output formats.
tags: rendering, ffmpeg, mp4, output, encode
---

# Rendering & Output

## Remotion CLI

```bash
# Basic render
npx remotion render <composition-id> <output-file>

# With fps and codec
npx remotion render MyVideo output.mp4 --fps=60 --codec=h264

# Frame sequence (high quality)
npx remotion render MyVideo ./frames/%04d.png --image-format=png

# Transparent alpha (MOV)
npx remotion render MyVideo output.mov --codec=prores --image-format=png
```

## FFmpeg Post-Processing

```bash
# Remotion frames -> final MP4 (high quality)
ffmpeg -framerate 30 -i ./frames/%04d.png \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  output_h264.mp4

# Voiceover + video + BGM mix
ffmpeg -i output_h264.mp4 -i voice.mp3 -i bgm.mp3 \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.4[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v libx264 -c:a aac \
  final_output.mp4

# Subtitle burn-in
ffmpeg -i final_output.mp4 -vf "ass=subtitle.ass" \
  -c:v libx264 -c:a aac \
  final_with_subs.mp4
```

## Output Specs

| Use | Codec | Resolution | CRF/Bitrate |
|---|---|---|---|
| General | H.264 | 1920x1080 | CRF 20-23 |
| Batch content | H.264 | 1920x1080 | CRF 25-28 |
| Archive | H.264 | 1920x1080 | CRF 15-18 |
| Transparent | Prores/MOV | any | lossless |
