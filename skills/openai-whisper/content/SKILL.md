---
name: openai-whisper
description: 本地离线语音转文字/翻译工具，基于OpenAI Whisper CLI封装，无需API密钥，所有处理均在本地完成。当用户要求将音频转录为文字、进行语音翻译、处理mp3/m4a/wav/flac等音频文件时使用。
---

# OpenAI Whisper 本地语音转文字技能

## 功能特性
- ✅ 本地离线语音转录，支持99种语言
- ✅ 语音翻译（任意语言转英文）
- ✅ 支持mp3、m4a、wav、flac等主流音频格式
- ✅ 支持txt、srt、vtt、json等多种输出格式
- ✅ 多档位模型可选，平衡速度与准确率
- ✅ 无网络依赖，数据全程本地留存

## 使用方法

### 基础语音转录
```
帮我转录这个音频：/Users/xxx/Documents/meeting.mp3
```

### 语音翻译
```
把这个日语音频翻译成英文：/Users/xxx/Documents/japanese_audio.m4a
```

### 自定义参数调用
```
用medium模型转录这个音频，输出srt字幕文件：
{
  "audio_path": "/Users/xxx/Documents/interview.wav",
  "model": "medium",
  "output_format": "srt",
  "output_dir": "/Users/xxx/Documents/transcript_result"
}
```

## 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| audio_path | string | ✅ | - | 音频文件完整路径 |
| model | string | ❌ | turbo | 模型：tiny/base/small/medium/large/turbo |
| task | string | ❌ | transcribe | 任务：transcribe(转录)/translate(翻译) |
| output_format | string | ❌ | txt | 格式：txt/srt/vtt/json/tsv |
| output_dir | string | ❌ | ./output | 输出目录 |

## 前置要求
1. 安装 Whisper CLI：
   - MacOS: `brew install openai-whisper`
   - 其他: `pip install openai-whisper`
2. 安装 ffmpeg（Whisper依赖）

## 注意事项
- 首次运行会自动下载模型到 `~/.cache/whisper` 目录
- 模型越大越准确，但速度越慢
- 所有处理均在本地完成，不会上传任何数据
