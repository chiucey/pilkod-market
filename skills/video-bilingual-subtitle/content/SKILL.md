---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8e7dd2506bab17988a86613450edbc8c
    PropagateID: 8e7dd2506bab17988a86613450edbc8c
    ReservedCode1: 3044022052e6587fe07dda727e8b59b8609a06d6003a8669059db5f2bd8dbce94176d3c702203b8e22612dbc0f27dad259da5009d3e5cbb20f4fba78a9c2c05256c678acabf6
    ReservedCode2: 3044022071900fb4b7f09c31c9a92e57e3b2f2f0f517e2eb23c39d09c9dd0453221aa41f0220468acf08f504c297c6f1cd8eae51f26e6242f54d460d9b8f9c23901223ac2686
author: MiniMax Agent
description: 视频中英双语字幕制作技能 - 使用Whisper语音识别转录视频音频，自动生成SRT字幕文件，并烧录到视频中
name: video-bilingual-subtitle
version: 1.0.0
---

## 技能概述

本技能用于为视频添加中英双语字幕。通过Whisper语音识别技术自动转录音频，结合FFmpeg视频处理工具，实现从音频转写到字幕烧录的完整流程。支持自动语言检测、精准确的时间戳对齐，以及将字幕直接嵌入视频输出。

适用人群：视频创作者、内容运营者、教育工作者、需要制作双语字幕的所有用户

适用场景：教育视频双语字幕、会议录像字幕、外语学习视频、社交媒体内容国际化

---

## 使用场景

1. **教育视频双语字幕制作**：将课程视频添加中英文字幕，方便国际学生观看
2. **会议/访谈字幕**：快速为会议录像生成字幕记录
3. **外语学习视频**：配合双语字幕提升学习效果
4. **社交媒体内容国际化**：为视频内容添加多语言字幕，扩大受众范围
5. **无障碍字幕**：为听力障碍用户提供字幕支持

---

## 核心内容

### 工作流程总览

```
输入视频 → 音频提取 → Whisper转录 → 字幕翻译 → 字幕格式转换 → 烧录到视频 → 输出成品
```

### 第一步：环境准备

#### 必需依赖

| 工具 | 安装命令 | 说明 |
|-----|---------|------|
| FFmpeg | 系统包管理器安装 | 用于音视频处理 |
| Python 3.8+ | - | 运行环境 |
| openai-whisper | `pip install openai-whisper` | 语音识别转录 |
| pydub | `pip install pydub` | 音频处理 |

#### 安装示例

```bash
# Ubuntu/Debian
apt install ffmpeg python3-pip

# 安装Python依赖
pip install openai-whisper pydub
```

### 第二步：音频转录

#### 使用Whisper转录

```bash
# 基本转录命令
python clipper.py --model base transcribe input.mp4 --language zh --output subtitle.srt --format srt
```

#### 参数说明

| 参数 | 说明 | 可选值 |
|-----|------|-------|
| `--model` | Whisper模型大小 | tiny, base, small, medium, large |
| `--language` | 转录语言 | zh（中文）, en（英文）, auto（自动检测） |
| `--format` | 输出格式 | srt, json, text |

#### 模型选择建议

| 模型 | 大小 | 速度 | 精度 | 推荐场景 |
|-----|------|------|------|---------|
| tiny | ~39MB | 最快 | 最低 | 快速预览 |
| base | ~139MB | 快 | 中等 | 一般用途（推荐） |
| small | ~461MB | 中等 | 高 | 重要内容 |
| medium | ~1.5GB | 慢 | 很高 | 精度要求高 |
| large | ~2.9GB | 最慢 | 最高 | 专业场景 |

### 第三步：字幕翻译与格式化

#### SRT字幕格式

```
1
00:00:00,000 --> 00:00:05,000
英文原文

2
00:00:05,000 --> 00:00:08,000
中文翻译
```

#### 双语字幕格式（上下排列）

```
1
00:00:00,000 --> 00:00:05,000
Hello everybody, Welcome to class.
大家好，欢迎来到课堂。

2
00:00:05,000 --> 00:00:08,000
Today we will learn about fan.
今天我们将学习关于风扇的知识。
```

### 第四步：字幕烧录

#### 使用FFmpeg烧录字幕

```bash
# 烧录字幕到视频
ffmpeg -i input.mp4 -vf "ass=subtitles.ass" -c:a copy output.mp4
```

#### ASS字幕格式（支持样式控制）

```
[Script Info]
Title: Bilingual Subtitles
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, Outline, Shadow, Alignment
Style: English, Arial, 24, &H00FFFFFF, 2, 2, 2
Style: Chinese, Microsoft YaHei, 28, &H00FFFFFF, 2, 2, 2

[Events]
Format: Layer, Start, End, Style, Text
Dialogue: 0, 0:00:00.00, 0:00:05.00, English,, 0,0,0,,Hello everybody
Dialogue: 0, 0:00:00.00, 0:00:05.00, Chinese,, 0,0,0,,大家好
```

### 第五步：自动化脚本

#### Python字幕烧录脚本

```python
#!/usr/bin/env python3
import subprocess
import os

def create_ass_subtitle(srt_path, ass_path, styles):
    """创建ASS格式字幕文件"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    ass_content = """[Script Info]
Title: Bilingual Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    blocks = content.strip().split('\n\n')
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            time_line = lines[1]
            times = time_line.split(' --> ')
            start = times[0].replace(',', '.')
            end = times[1].replace(',', '.')
            text = '\n'.join(lines[2:])

            ass_content += f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n"

    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(ass_content)

def burn_subtitles(video_path, ass_path, output_path):
    """烧录字幕到视频"""
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'ass={ass_path}',
        '-c:a', 'copy',
        '-y', output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

if __name__ == "__main__":
    video = "input.mp4"
    srt = "subtitle.srt"
    ass = "subtitle.ass"
    output = "output.mp4"

    create_ass_subtitle(srt, ass)
    if burn_subtitles(video, ass, output):
        print(f"Success: {output}")
```

---

## 示例

### 示例1：基础转录流程

```bash
# 1. 安装依赖
pip install openai-whisper pydub

# 2. 转录音频
python clipper.py --model base transcribe video.mp4 --language auto --output subtitle.srt

# 3. 烧录字幕
ffmpeg -i video.mp4 -vf " subtitles=subtitle.srt" -c:a copy output.mp4
```

### 示例2：批量处理多语言视频

```bash
#!/bin/bash
# 批量转录脚本

for video in videos/*.mp4; do
    filename=$(basename "$video" .mp4)
    echo "Processing: $filename"

    # 转录音频
    python clipper.py --model small transcribe "$video" \
        --language auto \
        --output "subtitles/${filename}_en.srt"

    # 复制并翻译为中文
    cp "subtitles/${filename}_en.srt" "subtitles/${filename}_cn.srt"
    # 编辑cn.srt文件手动翻译，或使用机器翻译

    # 烧录字幕
    ffmpeg -i "$video" \
        -vf "ass=subtitles/${filename}_en.ass" \
        -c:a copy "output/${filename}_en.mp4"
done
```

### 示例3：Python完整流程

```python
import whisper
import subprocess
import json

def transcribe_video(video_path, model_name="base"):
    """转录视频"""
    model = whisper.load_model(model_name)
    result = model.transcribe(video_path)
    return result

def save_srt(result, output_path):
    """保存为SRT格式"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(result['segments'], 1):
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")

def format_timestamp(seconds):
    """格式化时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def burn_subtitle(video_path, srt_path, output_path):
    """烧录字幕"""
    cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f'subtitles={srt_path}',
        '-c:a', 'copy',
        '-y', output_path
    ]
    subprocess.run(cmd, check=True)

# 使用示例
video = "input.mp4"
result = transcribe_video(video, "small")
save_srt(result, "subtitle.srt")
burn_subtitle(video, "subtitle.srt", "output.mp4")
```

---

## 注意事项

### 转录精度相关

1. **模型选择**：精度要求高时使用`small`或`medium`模型，base模型精度有限
2. **音频质量**：清晰、无背景噪音的音频转录效果更好
3. **语言指定**：明确指定语言（如`--language zh`）可提高转录准确率
4. **静音处理**：视频开头的静音部分可能被识别为无意义内容

### 字幕烧录相关

1. **视频编码兼容**：确保FFmpeg支持视频的编码格式，必要时重新编码
2. **字幕位置**：ASS格式可控制字幕位置，SRT格式默认底部居中
3. **字体显示**：确保目标设备安装了字幕使用的字体（中文推荐Microsoft YaHei）
4. **文件编码**：字幕文件必须使用UTF-8编码，避免中文乱码

### 翻译相关

1. **机器翻译局限**：Whisper仅转录音频，不提供翻译功能
2. **手动翻译**：重要内容建议人工校对翻译
3. **双语字幕**：可使用上下排列的双语字幕格式

### 性能相关

1. **GPU加速**：有NVIDIA GPU时可使用CUDA加速，显著提升速度
2. **内存需求**：large模型需要约10GB内存，base模型约1GB
3. **处理时间**：2分钟视频约需30-60秒转录时间（base模型）

---

## 拓展说明

### 相关技能推荐

- `video-trim-skill`：视频剪切与剪辑技能
- `audio-enhance-skill`：音频增强与降噪技能
- `subtitle-edit-skill`：字幕编辑与校对技能
- `video-compress-skill`：视频压缩与格式转换技能

### 进阶功能

1. **时间码微调**：可手动调整字幕时间码以匹配视频
2. **多轨字幕**：烧录多语言字幕轨道，用户可切换语言
3. **语音翻译**：结合语音翻译API实现自动翻译字幕
4. **批量处理**：使用脚本实现多视频并行处理

### 技术扩展方向

1. 支持更多语言的高精度转录
2. 集成AI翻译API实现自动双语字幕
3. 支持SRT/ASS/VTT等多种字幕格式
4. 提供字幕样式自定义界面
