#!/bin/bash
set -euo pipefail

# Node.js 安装脚本 (国内镜像)
# macOS: 通过 Homebrew 安装
# Linux: 通过 NodeSource 安装

GREEN='\033[38;2;47;191;113m'
YELLOW='\033[38;2;255;176;32m'
RED='\033[38;2;226;61;45m'
BLUE='\033[38;2;100;149;237m'
MUTED='\033[38;2;139;127;119m'
NC='\033[0m'

REQUIRED_VERSION=22
NPM_REGISTRY="https://registry.npmmirror.com"

echo -e "${BLUE}📦 Node.js 安装脚本 (v${REQUIRED_VERSION}+)${NC}"
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

# 检查是否已安装且版本满足要求
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v | cut -d'v' -f2)
    NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d'.' -f1)

    if [[ "$NODE_MAJOR" -ge "$REQUIRED_VERSION" ]]; then
        echo -e "${GREEN}✓${NC} Node.js 已安装: v$NODE_VERSION"

        # 配置 npm 镜像
        if command -v npm &> /dev/null; then
            echo -e "${YELLOW}→${NC} 配置 npm 国内镜像..."
            npm config set registry "$NPM_REGISTRY"
            echo -e "${GREEN}✓${NC} npm 镜像已设置为: $NPM_REGISTRY"
        fi
        exit 0
    else
        echo -e "${YELLOW}→${NC} Node.js 版本过低: v$NODE_VERSION (需要 v${REQUIRED_VERSION}+)"
    fi
else
    echo -e "${YELLOW}→${NC} Node.js 未安装"
fi

echo -e "${YELLOW}→${NC} 开始安装 Node.js ${REQUIRED_VERSION}..."

if [[ "$OS" == "macos" ]]; then
    # 检查 Homebrew
    if ! command -v brew &> /dev/null; then
        # 尝试加载 brew
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi

    if ! command -v brew &> /dev/null; then
        echo -e "${RED}❌ 需要先安装 Homebrew${NC}"
        echo -e "${YELLOW}请运行: ./install_homebrew.sh${NC}"
        exit 1
    fi

    echo -e "${YELLOW}→${NC} 通过 Homebrew 安装..."
    brew install node@${REQUIRED_VERSION}
    brew link node@${REQUIRED_VERSION} --overwrite --force 2>/dev/null || true

elif [[ "$OS" == "linux" ]]; then
    echo -e "${YELLOW}→${NC} 通过 NodeSource 安装..."

    if command -v apt-get &> /dev/null; then
        sudo apt-get update -y
        sudo apt-get install -y ca-certificates curl gnupg
        sudo mkdir -p /etc/apt/keyrings

        curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

        echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${REQUIRED_VERSION}.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list

        sudo apt-get update -y
        sudo apt-get install -y nodejs

    elif command -v dnf &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_${REQUIRED_VERSION}.x | sudo bash -
        sudo dnf install -y nodejs

    elif command -v yum &> /dev/null; then
        curl -fsSL https://rpm.nodesource.com/setup_${REQUIRED_VERSION}.x | sudo bash -
        sudo yum install -y nodejs
    else
        echo -e "${RED}❌ 无法检测到包管理器${NC}"
        exit 1
    fi
fi

# macOS Homebrew 安装后需要确保 node 在 PATH 中
if [[ "$OS" == "macos" ]]; then
    # Homebrew node@22 可能需要手动添加到 PATH
    if [[ -d "/opt/homebrew/opt/node@${REQUIRED_VERSION}/bin" ]]; then
        export PATH="/opt/homebrew/opt/node@${REQUIRED_VERSION}/bin:$PATH"
    elif [[ -d "/usr/local/opt/node@${REQUIRED_VERSION}/bin" ]]; then
        export PATH="/usr/local/opt/node@${REQUIRED_VERSION}/bin:$PATH"
    fi
fi

# 验证安装
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓${NC} Node.js 安装完成: $(node -v)"

    if command -v npm &> /dev/null; then
        echo -e "${GREEN}✓${NC} npm 版本: v$(npm -v)"

        # 配置 npm 镜像
        echo -e "${YELLOW}→${NC} 配置 npm 国内镜像..."
        npm config set registry "$NPM_REGISTRY"
        echo -e "${GREEN}✓${NC} npm 镜像已设置为: $NPM_REGISTRY"
    else
        echo -e "${YELLOW}⚠${NC} npm 未找到，可能需要重新打开终端"
    fi
else
    echo -e "${RED}❌ Node.js 安装失败${NC}"
    exit 1
fi

# 安装 pnpm
echo ""
echo -e "${YELLOW}→${NC} 安装 pnpm..."

if command -v pnpm &> /dev/null; then
    echo -e "${GREEN}✓${NC} pnpm 已安装: v$(pnpm -v)"
else
    if command -v corepack &> /dev/null; then
        corepack enable >/dev/null 2>&1 || true
        corepack prepare pnpm@latest --activate
    elif command -v npm &> /dev/null; then
        npm install -g pnpm
    else
        echo -e "${YELLOW}⚠${NC} npm 不可用，跳过 pnpm 安装"
    fi

    if command -v pnpm &> /dev/null; then
        echo -e "${GREEN}✓${NC} pnpm 安装完成: v$(pnpm -v)"
        pnpm config set registry "$NPM_REGISTRY"
        echo -e "${GREEN}✓${NC} pnpm 镜像已设置为: $NPM_REGISTRY"
    fi
fi

echo ""
echo -e "${GREEN}✓${NC} 安装完成!"
