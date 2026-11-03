#!/usr/bin/env bash
# 测试 WeChat Auto Publisher 技能

set -e

echo "=== 测试 WeChat Auto Publisher ==="
echo ""

# 检查技能目录结构
echo "1. 检查技能目录结构..."
if [ -d "scripts" ] && [ -d "templates" ] && [ -d "config" ]; then
    echo "✅ 目录结构完整"
else
    echo "❌ 目录结构不完整"
    exit 1
fi

# 检查脚本文件
echo "2. 检查脚本文件..."
scripts=("auto-publish.sh" "setup.sh" "utils.sh" "generate-content.sh" "generate-images.sh" "format-article.sh" "publish-wechat.sh")
all_scripts_ok=true

for script in "${scripts[@]}"; do
    if [ -f "scripts/$script" ] && [ -x "scripts/$script" ]; then
        echo "  ✅ $script"
    else
        echo "  ❌ $script"
        all_scripts_ok=false
    fi
done

if [ "$all_scripts_ok" = true ]; then
    echo "✅ 所有脚本文件正常"
else
    echo "❌ 部分脚本文件有问题"
fi

# 检查模板文件
echo "3. 检查模板文件..."
if [ -f "templates/tech-article.md" ] && [ -f "templates/business-report.md" ]; then
    echo "✅ 模板文件完整"
else
    echo "❌ 模板文件缺失"
fi

# 检查配置文件
echo "4. 检查配置文件..."
if [ -d "config/generators" ] && [ -d "config/image-sources" ]; then
    echo "✅ 配置目录完整"
else
    echo "❌ 配置目录缺失"
fi

# 检查示例文件
echo "5. 检查示例文件..."
if [ -f "example-topic.txt" ] && [ -f "example-output.md" ]; then
    echo "✅ 示例文件完整"
else
    echo "❌ 示例文件缺失"
fi

# 检查文档文件
echo "6. 检查文档文件..."
if [ -f "SKILL.md" ] && [ -f "README.md" ]; then
    echo "✅ 文档文件完整"
    
    # 检查SKILL.md格式
    if grep -q "^---$" SKILL.md && grep -q "name: wechat-auto-publisher" SKILL.md; then
        echo "✅ SKILL.md 格式正确"
    else
        echo "❌ SKILL.md 格式不正确"
    fi
else
    echo "❌ 文档文件缺失"
fi

echo ""
echo "=== 功能测试 ==="
echo ""

# 测试setup.sh
echo "7. 测试 setup.sh (检查模式)..."
if ./scripts/setup.sh --check --no-ip-check 2>&1 | grep -q "检查系统依赖"; then
    echo "✅ setup.sh 基本功能正常"
else
    echo "❌ setup.sh 功能异常"
fi

# 测试generate-content.sh
echo "8. 测试 generate-content.sh..."
test_output="/tmp/test-content-$$.md"
if ./scripts/generate-content.sh "测试主题" --output "$test_output" 2>&1 | grep -q "内容生成完成"; then
    echo "✅ generate-content.sh 功能正常"
    echo "   生成文件: $test_output ($(wc -l < "$test_output") 行)"
else
    echo "❌ generate-content.sh 功能异常"
fi

# 测试工具函数
echo "9. 测试工具函数..."
if ./scripts/utils.sh 2>&1 | grep -q "错误：无法加载"; then
    echo "✅ utils.sh 加载检查正常"
else
    echo "⚠️  utils.sh 加载检查异常"
fi

echo ""
echo "=== 测试总结 ==="
echo ""
echo "WeChat Auto Publisher 技能包创建完成！"
echo ""
echo "下一步操作："
echo "1. 配置微信公众号凭证："
echo "   在 ~/.openclaw/workspace/TOOLS.md 中添加 WECHAT_APP_ID 和 WECHAT_APP_SECRET"
echo ""
echo "2. 添加IP白名单："
echo "   运行: curl ifconfig.me 获取IP，添加到公众号后台白名单"
echo ""
echo "3. 测试完整流程："
echo "   ./scripts/auto-publish.sh \"测试主题\" --dry-run"
echo ""
echo "4. 实际发布："
echo "   ./scripts/auto-publish.sh \"你的选题\""
echo ""
echo "详细文档："
echo "  - 技能文档: cat SKILL.md | less"
echo "  - 使用说明: cat README.md"
echo "  - 主脚本帮助: ./scripts/auto-publish.sh --help"
echo ""

# 清理测试文件
[ -f "$test_output" ] && rm -f "$test_output"

echo "测试完成！"