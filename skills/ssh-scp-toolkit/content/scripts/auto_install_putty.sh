#!/bin/bash
# auto_install_putty.sh - 自动安装PuTTY组件
# 支持: Linux (Debian/RHEL/Arch), macOS, Windows

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            echo "debian"
        elif command -v yum &> /dev/null; then
            echo "rhel"
        elif command -v dnf &> /dev/null; then
            echo "rhel"
        elif command -v pacman &> /dev/null; then
            echo "arch"
        elif command -v zypper &> /dev/null; then
            echo "suse"
        else
            echo "linux-unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# 检测PuTTY工具是否已安装
check_putty_installed() {
    local cmd=$1
    if command -v "$cmd" &> /dev/null; then
        return 0
    fi
    return 1
}

# 检查所有必需工具
check_all_tools() {
    local all_found=true

    if ! check_putty_installed "plink"; then
        log_warn "plink 未安装"
        all_found=false
    fi

    if ! check_putty_installed "pscp"; then
        log_warn "pscp 未安装"
        all_found=false
    fi

    if ! check_putty_installed "puttygen"; then
        log_warn "puttygen 未安装"
        all_found=false
    fi

    $all_found
}

# 安装PuTTY (Debian/Ubuntu)
install_debian() {
    log_info "安装 PuTTY tools (Debian/Ubuntu)..."
    sudo apt-get update
    sudo apt-get install -y putty-tools putty
    log_info "安装完成"
}

# 安装PuTTY (RHEL/CentOS)
install_rhel() {
    log_info "安装 PuTTY (RHEL/CentOS)..."
    if command -v dnf &> /dev/null; then
        sudo dnf install -y putty
    else
        sudo yum install -y putty
    fi
    log_info "安装完成"
}

# 安装PuTTY (Arch Linux)
install_arch() {
    log_info "安装 PuTTY (Arch Linux)..."
    sudo pacman -S --noconfirm putty
    log_info "安装完成"
}

# 安装PuTTY (openSUSE)
install_suse() {
    log_info "安装 PuTTY (openSUSE)..."
    sudo zypper install -y putty
    log_info "安装完成"
}

# 安装PuTTY (macOS)
install_macos() {
    if command -v brew &> /dev/null; then
        log_info "安装 PuTTY (macOS via Homebrew)..."
        brew install putty
        log_info "安装完成"
    elif command -v port &> /dev/null; then
        log_info "安装 PuTTY (macOS via MacPorts)..."
        sudo port install putty
        log_info "安装完成"
    else
        log_error "未找到包管理器 (Homebrew 或 MacPorts)"
        log_info "请安装 Homebrew: https://brew.sh"
        return 1
    fi
}

# 安装PuTTY (Windows)
install_windows() {
    log_info "Windows环境安装说明:"
    echo ""
    echo "选项1: 使用Chocolatey (推荐)"
    echo "  choco install putty"
    echo ""
    echo "选项2: 使用Scoop"
    echo "  scoop install putty"
    echo ""
    echo "选项3: 手动下载"
    echo "  https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html"
    echo ""

    # 尝试使用winget安装
    if command -v winget &> /dev/null; then
        log_info "使用 winget 安装..."
        winget install PuTTY.PuTTY
        return $?
    fi

    return 1
}

# 主安装函数
install_putty() {
    local os=$1

    case $os in
        debian)
            install_debian
            ;;
        rhel)
            install_rhel
            ;;
        arch)
            install_arch
            ;;
        suse)
            install_suse
            ;;
        macos)
            install_macos
            ;;
        windows)
            install_windows
            ;;
        *)
            log_error "不支持的操作系统: $os"
            return 1
            ;;
    esac
}

# 验证安装
verify_installation() {
    log_info "验证安装..."

    if check_putty_installed "plink"; then
        log_info "plink: $(plink -V | head -1)"
    fi

    if check_putty_installed "pscp"; then
        log_info "pscp: $(pscp -V | head -1)"
    fi

    if check_putty_installed "puttygen"; then
        log_info "puttygen: $(puttygen -V | head -1)"
    fi
}

# 主流程
main() {
    echo "========================================"
    echo "  PuTTY 自动安装脚本"
    echo "========================================"
    echo ""

    log_info "检测系统环境..."
    local os=$(detect_os)
    log_info "检测到系统: $os"
    echo ""

    # 检查是否已安装
    if check_all_tools; then
        log_info "所有 PuTTY 工具已安装"
        verify_installation
        exit 0
    fi

    # 询问是否安装
    echo ""
    read -p "是否自动安装 PuTTY 工具? [Y/n]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]] && [[ ! -z $REPLY ]]; then
        log_info "取消安装"
        exit 0
    fi

    # 执行安装
    echo ""
    if install_putty "$os"; then
        echo ""
        verify_installation
        log_info "所有设置完成！"
    else
        log_error "安装失败，请手动安装"
        exit 1
    fi
}

# 执行主函数
main "$@"
