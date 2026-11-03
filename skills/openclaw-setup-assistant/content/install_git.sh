#!/bin/bash
set -euo pipefail

# Git 安装脚本
# macOS: 通过 Xcode Command Line Tools 安装
# Linux: 通过包管理器安装

GREEN='\033[38;2;47;191;113m'
YELLOW='\033[38;2;255;176;32m'
RED='\033[38;2;226;61;45m'
BLUE='\033[38;2;100;149;237m'
MUTED='\033[38;2;139;127;119m'
NC='\033[0m'

echo -e "${BLUE}🔧 Git 安装脚本${NC}"
echo ""

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
    OS="linux"
else
    echo -e "${RED}❌ 不支持的操作系统${NC}"
    exit 1
fi

# 检查是否已安装
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git 已安装: $(git --version)"
    exit 0
fi

echo -e "${YELLOW}→${NC} Git 未安装，开始安装..."

if [[ "$OS" == "macos" ]]; then
    echo -e "${YELLOW}→${NC} 通过 Xcode Command Line Tools 安装..."
    echo -e "${MUTED}(会弹出安装窗口，请点击「安装」)${NC}"

    xcode-select --install 2>/dev/null || true

    echo -e "${YELLOW}→${NC} 等待安装完成..."
    echo -e "${MUTED}安装完成后按 Enter 继续...${NC}"
    read -r

elif [[ "$OS" == "linux" ]]; then
    echo -e "${YELLOW}→${NC} 通过包管理器安装..."

    if command -v apt-get &> /dev/null; then
        sudo apt-get update -y
        sudo apt-get install -y git
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
    elif command -v yum &> /dev/null; then
        sudo yum install -y git
    else
        echo -e "${RED}❌ 无法检测到包管理器${NC}"
        exit 1
    fi
fi

# 验证安装
if command -v git &> /dev/null; then
    echo -e "${GREEN}✓${NC} Git 安装完成: $(git --version)"
else
    echo -e "${RED}❌ Git 安装失败${NC}"
    exit 1
fi
