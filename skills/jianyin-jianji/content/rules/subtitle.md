---
name: subtitle
description: SRT/ASS 字幕生成、时间轴对齐、字幕样式设置。
tags: subtitle, srt, ass, caption
---

# 字幕规则

## 工具选择

| 格式 | 适用场景 | 生成方式 |
|---|---|---|
| SRT | 简单字幕、兼容性优先 | Python 文本生成 |
| ASS | 高级样式（描边/动画/卡拉OK）| Python + FFmpeg ASS 滤镜 |

## SRT 字幕生成

```python
import os

def sec_to_srt(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    ms = int((sec % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def generate_srt(lines, output_path):
    """lines: [(start_sec, end_sec, text), ...]"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, (start, end, text) in enumerate(lines, 1):
            f.write(f"{i}\n{sec_to_srt(start)} --> {sec_to_srt(end)}\n{text}\n\n")
```

## TTS 时间轴同步（字幕对齐配音）

```python
# 步骤：配音音频 → Whisper 识别 → 生成 SRT
# 使用 audios_understand 工具：
# prompt: "返回纯 JSON，格式：{segments:[{start,end,text}]}"

# 1. 调用 audios_understand 分析配音
# 2. 提取 segments，生成 SRT
segments = [
    {"start": 0.5, "end": 2.1, "text": "欢迎来到 AI 剪辑教程"},
    {"start": 2.2, "end": 4.0, "text": "今天介绍字幕生成"},
]
lines = [(s["start"], s["end"], s["text"]) for s in segments]
generate_srt(lines, "~/.openclaw/jianyin-work/subs/subtitle.srt")
```

## ASS 高级字幕模板

```python
ASS_HEADER = """[Script Info]
Title: {title}
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{size},&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{events}
"""

def sec_to_ass(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int((sec % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_ass(events, output_path, font="Microsoft YaHei", size=48):
    events_str = ""
    for e in events:
        start = sec_to_ass(e["start"])
        end = sec_to_ass(e["end"])
        events_str += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{e['text']}\n"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ASS_HEADER.format(title="AI Subtitle", font=font, size=size, events=events_str))
```

## 字幕嵌入视频

```bash
# SRT 烧录
ffmpeg -i video.mp4 -vf "subtitles=subtitle.srt:force_style='FontName=Microsoft YaHei,FontSize=48'" \
  -c:v libx264 -crf 20 -c:a copy output_subtitle.mp4

# ASS 烧录（支持样式动画）
ffmpeg -i video.mp4 -vf "ass=subtitle.ass" \
  -c:v libx264 -crf 20 output_ass.mp4
```

## 字幕样式规范

| 平台/场景 | 字体大小 | 位置 | 样式 |
|---|---|---|---|
| 抖音/快手竖屏 | 60~80px | 底部 15% | 白色+3px黑描边 |
| B站横屏 | 36~48px | 底部 10% | 白色+1px黑描边 |
| 电影解说 | 42px | 中下 | 黄字+黑色描边 |
| 教程/课程 | 48px | 底部 15% | 白色+阴影 |
| 综艺/动感 | 56px | 底部 | 渐变+描边+入场动画 |
