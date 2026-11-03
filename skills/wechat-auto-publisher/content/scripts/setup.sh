#!/usr/bin/env bash
# WeChat Auto Publisher - 环境配置检查脚本
# 检查并配置全自动公众号发布所需的环境

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 路径定义
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TOOLS_MD="$HOME/.openclaw/workspace/TOOLS.md"

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 显示帮助
show_help() {
    cat << EOF
WeChat Auto Publisher 环境配置检查脚本

用法: $0 [选项]

选项:
  -h, --help      显示此帮助信息
  -f, --force     强制重新配置
  -c, --check     只检查不配置
  --no-ip-check   跳过IP白名单检查

功能:
  1. 检查系统依赖 (wenyan-cli, curl, jq等)
  2. 检查微信公众号凭证
  3. 检查IP白名单配置
  4. 检查AI API密钥 (可选)
  5. 初始化目录结构
  6. 生成配置文件示例

示例:
  $0              # 标准检查
  $0 --force      # 强制重新配置
  $0 --check      # 只检查不配置
  $0 --no-ip-check # 跳过IP检查
EOF
}

# 检查系统依赖
check_system_deps() {
    log_step "1. 检查系统依赖..."
    
    local missing_deps=()
    
    # 必需依赖
    if ! command -v wenyan &> /dev/null; then
        missing_deps+=("wenyan-cli")
        log_error "❌ wenyan-cli 未安装"
        log_info "  安装命令: npm install -g @wenyan-md/cli"
    else
        log_info "✅ wenyan-cli 已安装: $(wenyan --version)"
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
        log_error "❌ curl 未安装"
        log_info "  安装命令: apt-get install curl 或 yum install curl"
    else
        log_info "✅ curl 已安装"
    fi
    
    # 推荐依赖
    if ! command -v jq &> /dev/null; then
        log_warn "⚠️  jq 未安装 (JSON处理工具，推荐安装)"
        log_info "  安装命令: apt-get install jq 或 yum install jq"
    else
        log_info "✅ jq 已安装"
    fi
    
    # ImageMagick (可选，用于图片处理)
    if command -v convert &> /dev/null; then
        log_info "✅ ImageMagick 已安装 (支持图片生成)"
    else
        log_warn "⚠️  ImageMagick 未安装 (图片生成功能受限)"
    fi
    
    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少必需依赖: ${missing_deps[*]}"
        return 1
    fi
    
    return 0
}

# 检查微信公众号凭证
check_wechat_credentials() {
    log_step "2. 检查微信公众号凭证..."
    
    local app_id=""
    local app_secret=""
    
    # 首先检查环境变量
    if [ -n "${WECHAT_APP_ID:-}" ] && [ -n "${WECHAT_APP_SECRET:-}" ]; then
        app_id="$WECHAT_APP_ID"
        app_secret="$WECHAT_APP_SECRET"
        log_info "✅ 从环境变量读取凭证"
    else
        # 从TOOLS.md读取
        if [ -f "$TOOLS_MD" ]; then
            app_id=$(grep "export WECHAT_APP_ID=" "$TOOLS_MD" | head -1 | sed 's/.*export WECHAT_APP_ID=//' | tr -d ' ' | tr -d "'" | tr -d '"')
            app_secret=$(grep "export WECHAT_APP_SECRET=" "$TOOLS_MD" | head -1 | sed 's/.*export WECHAT_APP_SECRET=//' | tr -d ' ' | tr -d "'" | tr -d '"')
            
            if [ -n "$app_id" ] && [ -n "$app_secret" ]; then
                export WECHAT_APP_ID="$app_id"
                export WECHAT_APP_SECRET="$app_secret"
                log_info "✅ 从 TOOLS.md 读取凭证"
            fi
        fi
    fi
    
    # 检查凭证是否存在
    if [ -z "$app_id" ] || [ -z "$app_secret" ]; then
        log_error "❌ 微信公众号凭证未设置！"
        log_info ""
        log_info "请在 TOOLS.md 中添加以下内容："
        cat << EOF

## 🔐 WeChat Auto Publisher (全自动微信公众号发布)

# 微信公众号API凭证 (必需)
export WECHAT_APP_ID=你的AppID
export WECHAT_APP_SECRET=你的AppSecret

# AI生成配置 (可选)
export OPENAI_API_KEY=sk-xxx        # 如果使用OpenAI
export DEEPSEEK_API_KEY=sk-xxx      # 如果使用DeepSeek

# 图片配置 (可选)
export UNSPLASH_ACCESS_KEY=xxx      # Unsplash API密钥
export LOCAL_IMAGE_DIR=/path/to/images  # 本地图片目录
EOF
        return 1
    fi
    
    log_info "✅ 微信公众号凭证检查通过"
    log_info "  AppID: ${app_id:0:8}..."
    log_info "  AppSecret: ******"
    
    return 0
}

# 检查IP白名单
check_ip_whitelist() {
    if [ "${NO_IP_CHECK:-false}" = "true" ]; then
        log_step "跳过IP白名单检查"
        return 0
    fi
    
    log_step "3. 检查IP白名单..."
    
    # 获取公网IP
    log_info "获取公网IP地址..."
    local public_ip=""
    
    # 尝试多个IP查询服务
    for service in "ifconfig.me" "ipinfo.io/ip" "api.ipify.org" "icanhazip.com"; do
        if public_ip=$(curl -s --connect-timeout 5 "$service" 2>/dev/null); then
            if [ -n "$public_ip" ] && [[ "$public_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                break
            fi
        fi
    done
    
    if [ -z "$public_ip" ] || ! [[ "$public_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_warn "⚠️  无法获取公网IP地址"
        log_info "  请手动检查IP白名单"
        return 0
    fi
    
    log_info "✅ 公网IP地址: $public_ip"
    log_info ""
    log_info "请确保此IP已添加到微信公众号后台白名单："
    log_info "  1. 登录微信公众平台: https://mp.weixin.qq.com/"
    log_info "  2. 进入「设置与开发」→「基本配置」"
    log_info "  3. 找到「IP白名单」并添加: $public_ip"
    log_info ""
    log_info "注意：如果使用动态IP或代理，可能需要定期更新白名单"
    
    return 0
}

# 检查AI API配置
check_ai_config() {
    log_step "4. 检查AI生成配置..."
    
    local has_ai_config=false
    
    # 检查OpenAI
    if [ -n "${OPENAI_API_KEY:-}" ]; then
        log_info "✅ OpenAI API密钥已设置"
        log_info "  模型: ${OPENAI_MODEL:-gpt-4}"
        has_ai_config=true
    else
        log_warn "⚠️  OpenAI API密钥未设置"
        log_info "  如需使用OpenAI生成内容，请设置 OPENAI_API_KEY"
    fi
    
    # 检查DeepSeek
    if [ -n "${DEEPSEEK_API_KEY:-}" ]; then
        log_info "✅ DeepSeek API密钥已设置"
        log_info "  模型: ${DEEPSEEK_MODEL:-deepseek-chat}"
        has_ai_config=true
    else
        log_warn "⚠️  DeepSeek API密钥未设置"
        log_info "  如需使用DeepSeek生成内容，请设置 DEEPSEEK_API_KEY"
    fi
    
    # 检查其他AI配置
    if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
        log_info "✅ Claude API密钥已设置"
        has_ai_config=true
    fi
    
    if [ -n "${LOCAL_LLM_URL:-}" ]; then
        log_info "✅ 本地LLM配置: $LOCAL_LLM_URL"
        has_ai_config=true
    fi
    
    if [ "$has_ai_config" = false ]; then
        log_warn "⚠️  未设置任何AI API密钥"
        log_info "  将使用模板生成基础内容，或手动提供文章"
        log_info "  建议至少配置一个AI服务以获得更好效果"
    fi
    
    return 0
}

# 检查图片配置
check_image_config() {
    log_step "5. 检查图片配置..."
    
    # 检查Unsplash
    if [ -n "${UNSPLASH_ACCESS_KEY:-}" ]; then
        log_info "✅ Unsplash API密钥已设置"
        log_info "  将使用Unsplash获取高质量图片"
    else
        log_warn "⚠️  Unsplash API密钥未设置"
        log_info "  如需使用Unsplash图片，请设置 UNSPLASH_ACCESS_KEY"
    fi
    
    # 检查本地图片目录
    if [ -n "${LOCAL_IMAGE_DIR:-}" ]; then
        if [ -d "$LOCAL_IMAGE_DIR" ]; then
            local image_count=$(find "$LOCAL_IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l)
            log_info "✅ 本地图片目录: $LOCAL_IMAGE_DIR"
            log_info "  图片数量: $image_count"
        else
            log_warn "⚠️  本地图片目录不存在: $LOCAL_IMAGE_DIR"
        fi
    else
        log_warn "⚠️  本地图片目录未设置"
        log_info "  如需使用本地图片，请设置 LOCAL_IMAGE_DIR"
    fi
    
    # 检查默认图片资源
    local assets_dir="$SKILL_DIR/assets"
    if [ -d "$assets_dir" ]; then
        local default_images=$(find "$assets_dir" -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | wc -l)
        log_info "✅ 技能自带图片资源: $default_images 个"
    else
        log_warn "⚠️  技能图片资源目录不存在"
        log_info "  将使用简单生成的占位图片"
    fi
    
    return 0
}

# 初始化目录结构
init_directories() {
    log_step "6. 初始化目录结构..."
    
    local dirs=(
        "$SKILL_DIR/templates"
        "$SKILL_DIR/config"
        "$SKILL_DIR/config/generators"
        "$SKILL_DIR/config/image-sources"
        "$SKILL_DIR/references"
        "$SKILL_DIR/assets"
        "$SKILL_DIR/assets/tech-images"
        "$SKILL_DIR/assets/business-images"
        "$SKILL_DIR/assets/lifestyle-images"
        "$SKILL_DIR/output"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_info "📁 创建目录: $dir"
        fi
    done
    
    # 创建默认配置文件
    create_default_configs
    
    log_info "✅ 目录结构初始化完成"
}

# 创建默认配置文件
create_default_configs() {
    # 创建模板文件
    local templates_dir="$SKILL_DIR/templates"
    
    # 技术文章模板
    if [ ! -f "$templates_dir/tech-article.md" ]; then
        cat > "$templates_dir/tech-article.md" << 'EOF'
# {TOPIC}

## 概述
{TOPIC}是当前技术领域的重要发展方向，对行业和个人都有深远影响。

## 核心内容

### 1. 技术原理
介绍{TOPIC}的基本原理和关键技术。

### 2. 应用场景
分析{TOPIC}在实际工作中的应用场景和案例。

### 3. 学习路径
提供学习{TOPIC}的路线图和建议资源。

### 4. 最佳实践
分享{TOPIC}相关的最佳实践和经验教训。

## 实用工具推荐
- 🔧 工具一：相关开发工具
- 📚 工具二：学习资源平台
- 🛠️ 工具三：调试和测试工具

## 总结
{TOPIC}代表了技术发展的重要趋势，掌握相关知识对职业发展至关重要。

---
*本文由 WeChat Auto Publisher 自动生成*
*模板：技术文章 | 版本：1.0*
EOF
        log_info "📄 创建模板: tech-article.md"
    fi
    
    # 商业分析模板
    if [ ! -f "$templates_dir/business-report.md" ]; then
        cat > "$templates_dir/business-report.md" << 'EOF'
# {TOPIC}市场分析与商业洞察

## 执行摘要
本文分析{TOPIC}的市场现状、发展趋势和商业机会。

## 市场分析

### 1. 市场规模
- 当前市场规模及增长预测
- 主要细分领域分析
- 区域市场特点

### 2. 竞争格局
- 主要竞争者分析
- 市场份额分布
- 竞争策略比较

### 3. 用户洞察
- 目标用户画像
- 用户需求分析
- 消费行为趋势

## 机会与挑战

### 🟢 发展机会
1. 新兴技术应用
2. 政策支持方向
3. 市场空白领域

### 🔴 面临挑战
1. 技术门槛
2. 市场竞争
3. 法规限制

## 战略建议

### 短期策略 (1年内)
- 快速验证产品市场匹配
- 建立核心用户群体
- 完善产品基础功能

### 中期规划 (1-3年)
- 拓展市场份额
- 构建技术壁垒
- 探索商业模式

### 长期愿景 (3-5年)
- 行业领导者地位
- 生态体系建设
- 国际化扩张

## 投资建议
- 💰 推荐投资级别：积极关注
- 📈 增长潜力：中等偏高
- ⚠️ 风险等级：中等

---
*本文由 WeChat Auto Publisher 自动生成*
*模板：商业分析 | 版本：1.0*
EOF
        log_info "📄 创建模板: business-report.md"
    fi
    
    # 创建配置示例
    local config_dir="$SKILL_DIR/config"
    
    # OpenAI配置示例
    if [ ! -f "$config_dir/generators/openai-config.sh" ]; then
        cat > "$config_dir/generators/openai-config.sh" << 'EOF'
#!/usr/bin/env bash
# OpenAI 内容生成器配置

# API配置
export OPENAI_API_KEY="sk-your-openai-api-key-here"
export OPENAI_MODEL="gpt-4"
export OPENAI_BASE_URL="https://api.openai.com/v1"

# 生成参数
export OPENAI_TEMPERATURE="0.7"
export OPENAI_MAX_TOKENS="2000"
export OPENAI_TOP_P="0.9"
export OPENAI_FREQUENCY_PENALTY="0"
export OPENAI_PRESENCE_PENALTY="0"

# 提示词模板
export OPENAI_SYSTEM_PROMPT="你是一位专业的内容创作者，擅长撰写微信公众号文章。文章风格亲切自然，结构清晰，实用性强。"
export OPENAI_USER_PROMPT_TEMPLATE="请撰写一篇关于'{TOPIC}'的微信公众号文章。要求：\n1. 标题吸引人\n2. 结构清晰（引言、主体、结论）\n3. 语言亲切自然\n4. 包含实用建议\n5. 适当使用emoji增强可读性"
EOF
        chmod +x "$config_dir/generators/openai-config.sh"
        log_info "📄 创建配置: openai-config.sh"
    fi
}

# 生成配置报告
generate_config_report() {
    log_step "7. 生成配置报告..."
    
    local report_file="$SKILL_DIR/config/setup-report-$(date +%Y%m%d-%H%M%S).txt"
    
    cat > "$report_file" << EOF
WeChat Auto Publisher 环境配置报告
生成时间: $(date "+%Y-%m-%d %H:%M:%S")

=== 系统信息 ===
主机名: $(hostname)
系统: $(uname -a)
Shell: $SHELL
用户: $(whoami)

=== 依赖检查 ===
wenyan-cli: $(command -v wenyan >/dev/null && echo "已安装 ($(wenyan --version 2>/dev/null || echo "未知版本"))" || echo "未安装")
curl: $(command -v curl >/dev/null && echo "已安装" || echo "未安装")
jq: $(command -v jq >/dev/null && echo "已安装" || echo "未安装")
ImageMagick: $(command -v convert >/dev/null && echo "已安装" || echo "未安装")

=== 微信公众号凭证 ===
AppID: ${WECHAT_APP_ID:-未设置}
AppSecret: ${WECHAT_APP_SECRET:-未设置}

=== AI配置 ===
OpenAI API: ${OPENAI_API_KEY:+已设置}
DeepSeek API: ${DEEPSEEK_API_KEY:+已设置}
Claude API: ${ANTHROPIC_API_KEY:+已设置}
本地LLM: ${LOCAL_LLM_URL:+已设置}

=== 图片配置 ===
Unsplash: ${UNSPLASH_ACCESS_KEY:+已设置}
本地图片目录: ${LOCAL_IMAGE_DIR:-未设置}

=== 目录结构 ===
技能目录: $SKILL_DIR
模板目录: $SKILL_DIR/templates ($(ls "$SKILL_DIR/templates/"*.md 2>/dev/null | wc -l) 个模板)
配置目录: $SKILL_DIR/config
输出目录: $SKILL_DIR/output
资源目录: $SKILL_DIR/assets

=== 建议和提醒 ===
1. 确保微信公众号IP白名单已配置
2. 测试发布前建议使用 --dry-run 参数
3. 定期更新技能和依赖
4. 备份重要配置文件

=== 后续步骤 ===
1. 运行测试: ./scripts/auto-publish.sh "测试选题" --dry-run
2. 实际发布: ./scripts/auto-publish.sh "你的选题"
3. 查看文档: cat SKILL.md | less
EOF
    
    log_info "✅ 配置报告已生成: $report_file"
    log_info "  查看报告: cat $report_file"
}

# 主函数
main() {
    # 解析参数
    local force=false
    local check_only=false
    NO_IP_CHECK=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            --no-ip-check)
                NO_IP_CHECK=true
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║    WeChat Auto Publisher 环境配置检查             ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 执行检查
    local all_checks_passed=true
    
    check_system_deps || all_checks_passed=false
    echo ""
    
    check_wechat_credentials || all_checks_passed=false
    echo ""
    
    check_ip_whitelist
    echo ""
    
    check_ai_config
    echo ""
    
    check_image_config
    echo ""
    
    if [ "$check_only" = false ]; then
        init_directories
        echo ""
        
        generate_config_report
        echo ""
    fi
    
    # 显示总结
    if [ "$all_checks_passed" = true ]; then
        echo -e "${GREEN}=================================================${NC}"
        echo -e "${GREEN}✅ 所有必需检查通过！${NC}"
        echo -e "${GREEN}=================================================${NC}"
        echo ""
        echo "下一步建议："
        echo "  1. 运行测试: ./scripts/auto-publish.sh \"测试选题\" --dry-run"
        echo "  2. 实际发布: ./scripts/auto-publish.sh \"你的选题\""
        echo "  3. 查看帮助: ./scripts/auto-publish.sh --help"
    else
        echo -e "${YELLOW}=================================================${NC}"
        echo -e "${YELLOW}⚠️  部分检查未通过，请根据提示修复${NC}"
        echo -e "${YELLOW}=================================================${NC}"
        echo ""
        echo "需要修复的问题："
        echo "  1. 确保所有必需依赖已安装"
        echo "  2. 正确配置微信公众号凭证"
        echo "  3. 将服务器IP添加到公众号白名单"
        echo ""
        echo "修复后重新运行: $0"
    fi
    
    echo ""
    echo "更多信息请查看:"
    echo "  📖 技能文档: SKILL.md"
    echo "  📖 使用说明: README.md"
    echo "  🛠️  主脚本: ./scripts/auto-publish.sh"
}

# 运行主函数
main "$@"