#!/bin/bash
set -euo pipefail

# Moltbot 依赖一键安装脚本
# 按顺序安装: Git → Homebrew → Node.js → pnpm

GREEN='\033[38;2;47;191;113m'
YELLOW='\033[38;2;255;176;32m'
RED='\033[38;2;226;61;45m'
BLUE='\033[38;2;100;149;237m'
BOLD='\033[1m'
MUTED='\033[38;2;139;127;119m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo -e "${BOLD}${BLUE}🚀 Moltbot 依赖一键安装脚本${NC}"
echo -e "${MUTED}================================${NC}"
echo ""

# 不能以 root 运行
if [[ "$(id -u)" -eq 0 ]]; then
    echo -e "${RED}❌ 请不要以 root 用户运行此脚本${NC}"
    exit 1
fi

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}✓${NC} 检测到系统: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]] || [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
    OS="linux"
    echo -e "${GREEN}✓${NC} 检测到系统: Linux"
else
    echo -e "${RED}❌ 不支持的操作系统${NC}"
    exit 1
fi

echo ""

# 步骤 1: 安装 Git
echo -e "${BLUE}[1/3] 安装 Git${NC}"
echo -e "${MUTED}----------------------------${NC}"
if [[ -x "$SCRIPT_DIR/install_git.sh" ]]; then
    bash "$SCRIPT_DIR/install_git.sh"
else
    echo -e "${RED}❌ 找不到 install_git.sh${NC}"
    exit 1
fi
echo ""

# 步骤 2: 安装 Homebrew (仅 macOS)
if [[ "$OS" == "macos" ]]; then
    echo -e "${BLUE}[2/3] 安装 Homebrew${NC}"
    echo -e "${MUTED}----------------------------${NC}"
    if [[ -x "$SCRIPT_DIR/install_homebrew.sh" ]]; then
        bash "$SCRIPT_DIR/install_homebrew.sh"
    else
        echo -e "${RED}❌ 找不到 install_homebrew.sh${NC}"
        exit 1
    fi

    # 重新加载 brew 环境
    if [[ -f "/opt/homebrew/bin/brew" ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -f "/usr/local/bin/brew" ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    echo ""
else
    echo -e "${BLUE}[2/3] 跳过 Homebrew (Linux 不需要)${NC}"
    echo ""
fi

# 步骤 3: 安装 Node.js 和 pnpm
echo -e "${BLUE}[3/3] 安装 Node.js 和 pnpm${NC}"
echo -e "${MUTED}----------------------------${NC}"
if [[ -x "$SCRIPT_DIR/install_node.sh" ]]; then
    bash "$SCRIPT_DIR/install_node.sh"
else
    echo -e "${RED}❌ 找不到 install_node.sh${NC}"
    exit 1
fi
echo ""

# 完成
echo -e "${MUTED}================================${NC}"
echo -e "${GREEN}${BOLD}✅ 所有依赖安装完成!${NC}"
echo ""
echo -e "已安装:"
command -v git &> /dev/null && echo -e "  ${MUTED}•${NC} Git: ${GREEN}$(git --version | cut -d' ' -f3)${NC}"
command -v brew &> /dev/null && echo -e "  ${MUTED}•${NC} Homebrew: ${GREEN}$(brew --version | head -n1 | cut -d' ' -f2)${NC}"
command -v node &> /dev/null && echo -e "  ${MUTED}•${NC} Node.js: ${GREEN}$(node -v)${NC}"
command -v npm &> /dev/null && echo -e "  ${MUTED}•${NC} npm: ${GREEN}v$(npm -v)${NC}"
command -v pnpm &> /dev/null && echo -e "  ${MUTED}•${NC} pnpm: ${GREEN}v$(pnpm -v)${NC}"
echo ""
echo -e "${MUTED}现在可以安装 Moltbot:${NC}"
echo -e "  ${BLUE}curl -fsSL --proto '=https' --tlsv1.2 https://molt.bot/install.sh | bash${NC}"
echo ""
