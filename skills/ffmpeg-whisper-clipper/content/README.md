# FFmpeg Whisper 智能剪辑工具

## 功能特点

- **语音转文字**: 使用 OpenAI Whisper 进行高准确度语音识别
- **关键词剪辑**: 基于文字内容智能定位并剪辑相关片段
- **静音去除**: 自动检测并去除音视频中的静音部分
- **格式转换**: 支持多种音视频格式的转换和压缩
- **时间修剪**: 精确的时间范围剪辑

## 安装依赖

```bash
pip install openai-whisper pydub ffmpeg-python
```

确保系统已安装 FFmpeg：
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## 快速开始

### 1. 转录音视频

```bash
python clipper.py --model base transcribe input.mp4
```

### 2. 基于关键词剪辑

```bash
python clipper.py --model base clip input.mp4 --keywords "重要" "关键点" -o output.mp4
```

### 3. 时间范围剪辑

```bash
python clipper.py trim input.mp4 --start 10 --end 60 -o output.mp4
```

### 4. 去除静音

```bash
python clipper.py remove-silence input.mp4 -o output.mp4
```

### 5. 格式转换

```bash
python clipper.py convert input.mp4 -o output.avi --codec libx264
```

## Whisper 模型选择

| 模型 | 参数量 | 速度 | 准确度 |
|------|--------|------|--------|
| tiny | 39M | 最快 | 较低 |
| base | 74M | 快 | 中等 |
| small | 244M | 中 | 较高 |
| medium | 769M | 慢 | 高 |
| large | 1550M | 最慢 | 最高 |

默认使用 `base` 模型，平衡速度和准确度。

## 输出格式

- **SRT**: 带时间戳的字幕文件，可直接用于视频压制
- **JSON**: 完整的转录结果，包含所有片段的时间信息
- **TXT**: 纯文本转录内容

## 高级用法

### 合并相邻片段

使用 `--merge-gap` 参数合并时间间隔较小的片段：

```bash
python clipper.py clip video.mp4 --keywords "关键" -o out.mp4 --merge-gap 3.0
```

### 添加前后缓冲

使用 `--padding` 参数在每个片段前后添加额外时间：

```bash
python clipper.py clip video.mp4 --keywords "重要" -o out.mp4 --padding 1.0
```

### 指定语言

```bash
python clipper.py transcribe input.mp4 --language zh --format json
```

## 工作原理

1. **音频提取**: 如果输入是视频，自动提取音频流
2. **语音识别**: 使用 Whisper 模型进行语音转文字
3. **关键词匹配**: 在转录结果中搜索目标关键词
4. **时间合并**: 合并相邻的匹配片段
5. **FFmpeg 剪辑**: 使用 FFmpeg 按时间范围精确剪辑

## 常见问题

**Q: 转录速度慢怎么办？**
A: 使用更小的模型（如 `--model tiny`）或使用 GPU 加速。

**Q: 如何处理无声视频？**
A: 对于没有音频的视频，可以手动添加音频轨道或使用纯视频剪辑功能。

**Q: 支持批量处理吗？**
A: 可以编写简单的 shell 脚本批量处理多个文件。
