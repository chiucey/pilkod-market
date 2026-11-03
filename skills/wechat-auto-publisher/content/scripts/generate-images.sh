#!/usr/bin/env bash
# 图片生成器脚本
# 为文章生成/匹配封面图和章节配图

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
图片生成器 - WeChat Auto Publisher

用法: $0 [选项] "文章主题"

选项:
  -h, --help          显示此帮助信息
  -i, --input FILE    输入文章文件（用于分析内容）
  -o, --output DIR    输出目录 (默认: 自动创建)
  -s, --style STYLE   图片风格 (tech/business/lifestyle)
  -c, --count NUM     生成图片数量 (默认: 5)

示例:
  $0 "未来AI对工作的影响"
  $0 --input article.md --output ./images
  $0 "Python编程" --style tech --count 3
EOF
}

# 从本地图片库获取图片
get_image_from_local() {
    local topic="$1"
    local style="$2"
    local output_file="$3"
    
    if [ -z "${LOCAL_IMAGE_DIR:-}" ] || [ ! -d "$LOCAL_IMAGE_DIR" ]; then
        return 1
    fi
    
    # 根据主题和风格查找图片
    local search_dirs=()
    
    # 按风格搜索子目录
    if [ -d "$LOCAL_IMAGE_DIR/$style" ]; then
        search_dirs+=("$LOCAL_IMAGE_DIR/$style")
    fi
    
    # 搜索主目录
    search_dirs+=("$LOCAL_IMAGE_DIR")
    
    for dir in "${search_dirs[@]}"; do
        # 尝试查找相关图片
        local image_files=()
        
        # 根据关键词查找
        local keywords=$(echo "$topic" | tr ' ' '\n' | head -3)
        for keyword in $keywords; do
            find "$dir" -type f \( -name "*.jpg" -o -name "*.png" \) \
                -iname "*${keyword}*" 2>/dev/null | head -5 | while read -r img; do
                image_files+=("$img")
            done
        done
        
        # 如果没有找到关键词匹配，随机选择一张
        if [ ${#image_files[@]} -eq 0 ]; then
            find "$dir" -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | \
                shuf -n 1 | while read -r img; do
                image_files+=("$img")
            done
        fi
        
        # 如果找到图片，复制到输出文件
        if [ ${#image_files[@]} -gt 0 ]; then
            local selected_image="${image_files[0]}"
            cp "$selected_image" "$output_file" 2>/dev/null && return 0
        fi
    done
    
    return 1
}

# 从Unsplash获取图片
get_image_from_unsplash() {
    local topic="$1"
    local style="$2"
    local output_file="$3"
    
    if [ -z "${UNSPLASH_ACCESS_KEY:-}" ]; then
        return 1
    fi
    
    # Unsplash API调用（简化版）
    # 实际使用时需要根据Unsplash API调整
    
    log_debug "尝试从Unsplash获取图片: $topic"
    
    # 这里应该是实际的API调用，现在使用模拟
    return 1
}

# 生成占位图片
generate_placeholder_image() {
    local output_file="$1"
    local text="$2"
    local style="$3"
    
    log_info "生成占位图片: $text"
    
    # 尝试使用ImageMagick
    if command -v convert &> /dev/null; then
        # 根据风格选择颜色
        local gradient=""
        case "$style" in
            tech)
                gradient="gradient:#4A90E2-#9013FE"  # 蓝色到紫色
                ;;
            business)
                gradient="gradient:#2ECC71-#3498DB"  # 绿色到蓝色
                ;;
            lifestyle)
                gradient="gradient:#E74C3C-#F39C12"  # 红色到橙色
                ;;
            *)
                gradient="gradient:#4A90E2-#9013FE"
                ;;
        esac
        
        # 生成图片
        convert -size 1080x864 "$gradient" \
                -font Arial -pointsize 48 -fill white \
                -gravity center -draw "text 0,0 '$text'" \
                "$output_file" 2>/dev/null && return 0
    fi
    
    # 如果ImageMagick不可用，创建文本文件
    local txt_file="${output_file%.*}.txt"
    echo "图片占位符: $text" > "$txt_file"
    echo "风格: $style" >> "$txt_file"
    echo "尺寸: 1080x864 (微信推荐封面比例)" >> "$txt_file"
    echo "生成时间: $(date)" >> "$txt_file"
    echo "说明: 这是一个图片占位符，实际使用时请替换为真实图片" >> "$txt_file"
    
    # 将txt文件重命名为jpg以便后续处理
    mv "$txt_file" "$output_file"
    
    return 0
}

# 生成封面图
generate_cover_image() {
    local topic="$1"
    local style="$2"
    local output_dir="$3"
    
    local cover_file="$output_dir/cover.jpg"
    
    log_step "生成封面图..."
    
    # 尝试多个图片来源
    local sources=("local" "unsplash" "placeholder")
    
    for source in "${sources[@]}"; do
        case "$source" in
            local)
                if get_image_from_local "$topic" "$style" "$cover_file"; then
                    log_info "✅ 从本地图库获取封面图"
                    return 0
                fi
                ;;
            unsplash)
                if get_image_from_unsplash "$topic" "$style" "$cover_file"; then
                    log_info "✅ 从Unsplash获取封面图"
                    return 0
                fi
                ;;
            placeholder)
                if generate_placeholder_image "$cover_file" "$topic" "$style"; then
                    log_info "✅ 生成占位封面图"
                    return 0
                fi
                ;;
        esac
    done
    
    log_error "封面图生成失败"
    return 1
}

# 生成章节配图
generate_chapter_images() {
    local topic="$1"
    local style="$2"
    local output_dir="$3"
    local count="$4"
    
    log_step "生成章节配图 ($count 张)..."
    
    # 章节标题示例（实际应该从文章内容提取）
    local chapter_titles=(
        "引言"
        "核心内容"
        "案例分析"
        "实践建议"
        "总结展望"
        "技术原理"
        "应用场景"
        "学习路径"
        "最佳实践"
        "资源推荐"
    )
    
    local generated=0
    for ((i=1; i<=count && i<=${#chapter_titles[@]}; i++)); do
        local chapter_file="$output_dir/chapter$i.jpg"
        local title="${chapter_titles[$((i-1))]}"
        
        # 生成章节配图
        if generate_placeholder_image "$chapter_file" "$title - $topic" "$style"; then
            generated=$((generated + 1))
            log_debug "生成配图: chapter$i.jpg ($title)"
        fi
    done
    
    log_info "✅ 生成 $generated 张章节配图"
    return 0
}

# 分析文章内容提取关键词
extract_keywords() {
    local article_file="$1"
    local max_keywords="${2:-5}"
    
    if [ ! -f "$article_file" ]; then
        echo ""
        return 0
    fi
    
    # 简单关键词提取（从标题和副标题）
    local keywords=$(grep -E "^#+ " "$article_file" | head -5 | \
                    sed 's/^#\+ //' | tr ' ' '\n' | \
                    grep -v "^$" | head -"$max_keywords")
    
    echo "$keywords"
}

# 主函数
main() {
    # 默认参数
    local topic=""
    local input_file=""
    local output_dir=""
    local style="tech"
    local count=5
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -i|--input)
                input_file="$2"
                shift 2
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -s|--style)
                style="$2"
                shift 2
                ;;
            -c|--count)
                count="$2"
                shift 2
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
    
    # 如果没有提供主题，尝试从输入文件提取
    if [ -z "$topic" ] && [ -n "$input_file" ]; then
        if [ -f "$input_file" ]; then
            topic=$(extract_markdown_title "$input_file")
            log_info "从文件提取主题: $topic"
        fi
    fi
    
    if [ -z "$topic" ]; then
        log_error "请提供文章主题！"
        show_help
        exit 1
    fi
    
    # 创建输出目录
    if [ -z "$output_dir" ]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local safe_topic=$(echo "$topic" | tr -cd '[:alnum:]' | cut -c1-20)
        output_dir="/tmp/wechat-images-${safe_topic}-${timestamp}"
    fi
    
    ensure_dir "$output_dir"
    
    # 开始处理
    show_title "图片生成器"
    log_info "主题: $topic"
    log_info "风格: $style"
    log_info "输出目录: $output_dir"
    log_info "图片数量: $count"
    
    # 生成封面图
    if generate_cover_image "$topic" "$style" "$output_dir"; then
        log_info "✅ 封面图生成成功"
    else
        log_warn "⚠️  封面图生成失败，将继续生成章节配图"
    fi
    
    # 生成章节配图
    if generate_chapter_images "$topic" "$style" "$output_dir" "$count"; then
        log_info "✅ 章节配图生成成功"
    else
        log_warn "⚠️  部分章节配图生成失败"
    fi
    
    # 统计生成结果
    local total_images=$(find "$output_dir" -type f \( -name "*.jpg" -o -name "*.png" -o -name "*.txt" \) 2>/dev/null | wc -l)
    
    log_step "图片生成完成"
    log_info "总生成文件数: $total_images"
    log_info "输出目录内容:"
    ls -la "$output_dir/" 2>/dev/null | while IFS= read -r line; do
        log_info "  $line"
    done || true
    
    echo "$output_dir"
}

# 运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi