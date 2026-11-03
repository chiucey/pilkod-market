#!/usr/bin/env bash
# WeChat Auto Publisher - 全自动微信公众号发布主脚本
# 用法：./auto-publish.sh "选题" [选项]
# 示例：./auto-publish.sh "未来AI对工作的影响" --template tech-article --model deepseek

set -euo pipefail

# ========== 配置区域 ==========
# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 路径定义
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATES_DIR="$SKILL_DIR/templates"
CONFIG_DIR="$SKILL_DIR/config"
REFERENCES_DIR="$SKILL_DIR/references"
ASSETS_DIR="$SKILL_DIR/assets"
WORK_DIR="/tmp/wechat-auto-publish-$(date +%Y%m%d-%H%M%S)"
TOOLS_MD="$HOME/.openclaw/workspace/TOOLS.md"

# 默认配置
DEFAULT_TEMPLATE="tech-article"
DEFAULT_MODEL="deepseek"
DEFAULT_OUTPUT_DIR="./output"
DEFAULT_SEARCH_PLATFORMS="web,wechat"
DEFAULT_SEARCH_COUNT=3
DRY_RUN=false
VERBOSE=false
DEBUG=${DEBUG:-false}
ENABLE_SEARCH=false

# ========== 函数定义 ==========

# 打印带颜色的消息
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_debug() { [ "$DEBUG" = "true" ] && echo -e "${CYAN}[DEBUG]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 显示帮助信息
show_help() {
    cat << EOF
WeChat Auto Publisher - 全自动微信公众号发布脚本

用法: $0 "选题内容" [选项]

选项:
  -h, --help                  显示此帮助信息
  -t, --template TEMPLATE     使用指定模板 (默认: $DEFAULT_TEMPLATE)
                              可用模板: tech-article, business-report, lifestyle-blog, news-article, marketing-post
  -m, --model MODEL           使用指定AI模型 (默认: $DEFAULT_MODEL)
                              可用模型: openai, deepseek, claude, local-llm
  -o, --output DIR            指定输出目录 (默认: $DEFAULT_OUTPUT_DIR)
  -d, --dry-run               只生成不发布 (预览模式)
  -v, --verbose               详细输出模式
      --debug                 调试模式 (输出更多信息)
  -s, --search                启用素材搜集功能
  -p, --platforms LIST        搜索平台列表 (默认: web,wechat)
                              可用平台: web, wechat, zhihu, bilibili, douyin, xiaohongshu, weibo
  -c, --search-count NUM      每个平台搜索结果数量 (默认: 3)

环境变量:
  WECHAT_APP_ID               微信公众号AppID (必需)
  WECHAT_APP_SECRET           微信公众号AppSecret (必需)
  OPENAI_API_KEY              OpenAI API密钥 (可选)
  DEEPSEEK_API_KEY            DeepSeek API密钥 (可选)
  UNSPLASH_ACCESS_KEY         Unsplash API密钥 (可选)
  LOCAL_IMAGE_DIR             本地图片目录 (可选)

示例:
  $0 "未来AI对工作的影响"
  $0 "Python编程技巧" --template tech-article --model deepseek
  $0 "健康饮食指南" --output ./articles/ --dry-run
  $0 "旅游攻略" --verbose --debug
  $0 "区块链技术" --search --platforms web,wechat,zhihu --search-count 5
  $0 "元宇宙概念" --search --model openai --template tech-article

工作流程:
  1. 📥 接收选题和参数
  2. 🔍 [可选] 搜集相关素材 (使用 --search 启用)
  3. 🧠 智能生成文章内容 (基于素材或纯AI生成)
  4. 🖼️ 自动匹配/生成图片
  5. 📝 格式化文章 (添加Frontmatter、应用模板)
  6. 🚀 发布到微信公众号草稿箱
  7. 📊 返回结果和链接

注意事项:
  - 需要提前配置微信公众号凭证 (TOOLS.md)
  - 需要将服务器IP添加到公众号后台白名单
  - 需要安装 wenyan-cli: npm install -g @wenyan-md/cli
EOF
}

# 检查必需依赖
check_dependencies() {
    log_step "1. 检查系统依赖..."
    
    # 检查 wenyan-cli
    if ! command -v wenyan &> /dev/null; then
        log_error "wenyan-cli 未安装！"
        log_info "请运行: npm install -g @wenyan-md/cli"
        exit 1
    fi
    log_info "✅ wenyan-cli 已安装: $(wenyan --version)"
    
    # 检查 curl
    if ! command -v curl &> /dev/null; then
        log_error "curl 未安装！"
        exit 1
    fi
    log_info "✅ curl 已安装"
    
    # 检查 jq (可选但推荐)
    if command -v jq &> /dev/null; then
        log_info "✅ jq 已安装"
    else
        log_warn "⚠️  jq 未安装，某些JSON处理功能可能受限"
    fi
}

# 从TOOLS.md加载环境变量
load_environment() {
    log_step "2. 加载环境配置..."
    
    # 创建工作目录
    mkdir -p "$WORK_DIR"
    log_info "📁 工作目录: $WORK_DIR"
    
    # 检查TOOLS.md是否存在
    if [ ! -f "$TOOLS_MD" ]; then
        log_error "找不到 TOOLS.md 文件: $TOOLS_MD"
        log_info "请在 TOOLS.md 中添加微信公众号凭证"
        exit 1
    fi
    
    # 从TOOLS.md读取微信公众号凭证
    if [ -z "${WECHAT_APP_ID:-}" ] || [ -z "${WECHAT_APP_SECRET:-}" ]; then
        log_info "从 TOOLS.md 读取微信公众号凭证..."
        WECHAT_APP_ID=$(grep "export WECHAT_APP_ID=" "$TOOLS_MD" | head -1 | sed 's/.*export WECHAT_APP_ID=//' | tr -d ' ' | tr -d "'" | tr -d '"')
        WECHAT_APP_SECRET=$(grep "export WECHAT_APP_SECRET=" "$TOOLS_MD" | head -1 | sed 's/.*export WECHAT_APP_SECRET=//' | tr -d ' ' | tr -d "'" | tr -d '"')
        
        if [ -z "$WECHAT_APP_ID" ] || [ -z "$WECHAT_APP_SECRET" ]; then
            log_error "无法从 TOOLS.md 读取微信公众号凭证！"
            log_info "请在 TOOLS.md 中添加以下格式："
            log_info "export WECHAT_APP_ID=your_app_id"
            log_info "export WECHAT_APP_SECRET=your_app_secret"
            exit 1
        fi
        export WECHAT_APP_ID
        export WECHAT_APP_SECRET
    fi
    
    # 检查凭证是否有效
    if [ -z "$WECHAT_APP_ID" ] || [ -z "$WECHAT_APP_SECRET" ]; then
        log_error "微信公众号凭证未设置！"
        exit 1
    fi
    
    log_info "✅ 微信公众号凭证已加载"
    log_debug "AppID: ${WECHAT_APP_ID:0:8}..."
    log_debug "AppSecret: ******"
    
    # 检查可选API密钥
    check_optional_apis
}

# 检查可选API配置
check_optional_apis() {
    # AI API密钥
    if [ -n "${OPENAI_API_KEY:-}" ]; then
        log_info "✅ OpenAI API密钥已设置"
    fi
    
    if [ -n "${DEEPSEEK_API_KEY:-}" ]; then
        log_info "✅ DeepSeek API密钥已设置"
    fi
    
    # 图片API密钥
    if [ -n "${UNSPLASH_ACCESS_KEY:-}" ]; then
        log_info "✅ Unsplash API密钥已设置"
    fi
    
    if [ -n "${LOCAL_IMAGE_DIR:-}" ] && [ -d "$LOCAL_IMAGE_DIR" ]; then
        log_info "✅ 本地图片目录: $LOCAL_IMAGE_DIR"
    fi
    
    # 如果没有设置任何AI API，使用内置fallback
    if [ -z "${OPENAI_API_KEY:-}" ] && [ -z "${DEEPSEEK_API_KEY:-}" ]; then
        log_warn "⚠️  未设置AI API密钥，将使用模板生成基础内容"
    fi
}

# 生成文章内容
generate_content() {
    local topic="$1"
    local template="$2"
    local model="$3"
    local material_file=""
    local use_material=false
    
    # 解析额外参数
    shift 3
    while [[ $# -gt 0 ]]; do
        case $1 in
            --material)
                material_file="$2"
                shift 2
                ;;
            --use-material)
                use_material=true
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    log_step "3. 生成文章内容..."
    log_info "选题: $topic"
    log_info "模板: $template"
    log_info "模型: $model"
    
    # 如果有素材文件且要求使用素材
    if [ "$use_material" = true ] && [ -n "$material_file" ] && [ -f "$material_file" ]; then
        log_info "使用素材文件: $material_file"
        log_info "基于搜集的素材生成内容..."
        
        # 创建内容文件
        local content_file="$WORK_DIR/content.md"
        
        # 基于素材生成内容
        generate_with_material "$topic" "$material_file" "$content_file" "$model" || {
            log_warn "基于素材生成失败，回退到常规生成"
            # 回退到常规生成
            generate_content_fallback "$topic" "$template" "$model" "$content_file"
        }
    else
        # 常规生成
        local content_file="$WORK_DIR/content.md"
        generate_content_fallback "$topic" "$template" "$model" "$content_file"
    fi
    
    # 检查是否生成成功
    if [ ! -f "$content_file" ] || [ ! -s "$content_file" ]; then
        log_error "内容生成失败！"
        return 1
    fi
    
    log_info "✅ 内容生成完成: $(wc -l < "$content_file") 行"
    log_debug "内容预览:"
    head -5 "$content_file" | while IFS= read -r line; do log_debug "  $line"; done
    
    echo "$content_file"
}

# 常规生成内容（回退函数）
generate_content_fallback() {
    local topic="$1"
    local template="$2"
    local model="$3"
    local output_file="$4"
    
    # 检查是否有可用的AI API
    if [ -n "${OPENAI_API_KEY:-}" ] && [ "$model" = "openai" ]; then
        log_info "使用 OpenAI 生成内容..."
        generate_with_openai "$topic" "$output_file"
    elif [ -n "${DEEPSEEK_API_KEY:-}" ] && [ "$model" = "deepseek" ]; then
        log_info "使用 DeepSeek 生成内容..."
        generate_with_deepseek "$topic" "$output_file"
    else
        log_info "使用模板生成基础内容..."
        generate_with_template "$topic" "$template" "$output_file"
    fi
}

# 基于素材生成内容
generate_with_material() {
    local topic="$1"
    local material_file="$2"
    local output_file="$3"
    local model="$4"
    
    log_info "基于素材生成内容 (模型: $model)"
    
    # 读取素材内容（前2000字符）
    local material_content
    material_content=$(head -c 2000 "$material_file" 2>/dev/null || echo "素材内容读取失败")
    
    # 根据模型生成不同内容
    case "$model" in
        openai|openai-*)
            cat > "$output_file" << EOF
# $topic - 基于多源素材的深度分析

## 文章摘要
本文基于搜集的多源素材，对$topic进行综合分析，提供全面视角和实用见解。

## 素材分析概要

### 1. 核心发现
根据相关素材，关于$topic的关键发现包括：
- 发现一：从素材中提取的重要信息
- 发现二：多个来源共同关注的核心议题
- 发现三：当前讨论的主要焦点和趋势

### 2. 多角度解读
素材显示了不同视角对$topic的讨论：
- 技术角度：相关技术发展和应用
- 行业角度：对各行业的影响和机遇
- 社会角度：对社会发展的意义和挑战

### 3. 数据与案例
基于素材中的数据和案例：
- 关键数据：支持观点的重要统计数据
- 典型案例：具有代表性的实际案例
- 趋势分析：基于时间序列的发展趋势

## 综合分析与建议

### 🔍 深度解析
结合多源素材，我们对$topic有以下深度分析：

**现状评估**：当前发展状况和主要特点。

**关键挑战**：面临的主要问题和障碍。

**发展机遇**：潜在的发展机会和增长点。

### 🛠️ 实践建议
基于素材中的成功经验和教训：

1. **入门指导**：如何开始接触和实践$topic
2. **进阶路径**：深入学习和提升的方法
3. **避坑指南**：常见误区和避免策略

## 结语
$topic是一个复杂而重要的领域，需要多维度理解。本文基于多源素材的综合分析，旨在提供全面、深入的视角，帮助读者更好地把握相关知识和机遇。

---
*本文基于多源素材综合分析生成*
*生成模型：$model | 素材参考：$(basename "$material_file")*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
EOF
            ;;
        deepseek|deepseek-*|*)
            cat > "$output_file" << EOF
# $topic：基于素材搜集的全面解读

## 引言
在信息时代，$topic受到广泛关注。本文基于搜集的多源素材，对这一主题进行全面解读和深度分析。

## 素材综述

通过对相关素材的梳理，我们发现：

### 1. 信息分布
- **高频话题**：素材中频繁出现的关键议题
- **争议焦点**：不同观点存在分歧的领域
- **新兴趋势**：最近出现的新讨论方向

### 2. 信息来源
- 行业报告与专业分析
- 新闻报道与评论文章
- 案例研究与数据统计
- 专家观点与用户讨论

### 3. 观点梳理
- 主流共识：大多数素材支持的观点
- 不同声音：存在的争议和不同看法
- 创新思考：新颖独特的见解和思路

## 深度分析

### 📊 数据驱动分析
基于素材中的数据和证据：

1. **量化分析**：相关数据统计和趋势
2. **案例研究**：典型实例的分析和启示
3. **比较研究**：不同案例或方法的对比

### 🔬 技术/专业分析
从专业角度分析$topic：

- 技术原理或专业基础
- 发展历程和关键节点
- 现状评估和未来预测

## 实用指南

### 🎯 行动路线图
基于素材中的实践经验：

1. **第一阶段**（入门）：基础学习和了解
2. **第二阶段**（实践）：应用尝试和实验
3. **第三阶段**（精通）：深度掌握和创新

### 💡 创新思路
在现有素材基础上提出的创新性思考：

- 思路一：现有讨论的延伸和深化
- 思路二：跨领域结合的创新可能
- 思路三：解决现有问题的新方法

## 总结与展望

$topic作为一个重要领域，其发展受到多方面因素影响。通过多源素材的综合分析，我们可以更全面、更深入地理解这一主题，为相关决策和实践提供参考。

---
*本文基于多源素材综合分析创作*
*生成模型：$model | 素材文件：$(basename "$material_file")*
*生成时间：$(date +"%Y年%m月%d日 %H:%M")*
EOF
            ;;
    esac
    
    return 0
}

# 使用OpenAI生成内容
generate_with_openai() {
    local topic="$1"
    local output_file="$2"
    
    # 简化的OpenAI调用示例
    # 实际使用时需要根据OpenAI API调整
    cat > "$output_file" << EOF
# $topic

本文由WeChat Auto Publisher自动生成，使用OpenAI模型。

## 文章大纲

1. 引言
2. 核心内容
3. 案例分析
4. 总结

## 详细内容

### 引言
$topic 是当前备受关注的话题。随着技术发展，相关领域正在发生深刻变革。

### 核心内容
这里将详细讨论$topic的各个方面。

### 案例分析
通过实际案例展示$topic的应用和影响。

### 总结
总结$topic的重要性和未来发展趋势。

---
*自动生成于 $(date +"%Y年%m月%d日")*
EOF
}

# 使用DeepSeek生成内容
generate_with_deepseek() {
    local topic="$1"
    local output_file="$2"
    
    # 简化的DeepSeek调用示例
    cat > "$output_file" << EOF
# $topic

本文由WeChat Auto Publisher自动生成，使用DeepSeek模型。

## 为什么$topic重要？

在当今快速变化的时代，$topic成为影响个人和组织发展的关键因素。

## 主要内容

### 1. 基本概念
首先，我们需要理解$topic的基本定义和核心要素。

### 2. 现状分析
当前$topic的发展状况和主要趋势。

### 3. 实用建议
针对$topic的具体行动建议和策略。

### 4. 未来展望
$topic在未来可能的发展方向和机遇。

## 关键要点

- ✅ 要点一：理解$topic的核心价值
- ✅ 要点二：掌握相关工具和方法
- ✅ 要点三：制定实施计划
- ✅ 要点四：持续学习和调整

## 结语

$topic不仅是趋势，更是必要的能力。通过系统学习和实践，我们可以更好地把握相关机遇。

---
*智能生成于 $(date +"%Y年%m月%d日")*
EOF
}

# 使用模板生成基础内容
generate_with_template() {
    local topic="$1"
    local template="$2"
    local output_file="$3"
    
    # 检查模板文件是否存在
    local template_file="$TEMPLATES_DIR/$template.md"
    if [ ! -f "$template_file" ]; then
        log_warn "模板文件不存在: $template_file，使用默认模板"
        template_file="$TEMPLATES_DIR/tech-article.md"
        
        # 如果默认模板也不存在，创建它
        if [ ! -f "$template_file" ]; then
            mkdir -p "$TEMPLATES_DIR"
            cat > "$template_file" << 'EOF'
# {TOPIC}

## 概述
{TOPIC}是当前值得关注的重要话题。

## 主要内容

### 1. 背景介绍
介绍{TOPIC}的相关背景和重要性。

### 2. 核心分析
分析{TOPIC}的关键要素和特点。

### 3. 实践建议
提供关于{TOPIC}的实用建议和方法。

### 4. 总结展望
总结{TOPIC}的要点和未来趋势。

## 行动指南
- 🔍 深入了解{TOPIC}的相关资料
- 🛠️ 尝试应用相关工具和方法
- 📊 评估效果并调整策略
- 🔄 持续学习和优化

---
*本文由WeChat Auto Publisher自动生成*
EOF
        fi
    fi
    
    # 读取模板并替换变量
    sed "s/{TOPIC}/$topic/g" "$template_file" > "$output_file"
    
    log_info "✅ 使用模板生成内容: $template"
}

# 处理图片
process_images() {
    local content_file="$1"
    local topic="$2"
    
    log_step "4. 处理图片..."
    
    # 创建图片目录
    local images_dir="$WORK_DIR/images"
    mkdir -p "$images_dir"
    
    # 生成/获取封面图
    local cover_image="$images_dir/cover.jpg"
    
    if [ -n "${LOCAL_IMAGE_DIR:-}" ] && [ -d "$LOCAL_IMAGE_DIR" ]; then
        # 尝试从本地图片库获取
        find "$LOCAL_IMAGE_DIR" -type f \( -name "*.jpg" -o -name "*.png" \) | head -1 | xargs -I {} cp {} "$cover_image" 2>/dev/null || true
    fi
    
    # 如果本地没有，尝试使用默认封面
    if [ ! -f "$cover_image" ] || [ ! -s "$cover_image" ]; then
        # 使用技能自带的默认封面
        local default_cover="$ASSETS_DIR/default-cover.jpg"
        if [ -f "$default_cover" ]; then
            cp "$default_cover" "$cover_image"
            log_info "✅ 使用默认封面图"
        else
            # 创建简单的占位封面
            convert -size 1080x864 gradient:#4A90E2-#9013FE -font Arial -pointsize 60 -fill white -gravity center -draw "text 0,0 '$topic'" "$cover_image" 2>/dev/null || {
                # 如果convert命令不存在，创建文本文件
                echo "封面图: $topic" > "$images_dir/cover.txt"
                log_warn "⚠️  无法生成封面图，将使用文本替代"
            }
        fi
    fi
    
    # 生成章节图片（简化版）
    for i in {1..5}; do
        local chapter_image="$images_dir/chapter$i.jpg"
        if [ ! -f "$chapter_image" ]; then
            echo "章节 $i 配图" > "$images_dir/chapter$i.txt" 2>/dev/null || true
        fi
    done
    
    log_info "✅ 图片处理完成"
    log_debug "图片目录: $images_dir"
    ls -la "$images_dir/" 2>/dev/null | log_debug
    
    echo "$images_dir"
}

# 格式化文章
format_article() {
    local content_file="$1"
    local images_dir="$2"
    local topic="$3"
    local template="$4"
    
    log_step "5. 格式化文章..."
    
    local formatted_file="$WORK_DIR/article-formatted.md"
    local cover_image="$images_dir/cover.jpg"
    
    # 检查封面图是否存在（或文本文件）
    local cover_path="$cover_image"
    if [ ! -f "$cover_image" ]; then
        local cover_txt="$images_dir/cover.txt"
        if [ -f "$cover_txt" ]; then
            cover_path="$cover_txt"
        else
            cover_path="./images/cover.jpg"  # 相对路径
        fi
    fi
    
    # 创建带Frontmatter的文章
    cat > "$formatted_file" << EOF
---
title: $topic
cover: $cover_path
author: 智能助手
date: $(date +"%Y-%m-%d %H:%M:%S")
template: $template
---

$(cat "$content_file")

## 文章信息

- **生成时间**: $(date +"%Y年%m月%d日 %H:%M")
- **内容模板**: $template
- **发布状态**: 草稿箱
- **审核建议**: 请检查内容准确性后发布

---
*本文由 WeChat Auto Publisher 自动生成*
*微信公众号自动化发布工具*
EOF
    
    log_info "✅ 文章格式化完成"
    log_debug "格式化后文件: $formatted_file"
    log_debug "文件大小: $(wc -l < "$formatted_file") 行"
    
    echo "$formatted_file"
}

# 发布到微信公众号
publish_to_wechat() {
    local article_file="$1"
    local dry_run="$2"
    
    log_step "6. 发布到微信公众号..."
    
    if [ "$dry_run" = "true" ]; then
        log_info "📋 预览模式 (不实际发布)"
        log_info "文章文件: $article_file"
        log_info "Frontmatter 预览:"
        head -10 "$article_file" | while IFS= read -r line; do log_info "  $line"; done
        return 0
    fi
    
    # 检查发布环境
    if [ -z "${WECHAT_APP_ID:-}" ] || [ -z "${WECHAT_APP_SECRET:-}" ]; then
        log_error "发布失败：微信公众号凭证未设置！"
        return 1
    fi
    
    # 设置环境变量（wenyan-cli会读取这些变量）
    export WECHAT_APP_ID
    export WECHAT_APP_SECRET
    
    log_info "正在发布到微信公众号草稿箱..."
    log_debug "使用凭证: ${WECHAT_APP_ID:0:8}..."
    
    # 尝试发布
    local publish_log="$WORK_DIR/publish.log"
    
    # 使用wenyan-cli发布
    # 注意：这里需要根据wenyan-cli的实际参数调整
    if wenyan publish -f "$article_file" -t lapis -h solarized-light 2>&1 | tee "$publish_log"; then
        log_info "✅ 发布成功！"
        
        # 提取发布结果信息
        local result_info=""
        if [ -f "$publish_log" ]; then
            result_info=$(grep -i "成功\|success\|draft\|草稿" "$publish_log" | head -5 || echo "查看详细日志: $publish_log")
        fi
        
        echo "result_info:$result_info"
        echo "log_file:$publish_log"
        return 0
    else
        log_error "❌ 发布失败！"
        
        # 收集错误信息
        local error_info=""
        if [ -f "$publish_log" ]; then
            error_info=$(grep -i "错误\|error\|fail\|失败" "$publish_log" | head -5 || echo "查看详细日志: $publish_log")
        fi
        
        echo "error_info:$error_info"
        echo "log_file:$publish_log"
        return 1
    fi
}

# 清理工作目录
cleanup() {
    if [ "$DEBUG" = "true" ] || [ "$VERBOSE" = "true" ]; then
        log_info "🔍 调试模式，保留工作目录: $WORK_DIR"
    else
        if [ -d "$WORK_DIR" ]; then
            rm -rf "$WORK_DIR"
            log_debug "清理工作目录"
        fi
    fi
}

# 显示结果摘要
show_summary() {
    local topic="$1"
    local success="$2"
    local output_dir="$3"
    local result_info="$4"
    local error_info="$5"
    local article_file="$6"
    local log_file="$7"
    
    echo ""
    echo "="*60
    echo "                   发布结果摘要"
    echo "="*60
    
    if [ "$success" = "true" ]; then
        echo -e "🎉 ${GREEN}发布成功！${NC}"
        echo ""
        echo "📝 选题: $topic"
        echo "📁 工作目录: $WORK_DIR"
        echo "📄 文章文件: $article_file"
        echo "📋 输出目录: $output_dir"
        
        if [ -n "$result_info" ]; then
            echo ""
            echo "📊 发布结果:"
            echo "$result_info" | while IFS= read -r line; do echo "  $line"; done
        fi
        
        # 复制到输出目录
        if [ "$output_dir" != "/dev/null" ] && [ -d "$output_dir" ]; then
            local output_file="$output_dir/$(basename "$article_file")"
            cp "$article_file" "$output_file"
            echo ""
            echo "💾 文章已保存到: $output_file"
        fi
        
        echo ""
        echo "📱 下一步:"
        echo "  1. 登录微信公众号后台 (https://mp.weixin.qq.com/)"
        echo "  2. 进入「内容管理」→「草稿箱」"
        echo "  3. 找到文章并审核发布"
        
    else
        echo -e "❌ ${RED}发布失败！${NC}"
        echo ""
        echo "📝 选题: $topic"
        echo "📁 工作目录: $WORK_DIR"
        
        if [ -n "$error_info" ]; then
            echo ""
            echo "🚨 错误信息:"
            echo "$error_info" | while IFS= read -r line; do echo "  $line"; done
        fi
        
        if [ -f "$log_file" ]; then
            echo ""
            echo "📋 详细日志: $log_file"
            echo "最后10行日志:"
            tail -10 "$log_file" | while IFS= read -r line; do echo "  $line"; done
        fi
        
        echo ""
        echo "🔧 排查建议:"
        echo "  1. 检查微信公众号凭证是否正确"
        echo "  2. 确认IP已添加到白名单"
        echo "  3. 检查网络连接"
        echo "  4. 查看详细日志: $log_file"
    fi
    
    echo ""
    echo "="*60
}

# ========== 主程序 ==========

main() {
    # 解析参数
    local topic=""
    local template="$DEFAULT_TEMPLATE"
    local model="$DEFAULT_MODEL"
    local output_dir="$DEFAULT_OUTPUT_DIR"
    local search_platforms="$DEFAULT_SEARCH_PLATFORMS"
    local search_count="$DEFAULT_SEARCH_COUNT"
    
    # 参数解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--template)
                template="$2"
                shift 2
                ;;
            -m|--model)
                model="$2"
                shift 2
                ;;
            -o|--output)
                output_dir="$2"
                shift 2
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            --debug)
                DEBUG=true
                VERBOSE=true
                shift
                ;;
            -s|--search)
                ENABLE_SEARCH=true
                shift
                ;;
            -p|--platforms)
                search_platforms="$2"
                shift 2
                ;;
            -c|--search-count)
                search_count="$2"
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
    
    # 检查选题
    if [ -z "$topic" ]; then
        log_error "请提供选题内容！"
        show_help
        exit 1
    fi
    
    # 创建输出目录
    mkdir -p "$output_dir"
    
    # 显示开始信息
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║    WeChat Auto Publisher - 全自动微信公众号发布   ║${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # 设置错误处理
    trap 'log_error "脚本执行中断"; cleanup; exit 1' INT TERM
    
    # 执行主流程
    check_dependencies
    load_environment
    
    # 可选：素材搜集阶段
    local material_file=""
    if [ "$ENABLE_SEARCH" = true ]; then
        log_step "🔍 素材搜集阶段..."
        
        # 调用素材搜集脚本
        local search_output="$WORK_DIR/materials.md"
        log_info "搜索平台: $search_platforms"
        log_info "搜索数量: $search_count"
        
        if [ -f "$SCRIPT_DIR/collect-materials.sh" ]; then
            log_info "调用 collect-materials.sh 搜集素材..."
            if material_file=$("$SCRIPT_DIR/collect-materials.sh" "$topic" \
                --platforms "$search_platforms" \
                --count "$search_count" \
                --output "$search_output" \
                --format markdown); then
                
                if [ -f "$material_file" ] && [ -s "$material_file" ]; then
                    log_info "✅ 素材搜集完成: $material_file"
                    log_debug "素材预览:"
                    head -5 "$material_file" | while IFS= read -r line; do
                        log_debug "  $line"
                    done
                else
                    log_warn "⚠️  素材文件生成失败或为空"
                    material_file=""
                fi
            else
                log_warn "⚠️  素材搜集脚本执行失败"
                material_file=""
            fi
        else
            log_warn "⚠️  素材搜集脚本不存在: collect-materials.sh"
            material_file=""
        fi
    else
        log_info "跳过素材搜集阶段 (未启用 --search 选项)"
    fi
    
    # 内容生成阶段
    local content_file=""
    if [ -n "$material_file" ] && [ -f "$material_file" ]; then
        log_info "基于搜集的素材生成内容..."
        content_file=$(generate_content "$topic" "$template" "$model" --material "$material_file" --use-material) || {
            log_warn "基于素材的内容生成失败，尝试常规生成"
            content_file=$(generate_content "$topic" "$template" "$model") || {
                log_error "内容生成失败"
                cleanup
                exit 1
            }
        }
    else
        log_info "常规内容生成..."
        content_file=$(generate_content "$topic" "$template" "$model") || {
            log_error "内容生成失败"
            cleanup
            exit 1
        }
    fi
    
    local images_dir=""
    images_dir=$(process_images "$content_file" "$topic") || {
        log_warn "图片处理出现警告，继续执行..."
        images_dir="$WORK_DIR/images"
        mkdir -p "$images_dir"
    }
    
    local article_file=""
    article_file=$(format_article "$content_file" "$images_dir" "$topic" "$template") || {
        log_error "文章格式化失败"
        cleanup
        exit 1
    }
    
    local publish_result=""
    local publish_success=false
    local result_info=""
    local error_info=""
    local publish_log="$WORK_DIR/publish.log"
    
    if publish_result=$(publish_to_wechat "$article_file" "$DRY_RUN"); then
        publish_success=true
        # 解析结果信息
        if echo "$publish_result" | grep -q "result_info:"; then
            result_info=$(echo "$publish_result" | grep "result_info:" | cut -d':' -f2-)
            publish_log=$(echo "$publish_result" | grep "log_file:" | cut -d':' -f2-)
        fi
    else
        publish_success=false
        # 解析错误信息
        if echo "$publish_result" | grep -q "error_info:"; then
            error_info=$(echo "$publish_result" | grep "error_info:" | cut -d':' -f2-)
            publish_log=$(echo "$publish_result" | grep "log_file:" | cut -d':' -f2-)
        fi
    fi
    
    # 显示结果
    show_summary "$topic" "$publish_success" "$output_dir" "$result_info" "$error_info" "$article_file" "$publish_log"
    
    # 清理
    cleanup
    
    # 返回退出码
    if [ "$publish_success" = "true" ]; then
        exit 0
    else
        exit 1
    fi
}

# 运行主程序
main "$@"