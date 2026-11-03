---
name: music-identifier
description: "识别视频或音频文件中的背景音乐（BGM）。支持从视频提取音频轨道，通过音乐指纹识别API查找歌曲名称、歌手、专辑等信息。支持识别后自动下载音乐。触发词：识别BGM、找背景音乐、这是什么歌、音乐识别、视频BGM、bgm识别、歌曲识别、下载音乐、下载BGM"
description_zh: "识别视频/音频中的背景音乐BGM，通过音频指纹技术查找歌曲信息，支持自动下载"
version: 1.1.0
---

# Music Identifier — 音乐/BGM 识别器

> 从视频中找出背景音乐的名字，识别后可直接下载。支持本地视频/音频文件，调用在线音乐识别API。

## 功能

- 🎵 从视频文件中提取音频轨道
- 🔍 通过音频指纹识别歌曲（歌名、歌手、专辑）
- ⬇️ 识别成功后自动下载音乐（通过 yt-dlp 从 YouTube 搜索）
- 📋 支持多种识别引擎后端
- 💾 自动缓存识别结果，避免重复请求

## 支持的识别引擎

| 引擎 | 免费额度 | 需要API Key | 特点 |
|:---:|---:|:---:|---|
| **AudD** | 100次/天 | 可选（无Key也能用） | 最推荐，免费额度大 |
| **ACRCloud** | 100次/天 | ✅ 需要 | AHA Music底层引擎，精度高 |

## 快速使用

### 1. 识别视频中的BGM

```bash
python3 scripts/identify.py "/path/to/video.mp4" --engine audd
```

### 2. 识别音频文件

```bash
python3 scripts/identify.py "/path/to/audio.mp3" --engine audd
```

### 3. 指定音频片段（跳过前N秒，避免片头无音乐的空白）

```bash
python3 scripts/identify.py "/path/to/video.mp4" --engine audd --skip 5 --duration 30
```

### 4. 识别并自动下载音乐

```bash
python3 scripts/identify.py "/path/to/video.mp4" --engine audd --download
```

### 5. 指定下载目录

```bash
python3 scripts/identify.py "/path/to/video.mp4" --engine audd --download --download-dir ~/Desktop/music
```

## 参数说明

| 参数 | 默认值 | 说明 |
|:---|:---:|---|
| `--engine` | `audd` | 识别引擎：`audd` 或 `acrcloud` |
| `--skip` | `0` | 跳过开头多少秒（避免片头静音） |
| `--duration` | `30` | 识别片段长度（秒）|
| `--api-key` | 环境变量 | API Key（可选）|
| `--output` | 控制台 | 输出格式：`json` 或 `text` |
| `--download` | 关闭 | 识别成功后自动下载音乐 |
| `--download-dir` | ~/Music/music-identifier/ | 下载保存目录 |

## 使用流程

### Step 1: 提取音频（自动执行）

脚本会自动用 ffmpeg 从视频中提取音频。如果系统没有 ffmpeg，需要安装：

```bash
brew install ffmpeg  # macOS
```

### Step 2: 音频指纹识别

将音频片段发送到识别引擎API，返回匹配结果：

```json
{
  "title": "Holding Court",
  "artist": "Audiomachine",
  "album": "Quartetra",
  "release_date": "2015-01-01",
  "label": "Audiomachine",
  "confidence": 0.92
}
```

## API Key 配置

### AudD（推荐，可免Key使用）

- 注册：https://dashboard.audd.io/
- 免费额度：100次/天
- 设置环境变量：
  ```bash
  export AUDD_API_TOKEN="your-token-here"
  ```

### ACRCloud

- 注册：https://www.acrcloud.com/
- 免费额度：100次/天
- 需要获取 `host`、`access_key`、`access_secret`
- 设置环境变量：
  ```bash
  export ACR_HOST="identify-eu-west-1.acrcloud.com"
  export ACR_ACCESS_KEY="your-key"
  export ACR_SECRET="your-secret"
  ```

## 依赖安装

```bash
pip3 install requests
# 如果需要处理视频文件：
brew install ffmpeg
# 如果需要下载音乐：
pip3 install yt-dlp
```

## 注意事项

1. **纯音乐/器乐识别效果最好** —— 带人声的歌曲识别率接近100%
2. **音频时长建议 10-30 秒** —— 太短可能识别失败，太长浪费API额度
3. **避开静音段** —— 用 `--skip` 跳过片头片尾的空白
4. **翻唱/改编版可能无法识别** —— 指纹数据库以原版为主
5. **商用版权音乐库曲目**（如 Audiomachine、Two Steps From Hell）通常能被识别到
