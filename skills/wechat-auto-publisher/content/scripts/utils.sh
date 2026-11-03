#!/usr/bin/env bash
# WeChat Auto Publisher - 通用工具函数库

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志级别
LOG_LEVEL="${LOG_LEVEL:-info}" # debug, info, warn, error

# 日志函数
log_debug() {
    if [ "$LOG_LEVEL" = "debug" ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1" >&2
    fi
}

log_info() {
    if [ "$LOG_LEVEL" = "debug" ] || [ "$LOG_LEVEL" = "info" ]; then
        echo -e "${GREEN}[INFO]${NC} $1" >&2
    fi
}

log_warn() {
    if [ "$LOG_LEVEL" = "debug" ] || [ "$LOG_LEVEL" = "info" ] || [ "$LOG_LEVEL" = "warn" ]; then
        echo -e "${YELLOW}[WARN]${NC} $1" >&2
    fi
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1" >&2
}

# 检查命令是否存在
check_command() {
    local cmd="$1"
    if ! command -v "$cmd" &> /dev/null; then
        log_error "命令未找到: $cmd"
        return 1
    fi
    return 0
}

# 检查文件是否存在
check_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        log_error "文件不存在: $file"
        return 1
    fi
    return 0
}

# 检查目录是否存在
check_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        log_error "目录不存在: $dir"
        return 1
    fi
    return 0
}

# 创建目录（如果不存在）
ensure_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_debug "创建目录: $dir"
    fi
}

# 从TOOLS.md读取环境变量
load_from_tools_md() {
    local tools_md="$HOME/.openclaw/workspace/TOOLS.md"
    
    if [ ! -f "$tools_md" ]; then
        log_error "TOOLS.md 文件不存在: $tools_md"
        return 1
    fi
    
    # 读取微信公众号凭证
    local app_id=$(grep "export WECHAT_APP_ID=" "$tools_md" | head -1 | sed 's/.*export WECHAT_APP_ID=//' | tr -d ' ' | tr -d "'" | tr -d '"')
    local app_secret=$(grep "export WECHAT_APP_SECRET=" "$tools_md" | head -1 | sed 's/.*export WECHAT_APP_SECRET=//' | tr -d ' ' | tr -d "'" | tr -d '"')
    
    if [ -z "$app_id" ] || [ -z "$app_secret" ]; then
        log_error "无法从 TOOLS.md 读取微信公众号凭证"
        return 1
    fi
    
    export WECHAT_APP_ID="$app_id"
    export WECHAT_APP_SECRET="$app_secret"
    
    # 读取其他可选环境变量
    local openai_key=$(grep "export OPENAI_API_KEY=" "$tools_md" | head -1 | sed 's/.*export OPENAI_API_KEY=//' | tr -d ' ' | tr -d "'" | tr -d '"')
    local deepseek_key=$(grep "export DEEPSEEK_API_KEY=" "$tools_md" | head -1 | sed 's/.*export DEEPSEEK_API_KEY=//' | tr -d ' ' | tr -d "'" | tr -d '"')
    
    [ -n "$openai_key" ] && export OPENAI_API_KEY="$openai_key"
    [ -n "$deepseek_key" ] && export DEEPSEEK_API_KEY="$deepseek_key"
    
    return 0
}

# 获取公网IP
get_public_ip() {
    log_debug "获取公网IP地址..."
    
    local ip_services=(
        "ifconfig.me"
        "ipinfo.io/ip"
        "api.ipify.org"
        "icanhazip.com"
    )
    
    for service in "${ip_services[@]}"; do
        log_debug "尝试服务: $service"
        local ip=$(curl -s --connect-timeout 5 "$service" 2>/dev/null || true)
        
        if [ -n "$ip" ] && [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            log_debug "从 $service 获取到IP: $ip"
            echo "$ip"
            return 0
        fi
    done
    
    log_error "无法获取公网IP地址"
    return 1
}

# 验证IP格式
validate_ip() {
    local ip="$1"
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 0
    else
        return 1
    fi
}

# 生成随机字符串
random_string() {
    local length="${1:-8}"
    tr -dc 'a-zA-Z0-9' < /dev/urandom | head -c "$length"
}

# 生成时间戳
timestamp() {
    date +"%Y%m%d-%H%M%S"
}

# 生成日期
today() {
    date +"%Y年%m月%d日"
}

# 清理HTML标签（简化版）
strip_html() {
    echo "$1" | sed 's/<[^>]*>//g'
}

# 检查URL是否可访问
check_url() {
    local url="$1"
    local timeout="${2:-5}"
    
    if curl -s --max-time "$timeout" --head "$url" | head -n 1 | grep -q "HTTP"; then
        return 0
    else
        return 1
    fi
}

# 计算文件行数
count_lines() {
    local file="$1"
    if [ -f "$file" ]; then
        wc -l < "$file" | tr -d ' '
    else
        echo "0"
    fi
}

# 计算文件大小（人类可读格式）
human_size() {
    local size="$1"
    if [ "$size" -ge 1073741824 ]; then
        echo "$(echo "scale=2; $size/1073741824" | bc) GB"
    elif [ "$size" -ge 1048576 ]; then
        echo "$(echo "scale=2; $size/1048576" | bc) MB"
    elif [ "$size" -ge 1024 ]; then
        echo "$(echo "scale=2; $size/1024" | bc) KB"
    else
        echo "${size} B"
    fi
}

# 进度条显示
progress_bar() {
    local current="$1"
    local total="$2"
    local width="${3:-50}"
    
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))
    
    printf "\r["
    printf "%${filled}s" "" | tr ' ' '='
    printf "%${empty}s" "" | tr ' ' ' '
    printf "] %3d%%" "$percentage"
    
    if [ "$current" -eq "$total" ]; then
        printf "\n"
    fi
}

# 显示分隔线
separator() {
    local char="${1:-=}"
    local width="${2:-60}"
    printf "%${width}s\n" "" | tr ' ' "$char"
}

# 显示标题
show_title() {
    local title="$1"
    echo ""
    separator "="
    echo "    $title"
    separator "="
    echo ""
}

# 确认提示
confirm() {
    local message="${1:-是否继续？}"
    local default="${2:-Y}"
    
    local prompt="[Y/n]"
    if [ "$default" = "N" ] || [ "$default" = "n" ]; then
        prompt="[y/N]"
    fi
    
    read -p "$message $prompt " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]] || ([ -z "$REPLY" ] && [ "$default" = "Y" ]) || ([ -z "$REPLY" ] && [ "$default" = "y" ]); then
        return 0
    else
        return 1
    fi
}

# 安全退出
safe_exit() {
    local code="${1:-0}"
    local message="${2:-}"
    
    if [ -n "$message" ]; then
        if [ "$code" -eq 0 ]; then
            log_info "$message"
        else
            log_error "$message"
        fi
    fi
    
    exit "$code"
}

# 重试函数
retry() {
    local max_attempts="$1"
    local delay="$2"
    local command="$3"
    shift 3
    
    local attempt=1
    while [ "$attempt" -le "$max_attempts" ]; do
        log_debug "尝试 $attempt/$max_attempts: $command $*"
        
        if $command "$@"; then
            return 0
        fi
        
        if [ "$attempt" -lt "$max_attempts" ]; then
            log_warn "命令失败，${delay}秒后重试..."
            sleep "$delay"
        fi
        
        attempt=$((attempt + 1))
    done
    
    log_error "命令在 $max_attempts 次尝试后仍然失败: $command $*"
    return 1
}

# 提取markdown标题
extract_markdown_title() {
    local file="$1"
    grep -m 1 "^# " "$file" 2>/dev/null | sed 's/^# //' || echo "无标题"
}

# 检查markdown frontmatter
check_frontmatter() {
    local file="$1"
    
    if ! grep -q "^---$" "$file"; then
        log_error "Markdown文件缺少frontmatter分隔符 (---)"
        return 1
    fi
    
    if ! grep -q "^title:" "$file"; then
        log_error "Frontmatter缺少title字段"
        return 1
    fi
    
    if ! grep -q "^cover:" "$file"; then
        log_error "Frontmatter缺少cover字段"
        return 1
    fi
    
    return 0
}

# 获取文件扩展名
get_extension() {
    local file="$1"
    echo "${file##*.}"
}

# 检查图片文件
check_image_file() {
    local file="$1"
    local ext=$(get_extension "$file" | tr '[:upper:]' '[:lower:]')
    
    case "$ext" in
        jpg|jpeg|png|gif|bmp|webp)
            if [ -f "$file" ]; then
                return 0
            else
                return 1
            fi
            ;;
        *)
            return 1
            ;;
    esac
}

# 生成图片占位符（如果ImageMagick不可用）
generate_text_image() {
    local output_file="$1"
    local text="$2"
    local width="${3:-800}"
    local height="${4:-600}"
    
    # 尝试使用ImageMagick
    if command -v convert &> /dev/null; then
        convert -size "${width}x${height}" gradient:#4A90E2-#9013FE \
                -font Arial -pointsize 36 -fill white \
                -gravity center -draw "text 0,0 '$text'" \
                "$output_file" 2>/dev/null && return 0
    fi
    
    # 创建文本文件作为fallback
    echo "图片: $text" > "${output_file%.*}.txt"
    echo "尺寸: ${width}x${height}" >> "${output_file%.*}.txt"
    echo "生成时间: $(date)" >> "${output_file%.*}.txt"
    
    return 0
}