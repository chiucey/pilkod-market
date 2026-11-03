#!/bin/bash
# EvoMap 发布器 - 迁移脚本（从旧版本迁移到新 skill）

echo "🔄 迁移 EvoMap 发布器到新版 Skill..."
echo ""

OLD_DIR="/root/.openclaw/skills/evomap-publisher/scripts"
NEW_DIR="/workspace/skills/evomap-fast-publisher/scripts"

# 检查旧目录
if [ ! -d "$OLD_DIR" ]; then
    echo "❌ 错误：旧版本目录不存在 $OLD_DIR"
    exit 1
fi

# 检查新目录
if [ ! -d "$NEW_DIR" ]; then
    echo "❌ 错误：新版本目录不存在 $NEW_DIR"
    echo "   请先运行安装脚本"
    exit 1
fi

echo "📂 源目录：$OLD_DIR"
echo "📂 目标目录：$NEW_DIR"
echo ""

# 迁移运行时状态文件
echo "📋 迁移运行时状态文件..."
for file in node_state.json chain_state.json used-combos.json domain-history.json; do
    if [ -f "$OLD_DIR/$file" ]; then
        cp "$OLD_DIR/$file" "$NEW_DIR/$file"
        echo "   ✅ 迁移 $file"
    else
        echo "   ℹ️  $file (不存在，跳过)"
    fi
done

# 迁移节点配置
if [ -f "$OLD_DIR/nodes_info.json" ]; then
    cp "$OLD_DIR/nodes_info.json" "$NEW_DIR/nodes_info.json"
    echo "   ✅ 迁移 nodes_info.json"
fi

echo ""
echo "✅ 迁移完成！"
echo ""
echo "🚀 下一步:"
echo "   cd $NEW_DIR/.."
echo "   ./start.sh"
echo ""
echo "📊 查看状态:"
echo "   ./status.sh"
echo ""
