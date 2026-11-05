#!/usr/bin/env python3
"""
Feishu Voice Message Generator
TTS WAV → FFmpeg OGG-Opus → 输出文件路径

用法：python3 gen_voice.py "要说话的文字" [输出OGG路径]

依赖：
  - MiniMax TTS API (sk-cp-...)
  - FFmpeg: /workspace/installed_software/ffmpeg-pkg2/node_modules/@ffmpeg-installer/linux-x64/ffmpeg
  - Python 标准库（无需额外安装）
"""

import subprocess, os, sys, json

# ========== 配置 ==========
API_KEY = "sk-cp-GIEo-5tO6HIZm1FcMnP3XdzC11eG3V3-YkvUxEMXgxBSrwP25ChzH7Ru1MWtmo-ViUZqvf6xdwftrYGqq1S0-2IlHBNScE-bQFeo-Pqj-ATxPyraQKxCMqM"
VOICE_ID = "female-yujie"  # 御姐音
SPEED = 1.2
FFMPEG = "/workspace/installed_software/ffmpeg-pkg2/node_modules/@ffmpeg-installer/linux-x64/ffmpeg"
# ==========================

def tts(text):
    data = json.dumps({
        "model": "speech-2.8-hd",
        "text": text,
        "stream": False,
        "voice_setting": {"voice_id": VOICE_ID, "speed": SPEED},
        "audio_setting": {"sample_rate": 32000, "bitrate": 128000, "format": "wav"}
    }).encode()

    r = subprocess.run([
        "curl", "-s", "-X", "POST",
        "https://api.minimaxi.com/v1/t2a_v2",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", "@-"
    ], input=data, capture_output=True)

    resp = json.loads(r.stdout)
    if resp.get("base_resp", {}).get("status_code") != 0:
        raise Exception(f"TTS error: {resp.get('base_resp')}")
    return bytes.fromhex(resp["data"]["audio"])

def to_ogg(wav_data, out_path):
    wav_path = out_path.replace(".ogg", "_input.wav")
    with open(wav_path, "wb") as f:
        f.write(wav_data)

    r = subprocess.run([
        FFMPEG, "-i", wav_path,
        "-acodec", "libopus", "-ac", "1", "-ar", "16000", "-b:a", "32k",
        "-f", "ogg", out_path
    ], capture_output=True, text=True)

    os.unlink(wav_path)
    if r.returncode != 0:
        raise Exception(f"FFmpeg error: {r.stderr[-300:]}")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 gen_voice.py <文字内容> [输出路径]")
        sys.exit(1)

    text = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "/tmp/baize_voice.ogg"

    wav = tts(text)
    to_ogg(wav, out_path)
    print(out_path)

if __name__ == "__main__":
    main()
