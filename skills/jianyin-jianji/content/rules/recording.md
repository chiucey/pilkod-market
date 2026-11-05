---
name: recording
description: 录屏与智能缩放（参考 jianying-editor-skill upstream）。
tags: recording, screen, smartzoom, capture
---

# 录屏与智能缩放

## Linux 录屏方案

```bash
# FFmpeg 屏幕录制（X11）
ffmpeg -f x11grab -i :0.0 -c:v libx264 -preset ultrafast -r 30 \
  -s 1920x1080 output_screen.mp4

# 带系统音频录制
ffmpeg -f x11grab -i :0.0 -f pulse -i default \
  -c:v libx264 -c:a aac output_with_audio.mp4
```

## 智能缩放（点击位置放大）

jianying-editor-skill（Windows）支持鼠标点击位置自动放大关键帧。
Linux 环境可使用 FFmpeg zoompan 滤镜：

```bash
# 放大 1.5x，居中
ffmpeg -i recording.mp4 -vf \
  "zoompan=z='min(zoom+0.001,1.5)':d=30:x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2)" \
  zoomed.mp4
```

## 推荐工具

| 工具 | 平台 | 特点 |
|---|---|---|
| FFmpeg x11grab | Linux | 免费、命令行 |
| OBS Studio | 全平台 | 功能强、推流 |
| Scarlett 2i2 采集卡 | 硬件 | 游戏机/相机采集 |
