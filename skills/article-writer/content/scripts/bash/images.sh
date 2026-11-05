#!/usr/bin/env bash
# 配图建议 - 基于文章内容提供配图方案

set -e

SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/common.sh"

PROJECT_ROOT=$(get_project_root)
WORKSPACE_TYPE=$(get_active_workspace)
DRAFT_FILE="$1"

# 如果没有指定草稿，使用最新的
if [ -z "$DRAFT_FILE" ]; then
    DRAFT_FILE=$(get_latest_draft)
fi

if [ -z "$DRAFT_FILE" ] || [ ! -f "$DRAFT_FILE" ]; then
    echo "❌ 错误: 未找到草稿文件"
    echo "用法: images.sh [draft文件路径]"
    exit 1
fi

echo "✅ 草稿文件: $DRAFT_FILE"
echo "📝 工作区: $WORKSPACE_TYPE"
echo ""

# 统计文章信息
WORD_COUNT=$(count_chinese_words "$DRAFT_FILE")
PARAGRAPH_COUNT=$(grep -c '^[^#].*[。！？]$' "$DRAFT_FILE" 2>/dev/null || echo "0")

echo "📊 文章统计:"
echo "   字数: $WORD_COUNT"
echo "   段落数: $PARAGRAPH_COUNT"
echo ""

# 根据工作区类型给出配图建议
case "$WORKSPACE_TYPE" in
    wechat)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📱 公众号配图建议"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "配图规范:"
        echo "  • 封面图: 900×500px (16:9 比例)"
        echo "  • 内文图: 宽度 900px，高度自适应"
        echo "  • 建议数量: 每 500-800 字配 1 张图"
        echo ""
        RECOMMENDED_IMAGES=$((WORD_COUNT / 600))
        if [ $RECOMMENDED_IMAGES -lt 1 ]; then
            RECOMMENDED_IMAGES=1
        fi
        echo "推荐配图数量: $RECOMMENDED_IMAGES 张 (含封面)"
        ;;
    video)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎥 视频配图/分镜建议"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "分镜规范:"
        echo "  • 封面图: 1920×1080px (16:9)"
        echo "  • B-roll 素材: 每 20-30 秒切换一次"
        echo "  • 字幕卡片: 关键信息强调"
        echo ""
        ESTIMATED_DURATION=$((WORD_COUNT / 3))  # 约 3 字/秒
        RECOMMENDED_BROLLS=$((ESTIMATED_DURATION / 25))
        echo "预估时长: ${ESTIMATED_DURATION} 秒"
        echo "推荐 B-roll 数量: $RECOMMENDED_BROLLS 段"
        ;;
    *)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📄 通用配图建议"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "配图建议:"
        echo "  • 封面图: 根据平台要求调整"
        echo "  • 内文图: 辅助理解，适度配图"
        echo "  • 建议数量: 2-5 张"
        ;;
esac

echo ""
echo "💡 配图来源建议:"
echo "   1. Unsplash / Pexels (免费高质量图库)"
echo "   2. Midjourney / DALL-E (AI 生成图片)"
echo "   3. Canva / 创客贴 (设计工具)"
echo "   4. 自己拍摄 (真实性最高)"
echo ""
echo "📝 接下来:"
echo "   AI 将基于文章内容提供具体配图方案"
echo "   包括: 图片位置、配图主题、搜索关键词"
echo ""

# 创建配图方案文件
ARTICLE_DIR=$(dirname "$DRAFT_FILE")
IMAGES_PLAN="$ARTICLE_DIR/images-plan.md"

cat > "$IMAGES_PLAN" << EOF
# 配图方案

**文章**: $(basename "$DRAFT_FILE")
**工作区**: $WORKSPACE_TYPE
**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

## 配图列表

<!-- AI 将在此生成配图建议 -->

EOF

echo "✅ 已创建配图方案文件: $IMAGES_PLAN"
echo ""

# 输出信息供 AI 使用
output_json "{\"draft_file\": \"$DRAFT_FILE\", \"images_plan\": \"$IMAGES_PLAN\", \"workspace\": \"$WORKSPACE_TYPE\", \"word_count\": $WORD_COUNT}"
