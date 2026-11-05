#!/usr/bin/env bash
# 三遍审校 - 降低 AI 味的核心系统

set -e

SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/common.sh"

PROJECT_ROOT=$(get_project_root)
MODE="$1"  # content, style, detail
DRAFT_FILE="$2"

# 如果没有指定草稿，使用最新的
if [ -z "$DRAFT_FILE" ]; then
    DRAFT_FILE=$(get_latest_draft)
fi

if [ -z "$DRAFT_FILE" ] || [ ! -f "$DRAFT_FILE" ]; then
    echo "❌ 错误: 未找到草稿文件"
    echo "用法: audit.sh <mode> [draft文件路径]"
    echo "  mode: content (内容审校) | style (风格审校) | detail (细节审校)"
    exit 1
fi

# 验证 mode
if [ -z "$MODE" ]; then
    echo "❌ 错误: 未指定审校模式"
    echo "用法: audit.sh <mode> [draft文件路径]"
    echo "  mode: content (内容审校) | style (风格审校) | detail (细节审校)"
    exit 1
fi

# 创建审校日志目录
ARTICLE_DIR=$(dirname "$DRAFT_FILE")
AUDIT_LOG="$ARTICLE_DIR/audit-log.md"

# 初始化审校日志
if [ ! -f "$AUDIT_LOG" ]; then
    cat > "$AUDIT_LOG" << EOF
# 审校记录

**草稿文件**: $(basename "$DRAFT_FILE")
**创建时间**: $(date '+%Y-%m-%d %H:%M:%S')

---

EOF
fi

echo "✅ 草稿文件: $DRAFT_FILE"
echo "📝 审校模式: $MODE"
echo ""

# 显示当前字数
WORD_COUNT=$(count_chinese_words "$DRAFT_FILE")
echo "📊 当前字数: $WORD_COUNT"
echo ""

case "$MODE" in
    content)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 第一遍审校: 内容审校"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "关注维度:"
        echo "  ✓ 事实准确性 - 数据、引用是否正确"
        echo "  ✓ 逻辑连贯性 - 论证是否清晰有力"
        echo "  ✓ 结构完整性 - 开头、正文、结尾是否完整"
        echo "  ✓ 信息密度 - 是否有空话、套话"
        echo ""
        echo "💡 审校要点:"
        echo "   - 删除冗余信息"
        echo "   - 补充缺失论据"
        echo "   - 优化逻辑结构"
        ;;
    style)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎨 第二遍审校: 风格审校 (降 AI 味)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "关注维度:"
        echo "  ✓ 删除 AI 套话 - '随着...发展'、'在...背景下'"
        echo "  ✓ 拆解 AI 句式 - 过长、过于工整的排比句"
        echo "  ✓ 增加真实感 - 融入具体数字、案例、细节"
        echo "  ✓ 强化个性化 - 加入个人观点、经历"
        echo ""
        echo "💡 审校要点:"
        echo "   - 使用 text-audit.sh 检测 AI 味"
        echo "   - 优先替换为个人素材库的真实内容"
        echo "   - 目标: AI 检测率 < 30%"
        echo ""
        # 运行 AI 味检测
        if [ -f "$SCRIPT_DIR/text-audit.sh" ]; then
            echo "🔍 运行 AI 味检测..."
            echo ""
            bash "$SCRIPT_DIR/text-audit.sh" "$DRAFT_FILE" || true
            echo ""
        fi
        ;;
    detail)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✨ 第三遍审校: 细节审校"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "关注维度:"
        echo "  ✓ 标点符号 - 中英文标点使用规范"
        echo "  ✓ 排版格式 - 段落间距、列表格式"
        echo "  ✓ 用词准确 - 错别字、同音字"
        echo "  ✓ 节奏把控 - 句子长短搭配"
        echo ""
        echo "💡 审校要点:"
        echo "   - 最后的抛光工作"
        echo "   - 确保发布前完美"
        ;;
    *)
        echo "❌ 错误: 未知的审校模式: $MODE"
        echo "可用模式: content, style, detail"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 接下来:"
echo "   1. AI 将基于以上维度审校文章"
echo "   2. 修改建议将记录到 $AUDIT_LOG"
echo "   3. 完成后继续下一遍审校或发布"
echo ""

# 记录审校开始
echo "" >> "$AUDIT_LOG"
echo "## 审校: $MODE ($(date '+%Y-%m-%d %H:%M:%S'))" >> "$AUDIT_LOG"
echo "" >> "$AUDIT_LOG"

# 输出信息供 AI 使用
output_json "{\"draft_file\": \"$DRAFT_FILE\", \"mode\": \"$MODE\", \"word_count\": $WORD_COUNT, \"audit_log\": \"$AUDIT_LOG\"}"
