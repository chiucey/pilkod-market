#!/bin/bash
# Web Automation Skill 依赖安装脚本
# 支持选择性安装，避免版本冲突

set -e

echo "=========================================="
echo "  Web Automation Skill 依赖安装脚本"
echo "=========================================="
echo ""

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "📦 Python 版本: $PYTHON_VERSION"

if [[ ! "$PYTHON_VERSION" =~ ^3\.(8|9|10|11|12) ]]; then
    echo "❌ 错误: Python 版本过低，需要 3.8+"
    exit 1
fi

echo ""
echo "请选择安装模式："
echo "  1) 基础安装（仅浏览器自动化）"
echo "  2) 完整安装（包含 OCR）"
echo "  3) 完整安装（包含 PDF）"
echo "  4) 完整安装（所有功能）"
echo "  5) 自定义安装"
echo ""
read -p "请输入选项 [1-5]: " choice

case $choice in
    1)
        echo ""
        echo "📦 开始基础安装..."
        ;;
    2)
        echo ""
        echo "📦 开始安装（包含 OCR）..."
        INSTALL_OCR=true
        ;;
    3)
        echo ""
        echo "📦 开始安装（包含 PDF）..."
        INSTALL_PDF=true
        ;;
    4)
        echo ""
        echo "📦 开始完整安装..."
        INSTALL_OCR=true
        INSTALL_PDF=true
        ;;
    5)
        echo ""
        read -p "安装 OCR 功能？[y/N]: " install_ocr
        [[ "$install_ocr" =~ ^[Yy]$ ]] && INSTALL_OCR=true
        
        read -p "安装 PDF 功能？[y/N]: " install_pdf
        [[ "$install_pdf" =~ ^[Yy]$ ]] && INSTALL_PDF=true
        ;;
    *)
        echo "❌ 无效选项，退出"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  第 1 步：升级 pip"
echo "=========================================="
python3 -m pip install --upgrade pip setuptools wheel

echo ""
echo "=========================================="
echo "  第 2 步：安装核心依赖"
echo "=========================================="
pip install "playwright>=1.48.0"
pip install "browser-use>=0.2.0"
pip install "langchain>=0.1.0"
pip install "langchain-openai>=0.1.0"
pip install "langchain-anthropic>=0.1.0"
pip install "langchain-google-genai>=0.1.0"
pip install "requests>=2.28.0"
pip install "aiohttp>=3.8.0"
pip install "beautifulsoup4>=4.12.0"
pip install "lxml>=4.9.0"
pip install "pyyaml>=6.0"
pip install "numpy>=1.24.0"

echo ""
echo "=========================================="
echo "  第 3 步：安装 Playwright 浏览器"
echo "=========================================="
playwright install chromium || {
    echo "⚠️  Playwright 浏览器安装失败，请手动运行: playwright install chromium"
}

# OCR 安装
if [[ "$INSTALL_OCR" == "true" ]]; then
    echo ""
    echo "=========================================="
    echo "  第 4 步：安装 OCR 依赖"
    echo "=========================================="
    
    echo "📦 安装 PaddlePaddle..."
    pip install "paddlepaddle>=2.6.0" || {
        echo "⚠️  PaddlePaddle 安装失败"
        echo "   GPU 用户请参考: https://www.paddlepaddle.org.cn/install/quick"
    }
    
    echo "📦 安装 PaddleOCR..."
    pip install "paddleocr" || {
        echo "⚠️  PaddleOCR 安装失败"
    }
    
    echo "📦 安装图像处理库..."
    pip install opencv-python pillow || {
        echo "⚠️  图像处理库安装失败"
    }
else
    echo ""
    echo "⏭️  跳过 OCR 依赖安装"
fi

# PDF 安装
if [[ "$INSTALL_PDF" == "true" ]]; then
    echo ""
    echo "=========================================="
    echo "  第 5 步：安装 PDF 依赖"
    echo "=========================================="
    
    echo "📦 安装 MinerU (magic-pdf)..."
    pip install "magic-pdf[full]" || {
        echo "⚠️  MinerU 安装失败，尝试基础版本..."
        pip install "magic-pdf" || {
            echo "⚠️  magic-pdf 安装失败"
        }
    }
    
    echo "📦 安装 PDF 处理库..."
    pip install pypdf python-docx || {
        echo "⚠️  PDF 处理库安装失败"
    }
else
    echo ""
    echo "⏭️  跳过 PDF 依赖安装"
fi

echo ""
echo "=========================================="
echo "  第 6 步：环境检查"
echo "=========================================="
python3 scripts/check_env.py

echo ""
echo "=========================================="
echo "  安装完成！"
echo "=========================================="
echo ""
echo "📝 后续步骤："
echo ""
echo "1. 如果 Playwright 浏览器未安装，请运行："
echo "   playwright install chromium"
echo ""

if [[ "$INSTALL_PDF" == "true" ]]; then
    echo "2. 如果需要使用 PDF 功能，请确保 magic-pdf 正确安装"
    echo "   首次使用时会自动下载模型"
    echo ""
fi

if [[ "$INSTALL_OCR" == "true" ]]; then
    echo "3. 如果需要使用 OCR 功能，请确保 PaddleOCR 正确安装"
    echo "   首次使用时会自动下载模型"
    echo ""
fi

echo "4. 测试安装："
echo "   python scripts/check_env.py"
echo ""
