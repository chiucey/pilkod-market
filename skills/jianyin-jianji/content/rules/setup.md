---
name: setup
description: 环境初始化、路径配置、工作目录规范。
tags: setup, environment, path, workspace
---

# 环境初始化规则

## 工作目录

所有中间文件（配音/字幕/临时视频）统一存放在 `~/.openclaw/jianyin-work/`，最终成品输出到 `~/.openclaw/output/`。

```bash
# 自动创建目录（首次运行）
mkdir -p ~/.openclaw/jianyin-work/{temp,subs,tts,music,exports}
mkdir -p ~/.openclaw/output
```

## 素材路径规则

```
用户素材：~/.openclaw/jianyin-work/materials/
  └─ videos/     # 原始视频
  └─ audios/      # 配音/BGM
  └─ images/     # 图片素材

AI 生成：~/.openclaw/jianyin-work/temp/
  └─ generated_videos/   # 即梦/Seedance 生成
  └─ tts/          # TTS 音频
  └─ music/        # AI 生成音乐

输出：~/.openclaw/output/
```

## FFmpeg 环境检查

```bash
# 验证 FFmpeg 可用
ffmpeg -version | head -1

# 检查视频信息
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## 视频尺寸标准

| 类型 | 分辨率 | 比例 |
|---|---|---|
| 横屏视频 | 1920×1080 | 16:9 |
| 竖屏视频（短视频） | 1080×1920 | 9:16 |
| 方形视频 | 1080×1080 | 1:1 |
| 4K（可选） | 3840×2160 | 16:9 |

> 默认横屏 16:9。创建项目前先确认素材比例，不一致时先裁剪或缩放。
