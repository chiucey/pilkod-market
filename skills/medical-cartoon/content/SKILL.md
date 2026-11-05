---
name: medical-cartoon
description: 
  医学科普动画流水线。能读取PDF或网页提取医学概念，
  生成含分镜和解说词的结构化脚本，
  调用AI生成扁平医学插画并将图像动画化为视频片段，
  生成TTS中文配音，最终打包素材并提供FFmpeg拼接指引。
  触发词：生成科普动画、制作医学视频、读文献做动画、
  把论文做成视频、医学动画
---

# Medical Cartoon Skill

## 流程概览

```
文献输入 → 概念提取 → 科普脚本生成 → AI插画 → AI视频片段 → TTS配音 → 打包拼接
```

## 输入

- PDF文件路径、PubMed URL、或直接给医学主题
- 受众：普通公众（默认）
- 时长：每片段默认6秒

## Step 1 — 文献阅读

PDF：用 extract_content_from_websites 或 Python pdfplumber 提取文本。
URL：用 extract_content_from_websites 工具。

## Step 2 — 生成脚本

```bash
python3 scripts/generate_storyboard.py "主题" \
  --audience public --scenes 10 --duration 2 --output output/script.md
```

生成 Markdown 分镜表，含画面描述（英文详细prompt）、中文解说词、动画指令、时长。

## Step 3 — 生成医学插画

使用 image_synthesize 工具。

**标准 Prompt（英文，详细）：**
```
Flat medical illustration, clean white background, modern healthcare style,
anatomical accuracy, soft pastel colors, professional medical icon design,
no text, no people, [场景具体描述]
```

参数：aspect_ratio=16:9, resolution=1K
保存到：output/scenes/scene_01.png

## Step 4 — 图像转视频

使用 batch_image_to_video 工具，每次最多5个片段。

**动画指令参考：**
- 推进聚焦：smooth zoom in
- 场景过渡：gentle fade in, calm transition
- 图示动画：diagram animation, highlight effect

保存到：output/clips/clip_01.mp4

## Step 5 — TTS配音

使用 batch_text_to_audio 或 synthesize_speech 工具。

参数：lang=zh-CN, voice=female-tianmei, speed=1.0
解说词字数：6秒片段约30~35字，避免超长
保存到：output/voice/voice_01.mp3

## Step 6 — 拼接

所有素材目录：
```
output/
  scenes/      PNG插画
  clips/       MP4视频片段
  voice/       MP3配音文件
  script.md    分镜脚本
  assembly_guide.txt  FFmpeg指引
```

**FFmpeg命令：**
```bash
# 拼接视频
ffmpeg -f concat -safe 0 -i (ls clips/*.mp4 | while read f; do echo "file '$f'"; done) \
  -c:v libx264 -crf 23 -preset fast clips_merged.mp4

# 合并配音
ffmpeg -f concat -safe 0 -i (ls voice/*.mp3 | while read f; do echo "file '$f'"; done) \
  -c:a copy audio_merged.mp3

# 音画合成
ffmpeg -i clips_merged.mp4 -i audio_merged.mp3 \
  -c:v copy -c:a aac -shortest final.mp4
```

## 场景数量参考

| 目标时长 | 场景数 | 图像数 |
|---------|--------|--------|
| 1分钟   | 8~10   | 10张   |
| 2分钟   | 15~18  | 18张   |
| 3分钟   | 22~25  | 25张   |

超过25场景建议分集制作。

## 参考文件

- Prompt模板：references/prompt_templates.md
- 插画风格指南：references/style_guide.md
- 主脚本：scripts/main_pipeline.py
