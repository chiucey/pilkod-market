#!/bin/bash
# 安装文档转换脚本所需的依赖

echo "正在安装文档转换依赖..."

# 安装Python包
pip install python-docx pypdf reportlab -q

# 检查LibreOffice
if ! command -v libreoffice &> /dev/null; then
    echo "提示: LibreOffice未安装，Word转PDF功能将不可用"
    echo "安装命令: sudo apt install libreoffice"
fi

echo "依赖安装完成!"
