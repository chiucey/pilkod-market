#!/bin/bash
# ============================================================
# 股票简报触发脚本（被 cron 调用）
# 用法: ./run-briefing.sh AM    ← 开盘简报
#       ./run-briefing.sh PM    ← 收盘简报
# 数据源：新浪财经 API（静态接口，无需 JS）
# ============================================================

MODE="$1"
NOW=$(date "+%Y-%m-%d %H:%M:%S")
DATE=$(date +%Y-%m-%d)

if [ "$MODE" = "AM" ]; then
    REPORT_TYPE="📈 开盘分析简报"
elif [ "$MODE" = "PM" ]; then
    REPORT_TYPE="📊 收盘走势小结"
else
    echo "用法: $0 AM  或  $0 PM"
    exit 1
fi

# 路径解析：scripts/run-briefing.sh → 技能根目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="$SKILL_DIR/temp"
LOG_FILE="$TEMP_DIR/run.log"
LOCK_FILE="$TEMP_DIR/${DATE}-${MODE}-lock"

echo "[$NOW] [$REPORT_TYPE] 开始..." >> "$LOG_FILE"

# 判断是否为交易日
python3 "$SCRIPT_DIR/is_trading_day.py"
if [ $? -ne 0 ]; then
    echo "[$NOW] 今日非交易日，简报跳过" >> "$LOG_FILE"
    openclaw message send \
        --channel feishu \
        --target "chat:飞书群聊ID" \
        --message "🗓️ 今日（${DATE}）非交易日，股票简报暂停发布，明日正常推送。" \
        >> "$LOG_FILE" 2>&1
    echo "OK - $DATE 非交易日"
    exit 0
fi

# 防止重复执行（10分钟锁）
if [ -f "$LOCK_FILE" ]; then
    LOCK_AGE=$(( $(date +%s) - $(cat "$LOCK_FILE" 2>/dev/null) ))
    if [ ${LOCK_AGE:-999} -lt 600 ]; then
        echo "[$NOW] 10分钟内重复执行，跳过" >> "$LOG_FILE"
        exit 0
    fi
fi
echo "$(date +%s)" > "$LOCK_FILE"

echo "[$NOW] 交易日，开始生成简报（新浪财经API）..." >> "$LOG_FILE"

# 调用 Python 数据收集脚本
REPORT=$(python3 "$SCRIPT_DIR/stock_data.py" "$MODE" 2>&1)
PY_EXIT=$?

if [ $PY_EXIT -eq 0 ]; then
    # 发送飞书
    openclaw message send \
        --channel feishu \
        --target "chat:飞书群聊ID" \
        --message "$REPORT" \
        >> "$LOG_FILE" 2>&1
    SEND_EXIT=$?
    if [ $SEND_EXIT -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 飞书群聊发送成功" >> "$LOG_FILE"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 飞书群聊发送失败(code: $SEND_EXIT)" >> "$LOG_FILE"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ 数据收集失败(code: $PY_EXIT)" >> "$LOG_FILE"
    echo "[$REPORT]" >> "$LOG_FILE"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $REPORT_TYPE 执行完毕" >> "$LOG_FILE"
echo "OK - $REPORT_TYPE ($DATE $MODE)"