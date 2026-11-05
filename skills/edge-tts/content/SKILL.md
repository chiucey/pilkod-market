---
description: 使用 Microsoft Edge TTS 将文本转换为高质量音频。当用户要求将英文/中文文本转语音、生成TTS音频、创建语音播报时使用。支持多种声音选择（英文/中文男女声）和高清音频输出（192kbps, 48kHz）。
name: edge-tts
---

# Edge-TTS 文字转语音技能

## 技能概述

使用 Microsoft Edge TTS（edge-tts）将文本内容转换为高质量音频文件。

## 核心功能

- **多语言支持**：支持英文、中文等 40+ 语言，318 种声音
- **高质量输出**：默认生成 192kbps、48kHz 立体声 MP3
- **完全免费**：无需 API Key，直接使用微软 Edge TTS 服务
- **神经网络语音**：采用微软最新神经网络语音技术

## 可用声音

### 英文女声
| 声音 | 风格 | 快捷键 |
|------|------|--------|
| Aria | 新闻播音（推荐）| aria |
| Michelle | 新闻播音 | michelle |
| Emma | 活泼对话 | emma |
| Ava | 亲切对话 | ava |

### 英文男声
| 声音 | 风格 | 快捷键 |
|------|------|--------|
| Christopher | 新闻播音 | christopher |
| Guy | 新闻播音 | guy |

### 中文
| 声音 | 风格 | 快捷键 |
|------|------|--------|
| Xiaoxiao | 温柔女声 | xiaoxiao |
| Yunyang | 新闻播报 | yunyang |
| Yunxi | 活泼男声 | yunxi |

## 使用方式

### 安装依赖
```bash
pip install edge-tts -q && pip install ffmpeg-python -q
```

### 核心工具脚本

**文件**: `tts_tool.py`

```python
import asyncio
import edge_tts
import ffmpeg
import sys

async def generate_tts(text, voice="aria", output_file="output.mp3"):
    """生成高质量TTS音频"""
    voice_map = {
        "aria": "en-US-AriaNeural",
        "michelle": "en-US-MichelleNeural",
        "christopher": "en-US-ChristopherNeural",
        "guy": "en-US-GuyNeural",
        "emma": "en-US-EmmaNeural",
        "ava": "en-US-AvaNeural",
        "xiaoxiao": "zh-CN-XiaoxiaoNeural",
        "yunyang": "zh-CN-YunyangNeural",
        "yunxi": "zh-CN-YunxiNeural"
    }

    voice_id = voice_map.get(voice, voice)

    # 生成 ogg 格式临时文件
    temp_file = "temp_audio.ogg"
    communicate = edge_tts.Communicate(text, voice=voice_id)
    await communicate.save(temp_file)

    # 转换为高质量 MP3 (192kbps, 48kHz, 立体声)
    ffmpeg.input(temp_file).output(
        output_file,
        codec="libmp3lame",
        bitrate="192k",
        ar=48000,
        ac=2
    ).overwrite_output().run()

    print(f"音频已保存: {output_file}")

if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "Hello world"
    voice = sys.argv[2] if len(sys.argv) > 2 else "aria"
    output = sys.argv[3] if len(sys.argv) > 3 else "output.mp3"
    asyncio.run(generate_tts(text, voice, output))
```

## 调用命令

```bash
python tts_tool.py "文本内容" [声音ID] [输出文件]
```

### 示例
```bash
# 英文新闻播音
python tts_tool.py "This is a breaking news report..." aria news.mp3

# 中文温柔女声
python tts_tool.py "这是一段温柔的中文语音" xiaoxiao chinese.mp3

# 英文男声新闻
python tts_tool.py "The president announced today..." christopher report.mp3
```

## 音频质量规格

| 规格 | 数值 |
|------|------|
| 码率 | 192kbps |
| 采样率 | 48kHz |
| 声道 | 立体声 |
| 格式 | MP3 |

## 触发短语

- "把这段英文转成音频"
- "生成 TTS"
- "文字转语音"
- "帮我把这段话转成语音"
- "用新闻播音员的风格"
- "生成高清语音播报"

## 技术优势

- 完全免费，无需 API Key
- 支持 318 种声音、40+ 语言
- 神经网络语音，音质优秀
- 可调节语速、音调、音量
- 支持多种音频格式（MP3、WAV、OGG 等）
