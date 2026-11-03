#!/bin/bash
# EvoMap 快速发布器 - 启动脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 EvoMap 快速发布器 v4.0"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# 检查节点配置
if [ ! -f "nodes_info.json" ]; then
    echo "❌ 错误：nodes_info.json 不存在"
    echo "   请从 /root/.openclaw/skills/evomap-publisher/scripts/ 复制"
    exit 1
fi

# 显示节点数量
NODE_COUNT=$(cat nodes_info.json | grep -c "node_id" || echo "0")
echo "📊 配置节点数：$NODE_COUNT"
echo "🎯 日标发布：$((NODE_COUNT * 100)) 条/天"
echo ""

# 启动守护进程
echo "🚀 启动发布守护进程..."
node fast-publish-daemon-v2.js
