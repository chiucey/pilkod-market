---
name: jianying-workflow
description: 调用 jianying-workflow-generator 生成剪映 Pro 工程文件。
tags: jianying, workflow, draft, pro, edit
---

# 剪映 Pro 工程生成规则

## 工具

调用 `jianying-workflow-generator` skill 生成可在剪映 Pro 中直接打开的 `.draft` 工程文件。

## 工作流

```
1. 明确剪辑需求（读取 rules/script.md）
2. 收集素材路径（本地视频/图片/音频）
3. 调用 jianying-workflow-generator
4. 输出 .draft 工程文件
5. 用户在剪映 Pro 中打开工程 → 进一步编辑或导出
```

## 调用方式

**读取 jianying-workflow-generator SKILL.md：**
```
路径：/workspace/skills/jianying-workflow-generator/SKILL.md
```

**核心参数**：
```python
# 根据 SKILL.md 说明，传递以下参数：
{
    "video_path": "/path/to/video.mp4",       # 主视频路径
    "audio_path": "/path/to/voice.mp3",       # 配音/旁白路径
    "subtitle_path": "/path/to/subtitle.ass", # 字幕文件路径
    "music_path": "/path/to/bgm.mp3",         # 背景音乐路径
    "output_draft_path": "/path/to/output.draft",
    # 可选：字幕样式、视频比例、转场类型、BGM 混音比例
}
```

## 工程文件规格

剪映 Pro `.draft` 文件本质是 JSON，结构如下：

```json
{
  "draft_data": {
    "draft_name": "AI剪辑项目",
    "draft_width": 1920,
    "draft_height": 1080,
    "draft_framerate": 30,
    "tracks": [
      {
        "type": "video",
        "track_name": "主轨",
        "segments": [
          {
            "material_id": "uuid-xxx",
            "source": "file:///path/to/video.mp4",
            "start": 0,
            "duration": 30,
            "timeline_in": 0,
            "timeline_out": 30
          }
        ]
      },
      {
        "type": "audio",
        "track_name": "配音",
        "segments": [...]
      }
    ]
  }
}
```

## 混合策略（推荐）

| 素材来源 | 处理方式 |
|---|---|
| 用户本地素材 | 用此规则生成剪映工程 |
| AI 生成素材（即梦/Seedance） | 用 `rules/video-generate.md` 先生成视频，再导入剪映工程 |
| 配音/BGM | 用 `rules/tts-voice.md` / `rules/music.md` 先生成音频 |
| 字幕 | 用 `rules/subtitle.md` 先生成 ass 文件 |

**完整流水线**：
```
AI 生成图片 → batch_image_to_video → 视频素材
                    ↓
              生成配音（TTS）+ BGM
                    ↓
              生成字幕（SRT/ASS）
                    ↓
              调用此规则生成 .draft 工程
                    ↓
              用户在剪映 Pro 打开 → 微调 → 导出
```

## 局限性

- 生成的 `.draft` 文件需要与剪映 Pro 版本兼容
- 建议告知用户：剪映 Pro 需 v5.9+（Windows）
- 最终渲染推荐在剪映 Pro 内完成（而非 FFmpeg），以获得最佳画质
