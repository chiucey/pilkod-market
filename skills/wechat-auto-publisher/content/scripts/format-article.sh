#!/usr/bin/env bash
# 文章格式化脚本
# 将原始内容格式化为微信公众号标准格式

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
文章格式化器 - WeChat Auto Publisher

用法: $0 [选项]

选项:
  -h, --help          显示此帮助信息
  -i, --input FILE    输入文章文件 (必需)
  -c, --cover FILE    封面图片文件 (必需)
  -o, --output FILE   输出文件 (默认: 自动生成)
  -t, --template NAME 模板名称 (默认: tech-article)
  -a, --author NAME   作者名称 (默认: 智能助手)
  --title TITLE       文章标题 (默认: 从内容提取)

示例:
  $0 --input content.md --cover cover.jpg
  $0 -i content.md -c cover.jpg -t business-report
  $0 -i content.md -c cover.jpg --title "自定义标题"
EOF
}

# 从内容提取标题
extract_title_from_content() {
    local content_file="$1"
    
    # 尝试从第一行标题提取
    local title=$(grep -m 1 "^# " "$content_file" 2>/dev/null | sed 's/^# //' || true)
    
    if [ -n "$title" ]; then
        echo "$title"
        return 0
    fi
    
    # 尝试从文件名提取
    local filename=$(basename "$content_file" .md)
    filename=$(basename "$filename" .txt)
    
    # 清理文件名
    echo "$filename" | sed 's/_/ /g' | sed 's/-/ /g'
}

# 检查封面图
validate_cover_image() {
    local cover_file="$1"
    
    if [ ! -f "$cover_file" ]; then
        log_error "封面图文件不存在: $cover_file"
        return 1
    fi
    
    # 检查文件类型
    local extension="${cover_file##*.}"
    extension=$(echo "$extension" | tr '[:upper:]' '[:lower:]')
    
    case "$extension" in
        jpg|jpeg|png|gif|bmp|webp)
            # 有效的图片格式
            ;;
        txt)
            log_warn "封面图是文本文件，将作为占位符使用"
            return 0
            ;;
        *)
            log_error "不支持的封面图格式: .$extension"
            log_info "支持的格式: jpg, jpeg, png, gif, bmp, webp"
            return 1
            ;;
    esac
    
    return 0
}

# 应用模板样式
apply_template_styles() {
    local content="$1"
    local template="$2"
    
    # 根据模板添加特定样式提示
    case "$template" in
        tech-article)
            # 技术文章样式
            content=$(echo "$content" | sed '/^## 实用工具推荐$/i\
\
## 技术要点\
以下是对本文技术要点的总结：')
            ;;
        business-report)
            # 商业报告样式
            content=$(echo "$content" | sed '/^## 投资建议$/i\
\
## 执行摘要回顾\
本文分析了相关市场现状并提出了战略建议。')
            ;;
        lifestyle-blog)
            # 生活博客样式
            content=$(echo "$content" | sed '1i\
> 生活感悟，与你分享 🌟\
')
            ;;
    esac
    
    echo "$content"
}

# 添加微信公众号优化
add_wechat_optimizations() {
    local content="$1"
    
    # 确保段落之间有适当间距
    content=$(echo "$content" | sed 's/^$/\\\
/g')
    
    # 为长段落添加分割线
    content=$(echo "$content" | awk '
        BEGIN { para_length = 0; para_lines = 0 }
        /^$/ { 
            if (para_lines > 5 && para_length > 500) {
                print "---"
            }
            para_length = 0
            para_lines = 0
            print
            next
        }
        {
            para_length += length($0)
            para_lines++
            print
        }
    ')
    
    echo "$content"
}

# 格式化文章内容
format_article_content() {
    local input_file="$1"
    local title="$2"
    local cover_file="$3"
    local author="$4"
    local template="$5"
    
    log_step "格式化文章内容..."
    
    # 读取原始内容
    if [ ! -f "$input_file" ]; then
        log_error "输入文件不存在: $input_file"
        return 1
    fi
    
    local content=$(cat "$input_file")
    
    # 移除可能的现有frontmatter
    content=$(echo "$content" | sed '/^---$/,/^---$/d')
    
    # 应用模板样式
    content=$(apply_template_styles "$content" "$template")
    
    # 添加微信公众号优化
    content=$(add_wechat_optimizations "$content")
    
    # 构建frontmatter
    local frontmatter="---
title: $title
cover: $cover_file
author: $author
date: $(date +"%Y-%m-%d %H:%M:%S")
template: $template
wechat_optimized: true
generator: WeChat Auto Publisher
version: 1.0
---"
    
    # 合并frontmatter和内容
    echo "$frontmatter"
    echo ""
    echo "$content"
    echo ""
    echo "---"
    echo "*本文由 WeChat Auto Publisher 自动生成*"
    echo "*生成时间: $(date +"%Y年%m月%d日 %H:%M")*"
    echo "*微信公众号: 自动化发布工具*"
}

# 主函数
main() {
    # 默认参数
    local input_file=""
    local cover_file=""
    local output_file=""
    local template="tech-article"
    local author="智能助手"
    local custom_title=""
    
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
            -c|--cover)
                cover_file="$2"
                shift 2
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -t|--template)
                template="$2"
                shift 2
                ;;
            -a|--author)
                author="$2"
                shift 2
                ;;
            --title)
                custom_title="$2"
                shift 2
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查必需参数
    if [ -z "$input_file" ]; then
        log_error "请指定输入文件！"
        show_help
        exit 1
    fi
    
    if [ -z "$cover_file" ]; then
        log_error "请指定封面图文件！"
        show_help
        exit 1
    fi
    
    # 验证封面图
    validate_cover_image "$cover_file" || exit 1
    
    # 确定标题
    local title=""
    if [ -n "$custom_title" ]; then
        title="$custom_title"
    else
        title=$(extract_title_from_content "$input_file")
    fi
    
    if [ -z "$title" ]; then
        title="未命名文章"
        log_warn "无法提取文章标题，使用默认标题"
    fi
    
    # 确定输出文件
    if [ -z "$output_file" ]; then
        local timestamp=$(date +%Y%m%d-%H%M%S)
        local safe_title=$(echo "$title" | tr -cd '[:alnum:]' | cut -c1-20)
        output_file="/tmp/wechat-formatted-${safe_title}-${timestamp}.md"
    fi
    
    # 显示处理信息
    show_title "文章格式化器"
    log_info "输入文件: $input_file"
    log_info "封面图: $cover_file"
    log_info "文章标题: $title"
    log_info "作者: $author"
    log_info "模板: $template"
    log_info "输出文件: $output_file"
    
    # 格式化文章
    log_step "开始格式化..."
    
    if format_article_content "$input_file" "$title" "$cover_file" "$author" "$template" > "$output_file"; then
        log_info "✅ 文章格式化成功"
    else
        log_error "❌ 文章格式化失败"
        exit 1
    fi
    
    # 验证输出文件
    if [ ! -f "$output_file" ] || [ ! -s "$output_file" ]; then
        log_error "输出文件创建失败"
        exit 1
    fi
    
    # 检查frontmatter
    if ! check_frontmatter "$output_file"; then
        log_warn "⚠️  输出文件的frontmatter可能不完整"
    fi
    
    # 显示结果统计
    local line_count=$(count_lines "$output_file")
    local file_size=$(du -h "$output_file" | cut -f1)
    
    log_step "格式化完成"
    log_info "输出文件: $output_file"
    log_info "文件大小: $file_size"
    log_info "总行数: $line_count"
    
    # 显示frontmatter预览
    log_info "Frontmatter预览:"
    head -10 "$output_file" | while IFS= read -r line; do
        log_info "  $line"
    done
    
    echo "$output_file"
}

# 运行主函数
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi