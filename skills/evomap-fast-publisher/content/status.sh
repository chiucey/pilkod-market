#!/bin/bash
# EvoMap 快速发布器 - 状态检查脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════════"
echo "📊 EvoMap 发布器状态检查"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 检查进程状态
echo "🔄 进程状态:"
PUB_PID=$(pgrep -f "fast-publish-daemon-v2.js" || echo "")
if [ -n "$PUB_PID" ]; then
    echo "   ✅ 发布守护进程运行中 (PID: $PUB_PID)"
else
    echo "   ❌ 发布守护进程未运行"
fi

TASK_PID=$(pgrep -f "task-mode-daemon.js" || echo "")
if [ -n "$TASK_PID" ]; then
    echo "   ✅ 任务模式守护进程运行中 (PID: $TASK_PID)"
else
    echo "   ℹ️  任务模式守护进程未运行"
fi
echo ""

# 检查配置文件
echo "📁 配置文件:"
if [ -f "nodes_info.json" ]; then
    NODE_COUNT=$(cat nodes_info.json | grep -c "node_id" || echo "0")
    echo "   ✅ nodes_info.json ($NODE_COUNT 个节点)"
else
    echo "   ❌ nodes_info.json 不存在"
fi

if [ -f "config.js" ]; then
    echo "   ✅ config.js"
else
    echo "   ❌ config.js 不存在"
fi
echo ""

# 检查状态文件
echo "📊 状态文件:"
for file in node_state.json chain_state.json used-combos.json domain-history.json; do
    if [ -f "$file" ]; then
        SIZE=$(ls -lh "$file" | awk '{print $5}')
        echo "   ✅ $file ($SIZE)"
    else
        echo "   ℹ️  $file (不存在)"
    fi
done
echo ""

# 显示今日发布统计
echo "📈 今日发布统计:"
if [ -f "node_state.json" ]; then
    TODAY=$(date -u +%Y-%m-%d)
    echo "   日期：$TODAY"
    cat node_state.json | grep -A 10 "\"$TODAY\"" | head -20 || echo "   暂无今日数据"
else
    echo "   暂无状态数据"
fi
echo ""

# 显示 Chain 统计
echo "🔗 Chain 统计:"
if [ -f "chain_state.json" ]; then
    CHAIN_COUNT=$(cat chain_state.json | grep -c "chain_id" || echo "0")
    echo "   总 Chain 数：$CHAIN_COUNT"
else
    echo "   暂无 Chain 数据"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
