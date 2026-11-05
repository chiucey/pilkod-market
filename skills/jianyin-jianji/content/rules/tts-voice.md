---
name: tts-voice
description: TTS 配音生成、声音克隆、音量调整。
tags: tts, voice, dubbing, voiceover, audio, synthesize
---

# TTS 配音规则

## 工具选择

| 工具 | 用途 | 限制 |
|---|---|---|
| `batch_text_to_audio` | 短文本批量 TTS | MiniMax TTS |
| `synthesize_speech` | 单条高质量配音 | 支持克隆声音 |
| `upload_clone_audio` + `clone_voice` | 声音克隆 | 需要 10s~5min 原始音频 |

## 基础 TTS 配音

```python
# 单条配音（batch_text_to_audio）
batch_text_to_audio(
    count=1,
    text_list=["欢迎来到 AI 剪辑教程，今天我们将演示自动字幕生成。"],
    output_file_list=["~/.openclaw/jianyin-work/tts/voice_001.mp3"],
    voice_list=["male-qn-qingse"],  # 可选：自定义 voice_id
    speed_list=[1.0],
    volume_list=[1.0],
    emotion_list=["happy"]  # happy/sad/angry/neutral
)

# 批量配音
batch_text_to_audio(
    count=3,
    text_list=["第一段配音文本", "第二段配音文本", "第三段配音文本"],
    output_file_list=[
        "~/.openclaw/jianyin-work/tts/part1.mp3",
        "~/.openclaw/jianyin-work/tts/part2.mp3",
        "~/.openclaw/jianyin-work/tts/part3.mp3",
    ],
    voice_list=["male-qn-qingse", "male-qn-qingse", "male-qn-qingse"],
    speed_list=[1.0, 1.0, 1.0],
    emotion_list=["neutral", "neutral", "neutral"],
)
```

## 获取可用声音

```python
# 列出所有可用声音
get_voice_list()
# 返回: voice_id + voice_name 列表
```

## 声音克隆

```python
# Step 1: 上传原始音频（10s~5min，MP3/WAV/M4A）
upload_clone_audio(audio_file_path="~/.openclaw/jianyin-work/materials/audios/reference.mp3")
# 返回: file_id

# Step 2: 克隆声音
clone_voice(
    file_id="上文返回的file_id",
    voice_id="my_voice_clone",  # 自定义 voice ID
    demo_text="这段文字用于预览克隆效果"  # 10~50字
)

# Step 3: 使用克隆声音
synthesize_speech(
    text="这是克隆声音的配音内容。",
    output_file="~/.openclaw/jianyin-work/tts/clone_demo.mp3",
    voice_id="my_voice_clone",
    speed=1.0,
    pitch=0,
    volume=1.0
)
```

## 音量与语速调整

```bash
# 音量归一化（避免过大或过小）
ffmpeg -i voice.mp3 -af "volume=1.0, loudnorm=I=-16:LRA=11" normalized.mp3

# 语速调整（1.5x 加速，不改变音高）
ffmpeg -i voice.mp3 -af "asetrate=44100*1.2,aresample=44100" faster.mp3

# 音量淡入淡出
ffmpeg -i voice.mp3 -af "afade=t=in:st=0:d=0.5,afade=t=out:st=-1:d=0.5" fade.mp3
```

## 配音混音（人声+BGM）

```bash
# 人声 100%，BGM 40%，人声优先
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.4[BGM];[0:a][BGM]amix=inputs=2:duration=first[aout]" \
  -map "[aout]" mixed.mp3
```

## TTS 配音检查清单

- [ ] 文本无错别字（生成前朗读一遍）
- [ ] 避免生僻字/多音字（AI 可能读错）
- [ ] 人名/品牌名提前注音
- [ ] 时长与视频匹配（配音比视频长 → 截断；配音短 → 静音填充）
- [ ] 语速适合内容（教程宜慢，信息流宜快）
