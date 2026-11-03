#!/bin/bash
# Web Automation Skill - 一键安装脚本
# 自动安装所有依赖包（不指定版本号，避免版本冲突）

set -e  # 遇到错误立即退出

echo "========================================"
echo "Web Automation Skill - 依赖安装"
echo "========================================"
echo ""

# 检查 Python 版本
echo "[1/4] 检查 Python 环境..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"

# 检查 pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，请先安装 pip"
    exit 1
fi
echo "✅ pip3 可用"
echo ""

# 升级 pip
echo "[2/4] 升级 pip..."
pip3 install --upgrade pip -q
echo "✅ pip 已升级到最新版本"
echo ""

# 安装 Python 依赖（不指定版本号）
echo "[3/4] 安装 Python 依赖包..."
echo "正在安装：playwright, browser-use, paddlex, opencv-python, magic-pdf, pillow, pypdf, beautifulsoup4, lxml, pyyaml, langchain, python-docx, numpy, requests"
echo ""

pip3 install \
    playwright \
    browser-use \
    paddlex \
    opencv-python \
    magic-pdf \
    pillow \
    pypdf \
    beautifulsoup4 \
    lxml \
    pyyaml \
    langchain \
    python-docx \
    numpy \
    requests \
    -q

echo "✅ Python 依赖包安装完成"
echo ""

# 安装系统依赖
echo "[4/4] 安装系统依赖..."
echo "正在安装 Playwright 浏览器..."
playwright install chromium --with-deps -q
echo "✅ Playwright Chromium 安装完成"

echo "正在下载 Magic-PDF 模型..."
magic-pdf download -q 2>/dev/null || echo "⚠️ Magic-PDF 模型下载失败（可能需要手动配置）"
echo "✅ Magic-PDF 配置完成"
echo ""

# 验证安装
echo "========================================"
echo "验证安装结果"
echo "========================================"

echo ""
echo "Python 包版本检查："
pip3 list | grep -E "(playwright|browser-use|paddleocr|paddlepaddle|opencv|magic-pdf|pillow|pypdf|beautifulsoup4|lxml|pyyaml|langchain|python-docx|numpy|requests)" | while read line; do
    echo "  ✅ $line"
done

echo ""
echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo ""
echo "注意："
echo "  - LibreOffice 需要单独安装（系统级）"
echo "  - Ubuntu/Debian: sudo apt-get install libreoffice"
echo "  - CentOS/RHEL: sudo yum install libreoffice"
echo "  - macOS: brew install libreoffice"
echo ""
echo "如遇到问题，请检查错误信息或手动安装缺失的包。"
