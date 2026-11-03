#!/usr/bin/env bash
# 音乐MV渲染辅助脚本
# 用法: ./scripts/render.sh <project_dir> <composition_id> [output_name]
# 示例: ./scripts/render.sh ./my-mv music-mv music-mv

set -euo pipefail

PROJECT_DIR="${1:-.}"
COMPOSITION="${2:-music-mv}"
OUTPUT_NAME="${3:-music-mv}"
CONCURRENCY="${CONCURRENCY:-4}"
JPEG_QUALITY="${JPEG_QUALITY:-80}"

echo "===== 音乐MV渲染 ====="
echo "项目目录: $PROJECT_DIR"
echo "合成ID:   $COMPOSITION"
echo "输出:     out/${OUTPUT_NAME}.mp4"

cd "$PROJECT_DIR"

# 校验环境
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "❌ FFmpeg 未安装" >&2
  exit 1
fi

# 渲染
npx remotion render src/index.ts "$COMPOSITION" \
  "out/${OUTPUT_NAME}.mp4" \
  --concurrency="$CONCURRENCY" \
  --jpeg-quality="$JPEG_QUALITY"

echo ""
echo "✅ 渲染完成: out/${OUTPUT_NAME}.mp4"

# 打印视频信息
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=width,height,r_frame_rate,codec_name \
  -of default=noprint_wrappers=1 "out/${OUTPUT_NAME}.mp4"
