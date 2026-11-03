---
name: music
description: AI 生成背景音乐、BGM 混音、版权音乐搜索。
tags: music, bgm, soundtrack, audio, mix
---

# 背景音乐规则

## 工具选择

| 工具 | 用途 |
|---|---|
| `batch_text_to_music` | AI 生成自定义风格音乐（MiniMax） |
| FFmpeg amix | 混音：配音+BGM |

## AI 生成 BGM

```python
batch_text_to_music(
    count=1,
    prompt_list=["轻快的背景音乐，适合阳光感短视频，正能量，明亮钢琴+电子节拍"],
    lyrics_list=["[Verse]\n(upbeat positive music)\n\n[Chorus]\n(energetic feel-good melody)"],
    output_file_list=["~/.openclaw/jianyin-work/music/bgm_upbeat.mp3"],
    format_list=["mp3"],
    bitrate_list=[128000],
)
```

**提示词结构**：
- 风格：`Pop/Jazz/Electronic/Classical/Cinematic/Lo-Fi`
- 情绪：`happy/sad/energetic/calm/epic/mysterious`
- 乐器：`piano/guitar/strings/synth/drums`
- 场景：`适合 vlog/广告/电影/游戏`

**歌词说明**：不唱出来的纯音乐背景，lyrics 用语气标记（括号表示纯情绪）或不写。

## BGM 时长处理

```bash
# 截取指定时长 BGM（与视频时长一致）
ffmpeg -i bgm_full.mp3 -t 60 -c copy bgm_60s.mp3

# 循环 BGM（超长视频）
ffmpeg -stream_loop -1 -i bgm.mp3 -t 180 bgm_3min.mp3

# BGM 淡入淡出（头尾自然）
ffmpeg -i bgm.mp3 -af "afade=t=in:st=0:d=1.5,afade=t=out:st=58:d=2" bgm_fade.mp3
```

## BGM 与配音混音

```bash
# 标准混音：配音为主（1.0），BGM 为辅（0.3~0.5）
ffmpeg -i voice.mp3 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.4[BGM];[0:a][BGM]amix=inputs=2:duration=first:dropout_transition=2[aout]" \
  -map "[aout]" mixed_voice_bgm.mp3

# 录音棚级处理（响度归一化）
ffmpeg -i mixed_voice_bgm.mp3 \
  -af "loudnorm=I=-16:LRA=11:TP=-1.5" final_audio.mp3
```

## 平台 BGM 推荐速查

| 平台 | 风格建议 | 时长建议 |
|---|---|---|
| 抖音/快手 | 节奏感强、前3秒抓耳 | 15~60s |
| B站 | 风格多元、可较长 | 1~5min |
| 微信视频号 | 轻商务、不过于吵闹 | 30s~3min |
| 电商广告 | 科技感/活力/信任感 | 15~30s |
| 电影/纪录片 | 氛围感、情绪铺垫 | 按需 |
