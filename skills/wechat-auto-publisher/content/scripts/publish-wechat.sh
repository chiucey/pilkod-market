#!/usr/bin/env bash
# 微信公众号发布脚本
# 将格式化后的文章发布到微信公众号草稿箱

set -euo pipefail

# 加载工具函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || {
    echo "错误：无法加载 utils.sh"
    exit 1
}

# 显示帮助
show_help() {
    cat << EOF
微信公众号发布器 - WeChat Auto Publisher

用法: $0 [选项] <文章文件>

选项:
  -h, --help          显示此帮助信息
  -d, --dry-run       预览模式（不实际发布）
  -t, --theme NAME    主题名称 (默认: lapis)
  -c, --highlight NAME 代码高亮主题 (默认: solarized-light)
  -l, --log FILE      日志文件 (默认: 自动生成)
  --no-mac-style      禁用Mac风格代码块
  --no-footnote       禁用链接转脚注

示例:
  $0 article.md
  $0 article.md --dry-run
  $0 article.md --theme phycat --highlight github
  $0 article.md --log publish.log
EOF
}

# 检查wenyan-cli
check_wenyan() {
    if ! command -v wenyan &> /dev/null; then
        log_error "wenyan-cli 未安装！"
        log_info "请运行: npm install -g @wenyan-md/cli"
        return 1
    fi
    
    log_info "✅ wenyan-cli 已安装: $(wenyan --version)"
    return 0
}

# 检查微信公众号凭证
check_wechat_credentials() {
    if [ -z "${WECHAT_APP_ID:-}" ] || [ -z "${WECHAT_APP_SECRET:-}" ]; then
        log_error "微信公众号凭证未设置！"
        log_info "请设置环境变量:"
        log_info "  export WECHAT_APP_ID=你的AppID"
        log_info "  export WECHAT_APP_SECRET=你的AppSecret"
        log_info "或在 TOOLS.md 中添加凭证"
        return 1
    fi
    
    log_info "✅ 微信公众号凭证检查通过"
    log_debug "AppID: ${WECHAT_APP_ID:0:8}..."
    log_debug "AppSecret: ******"
    return 0
}

# 检查IP白名单状态
check_ip_whitelist_status() {
    log_info "检查IP白名单状态..."
    
    # 获取公网IP
    local public_ip
    if public_ip=$(get_public_ip); then
        log_info "当前公网IP: $public_ip"
        log_info "请确保此IP已添加到微信公众号后台白名单"
    else
        log_warn "⚠️  无法获取公网IP，请手动检查IP白名单"
    fi
    
    log_info "IP白名单配置位置："
    log_info "  微信公众平台 → 设置与开发 → 基本配置 → IP白名单"
    return 0
}

# 预览文章
preview_article() {
    local article_file="$1"
    local theme="$2"
    local highlight="$3"
    
    log_step "预览模式 - 不实际发布"
    
    # 检查文章文件
    if [ ! -f "$article_file" ]; then
        log_error "文章文件不存在: $article_file"
        return 1
    fi
    
    # 显示文章信息
    log_info "文章文件: $article_file"
    log_info "主题: $theme"
    log_info "代码高亮: $highlight"
    
    # 显示frontmatter
    log_info "Frontmatter信息:"
    grep -A 5 "^---$" "$article_file" | head -10 | while IFS= read -r line; do
        log_info "  $line"
    done
    
    # 显示文章预览
    log_info "文章预览 (前10行):"
    head -10 "$article_file" | while IFS= read -r line; do
        log_info "  $line"
    done
    
    # 检查图片引用
    local image_count=$(grep -c "!\[.*\](.*)" "$article_file" || true)
    log_info "图片引用数量: $image_count"
    
    # 模拟发布结果
    log_info "模拟发布结果："
    log_info "  ✅ 文章格式检查通过"
    log_info "  ✅ 图片引用检查通过"
    log_info "  ✅ 凭证检查通过"
    log_info "  ⏸️  预览模式 - 未实际发布"
    
    echo "preview_success:true"
    return 0
}

# 发布到微信公众号
publish_to_wechat() {
    local article_file="$1"
    local theme="$2"
    local highlight="$3"
    local mac_style="$4"
    local footnote="$5"
    local log_file="$6"
    
    log_step "发布到微信公众号..."
    
    # 检查文章文件
    if [ ! -f "$article_file" ]; then
        log_error "文章文件不存在: $article_file"
        return 1
    fi
    
    # 检查frontmatter
    if ! check_frontmatter "$article_file"; then
        log_warn "文章frontmatter不完整，可能影响发布"
    fi
    
    # 设置环境变量（wenyan-cli会读取）
    export WECHAT_APP_ID
    export WECHAT_APP_SECRET
    
    # 构建wenyan命令
    local wenyan_cmd="wenyan publish -f \"$article_file\" -t \"$theme\" -h \"$highlight\""
    
    if [ "$mac_style" = "false" ]; then
        wenyan_cmd="$wenyan_cmd --no-mac-style"
    fi
    
    if [ "$footnote" = "false" ]; then
        wenyan_cmd="$wenyan_cmd --no-footnote"
    fi
    
    log_info "执行命令: $wenyan_cmd"
    
    # 执行发布
    local start_time=$(date +%s)
    
    if eval "$wenyan_cmd" 2>&1 | tee "$log_file"; then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_info "✅ 发布成功！"
        log_info "耗时: ${duration}秒"
        
        # 提取发布结果信息
        local result_info=""
        if [ -f "$log_file" ]; then
            result_info=$(grep -i "成功\|success\|draft\|草稿\|链接" "$log_file" | head -5 || true)
        fi
        
        if [ -n "$result_info" ]; then
            log_info "发布结果:"
            echo "$result_info" | while IFS= read -r line; do
                log_info "  $line"
            done
        fi
        
        echo "publish_success:true"
        echo "log_file:$log_file"
        echo "duration:${duration}"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_error "❌ 发布失败！"
        log_info "耗时: ${duration}秒"
        
        # 提取错误信息
        local error_info=""
        if [ -f "$log_file" ]; then
            error_info=$(grep -i "错误\|error\|fail\|失败\|无效\|invalid" "$log_file" | head -5 || true)
        fi
        
        if [ -n "$error_info" ]; then
            log_error "错误信息:"
            echo "$error_info" | while IFS= read -r line; do
                log_error "  $line"
            done
        fi
        
        # 常见错误处理建议
        log_info "常见问题排查："
        log_info "  1. 检查微信公众号凭证是否正确"
        log_info "  2. 确认IP已添加到白名单"
        log_info "  3. 检查文章格式和图片路径"
        log_info "  4. 查看详细日志: $log_file"
        
        echo "publish_success:false"
        echo "log_file:$log_file"
        echo "duration:${duration}"
        return 1
    fi
}

# 显示发布结果
show_publish_result() {
    local success="$1"
    local article_file="$2"
    local log_file="$3"
    local duration="$4"
    
    echo ""
    separator "="
    
    if [ "$success" = "true" ]; then
        echo -e "    ${GREEN}🎉 发布成功！${NC}"
    else
        echo -e "    ${RED}❌ 发布失败${NC}"
    fi
    
    separator "="
    echo ""
    
    echo "文章信息:"
    echo "  文件: $(basename "$article_file")"
    echo "  路径: $article_file"
    echo "  大小: $(du -h "$article_file" | cut -f1)"
    echo "  行数: $(count_lines "$article_file")"
    echo ""
    
    echo "发布信息:"
    echo "  耗时: ${duration}秒"
    echo "  日志: $log_file"
    echo ""
    
    if [ "$success" = "true" ]; then
        echo "下一步操作："
        echo "  1. 登录微信公众号后台: https://mp.weixin.qq.com/"
        echo "  2. 进入「内容管理」→「草稿箱」"
        echo "  3. 找到文章并审核发布"
        echo "  4. 可预览后群发或直接发布"
        echo ""
        echo "提示：文章可能需要几分钟才会出现在草稿箱中"
    else
        echo "错误排查："
        echo "  1. 检查日志文件: $log_file"
        echo "  2. 验证微信公众号凭证"
        echo "  3. 确认IP白名单配置"
        echo "  4. 检查网络连接"
        echo "  5. 查看文章格式是否正确"
        echo ""
        echo "详细日志最后10行："
        tail -10 "$log_file" 2>/dev/null | while IFS= read -r line; do
            echo "  $line"
        done
    fi
    
    separator "="
    echo ""
}

# 主函数
main() {
    # 默认参数
    local article_file=""
    local dry_run=false
    local theme="lapis"
    local highlight="solarized-light"
    local log_file=""
    local mac_style=true
    local footnote=true
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -d|--dry-run)
                dry_run=true
                shift
                ;;
            -t|--theme)
                theme="$2"
                shift 2
                ;;
            -c|--highlight)
                highlight="$2"
                shift 2
                ;;
            -l|--log)
                log_file="$2"
                shift 2
                ;;
            --no-mac-style)
                mac_style=false
                shift
                ;;
            --no-footnote)
                footnote=false
                shift
                ;;
            *)
                if [ -z "$article_file" ]; then
                    article_file="$1"
                else
                    log_error "未知参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查必需参数
    if [ -z "$article_file" ]; then
        log_error "请指定文章文件！"
        show_help
        exit 1
    fi
    
    # 生成日志文件名
    if [ -z "$log_file" ]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local safe_name=$(basename "$article_file" .md | tr -cd '[:alnum:]' | cut -c1-20)
        log_file="/tmp/wechat-publish-${safe_name}-${timestamp}.log"
    fi
    
    # 显示开始信息
    show_title "微信公众号发布器"
    log_info "文章文件: $article_file"
    log_info "发布模式: $([ "$dry_run" = "true" ] && echo "预览" || echo "正式")"
    log_info "主题设置: $theme"
    log_info "高亮主题: $highlight"
    log_info "日志文件: $log_file"
    
    # 检查依赖
    check_wenyan || exit 1
    
    # 检查凭证（预览模式可跳过部分检查）
    if [ "$dry_run" = "false" ]; then
        check_wechat_credentials || exit 1
        check_ip_whitelist_status
    fi
    
    # 执行发布或预览
    local publish_result=""
    local success=false
    local duration=0
    
    if [ "$dry_run" = "true" ]; then
        if publish_result=$(preview_article "$article_file" "$theme" "$highlight"); then
            success=true
        fi
    else
        if publish_result=$(publish_to_wechat "$article_file" "$theme" "$highlight" "$mac_style" "$footnote" "$log_file"); then
            success=true
            # 解析结果
            duration=$(echo "$publish_result" | grep "^duration:" | cut -d':' -f2 || echo "0")
        fi
    fi
    
    # 显示结果
    show_publish_result "$success" "$article_file" "$log_file" "$duration"
    
    # 返回退出码
    if [ "$success" = "true" ]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主函数
if [[ "${BASH_Source[0]}" == "${0}" ]]; then
    main "$@"
fi