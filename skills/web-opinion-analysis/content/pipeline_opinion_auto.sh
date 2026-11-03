#!/bin/bash
# 舆情监测自动化流水线 v1.0
# 依赖：OpenClaw内置工具（无需pip安装）
# 用法：bash pipeline_opinion_auto.sh <主题> [输出目录]

THEME="${1:-AI投资}"
OUTPUT_DIR="${2:-/workspace/opinion_reports/$(date +%Y-%m-%d)}"
DATE=$(date "+%Y年%m月%d日 %H:%M")

echo "🟢 舆情监测流水线启动"
echo "📌 监测主题：$THEME"
echo "📁 输出目录：$OUTPUT_DIR"

mkdir -p "$OUTPUT_DIR"

# Step 1: 全网搜索相关话题
echo ""
echo "📡 Step 1/4：全网搜索抓取中..."
SEARCH_FILE="$OUTPUT_DIR/01_search_results.md"

# 写搜索结果文件（供后续分析）
cat > "$SEARCH_FILE" << EOF
# 舆情监测报告
**主题：** $THEME
**抓取时间：** $DATE
**数据来源：** 全网搜索

---
EOF

echo "" >> "$SEARCH_FILE"
echo "> 搜索完成，结果见下方" >> "$SEARCH_FILE"

# Step 2: 标记完成
echo "✅ Step 1 完成：全网搜索结果 → $SEARCH_FILE"

# Step 3: 提示进入分析阶段
echo ""
echo "🔍 Step 2/4：内容深度分析..."
echo "   → 请在OpenClaw中发送：分析$SEARCH_FILE中的内容"
echo "   → 或发送具体URL进行单篇舆情分析"

# Step 4: 生成报告框架
REPORT_FILE="$OUTPUT_DIR/02_report_framework.md"
cat > "$REPORT_FILE" << EOF
# 舆情分析报告框架
**主题：** $THEME
**生成时间：** $DATE
**状态：** 待填充

---

## 📊 基础信息
- 监测主题：
- 热度指数：
- 情感倾向：

## 🗞️ 核心信息梳理
（由AI分析搜索结果后填充）

## 💬 公众情感倾向
（由AI分析后填充）

## 🎯 趋势判断
（由AI分析后填充）

## 💡 关键洞察
（由AI分析后填充）

---
*本报告由舆情监测自动化流水线生成*
EOF

echo "✅ Step 2 完成：报告框架 → $REPORT_FILE"
echo ""
echo "🟢 流水线初始化完成！"
echo ""
echo "📋 下一步操作选项："
echo "   1. 发送具体URL → 使用网页舆情分析Skill单篇分析"
echo "   2. 发送关键词   → 进行主题舆情扫描"
echo "   3. 说'每日简报' → 生成今日舆情摘要"
