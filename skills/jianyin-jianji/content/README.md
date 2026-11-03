# jianyin-jianji — AI 视频剪辑专家 Skill

> 基于即梦/Seedance 视频生成 + FFmpeg 专业剪辑 + 剪映工作流

## 功能

- 视频生成（即梦/Seedance T2V + I2V）
- 专业剪辑（FFmpeg 剪切/合并/调色/转场）
- 字幕系统（SRT/ASS，时间轴对齐）
- TTS 配音（MiniMax + 声音克隆）
- AI BGM 生成 + 混音
- 剪映 Pro 工程生成（.draft）
- 批量导出 + Cron 自动化

## 目录结构

```
jianyin-jianji/
├── SKILL.md
├── rules/
│   ├── setup.md          环境初始化
│   ├── script.md         脚本生成
│   ├── video-generate.md AI视频生成
│   ├── ffmpeg-edit.md    FFmpeg剪辑
│   ├── subtitle.md       字幕
│   ├── tts-voice.md      配音
│   ├── music.md          背景音乐
│   ├── effects.md        特效/转场
│   ├── jianying-workflow.md 剪映工程
│   ├── batch-export.md   批量导出
│   └── recording.md      录屏
├── scripts/
│   └── auto_render.py    批量渲染
└── examples/
    ├── quick-edit-demo.py
    └── ai-video-demo.py
```

## MIT License
