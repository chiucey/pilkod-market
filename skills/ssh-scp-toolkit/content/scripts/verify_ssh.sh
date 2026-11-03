#!/bin/bash
# SSH-SCP Toolkit 验证脚本
# 验证技能结构和必要文件

set -e

SKILL_DIR="${1:-.}"

echo "=========================================="
echo "SSH-SCP Toolkit 验证脚本"
echo "=========================================="
echo ""

# 检查目录结构
echo "[1/5] 检查目录结构..."
if [ ! -d "$SKILL_DIR" ]; then
    echo "❌ 错误: 目录 $SKILL_DIR 不存在"
    exit 1
fi

if [ ! -d "$SKILL_DIR/scripts" ]; then
    echo "⚠️  警告: scripts/ 目录不存在"
fi

if [ ! -d "$SKILL_DIR/references" ]; then
    echo "⚠️  警告: references/ 目录不存在"
fi

echo "✅ 目录结构检查完成"
echo ""

# 检查必需文件
echo "[2/5] 检查必需文件..."
REQUIRED_FILES=("SKILL.md" "_meta.json")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$SKILL_DIR/$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ 错误: $file 不存在"
        exit 1
    fi
done
echo ""

# 验证SKILL.md的frontmatter
echo "[3/5] 验证SKILL.md frontmatter..."
if head -n 1 "$SKILL_DIR/SKILL.md" | grep -q "^---"; then
    echo "✅ SKILL.md 第一行是 ---"
else
    echo "❌ 错误: SKILL.md 必须以 --- 开头"
    exit 1
fi

if grep -q "^name:" "$SKILL_DIR/SKILL.md"; then
    echo "✅ name 字段存在"
else
    echo "❌ 错误: 缺少 name 字段"
    exit 1
fi

if grep -q "^description:" "$SKILL_DIR/SKILL.md"; then
    echo "✅ description 字段存在"
else
    echo "❌ 错误: 缺少 description 字段"
    exit 1
fi
echo ""

# 验证_meta.json
echo "[4/5] 验证_meta.json..."
if grep -q '"id"' "$SKILL_DIR/_meta.json"; then
    echo "✅ id 字段存在"
else
    echo "❌ 错误: 缺少 id 字段"
    exit 1
fi

if grep -q '"version"' "$SKILL_DIR/_meta.json"; then
    echo "✅ version 字段存在"
else
    echo "❌ 错误: 缺少 version 字段"
    exit 1
fi
echo ""

# 检查内容完整性
echo "[5/5] 检查内容完整性..."
if grep -q "plink" "$SKILL_DIR/SKILL.md"; then
    echo "✅ SSH命令执行指南存在"
else
    echo "⚠️  警告: 未找到SSH命令执行内容"
fi

if grep -q "pscp" "$SKILL_DIR/SKILL.md"; then
    echo "✅ SCP文件传输指南存在"
else
    echo "⚠️  警告: 未找到SCP文件传输内容"
fi
echo ""

echo "=========================================="
echo "验证完成！"
echo "=========================================="
