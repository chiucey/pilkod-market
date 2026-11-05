---
name: ffmpeg-edit
description: FFmpeg 视频剪辑、合并、裁剪、转码、加字幕等核心操作。
tags: ffmpeg, cut, merge, trim, encode, subtitle
---

# FFmpeg 剪辑规则

## 基础检查

```bash
# 查看视频信息
ffprobe -v quiet -print_format json -show_streams -show_format input.mp4

# 关键字段：
# - duration（总时长，秒）
# - width, height（分辨率）
# - codec_name（编码：h264/h265/vp9）
# - r_frame_rate（帧率：30/60）
```

## 常用操作

### 剪切（trim）

```bash
# 从 10s 切到 30s（-ss 前置更快）
ffmpeg -ss 10 -to 30 -i input.mp4 -c:v libx264 -c:a aac -avoid_negative_ts make_zero output.mp4

# 按帧切（更精确）
ffmpeg -i input.mp4 -ss 00:00:10 -to 00:00:30 -c copy output.mp4
```

### 合并（concat）

```bash
# 同编码合并（最快）
ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4

# 不同编码重编码合并
ffmpeg -f concat -safe 0 -i filelist.txt -c:v libx264 -c:a aac output.mp4
```

### 缩放（scale）

```bash
# 缩放到 1080p
ffmpeg -i input.mp4 -vf "scale=1920:1080" -c:a copy output.mp4

# 按比例缩放（不拉伸）
ffmpeg -i input.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease" output.mp4
```

### 格式转换

```bash
# 转为 H.264 + AAC（兼容性最好）
ffmpeg -i input.webm -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k output.mp4

# 转为 H.265（更小体积）
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -c:a aac output.mp4

# 提取音频
ffmpeg -i input.mp4 -vn -c:a libmp3lame -b:a 192k audio.mp3
```

### 旋转/翻转

```bash
# 顺时针旋转 90°
ffmpeg -i input.mp4 -vf "transpose=1" output.mp4

# 水平翻转
ffmpeg -i input.mp4 -vf "hflip" output.mp4
```

### 截取封面

```bash
# 截取第 1s 帧作为封面
ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 cover.jpg

# 截取多帧拼成一张
ffmpeg -i input.mp4 -vf "select=eq(n\,0)+eq(n\,30)+eq(n\,60),scale=400:-1,tile=3x1" cover.jpg
```

## ASS 字幕烧录

```bash
# ASS 字幕嵌入视频（字体必须内嵌）
ffmpeg -i input.mp4 -vf "ass=subtitle.ass" \
  -c:v libx264 -crf 20 -c:a copy \
  output_with_subtitle.mp4

# SRT 字幕嵌入
ffmpeg -i input.mp4 -vf "subtitles=subtitle.srt" \
  -c:v libx264 -c:a aac output.mp4
```

## 音视频合成

```bash
# 配音+视频+BGM 混音
ffmpeg -i video.mp4 -i voice.mp3 -i bgm.mp3 \
  -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.5[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v libx264 -c:a aac output.mp4
```

## 输出规范

| 用途 | 编码 | 分辨率 | 码率参考 |
|---|---|---|---|
| 短视频/朋友圈 | H.264 | 1080×1920（竖）| 8~15 Mbps |
| 正式长视频 | H.264 | 1920×1080 | 15~30 Mbps |
| 压缩/存档 | H.265 | 任意 | CRF 28~32 |
| 封面图 | JPG/PNG | 1280×720 | — |
