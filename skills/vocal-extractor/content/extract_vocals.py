#!/usr/bin/env python3
"""
Vocal Extractor — Demucs htdemucs_ft 人声提取脚本
用法: python3 extract_vocals.py <输入文件> [输出目录]

依赖: pip3 install demucs librosa soundfile --break-system-packages
"""
import warnings
warnings.filterwarnings('ignore')
import sys
import os
import glob

# ─────────────────────────────────────────────
# 1. Patch torchaudio.save → soundfile
#    解决 torchcodec 缺失导致的保存崩溃问题
# ─────────────────────────────────────────────
import torch
import soundfile as sf
import numpy as np

_patched_torch_save_calls = 0
def _patched_torch_save(path, src, sr, **kwargs):
    global _patched_torch_save_calls
    _patched_torch_save_calls += 1
    arr = src.cpu().numpy()
    if arr.ndim == 2 and arr.shape[0] < arr.shape[1]:
        arr = arr.T  # (channels, samples) → (samples, channels)
    arr = np.clip(arr, -1.0, 1.0).astype('float32')
    sf.write(str(path), arr, sr)
    print(f"  ✓ 已保存: {os.path.basename(path)}")

import torchaudio
torchaudio.save = _patched_torch_save

# ─────────────────────────────────────────────
# 2. 准备音频输入
# ─────────────────────────────────────────────
if len(sys.argv) < 2:
    print("用法: python3 extract_vocals.py <输入文件> [输出目录]")
    print("支持格式: mp3/wav/flac/ogg/m4a/mp4/avi/mov/mkv")
    sys.exit(1)

input_path = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.splitext(input_path)[0]

if not os.path.exists(input_path):
    print(f"❌ 文件不存在: {input_path}")
    sys.exit(1)

os.makedirs(output_dir, exist_ok=True)

# 检测是否是视频，需要先用 ffmpeg 提音
VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
_, ext = os.path.splitext(input_path)
ext = ext.lower()

if ext in VIDEO_EXTS:
    print(f"🎬 检测到视频文件，先提取音频...")
    audio_path = os.path.join(output_dir, '_temp_audio.wav')
    ret = os.system(f'ffmpeg -y -i "{input_path}" -vn -acodec pcm_s16le -ar 44100 -ac 2 "{audio_path}" 2>/dev/null')
    if ret != 0:
        print("❌ ffmpeg 提取音频失败，请确认已安装 ffmpeg")
        sys.exit(1)
    print(f"  音频提取完成 → {audio_path}")
else:
    audio_path = input_path

# ─────────────────────────────────────────────
# 3. 加载 Demucs htdemucs_ft 模型
# ─────────────────────────────────────────────
print("🚀 加载 Demucs htdemucs_ft 模型（首次运行会下载 ~160MB）...")
from demucs.pretrained import get_model
from demucs.apply import apply_model
import librosa

model = get_model('htdemucs_ft')
model.eval()
print("  ✅ 模型加载完成")

# ─────────────────────────────────────────────
# 4. 加载音频 → torch.Tensor
# ─────────────────────────────────────────────
print(f"📂 加载音频: {os.path.basename(audio_path)}")
wav, sr = librosa.load(audio_path, sr=44100, mono=False)
# librosa: (channels, samples) if mono=False
if wav.ndim == 1:
    wav = np.stack([wav, wav])
wav = torch.from_numpy(wav).float()
print(f"  音频: shape={wav.shape}, sr={sr}Hz")

# ─────────────────────────────────────────────
# 5. Demucs 分离（CPU）
# ─────────────────────────────────────────────
print("🔬 分离中（CPU，预计45秒）...")
wav_batched = wav.unsqueeze(0)  # (1, channels, samples)

with torch.no_grad():
    sources = apply_model(model, wav_batched, device='cpu')

sources = sources[0]  # (sources, channels, samples)
print("  ✅ 分离完成！")

# ─────────────────────────────────────────────
# 6. 保存所有音轨
# ─────────────────────────────────────────────
source_names = model.sources  # ['drums', 'bass', 'other', 'vocals']

print("\n📁 输出目录:", output_dir)
for i, name in enumerate(source_names):
    stem = sources[i]  # torch.Tensor (channels, samples)
    out_path = os.path.join(output_dir, f'{name}.wav')
    torchaudio.save(out_path, stem, sr)
    mb = os.path.getsize(out_path) / 1024 / 1024
    icon = "🎤" if name == "vocals" else "🥁" if name == "drums" else "🎸"
    print(f"  {icon} {name}.wav  {mb:.1f} MB")

# 清理临时音频
if audio_path != input_path and os.path.exists(audio_path):
    os.remove(audio_path)

print(f"""
🎉 全部完成！
   人声文件: {os.path.join(output_dir, 'vocals.wav')}
""")
