#!/bin/bash
# AMR 转 MP3 脚本（用于微信语音等 AMR 格式录音）
# 用法: ./amr_to_mp3.sh <input.amr> [output.mp3]

INPUT="$1"
if [ -z "$INPUT" ]; then
  echo "用法: $0 <输入.amr> [输出.mp3]"
  exit 1
fi

OUTPUT="${2:-${INPUT%.amr}.mp3}"

if ! command -v ffmpeg &>/dev/null; then
  echo "错误: ffmpeg 未安装"
  exit 1
fi

ffmpeg -y -i "$INPUT" -acodec libmp3lame -ab 128k "$OUTPUT" 2>&1
if [ $? -eq 0 ]; then
  echo "转换成功: $OUTPUT"
else
  echo "转换失败"
  exit 1
fi