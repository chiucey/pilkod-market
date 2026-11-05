#!/bin/bash
set -euo pipefail

# Homebrew 安装脚本 (清华镜像)
# 参考: https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/

GREEN='\033[38;2;47;191;113m'
YELLOW='\033[38;2;255;176;32m'
RED='\033[38;2;226;61;45m'
BLUE='\033[38;2;100;149;237m'
MUTED='\033[38;2;139;127;119m'
NC='\033[0m'

echo -e "${BLUE}🍺 Homebrew 安装脚本 (清华镜像)${NC}"
echo ""

# 仅支持 macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}Homebrew 主要用于 macOS，Linux 请使用 Linuxbrew${NC}"
    exit 0
fi

# 不能以 root 运行
if [[ "$(id -u)" -eq 0 ]]; then
    echo -e "${RED}❌ 请不要以 root 用户运行此脚本${NC}"
    exit 1
fi

# 检查是否已安装
if command -v brew &> /dev/null; then
    echo -e "${GREEN}✓${NC} Homebrew 已安装: $(brew --version | head -n1)"
    echo -e "${YELLOW}→${NC} 配置国内镜像源..."

    # 配置镜像
    export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
    export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
    export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
    export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"

    git -C "$(brew --repo)" remote set-url origin "$HOMEBREW_BREW_GIT_REMOTE"

    # 写入 shell 配置
    SHELL_RC="$HOME/.zshrc"
    [[ "$SHELL" == *"bash"* ]] && SHELL_RC="$HOME/.bashrc"

    if ! grep -q "HOMEBREW_BOTTLE_DOMAIN" "$SHELL_RC" 2>/dev/null; then
        cat >> "$SHELL_RC" << 'EOF'

# Homebrew 国内镜像 (清华)
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
EOF
    fi

    echo -e "${GREEN}✓${NC} 镜像源已配置"
    exit 0
fi

# 检查 Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ 需要先安装 Git${NC}"
    echo -e "${YELLOW}请运行: ./install_git.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}→${NC} 开始安装 Homebrew..."
echo -e "${MUTED}(安装过程中需要输入密码)${NC}"
echo ""

# 设置环境变量（使用清华镜像）
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
export HOMEBREW_INSTALL_FROM_API=1

INSTALL_SUCCESS=false

# 方式1: 尝试清华镜像 git clone
echo -e "${YELLOW}→${NC} 尝试清华镜像..."
INSTALL_DIR="/tmp/brew-install-$$"
if git clone --depth=1 https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/install.git "$INSTALL_DIR" 2>/dev/null; then
    echo -e "${YELLOW}→${NC} 执行安装..."
    if /bin/bash "$INSTALL_DIR/install.sh"; then
        INSTALL_SUCCESS=true
    fi
    rm -rf "$INSTALL_DIR"
fi

# 方式2: 尝试中科大镜像
if [[ "$INSTALL_SUCCESS" == "false" ]]; then
    echo -e "${YELLOW}→${NC} 尝试中科大镜像..."
    export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.ustc.edu.cn/brew.git"
    if curl -fsSL https://mirrors.ustc.edu.cn/misc/brew-install.sh -o /tmp/brew-install.sh 2>/dev/null; then
        if /bin/bash /tmp/brew-install.sh; then
            INSTALL_SUCCESS=true
        fi
        rm -f /tmp/brew-install.sh
    fi
fi

# 方式3: 使用官方脚本（环境变量已设置为国内镜像）
if [[ "$INSTALL_SUCCESS" == "false" ]]; then
    echo -e "${YELLOW}→${NC} 尝试官方脚本..."
    if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"; then
        INSTALL_SUCCESS=true
    fi
fi

if [[ "$INSTALL_SUCCESS" == "false" ]]; then
    echo -e "${RED}❌ Homebrew 安装失败${NC}"
    echo ""
    echo -e "${YELLOW}请尝试手动安装:${NC}"
    echo -e "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# 重新设置为清华镜像
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"

# 添加到 PATH
echo ""
echo -e "${YELLOW}→${NC} 配置环境变量..."

SHELL_RC="$HOME/.zshrc"
[[ "$SHELL" == *"bash"* ]] && SHELL_RC="$HOME/.bashrc"

# Apple Silicon Mac
if [[ -f "/opt/homebrew/bin/brew" ]]; then
    BREW_PATH="/opt/homebrew/bin/brew"
# Intel Mac
elif [[ -f "/usr/local/bin/brew" ]]; then
    BREW_PATH="/usr/local/bin/brew"
fi

if [[ -n "${BREW_PATH:-}" ]]; then
    # 添加 brew 到 PATH
    if ! grep -q 'brew shellenv' "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Homebrew" >> "$SHELL_RC"
        echo "eval \"\$($BREW_PATH shellenv)\"" >> "$SHELL_RC"
    fi

    # 添加镜像配置
    if ! grep -q "HOMEBREW_BOTTLE_DOMAIN" "$SHELL_RC" 2>/dev/null; then
        cat >> "$SHELL_RC" << 'EOF'

# Homebrew 国内镜像 (清华)
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles"
export HOMEBREW_API_DOMAIN="https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/api"
EOF
    fi

    # 立即生效
    eval "$($BREW_PATH shellenv)"
fi

echo ""
echo -e "${GREEN}✓${NC} Homebrew 安装完成!"
echo ""
echo -e "${MUTED}请运行以下命令使配置生效:${NC}"
echo -e "  ${BLUE}source $SHELL_RC${NC}"
echo ""
echo -e "${MUTED}或者重新打开终端${NC}"
