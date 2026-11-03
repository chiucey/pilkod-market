#!/bin/bash
# EvoMap 快速发布器 - 停止脚本

echo "🛑 停止 EvoMap 发布守护进程..."

# 查找进程
PIDS=$(pgrep -f "fast-publish-daemon-v2.js" || echo "")

if [ -z "$PIDS" ]; then
    echo "ℹ️  没有找到运行中的发布进程"
else
    echo "📋 找到进程：$PIDS"
    kill $PIDS 2>/dev/null
    echo "✅ 已发送停止信号"
fi

# 任务模式进程
TASK_PIDS=$(pgrep -f "task-mode-daemon.js" || echo "")

if [ -z "$TASK_PIDS" ]; then
    echo "ℹ️  没有找到运行中的任务模式进程"
else
    echo "📋 找到任务模式进程：$TASK_PIDS"
    kill $TASK_PIDS 2>/dev/null
    echo "✅ 已发送停止信号"
fi

echo ""
echo "💡 提示：进程可能需要几秒完成当前操作后退出"
