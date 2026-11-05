#!/bin/bash
# MD Factory - 安装脚本

set -e

echo "=========================================="
echo "MD Factory 安装程序"
echo "内容结构化与Markdown生成引擎"
echo "=========================================="

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误：未找到Python3，请先安装Python 3.10+"
    exit 1
fi
echo "Python版本：$(python3 --version)"

echo ""
echo "[2/4] 安装依赖..."
pip install -r requirements.txt

echo ""
echo "[3/4] 设置执行权限..."
chmod +x convert.py
chmod +x batch_convert.py

echo ""
echo "[4/4] 验证安装..."
python3 -c "from markitdown import MarkItDown; print('MarkItDown OK')" 2>/dev/null || echo "注意：请确保markitdown已安装"

echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "快速开始："
echo "  知识卡片: python convert.py doc.pdf -o card.md --template knowledge-card"
echo "  爆款文章: python convert.py article.html -o post.md --template article"
echo "  技术文档: python convert.py api.docx -o tech.md --template tech-doc"
echo "  列出模板: python convert.py --list-templates"
echo ""
echo "查看完整文档: cat SKILL.md"
echo "=========================================="
