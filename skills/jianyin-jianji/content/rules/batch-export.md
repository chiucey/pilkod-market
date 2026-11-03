---
name: batch-export
description: 批量导出、自动化流水线、Cron 定时剪辑任务。
tags: batch, export, pipeline, automation, cron
---

# 批量导出与自动化规则

## 批量渲染流程

```python
tasks = [
    {"name": "视频A", "video": "a.mp4", "voice": "a_voice.mp3", "bgm": "bgm1.mp3"},
    {"name": "视频B", "video": "b.mp4", "voice": "b_voice.mp3", "bgm": "bgm2.mp3"},
]
for task in tasks:
    # 配音+BGM混音 + 字幕烧录 + 输出
    exec(f"ffmpeg -i {task['video']} -i {task['voice']} -i {task['bgm']} ... {task['name']}_final.mp4")
```

## 批量渲染脚本

```bash
#!/bin/bash
INPUT_DIR="$HOME/.openclaw/jianyin-work/temp"
OUTPUT_DIR="$HOME/.openclaw/output"
mkdir -p "$OUTPUT_DIR"

for video in "$INPUT_DIR"/*.mp4; do
    name=$(basename "$video" .mp4)
    voice="$HOME/.openclaw/jianyin-work/tts/${name}.mp3"
    bgm="$HOME/.openclaw/jianyin-work/music/bgm_default.mp3"
    sub="$HOME/.openclaw/jianyin-work/subs/${name}.ass"

    if [ -f "$voice" ] && [ -f "$bgm" ]; then
        ffmpeg -y -i "$video" -i "$voice" -i "$bgm" \
          -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.4[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]" \
          -map 0:v -map "[aout]" \
          -c:v libx264 -crf 20 -preset fast \
          "$OUTPUT_DIR/${name}_mixed.mp4"
        [ -f "$sub" ] && ffmpeg -y -i "$OUTPUT_DIR/${name}_mixed.mp4" \
          -vf "ass=$sub" "$OUTPUT_DIR/${name}_final.mp4"
    else
        ffmpeg -y -i "$video" -c:v libx264 -crf 20 "$OUTPUT_DIR/${name}_final.mp4"
    fi
    echo "Done: ${name}"
done
```

## Cron 定时剪辑

```python
cron(action="add", job={
    "name": "每日视频批量导出",
    "schedule": {"kind": "cron", "expr": "0 2 * * *", "tz": "Asia/Shanghai"},
    "payload": {
        "kind": "agentTurn",
        "message": "执行批量混音任务，输出到 ~/.openclaw/output/，完成后通知我",
    },
    "sessionTarget": "isolated",
    "delivery": {"mode": "announce"},
    "enabled": True,
})
```

## 质量检查

- [ ] 文件 MD5 校验
- [ ] 磁盘空间检查
- [ ] 错误日志记录
- [ ] 完成后消息通知
