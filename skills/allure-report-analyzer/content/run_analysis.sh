#!/bin/bash
# Allure 报告分析器 - CI/CD 集成脚本
# 用法: ./run_analysis.sh [报告路径] [输出路径]

set -e

# 配置
REPORT_PATH="${1:-./allure-report}"
OUTPUT_PATH="${2:-./test-analysis.json}"
VERBOSE="${VERBOSE:-false}"

echo "=========================================="
echo "  Allure 报告自动分析"
echo "=========================================="
echo "报告路径: $REPORT_PATH"
echo "输出路径: $OUTPUT_PATH"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "Python3 未安装"
    exit 1
fi

# 检查分析器脚本
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ANALYZER_SCRIPT="$SCRIPT_DIR/allure_analyzer.py"

if [ ! -f "$ANALYZER_SCRIPT" ]; then
    echo "分析器脚本不存在: $ANALYZER_SCRIPT"
    exit 1
fi

# 执行分析
echo "开始分析..."
python3 "$ANALYZER_SCRIPT" --path "$REPORT_PATH" --output "$OUTPUT_PATH" --verbose

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "分析完成!"

    # 提取关键指标
    if [ -f "$OUTPUT_PATH" ]; then
        echo ""
        echo "关键指标摘要:"
        echo "   详细报告: $OUTPUT_PATH"
    fi
else
    echo ""
    echo "分析失败!"
    exit 1
fi
