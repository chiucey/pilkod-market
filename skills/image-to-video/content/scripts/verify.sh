#!/usr/bin/env bash
# 图生视频产物校验脚本
# 用法: ./scripts/verify.sh <video.mp4>
# 说明: 校验MP4视频参数，并可提取关键帧缩略图

set -euo pipefail

VIDEO="${1:?用法: $0 <video.mp4>}"

if [ ! -f "$VIDEO" ]; then
  echo "❌ 文件不存在: $VIDEO" >&2
  exit 1
fi

echo "===== 视频参数 ====="
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=width,height,r_frame_rate,codec_name \
  -of default=noprint_wrappers=1 "$VIDEO"

echo ""
echo "===== 提取关键帧(2s处) ====="
OUT="${VIDEO%.mp4}_frame.png"
ffmpeg -y -ss 2 -i "$VIDEO" -frames:v 1 "$OUT" 2>/dev/null
if [ -f "$OUT" ]; then
  echo "✅ 关键帧已保存: $OUT"
else
  echo "⚠️ 关键帧提取失败"
fi

echo ""
echo "✅ 校验完成"
