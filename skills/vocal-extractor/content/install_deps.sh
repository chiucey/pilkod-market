#!/bin/bash
# install_deps.sh — 安装人声提取技能所需依赖
# 用法: bash install_deps.sh
set -e
echo "📦 安装人声提取技能依赖..."
pip3 install demucs librosa soundfile --break-system-packages -q
echo "✅ 依赖安装完成！"
echo ""
echo "可用模型:"
python3 -c "from demucs.pretrained import get_model; print('  htdemucs_ft  ← 推荐（最佳音质）'); print('  htdemucs  ← 快速（稍低音质）'); print('  mdx  ← 通用')"
echo ""
echo "使用示例:"
echo "  python3 extract_vocals.py 输入音频.mp3"
echo "  python3 extract_vocals.py 视频.mp4 输出目录"
