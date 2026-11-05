#!/usr/bin/env bash
# 文档爬取脚本 - 支持 URL 和 PDF

set -e

SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/common.sh"

PROJECT_ROOT=$(get_project_root)
KNOWLEDGE_DIR="$PROJECT_ROOT/_knowledge_base"

# 解析参数
NAME=""
URL=""
PDF=""
DYNAMIC=false
MAX_PAGES=200

function usage() {
    echo "用法: research-docs.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --name NAME       项目名称（必需）"
    echo "  --url URL         文档网站 URL"
    echo "  --pdf PATH        PDF 文件路径"
    echo "  --dynamic         使用动态爬虫（Puppeteer）"
    echo "  --max-pages NUM   最大爬取页数（默认: 200）"
    echo "  -h, --help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  research-docs.sh --name vue --url https://vuejs.org/guide/"
    echo "  research-docs.sh --name manual --pdf ~/Downloads/manual.pdf"
    exit 1
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            NAME="$2"
            shift 2
            ;;
        --url)
            URL="$2"
            shift 2
            ;;
        --pdf)
            PDF="$2"
            shift 2
            ;;
        --dynamic)
            DYNAMIC=true
            shift
            ;;
        --max-pages)
            MAX_PAGES="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "❌ 未知参数: $1"
            usage
            ;;
    esac
done

# 验证必需参数
if [ -z "$NAME" ]; then
    echo "❌ 错误: 必须提供项目名称 (--name)"
    usage
fi

if [ -z "$URL" ] && [ -z "$PDF" ]; then
    echo "❌ 错误: 必须提供 URL (--url) 或 PDF (--pdf)"
    usage
fi

if [ -n "$URL" ] && [ -n "$PDF" ]; then
    echo "❌ 错误: 不能同时提供 URL 和 PDF"
    usage
fi

# 检查 PDF 文件是否存在
if [ -n "$PDF" ] && [ ! -f "$PDF" ]; then
    echo "❌ 错误: PDF 文件不存在: $PDF"
    exit 1
fi

# 创建知识库目录
mkdir -p "$KNOWLEDGE_DIR"

# 检测是否为文档网站
if [ -n "$URL" ]; then
    if [[ "$URL" =~ (docs\.|/docs/|/guide/|/api/|/documentation/) ]]; then
        echo "✅ 检测到文档网站: $URL"
    else
        echo "⚠️  URL 可能不是文档网站，但仍会尝试爬取"
    fi
fi

# 输出信息
echo ""
echo "📋 爬取配置:"
echo "  - 项目名称: $NAME"
if [ -n "$URL" ]; then
    echo "  - URL: $URL"
    echo "  - 动态爬虫: $DYNAMIC"
    echo "  - 最大页数: $MAX_PAGES"
else
    echo "  - PDF: $PDF"
fi
echo "  - 输出目录: $KNOWLEDGE_DIR"
echo ""

# 构建命令
CMD="cd \"$PROJECT_ROOT\" && tsx src/commands/research-docs.ts"
CMD="$CMD --name \"$NAME\""

if [ -n "$URL" ]; then
    CMD="$CMD --url \"$URL\""
fi

if [ -n "$PDF" ]; then
    CMD="$CMD --pdf \"$PDF\""
fi

if [ "$DYNAMIC" = true ]; then
    CMD="$CMD --dynamic"
fi

CMD="$CMD --max-pages $MAX_PAGES"
CMD="$CMD --output \"$KNOWLEDGE_DIR\""

# 执行爬取
echo "🚀 开始爬取..."
echo ""

eval "$CMD"

# 输出结果路径
RAW_DIR="$KNOWLEDGE_DIR/raw/$NAME"
INDEXED_DIR="$KNOWLEDGE_DIR/indexed"

if [ -d "$RAW_DIR" ]; then
    echo ""
    echo "✅ 爬取完成!"
    echo ""
    echo "📁 文件位置:"
    echo "  - 原始数据: $RAW_DIR"
    echo "  - 知识库: $INDEXED_DIR"
    echo ""
    echo "💡 查看索引:"
    echo "  cat \"$INDEXED_DIR/${NAME}-index.md\""
    echo ""
    
    # 输出 JSON 供 AI 使用
    output_json "{\"raw_dir\": \"$RAW_DIR\", \"indexed_dir\": \"$INDEXED_DIR\", \"name\": \"$NAME\"}"
fi

