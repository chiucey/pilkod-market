#!/usr/bin/env bash
# WeChat Auto Publisher 安装脚本
# 一键安装全自动微信公众号发布技能到OpenClaw

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 显示帮助
show_help() {
    cat << EOF
WeChat Auto Publisher 安装脚本

用法: $0 [选项]

选项:
  -h, --help          显示此帮助信息
  -d, --dir DIR       指定OpenClaw技能目录 (默认: ~/.openclaw/workspace/skills)
  -f, --force         强制覆盖已存在的技能
  -c, --check-only    只检查不安装
  --no-deps           跳过依赖检查

示例:
  $0                   # 标准安装
  $0 --force          # 强制覆盖安装
  $0 --dir /custom/path  # 安装到自定义目录
  $0 --check-only     # 只检查环境
EOF
}

# 检查依赖
check_dependencies() {
    log_step "1. 检查系统依赖..."
    
    local missing_deps=()
    local optional_deps=()
    
    # 必需依赖
    if ! command -v wenyan &> /dev/null; then
        missing_deps+=("wenyan-cli")
        log_error "❌ wenyan-cli 未安装"
        log_info "  安装命令: npm install -g @wenyan-md/cli"
    else
        log_info "✅ wenyan-cli 已安装: $(wenyan --version 2>/dev/null || echo '未知版本')"
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
        log_error "❌ curl 未安装"
    else
        log_info "✅ curl 已安装"
    fi
    
    # 可选依赖
    if ! command -v jq &> /dev/null; then
        optional_deps+=("jq")
        log_warn "⚠️  jq 未安装 (JSON处理工具，推荐安装)"
    else
        log_info "✅ jq 已安装"
    fi
    
    if ! command -v convert &> /dev/null; then
        optional_deps+=("ImageMagick")
        log_warn "⚠️  ImageMagick 未安装 (图片生成功能受限)"
    else
        log_info "✅ ImageMagick 已安装"
    fi
    
    # 检查npm是否安装（用于wenyan-cli）
    if ! command -v npm &> /dev/null; then
        log_warn "⚠️  npm 未安装，无法安装wenyan-cli"
    else
        log_info "✅ npm 已安装"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少必需依赖: ${missing_deps[*]}"
        return 1
    fi
    
    if [ ${#optional_deps[@]} -gt 0 ]; then
        log_warn "缺少可选依赖: ${optional_deps[*]}"
        log_info "这些依赖不是必需的，但推荐安装以获得完整功能"
    fi
    
    return 0
}

# 检查OpenClaw目录
check_openclaw_dir() {
    local target_dir="$1"
    
    log_step "2. 检查OpenClaw目录..."
    
    # 检查目标目录是否存在
    if [ ! -d "$target_dir" ]; then
        log_error "OpenClaw技能目录不存在: $target_dir"
        log_info "请确保OpenClaw已正确安装"
        log_info "或者使用 --dir 参数指定自定义目录"
        return 1
    fi
    
    log_info "✅ OpenClaw技能目录: $target_dir"
    
    # 检查是否有写入权限
    if [ ! -w "$target_dir" ]; then
        log_error "没有写入权限: $target_dir"
        log_info "请使用具有写入权限的用户运行此脚本"
        return 1
    fi
    
    return 0
}

# 检查是否已存在
check_existing_skill() {
    local target_dir="$1"
    local skill_name="wechat-auto-publisher"
    local skill_path="$target_dir/$skill_name"
    
    if [ -d "$skill_path" ]; then
        log_warn "技能已存在: $skill_path"
        
        if [ "$FORCE_INSTALL" = true ]; then
            log_info "强制覆盖模式启用，将备份原有技能"
            local backup_dir="${skill_path}-backup-$(date +%Y%m%d-%H%M%S)"
            if mv "$skill_path" "$backup_dir" 2>/dev/null; then
                log_info "✅ 原有技能已备份到: $backup_dir"
            else
                log_error "备份失败，请手动处理"
                return 1
            fi
        else
            log_error "技能已存在，使用 --force 参数覆盖安装"
            log_info "或手动备份/删除原有技能: rm -rf $skill_path"
            return 1
        fi
    fi
    
    return 0
}

# 安装技能
install_skill() {
    local source_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local target_dir="$1"
    local skill_name="wechat-auto-publisher"
    local skill_path="$target_dir/$skill_name"
    
    log_step "3. 安装技能文件..."
    
    # 创建目标目录
    mkdir -p "$skill_path"
    
    # 复制文件
    log_info "正在复制技能文件..."
    
    # 复制所有可见文件和目录
    for item in "$source_dir"/*; do
        local item_name=$(basename "$item")
        
        # 跳过安装脚本本身和一些特殊文件
        case "$item_name" in
            install.sh|wechat-auto-publisher-v1.0.0.tar.gz)
                continue
                ;;
        esac
        
        if [ -e "$item" ]; then
            cp -r "$item" "$skill_path/"
            log_info "  📄 $item_name"
        fi
    done
    
    # 设置执行权限
    log_info "设置执行权限..."
    chmod +x "$skill_path/scripts/"*.sh 2>/dev/null || true
    chmod +x "$skill_path/test-skill.sh" 2>/dev/null || true
    
    log_info "✅ 技能文件安装完成"
    log_info "安装路径: $skill_path"
    
    echo "$skill_path"
}

# 验证安装
verify_installation() {
    local skill_path="$1"
    
    log_step "4. 验证安装..."
    
    # 检查关键文件
    local required_files=(
        "$skill_path/SKILL.md"
        "$skill_path/scripts/auto-publish.sh"
        "$skill_path/scripts/setup.sh"
        "$skill_path/templates/tech-article.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "关键文件缺失: $(basename "$file")"
            return 1
        fi
    done
    
    # 检查脚本可执行权限
    if [ ! -x "$skill_path/scripts/auto-publish.sh" ]; then
        log_error "主脚本不可执行"
        return 1
    fi
    
    log_info "✅ 安装验证通过"
    return 0
}

# 显示安装完成信息
show_completion() {
    local skill_path="$1"
    
    echo ""
    echo "="*60
    echo "              WeChat Auto Publisher 安装完成"
    echo "="*60
    echo ""
    
    echo "🎉 恭喜！技能已成功安装到："
    echo "   $skill_path"
    echo ""
    
    echo "📋 下一步操作："
    echo ""
    echo "1. 配置微信公众号凭证："
    echo "   编辑 ~/.openclaw/workspace/TOOLS.md 文件"
    echo "   添加 WECHAT_APP_ID 和 WECHAT_APP_SECRET"
    echo ""
    echo "2. 添加IP白名单："
    echo "   运行: curl ifconfig.me"
    echo "   将显示的IP添加到微信公众号后台白名单"
    echo ""
    echo "3. 测试安装："
    echo "   cd $skill_path"
    echo "   ./test-skill.sh"
    echo ""
    echo "4. 测试预览模式："
    echo "   ./scripts/auto-publish.sh \"测试主题\" --dry-run"
    echo ""
    echo "5. 开始使用："
    echo "   ./scripts/auto-publish.sh \"你的选题\""
    echo ""
    
    echo "📚 文档资源："
    echo "   - 完整文档: cat $skill_path/SKILL.md | less"
    echo "   - 安装指南: cat $skill_path/INSTALL.md"
    echo "   - 快速开始: cat $skill_path/README.md"
    echo "   - 脚本帮助: $skill_path/scripts/auto-publish.sh --help"
    echo ""
    
    echo "🔧 模块化使用："
    echo "   你也可以单独使用各个功能模块："
    echo "   - 内容生成: ./scripts/generate-content.sh"
    echo "   - 图片生成: ./scripts/generate-images.sh"
    echo "   - 文章格式化: ./scripts/format-article.sh"
    echo "   - 微信公众号发布: ./scripts/publish-wechat.sh"
    echo ""
    
    echo "🆘 需要帮助？"
    echo "   运行: $skill_path/scripts/setup.sh --help"
    echo "   或查看: $skill_path/references/troubleshooting.md"
    echo ""
    
    echo "="*60
    echo ""
    
    log_info "安装完成！开始你的公众号自动化之旅吧！ 🚀"
}

# 主函数
main() {
    # 默认参数
    local target_dir="$HOME/.openclaw/workspace/skills"
    local check_only=false
    local skip_deps=false
    FORCE_INSTALL=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dir)
                target_dir="$2"
                shift 2
                ;;
            -f|--force)
                FORCE_INSTALL=true
                shift
                ;;
            -c|--check-only)
                check_only=true
                shift
                ;;
            --no-deps)
                skip_deps=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示开始信息
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║    WeChat Auto Publisher 安装脚本                ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 检查模式
    if [ "$check_only" = true ]; then
        log_step "检查模式 - 只检查不安装"
        check_dependencies
        check_openclaw_dir "$target_dir"
        log_info "✅ 环境检查完成"
        exit 0
    fi
    
    # 检查依赖
    if [ "$skip_deps" = false ]; then
        check_dependencies || {
            log_error "依赖检查失败，安装中止"
            log_info "使用 --no-deps 跳过依赖检查（不推荐）"
            exit 1
        }
    else
        log_warn "⚠️  跳过依赖检查，请确保必要依赖已安装"
    fi
    
    # 检查目标目录
    check_openclaw_dir "$target_dir" || exit 1
    
    # 检查是否已存在
    check_existing_skill "$target_dir" || exit 1
    
    # 安装技能
    local skill_path=""
    skill_path=$(install_skill "$target_dir") || {
        log_error "安装失败"
        exit 1
    }
    
    # 验证安装
    verify_installation "$skill_path" || {
        log_error "安装验证失败"
        exit 1
    }
    
    # 显示完成信息
    show_completion "$skill_path"
}

# 运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi