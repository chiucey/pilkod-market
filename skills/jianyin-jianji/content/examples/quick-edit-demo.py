#!/usr/bin/env python3
"""快速剪辑示例 — 用户视频 + 配音 + BGM + 字幕"""
import subprocess, os

WORK = os.path.expanduser("~/.openclaw/jianyin-work")
VOICE_FILE = os.path.join(WORK, "tts/demo_voice.mp3")
BGM_FILE   = os.path.join(WORK, "music/bgm_default.mp3")
SUB_FILE   = os.path.join(WORK, "subs/demo_sub.srt")
VIDEO_IN   = os.path.join(WORK, "temp/video_input.mp4")
FINAL_OUT  = os.path.expanduser("~/.openclaw/output/demo_final.mp4")

def run(cmd, tag):
    print(f"[{tag}] {cmd[:60]}...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(r.stdout or "ok")
    if r.returncode != 0: print("ERROR:", r.stderr[:200])
    return r.returncode == 0

# 1. 截取 BGM 到视频时长（假设 30s）
run(f'ffmpeg -y -i {BGM_FILE} -t 30 -c copy {WORK}/temp/bgm_trim.mp3', "BGM截取")

# 2. 混音（配音 100% + BGM 40%）
run(f"""ffmpeg -y -i {VOICE_FILE} -i {WORK}/temp/bgm_trim.mp3 \
  -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.4[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]" \
  -map "[aout]" {WORK}/temp/mixed_audio.mp3""", "混音")

# 3. 合成视频
cmd = f"""ffmpeg -y -i {VIDEO_IN} -i {WORK}/temp/mixed_audio.mp3 \
  -vf "ass={SUB_FILE}" -c:v libx264 -crf 20 -c:a aac -shortest {FINAL_OUT}"""
run(cmd, "字幕烧录+最终输出")
print(f"\n=== DONE: {FINAL_OUT} ===")
