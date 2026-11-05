#!/usr/bin/env bash
# 萝卜看票量化信号 — 入口脚本
# 用法:
#   bash run.sh <股票代码>           # 简洁分析
#   bash run.sh --verbose <代码>     # 详细分析
#   bash run.sh --score <代码>       # 仅共振评分
#   bash run.sh --json <代码>        # JSON输出
# 示例:
#   bash run.sh 601231
#   bash run.sh --verbose 300657

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_FILE="${SCRIPT_DIR}/quant_signal.py"

# 取消代理（腾讯API直连）
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY NO_PROXY
export NO_PROXY="*"

if [ ! -f "$SCRIPT_FILE" ]; then
    echo "[错误] 找不到脚本: $SCRIPT_FILE"
    exit 1
fi

if [ -z "$1" ]; then
    echo "=== 萝卜看票 量化信号扫描器 ==="
    echo ""
    echo "用法:"
    echo "  bash run.sh <股票代码>           # 简洁分析"
    echo "  bash run.sh --verbose <代码>     # 详细分析"
    echo "  bash run.sh --score <代码>       # 仅共振评分"
    echo "  bash run.sh --json <代码>        # JSON输出"
    echo ""
    echo "示例:"
    echo "  bash run.sh 601231"
    echo "  bash run.sh --verbose 300657"
    echo "  bash run.sh 601231 600519 000858  # 批量"
    exit 0
fi

echo "=== 萝卜看票 量化信号 ==="

timeout 120 python3 "$SCRIPT_FILE" "$@" 2>&1
RC=$?

if [ $RC -eq 124 ]; then
    echo "[超时] 数据获取超时，请稍后重试"
elif [ $RC -ne 0 ] && [ $RC -le 127 ]; then
    echo "[错误] 脚本异常，退出码: $RC"
fi

exit $RC
