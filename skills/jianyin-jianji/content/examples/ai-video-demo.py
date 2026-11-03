#!/usr/bin/env python3
"""AI 生成视频示例 — 即梦/Seedance + 配音 + 字幕"""
import os

WORK = os.path.expanduser("~/.openclaw/jianyin-work")
SCRIPT = """欢迎来到 AI 剪辑新时代。
在这里，你只需要告诉 AI 想做什么，
它就能全自动完成从脚本到配音到特效的一切。"""

# === 实际操作提示（由 AI Agent 执行）===
print("=" * 50)
print("AI 视频生成流水线")
print("=" * 50)
print()
print("【Step 1】生成 AI 图片（可选）")
print("  image_synthesize(prompt='科技感宣传封面，蓝色光效')")
print()
print("【Step 2】图片转视频（I2V）")
print("  batch_image_to_video(image_file='cover.png', prompt='缓慢推进镜头', duration=6)")
print()
print("【Step 3】生成配音（TTS）")
print(f"  synthesize_speech(text='{SCRIPT}', voice_id='male-qn-qingse')")
print()
print("【Step 4】生成背景音乐")
print("  batch_text_to_music(prompt='科技感背景音乐，节奏轻快')")
print()
print("【Step 5】Whisper 分析配音时间轴 -> 生成 SRT")
print("  audios_understand(audio=demo_voice.mp3)")
print()
print("【Step 6】FFmpeg 合成最终视频")
print("  ffmpeg -i generated_video.mp4 -i voice.mp3 -i bgm.mp3 \\")
print("    -vf ass=demo.ass -c:v libx264 -c:a aac ai_final.mp4")
print()
print("【Step 7】上传 CDN / 发送给用户")
print("  upload_to_cdn(file_path='/root/.openclaw/output/ai_final.mp4')")
