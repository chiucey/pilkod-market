#!/usr/bin/env bash
# 素材搜集器 - WeChat Auto Publisher 增强版
# 输入：选题、搜索平台、数量限制
# 输出：素材摘要文件

set -euo pipefail

# 加载工具函数
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/utils.sh" 2>/dev/null || {
    echo "错误：无法加载 utils.sh"
    exit 1
}

# 默认配置
DEFAULT_SEARCH_PLATFORMS="web,wechat"
DEFAULT_RESULT_COUNT=5
DEFAULT_OUTPUT_FORMAT="markdown"

# 显示帮助
show_help() {
    cat << EOF
素材搜集器 - WeChat Auto Publisher 增强版

用法: $0 [选项] "选题内容"

选项:
  -h, --help          显示此帮助信息
  -p, --platforms LIST 搜索平台列表 (默认: $DEFAULT_SEARCH_PLATFORMS)
                      可用平台: web, wechat, zhihu, bilibili, douyin, xiaohongshu, weibo
  -c, --count NUM     每个平台的结果数量 (默认: $DEFAULT_RESULT_COUNT)
  -o, --output FILE   输出文件 (默认: 自动生成)
  -f, --format FORMAT 输出格式: markdown, json, text (默认: $DEFAULT_OUTPUT_FORMAT)
      --debug         调试模式

示例:
  $0 "未来AI对工作的影响"
  $0 "Python编程技巧" --platforms web,wechat,zhihu --count 3
  $0 "健康饮食指南" --output materials.md --format json
EOF
}

# 检查搜索工具依赖
check_search_tools() {
    log_step "检查搜索工具依赖..."
    
    # 检查 curl
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装！"
        exit 1
    fi
    log_info "✅ curl 已安装"
    
    # 检查 jq (用于JSON处理)
    if command -v jq &> /dev/null; then
        log_info "✅ jq 已安装"
    else
        log_warn "⚠️  jq 未安装，JSON处理功能受限"
    fi
    
    # 检查 Python3
    if command -v python3 &> /dev/null; then
        log_info "✅ python3 已安装"
    else
        log_warn "⚠️  python3 未安装，部分高级搜索功能不可用"
    fi
    
    # 检查是否安装了 agent-reach
    if [ -d "$HOME/.agent-reach" ] || [ -f "/usr/local/bin/agent-reach" ]; then
        log_info "✅ agent-reach 已安装"
    else
        log_warn "⚠️  agent-reach 未安装，部分平台搜索功能受限"
    fi
}

# 通用网页搜索（使用 DuckDuckGo HTML 接口）
search_web() {
    local query="$1"
    local count="$2"
    local output_file="$3"
    
    log_info "🌐 网页搜索: $query (数量: $count)"
    
    # URL编码查询
    local encoded_query
    encoded_query=$(echo "$query" | sed 's/ /+/g')
    
    # DuckDuckGo HTML搜索
    local search_url="https://html.duckduckgo.com/html/?q=$encoded_query"
    
    log_debug "搜索URL: $search_url"
    
    # 获取搜索结果页面
    local html_content
    html_content=$(curl -s -A "Mozilla/5.0" "$search_url") || {
        log_warn "网页搜索失败，使用备用方法"
        return 1
    }
    
    # 提取搜索结果（简化版）
    echo "# 网页搜索结果: $query" > "$output_file"
    echo "" >> "$output_file"
    
    # 使用简单的grep提取标题和链接
    echo "$html_content" | grep -o '<a[^>]*class="result__url"[^>]*>[^<]*</a>' | head -"$count" | while read -r line; do
        # 提取标题
        local title
        title=$(echo "$line" | sed 's/<[^>]*>//g' | xargs)
        
        # 提取链接（简化版）
        local url
        url=$(echo "$line" | grep -o 'href="[^"]*"' | sed 's/href="//' | sed 's/"//')
        
        if [ -n "$title" ] && [ -n "$url" ]; then
            echo "## $title" >> "$output_file"
            echo "链接: $url" >> "$output_file"
            
            # 尝试获取页面摘要
            if command -v python3 &> /dev/null; then
                local summary
                summary=$(python3 -c "
import urllib.request
import urllib.error
try:
    with urllib.request.urlopen('$url', timeout=5) as response:
        html = response.read().decode('utf-8', errors='ignore')
        # 简单提取前200个字符
        import re
        text = re.sub('<[^>]+>', ' ', html)
        text = ' '.join(text.split()[:50])
        print(text[:200])
except:
    print('无法获取页面内容')
")
                echo "摘要: $summary..." >> "$output_file"
            fi
            
            echo "" >> "$output_file"
        fi
    done
    
    local result_count
    result_count=$(grep -c "## " "$output_file" || echo 0)
    
    if [ "$result_count" -gt 0 ]; then
        log_info "✅ 网页搜索完成: $result_count 个结果"
    else
        log_warn "⚠️  网页搜索结果为空"
    fi
}

# 微信公众号文章搜索（简化版）
search_wechat() {
    local query="$1"
    local count="$2"
    local output_file="$3"
    
    log_info "📰 微信公众号搜索: $query (数量: $count)"
    
    # 检查是否有 agent-reach 可用
    if [ -f "$HOME/.agent-reach/tools/wechat-article-for-ai/main.py" ]; then
        log_info "使用 agent-reach 搜索微信公众号文章..."
        
        # 调用 agent-reach 的微信搜索功能
        cd "$HOME/.agent-reach/tools/wechat-article-for-ai" && \
        python3 main.py --search "$query" --limit "$count" > "$output_file.tmp" 2>/dev/null || true
        
        if [ -s "$output_file.tmp" ]; then
            echo "# 微信公众号搜索结果: $query" > "$output_file"
            echo "" >> "$output_file"
            cat "$output_file.tmp" >> "$output_file"
            log_info "✅ 微信公众号搜索完成"
            rm -f "$output_file.tmp"
            return 0
        fi
    fi
    
    # 备用方法：使用搜索引擎搜索微信公众号文章
    log_info "使用备用方法搜索微信公众号文章..."
    
    # 搜索包含 "site:mp.weixin.qq.com" 的结果
    local encoded_query
    encoded_query=$(echo "$query site:mp.weixin.qq.com" | sed 's/ /+/g')
    
    local search_url="https://html.duckduckgo.com/html/?q=$encoded_query"
    
    echo "# 微信公众号搜索结果: $query" > "$output_file"
    echo "" >> "$output_file"
    echo "> 注：由于 API 限制，仅显示通过公开搜索引擎找到的微信公众号文章" >> "$output_file"
    echo "" >> "$output_file"
    
    curl -s -A "Mozilla/5.0" "$search_url" | grep -o '<a[^>]*class="result__url"[^>]*>[^<]*</a>' | head -"$count" | while read -r line; do
        local title
        title=$(echo "$line" | sed 's/<[^>]*>//g' | xargs)
        
        local url
        url=$(echo "$line" | grep -o 'href="[^"]*"' | sed 's/href="//' | sed 's/"//')
        
        if [[ "$url" == *"mp.weixin.qq.com"* ]] && [ -n "$title" ]; then
            echo "## $title" >> "$output_file"
            echo "链接: $url" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done
    
    local result_count
    result_count=$(grep -c "## " "$output_file" || echo 0)
    
    if [ "$result_count" -gt 0 ]; then
        log_info "✅ 微信公众号搜索完成: $result_count 个结果"
    else
        log_warn "⚠️  微信公众号搜索结果为空"
        echo "未找到相关微信公众号文章。" >> "$output_file"
    fi
}

# 知乎搜索（简化版）
search_zhihu() {
    local query="$1"
    local count="$2"
    local output_file="$3"
    
    log_info "📚 知乎搜索: $query (数量: $count)"
    
    echo "# 知乎搜索结果: $query" > "$output_file"
    echo "" >> "$output_file"
    
    # 使用搜索引擎搜索知乎
    local encoded_query
    encoded_query=$(echo "$query site:zhihu.com" | sed 's/ /+/g')
    
    local search_url="https://html.duckduckgo.com/html/?q=$encoded_query"
    
    curl -s -A "Mozilla/5.0" "$search_url" | grep -o '<a[^>]*class="result__url"[^>]*>[^<]*</a>' | head -"$count" | while read -r line; do
        local title
        title=$(echo "$line" | sed 's/<[^>]*>//g' | xargs)
        
        local url
        url=$(echo "$line" | grep -o 'href="[^"]*"' | sed 's/href="//' | sed 's/"//')
        
        if [[ "$url" == *"zhihu.com"* ]] && [ -n "$title" ]; then
            echo "## $title" >> "$output_file"
            echo "链接: $url" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done
    
    local result_count
    result_count=$(grep -c "## " "$output_file" || echo 0)
    
    if [ "$result_count" -gt 0 ]; then
        log_info "✅ 知乎搜索完成: $result_count 个结果"
    else
        log_warn "⚠️  知乎搜索结果为空"
        echo "未找到相关知乎内容。" >> "$output_file"
    fi
}

# B站搜索（简化版）
search_bilibili() {
    local query="$1"
    local count="$2"
    local output_file="$3"
    
    log_info "🎬 B站搜索: $query (数量: $count)"
    
    echo "# B站搜索结果: $query" > "$output_file"
    echo "" >> "$output_file"
    
    # 使用搜索引擎搜索B站
    local encoded_query
    encoded_query=$(echo "$query site:bilibili.com" | sed 's/ /+/g')
    
    local search_url="https://html.duckduckgo.com/html/?q=$encoded_query"
    
    curl -s -A "Mozilla/5.0" "$search_url" | grep -o '<a[^>]*class="result__url"[^>]*>[^<]*</a>' | head -"$count" | while read -r line; do
        local title
        title=$(echo "$line" | sed 's/<[^>]*>//g' | xargs)
        
        local url
        url=$(echo "$line" | grep -o 'href="[^"]*"' | sed 's/href="//' | sed 's/"//')
        
        if [[ "$url" == *"bilibili.com"* ]] && [ -n "$title" ]; then
            echo "## $title" >> "$output_file"
            echo "链接: $url" >> "$output_file"
            echo "" >> "$output_file"
        fi
    done
    
    local result_count
    result_count=$(grep -c "## " "$output_file" || echo 0)
    
    if [ "$result_count" -gt 0 ]; then
        log_info "✅ B站搜索完成: $result_count 个结果"
    else
        log_warn "⚠️  B站搜索结果为空"
        echo "未找到相关B站视频。" >> "$output_file"
    fi
}

# 整理搜索结果，生成素材摘要
generate_material_summary() {
    local topic="$1"
    local search_dir="$2"
    local output_file="$3"
    local format="$4"
    
    log_step "整理搜索结果，生成素材摘要..."
    
    # 收集所有搜索结果
    local all_results=""
    
    for platform_file in "$search_dir"/*.md; do
        if [ -f "$platform_file" ] && [ -s "$platform_file" ]; then
            local platform_name
            platform_name=$(basename "$platform_file" .md)
            all_results="$all_results\n\n=== $platform_name ===\n$(cat "$platform_file")"
        fi
    done
    
    if [ -z "$all_results" ]; then
        log_warn "⚠️  所有平台搜索结果均为空"
        echo "# 素材搜集结果: $topic" > "$output_file"
        echo "" >> "$output_file"
        echo "## 搜索结果摘要" >> "$output_file"
        echo "未找到相关素材。" >> "$output_file"
        return 0
    fi
    
    # 根据格式生成输出
    case "$format" in
        json)
            # 简化版JSON输出
            echo "{" > "$output_file"
            echo "  \"topic\": \"$topic\"," >> "$output_file"
            echo "  \"materials\": [" >> "$output_file"
            
            # 这里可以添加更复杂的JSON转换
            echo "    {\"note\": \"原始结果请查看 $search_dir 目录\"}" >> "$output_file"
            
            echo "  ]" >> "$output_file"
            echo "}" >> "$output_file"
            ;;
        text)
            echo "素材搜集结果: $topic" > "$output_file"
            echo "" >> "$output_file"
            echo "=== 搜索结果 ===" >> "$output_file"
            echo "$all_results" | sed 's/^#/##/g' >> "$output_file"
            ;;
        markdown|*)
            echo "# 素材搜集结果: $topic" > "$output_file"
            echo "" >> "$output_file"
            echo "## 搜索结果摘要" >> "$output_file"
            echo "" >> "$output_file"
            echo "以下是根据选题 **\"$topic\"** 从多个平台搜集的相关素材：" >> "$output_file"
            echo "" >> "$output_file"
            
            # 统计结果
            local total_results=0
            for platform_file in "$search_dir"/*.md; do
                if [ -f "$platform_file" ] && [ -s "$platform_file" ]; then
                    local platform_name
                    platform_name=$(basename "$platform_file" .md)
                    local count
                    count=$(grep -c "## " "$platform_file" 2>/dev/null || echo 0)
                    total_results=$((total_results + count))
                    echo "- **${platform_name}**: $count 个结果" >> "$output_file"
                fi
            done
            
            echo "" >> "$output_file"
            echo "## 详细结果" >> "$output_file"
            echo "" >> "$output_file"
            echo "$all_results" >> "$output_file"
            
            echo "" >> "$output_file"
            echo "## 使用建议" >> "$output_file"
            echo "" >> "$output_file"
            echo "1. **参考素材**：以上素材可作为文章创作的参考" >> "$output_file"
            echo "2. **引用注明**：如需引用，请注明出处" >> "$output_file"
            echo "3. **原创优先**：建议基于素材创作原创内容，而非直接复制" >> "$output_file"
            echo "4. **版权注意**：注意素材的版权情况，避免侵权" >> "$output_file"
            ;;
    esac
    
    log_info "✅ 素材摘要生成完成: $output_file"
    log_info "总计结果: $total_results 个"
}

# 主函数
main() {
    # 默认参数
    local topic=""
    local platforms="$DEFAULT_SEARCH_PLATFORMS"
    local count="$DEFAULT_RESULT_COUNT"
    local output_file=""
    local format="$DEFAULT_OUTPUT_FORMAT"
    local debug=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -p|--platforms)
                platforms="$2"
                shift 2
                ;;
            -c|--count)
                count="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -f|--format)
                format="$2"
                shift 2
                ;;
            --debug)
                debug=true
                shift
                ;;
            *)
                if [ -z "$topic" ]; then
                    topic="$1"
                else
                    log_error "未知参数: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # 检查选题
    if [ -z "$topic" ]; then
        log_error "请提供选题内容！"
        show_help
        exit 1
    fi
    
    # 设置日志级别
    if [ "$debug" = true ]; then
        export LOG_LEVEL="debug"
    fi
    
    # 显示开始信息
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║        素材搜集器 - WeChat Auto Publisher         ║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 检查依赖
    check_search_tools
    
    # 创建工作目录
    local work_dir
    work_dir=$(mktemp -d "/tmp/wechat-search-$(date +%Y%m%d-%H%M%S)-XXXXXX")
    log_info "📁 工作目录: $work_dir"
    
    # 生成输出文件名
    if [ -z "$output_file" ]; then
        local timestamp
        timestamp=$(date +%Y%m%d-%H%M%S)
        local safe_topic
        safe_topic=$(echo "$topic" | tr -cd '[:alnum:]' | cut -c1-20)
        output_file="/tmp/wechat-materials-${safe_topic}-${timestamp}.md"
    fi
    
    log_step "开始搜集素材..."
    log_info "选题: $topic"
    log_info "平台: $platforms"
    log_info "数量: $count"
    log_info "格式: $format"
    log_info "输出: $output_file"
    
    # 按平台搜索
    IFS=',' read -ra platform_array <<< "$platforms"
    
    for platform in "${platform_array[@]}"; do
        platform=$(echo "$platform" | xargs)  # 去除空格
        
        case "$platform" in
            web)
                search_web "$topic" "$count" "$work_dir/web.md"
                ;;
            wechat)
                search_wechat "$topic" "$count" "$work_dir/wechat.md"
                ;;
            zhihu)
                search_zhihu "$topic" "$count" "$work_dir/zhihu.md"
                ;;
            bilibili)
                search_bilibili "$topic" "$count" "$work_dir/bilibili.md"
                ;;
            douyin)
                # 抖音搜索（暂未实现）
                log_warn "抖音搜索功能暂未实现，跳过"
                ;;
            xiaohongshu)
                # 小红书搜索（暂未实现）
                log_warn "小红书搜索功能暂未实现，跳过"
                ;;
            weibo)
                # 微博搜索（暂未实现）
                log_warn "微博搜索功能暂未实现，跳过"
                ;;
            *)
                log_warn "未知平台: $platform，跳过"
                ;;
        esac
    done
    
    # 生成素材摘要
    generate_material_summary "$topic" "$work_dir" "$output_file" "$format"
    
    # 显示结果
    local line_count
    line_count=$(wc -l < "$output_file" 2>/dev/null || echo 0)
    local file_size
    file_size=$(du -h "$output_file" 2>/dev/null | cut -f1 || echo "未知")
    
    log_info "✅ 素材搜集完成"
    log_info "  文件: $output_file"
    log_info "  行数: $line_count"
    log_info "  大小: $file_size"
    log_info "  原始文件目录: $work_dir"
    
    # 显示前几行预览
    log_info "预览:"
    head -10 "$output_file" | while IFS= read -r line; do
        log_info "  $line"
    done
    
    echo ""
    log_info "📋 下一步:"
    log_info "  1. 查看完整结果: cat $output_file"
    log_info "  2. 查看原始文件: ls $work_dir"
    log_info "  3. 使用素材生成文章: ./generate-content.sh --material $output_file \"$topic\""
    
    # 返回结果文件路径
    echo "$output_file"
}

# 运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi