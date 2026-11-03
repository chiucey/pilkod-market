#!/bin/bash
# 尾盘动量选股扫描 - 每日定时执行脚本
# 由 OpenClaw cron 调用 (12:30 北京时间 / 04:30 UTC)
# 执行完成后写入结果文件，供 agent 读取并推送给用户

SCRIPT_DIR="/workspace/skills/stock-intel"
REPORT_FILE="/workspace/skills/stock-intel/latest_scan.json"
LOG_FILE="/workspace/skills/stock-intel/scan.log"

export PYTHONPATH="/usr/local/lib/python3.11/dist-packages:$PYTHONPATH"
export PATH="/usr/local/bin:$PATH"

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] 开始执行选股扫描..." >> "$LOG_FILE"

# 执行扫描（静音模式，输出JSON）
# 执行扫描（静默AKShare进度条，只保留最终JSON结果）
python3 "$SCRIPT_DIR/strategy.py" scan 2>/dev/null | tail -20 > "$REPORT_FILE"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date)] 扫描成功" >> "$LOG_FILE"
else
    echo "[$(date)] 扫描失败，exit=$EXIT_CODE" >> "$LOG_FILE"
fi

exit $EXIT_CODE
