#!/bin/bash
# SJTU 论文排版助手 - Skill 结构验证脚本
# 验证 my-skill/ 目录结构、YAML frontmatter、关键内容

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0
WARNINGS=0

echo "============================================"
echo " SJTU 论文排版助手 - Skill 结构验证"
echo "============================================"
echo ""

# 检查文件是否存在
check_file() {
    local file="$1"
    local desc="$2"
    local optional="${3:-false}"

    if [ -f "$SKILL_DIR/$file" ]; then
        local size=$(wc -c < "$SKILL_DIR/$file")
        echo "  ✓ $file ($desc) - ${size}B"
    else
        if [ "$optional" = "true" ]; then
            echo "  ⚠ $file ($desc) - 可选文件，未找到"
            WARNINGS=$((WARNINGS + 1))
        else
            echo "  ✗ $file ($desc) - 缺少必需文件!"
            ERRORS=$((ERRORS + 1))
        fi
    fi
}

# 检查 YAML frontmatter
check_frontmatter() {
    local file="$1"
    local filepath="$SKILL_DIR/$file"

    if [ ! -f "$filepath" ]; then
        return
    fi

    local first_line=$(head -1 "$filepath")
    if [ "$first_line" = "---" ]; then
        if grep -q "^name:" "$filepath" && grep -q "^description:" "$filepath"; then
            echo "  ✓ $file YAML frontmatter 完整 (name + description)"
        else
            echo "  ✗ $file YAML frontmatter 缺少 name 或 description"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "  ✗ $file 未以 YAML frontmatter (---) 开头!"
        ERRORS=$((ERRORS + 1))
    fi
}

# 检查 UTF-8 编码
check_utf8() {
    local file="$1"
    local filepath="$SKILL_DIR/$file"

    if [ ! -f "$filepath" ]; then
        return
    fi

    if file "$filepath" | grep -q "UTF-8\|ASCII\|Non-ISO"; then
        echo "  ✓ $file 编码正确"
    else
        echo "  ⚠ $file 编码可能不是 UTF-8"
        WARNINGS=$((WARNINGS + 1))
    fi
}

echo "[目录结构检查]"
echo ""
check_file "SKILL.md" "技能主说明"
check_file "template.md" "对话模板" "true"
check_file "examples/sample.md" "示例输出"
check_file "scripts/validate.sh" "验证脚本"

echo ""
echo "[YAML frontmatter 检查]"
echo ""
check_frontmatter "SKILL.md"
check_frontmatter "template.md"
check_frontmatter "examples/sample.md"
check_frontmatter "README.md" "true"
check_frontmatter "examples/feedback.md" "true"

echo ""
echo "[编码检查]"
echo ""
check_utf8 "SKILL.md"
check_utf8 "template.md"

echo ""
echo "[内容检查]"
echo ""

# 检查 SKILL.md 必需内容
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    if grep -q "撰写规范\|2022\|上海交通大学" "$SKILL_DIR/SKILL.md"; then
        echo "  ✓ SKILL.md 包含规范依据引用"
    else
        echo "  ✗ SKILL.md 缺少规范依据"
        ERRORS=$((ERRORS + 1))
    fi

    for keyword in "排版" "黑体" "宋体" "参考文献" "页眉" "标点" "全角" "变量.*斜体"; do
        if grep -q "$keyword" "$SKILL_DIR/SKILL.md"; then
            :
        else
            echo "  ⚠ SKILL.md 缺少关键词: $keyword"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
fi

# 检查 template.md
if [ -f "$SKILL_DIR/template.md" ]; then
    for keyword in "三号黑体" "小四号宋体" "固定值 20 磅" "GB/T 7714" "标点符号" "全角" "半角" "变量.*斜体" "编号连续"; do
        if grep -q "$keyword" "$SKILL_DIR/template.md"; then
            :
        else
            echo "  ⚠ template.md 缺少格式细则: $keyword"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
fi

# 检查 examples/sample.md
if [ -f "$SKILL_DIR/examples/sample.md" ]; then
    if grep -q "LaTeX\|Word 样式" "$SKILL_DIR/examples/sample.md"; then
        echo "  ✓ sample.md 包含双格式示例"
    else
        echo "  ⚠ sample.md 缺少输出格式示例"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

echo ""
echo "============================================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo " 结果: ✓ 全部通过"
elif [ $ERRORS -eq 0 ] && [ $WARNINGS -gt 0 ]; then
    echo " 结果: ✓ 通过（$WARNINGS 个警告）"
else
    echo " 结果: ✗ 未通过（$ERRORS 个错误，$WARNINGS 个警告）"
fi
echo "============================================"
exit $ERRORS
