# 视频字幕生成器使用指南

## 安装依赖

```bash
# 安装 Whisper
pip install openai-whisper

# 安装 FFmpeg (Linux/macOS)
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg

# Windows:
# 从 https://ffmpeg.org/download.html 下载并添加到 PATH
```

## 快速开始

### 基本用法

```bash
# 为视频生成字幕文件
python scripts/generate_subtitles.py video.mp4

# 使用更大的模型提高准确性
python scripts/generate_subtitles.py video.mp4 -m medium

# 同时生成字幕文件并烧录到视频
python scripts/generate_subtitles.py video.mp4 --burn
```

### 高级选项

```bash
# 自定义字体大小
python scripts/generate_subtitles.py video.mp4 --burn --font-size 64

# 自定义字体颜色
python scripts/generate_subtitles.py video.mp4 --burn --font-color yellow

# 指定输出目录
python scripts/generate_subtitles.py video.mp4 -o /path/to/output/
```

## Whisper 模型选择

| 模型 | 参数量 | 英文准确率 | 中文准确率 | 推荐场景 |
|------|--------|-----------|-----------|---------|
| tiny | 39M | ~17% | ~17% | 快速测试 |
| base | 74M | ~25% | ~25% | 默认推荐 |
| small | 244M | ~50% | ~50% | 较高准确性 |
| medium | 769M | ~65% | ~65% | 专业用途 |
| large | 1550M | ~75% | ~75% | 最高准确性 |

## 字幕样式自定义

可通过修改脚本中的样式参数来自定义字幕外观：

```python
# 在 burn_subtitles 函数中修改
style = f"FontSize={font_size},"  # 字体大小
style += f"PrimaryColour=&H{color},"  # 颜色
style += "Alignment=2,"  # 位置 (2=底部居中)
style += "MarginV=50"  # 距底部边距
```

## 常见问题

### Q: 识别结果不准确怎么办？
A: 尝试使用更大的 Whisper 模型（如 medium 或 large），或使用 GPU 进行推理。

### Q: 如何处理多语言视频？
A: Whisper 支持多语言自动检测，如需指定语言可修改 transcribe_audio 函数。

### Q: 字幕时间轴不准怎么办？
A: 检查音频质量，确保视频中有清晰的语音。
