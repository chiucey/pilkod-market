---
name: ffmpeg-whisper-clipper
description: 智能音视频剪辑工具，结合 FFmpeg 和 Whisper 语音识别实现基于文字的精准剪辑。适用于视频后期制作、播客剪辑、会议录音整理等场景。触发词：视频剪辑、音频剪辑、whisper剪辑、语音转文字剪辑
---

# FFmpeg Whisper 智能剪辑工具

## 技能概述

本工具将 FFmpeg 的强大音视频处理能力与 Whisper 的精确语音识别技术相结合，提供基于文字内容的智能剪辑体验。

## 核心功能

### 1. 语音转文字转录
- 支持多种 Whisper 模型（tiny/base/small/medium/large）
- 输出带时间戳的 SRT/JSON 格式字幕
- 支持中文、英文、日文等 100+ 语言

### 2. 基于文字的精准剪辑
- 按关键词/句子选择剪辑片段
- 支持时间范围精确剪辑
- 自动去除静音/空白片段

### 3. 音频/视频处理
- 视频格式转换与压缩
- 音频提取与降噪
- 片段合并与分割

## 使用方法

### 基本转录
```bash
python clipper.py transcribe input.mp4 --model base --output srt
```

### 关键词剪辑
```bash
python clipper.py clip input.mp4 --keywords "重要" "关键点" --model base
```

### 时间范围剪辑
```bash
python clipper.py trim input.mp4 --start 00:01:30 --end 00:05:45 --output clip.mp4
```

## 依赖要求

- Python 3.8+
- FFmpeg（系统安装）
- openai-whisper
- pydub
- ffmpeg-python

## 输出格式

- SRT 字幕文件（带时间戳）
- JSON 转录结果
- 剪辑后的视频/音频文件
