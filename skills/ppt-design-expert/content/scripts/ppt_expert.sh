#!/bin/bash
# ppt_expert.sh - 一键启动PPT设计专家
# 用法: bash ~/reading-writing-project/scripts/ppt_expert.sh

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="$HOME/reading-writing-project"

echo "================================================"
echo "PPT设计专家  v1.0"
echo "演说之禅 + 金字塔原理 + 高桥流简洁法"
echo "================================================"

# Step 1: 检查Python依赖
echo ""
echo "[检查] python-pptx..."
if python3 -c "from pptx import Presentation" 2>/dev/null; then
    echo "✅ python-pptx 已安装"
else
    echo "📦 正在安装 python-pptx..."
    pip3 install python-pptx
fi

# Step 2: 运行设计专家
echo ""
echo "[启动] PPT设计专家交互流程..."
python3 "$SCRIPT_DIR/scripts/ppt_design_expert.py"

echo ""
echo "================================================"
echo "✅ 设计完成！"
echo "================================================"
echo "下一步:"
echo "  python3 $SCRIPT_DIR/scripts/pptx_build.py <生成的JSON文件> [风格]"
echo ""
echo "可用风格: 商务专业 / 学术严谨 / 活泼教学 / 中国古典 / 简约现代"