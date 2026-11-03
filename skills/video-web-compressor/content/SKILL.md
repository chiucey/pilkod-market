---
name: video-web-compressor
description: Compresses video files for web transmission. Use this skill when the user wants to reduce video file size while maintaining good quality for web playback, typically by downsampling to 1080p, lowering frame rate to 24fps, and optimizing for streaming.
---

# Video Web Compressor

This skill provides a standardized workflow for compressing video files to make
them suitable for web transmission and playback.

## Workflow

When a user requests video compression for web use, follow these steps:

1. **Analyze Input**: Use `ffprobe` to check the current resolution,
    frame rate, and bitrate of the source file.
2. **Execute Compression**: Use `ffmpeg` with the following optimized
    parameters:
   - **Resolution**: Scale to 1080p height (`-vf "scale=-2:1080"`) unless
   the source is already smaller.
   - **Frame Rate**: Reduce to 24fps (`fps=24`) to save bandwidth while 
   maintaining cinematic motion.
   - **Codec**: Use H.264 (`-c:v libx264`).
   - **Quality**: Set CRF to 24 (`-crf 24`) for a good balance between 
   quality and file size.
   - **Preset**: Use `medium` for efficient encoding.
   - **Web Optimization**: Use `-movflags +faststart` to move metadata 
   to the beginning of the file, enabling instant playback (streaming).

## Standard Command

```bash
ffmpeg -i "input_file.mov" -vf "scale=-2:1080,fps=24" -c:v libx264 -crf 24 -preset medium -movflags +faststart "output_file.mp4"
```

## Considerations

- **Aspect Ratio**: Always use `scale=-2:1080` to maintain the original aspect
ratio and ensure the width is divisible by 2 (required by many encoders).
- **Audio**: If the source has audio, it will be copied by default or 
re-encoded if necessary. To strip audio, add `-an`.
- **Naming**: Prefer `.mp4` as the output extension for maximum web 
compatibility.
