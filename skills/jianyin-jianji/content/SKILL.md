---
name: jianyin-jianji
description: >
  AI 视频剪辑专家 Skill。基于即梦(吉梦)/Seedance 视频生成 + 剪映工作流 + FFMPEG 智能剪辑，
  支持：脚本生成、视频生成、视频剪辑（素材剪辑/字幕/TTS配音/音乐/特效）、自动化批量导出。
  触发关键词：剪辑、短视频、字幕、配音、背景音乐、特效、转场、视频剪辑、剪映工作流、来个剪辑。
---

# 🎬 jianyin-jianji — AI 视频剪辑专家

## 平台说明

本 Skill 运行于 **OpenClaw + MaxClaw** 环境，核心工具链：

| 工具 | 用途 |
|---|---|
| `image_synthesize` / `gen_videos` / `batch_text_to_video` | AI 生成图片/视频（即梦/Seedance） |
| `batch_image_to_video` | 图片转视频（I2V） |
| `videos_understand` | AI 视频内容理解与分析 |
| `batch_text_to_audio` / `synthesize_speech` | TTS 配音 |
| `batch_text_to_music` | AI 生成背景音乐 |
| `exec`（FFmpeg） | 视频合并、格式转换、裁剪、转码 |
| `jianying-workflow-generator` | 生成剪映 Pro 工程文件（`.draft`） |
| `jianying-editor-skill`（上游） | Windows 环境下操控剪映桌面版 |

> **剪辑策略**：素材已在本地 → 用 `jianying-workflow-generator` 生成剪映工作流 + FFmpeg 处理；素材需要 AI 生成 → 用即梦/Seedance/MCP 视频工具。

---

## 核心工作流

### 0）快速剪辑（默认"来个剪辑"）
```
1. 理解需求 → 确定视频类型（宣传/教程/日常/影评）
2. 判断素材来源：
   - 用户提供了素材 → 用 FFmpeg 剪辑 + 加字幕/音乐
   - 需要 AI 生成 → 调用即梦/Seedance 生成素材
3. 组装脚本：字幕(ass) → 配音(mp3) → BGM → 转场
4. 输出最终视频文件
```

### 1）自动化影评/解说视频（全自动流水线）
```
1. videos_understand：分析原始视频内容
2. 生成解说词文案（LLM）
3. synthesize_speech：生成配音
4. batch_text_to_music：生成背景音乐
5. FFmpeg：将配音/音乐合成到视频
6. 生成 ass 字幕文件
7. 输出完整解说视频
```

### 2）即梦/Seedance 文生视频工作流
```
1. 用户提供或 AI 生成图片（image_synthesize）
2. batch_image_to_video：图片转视频（I2V）
3. 或直接 batch_text_to_video：文字生视频
4. FFmpeg：拼接+加片头片尾
5. 合成字幕+BGM
```

### 3）剪映 Pro 工程生成
```
1. 分析剪辑需求
2. 调用 jianying-workflow-generator 生成 .draft 工作流
3. 输出可在剪映 Pro 中直接打开的工程文件
```

---

## 规则文件索引

| 规则 | 触发时机 |
|---|---|
| `rules/setup.md` | 初始化环境、路径配置 |
| `rules/script.md` | 理解剪辑需求，生成脚本/文案 |
| `rules/video-generate.md` | 即梦/Seedance 图片生视频、视频拼接 |
| `rules/ffmpeg-edit.md` | FFmpeg 剪辑、合并、转码、加字幕 |
| `rules/subtitle.md` | SRT/ASS 字幕生成、时间轴对齐 |
| `rules/tts-voice.md` | TTS 配音、声音克隆 |
| `rules/music.md` | BGM 生成与混音 |
| `rules/effects.md` | 转场、滤镜、调色 |
| `rules/jianying-workflow.md` | 剪映 Pro 工程生成 |
| `rules/batch-export.md` | 批量导出、自动化流水线 |
| `rules/recording.md` | 录屏+智能缩放（jianying-editor-skill upstream）|

---

## 执行检查清单（每次剪辑必查）

- [ ] 视频尺寸正确（横屏 1920×1080 / 竖屏 1080×1920）
- [ ] 视频时长与脚本/配音时长匹配
- [ ] 字幕文件时间轴与配音对齐
- [ ] BGM 在人声轨道下（音量 0.5~0.7）
- [ ] 片头片尾完整（品牌标识/字幕版权）
- [ ] 最终文件格式：MP4，H.264 编码

---

## 常见任务快速入口

| 用户需求 | 执行规则 | 关键工具 |
|---|---|---|
| 剪个视频 | `rules/ffmpeg-edit.md` | FFmpeg |
| 加字幕 | `rules/subtitle.md` | FFmpeg ass |
| 配音旁白 | `rules/tts-voice.md` | synthesize_speech |
| AI 生成视频 | `rules/video-generate.md` | gen_videos / batch_text_to_video |
| 加背景音乐 | `rules/music.md` | batch_text_to_music |
| 生成剪映工程 | `rules/jianying-workflow.md` | jianying-workflow-generator |
| 批量导出 | `rules/batch-export.md` | FFmpeg + cron |
| 转场特效 | `rules/effects.md` | FFmpeg + filter |
| 分析视频内容 | — | videos_understand |
