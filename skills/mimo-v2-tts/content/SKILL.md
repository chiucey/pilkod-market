---
name: mimo-v2-tts
description: 小米 MiMo V2 文本转语音 (TTS) 技能。当用户要求将文本转换为语音、使用 TTS 生成音频、使用小米语音合成、创建语音播报、制作音频文件时使用。
---

# MiMo V2 TTS 语音合成技能

## 功能概述

封装小米 MiMo V2 TTS API，支持将文本转换为自然流畅的语音输出。

## 核心参数

| 参数 | 必填 | 说明 |
|------|------|------|
| text | 是 | 要合成的文本内容 |
| voice | 否 | 音色选择，默认 `mimo_default` |
| format | 否 | 音频格式，默认 `wav` |
| style | 否 | 语音风格标签 |

## 可用音色

| 音色名称 | 参数值 |
|----------|--------|
| MiMo-默认 | `mimo_default` |
| 中文女声 | `default_zh` |
| 英文女声 | `default_en` |

## 风格控制

在文本开头添加 `<|style:style_name|>` 标签：

| 风格类型 | 示例 |
|----------|------|
| 语速控制 | `_Speed up` / `_Slow down` |
| 情感变化 | `_Happy` / `_Sad` / `_Angry` |
| 角色扮演 | `_Sun Wukong` / `_Lin Daiyu` |
| 风格变化 | `_Whisper` / `_Clamped voice` / `_Taiwanese accent` |
| 方言 | `_Northeastern dialect` / `_Sichuan dialect` / `_Henan dialect` / `_Cantonese` |

## 使用方式

### 方式一：直接调用 API

```
POST https://api.xiaomimimo.com/v1/chat/completions
Headers: api-key: $MIMO_API_KEY
```

### 方式二：使用客户端脚本

```python
from scripts.mimo_tts_client import MimoTTSClient

client = MimoTTSClient(api_key="your_api_key")
audio_bytes = client.synthesize(
    text="你好，欢迎使用小米语音合成",
    voice="mimo_default",
    style="_Happy"
)
```

## 注意事项

1. 目标文本必须放在 `role: assistant` 的消息中
2. `user` 角色消息可选，用于调整语气和风格
3. 唱歌风格：在文本开头添加 `<|sing|>` 标签
4. 返回的音频数据为 base64 编码，需解码后保存
