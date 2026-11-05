#!/bin/bash
# EvoMap 快速发布器 - 安装脚本

echo "🚀 安装 EvoMap 快速发布器 Skill..."

# 检查目录
if [ ! -d "/workspace/skills/evomap-fast-publisher" ]; then
    echo "❌ Skill 目录不存在"
    exit 1
fi

# 复制节点配置（如果原文件存在）
if [ -f "/root/.openclaw/skills/evomap-publisher/scripts/nodes_info.json" ]; then
    echo "📋 复制节点配置..."
    cp /root/.openclaw/skills/evomap-publisher/scripts/nodes_info.json /workspace/skills/evomap-fast-publisher/scripts/
fi

# 复制运行时状态文件（如果存在）
for file in node_state.json chain_state.json used-combos.json domain-history.json; do
    if [ -f "/root/.openclaw/skills/evomap-publisher/scripts/$file" ]; then
        echo "📋 复制 $file ..."
        cp "/root/.openclaw/skills/evomap-publisher/scripts/$file" "/workspace/skills/evomap-fast-publisher/scripts/"
    fi
done

# 设置执行权限
chmod +x /workspace/skills/evomap-fast-publisher/scripts/*.js 2>/dev/null || true

echo ""
echo "✅ 安装完成！"
echo ""
echo "📂 安装位置：/workspace/skills/evomap-fast-publisher/"
echo ""
echo "🚀 启动命令:"
echo "   cd /workspace/skills/evomap-fast-publisher/scripts"
echo "   node fast-publish-daemon-v2.js"
echo ""
echo "📋 任务模式（可选）:"
echo "   node task-mode-daemon.js"
echo ""
