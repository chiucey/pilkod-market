#!/usr/bin/env python3
"""
技能验证脚本 - 专职社群运营师
验证 SKILL.md 的 frontmatter、结构和内容质量
"""

import os
import re
import sys
import json
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(msg, color=None):
    prefix = f"{color}{Colors.BOLD}" if color else ""
    suffix = Colors.END
    print(f"{prefix}{msg}{suffix}")

def check_frontmatter(skill_path):
    """验证 frontmatter 格式"""
    issues = []

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        issues.append("❌ SKILL.md 必须以 '---' 开头（frontmatter 必须在第一行）")
        return issues, False

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        issues.append("❌ 缺少 frontmatter 结束标记 '---'")
        return issues, False

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    if not re.search(r'^name:\s*\S+', frontmatter_text, re.MULTILINE):
        issues.append("❌ frontmatter 缺少 'name' 字段")

    if not re.search(r'^description:\s*\S+', frontmatter_text, re.MULTILINE):
        issues.append("❌ frontmatter 缺少 'description' 字段")

    # 检查 description 触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1)
        if '当用户说' not in desc and 'Use when' not in desc.lower():
            issues.append("⚠️ 建议 description 包含触发短语（如'当用户说...'）")

    return issues, len(issues) == 0

def check_structure(skill_dir):
    """验证目录结构"""
    issues = []

    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            issues.append(f"❌ 缺少必需文件: {file}")

    # 检查 _meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                issues.append("❌ _meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                issues.append("❌ _meta.json 缺少 'version' 字段")
        except json.JSONDecodeError:
            issues.append("❌ _meta.json 格式错误")

    return issues, len(issues) == 0

def check_naming(skill_dir):
    """检查命名规范"""
    issues = []
    skill_name = os.path.basename(skill_dir)

    # 检查是否包含非ASCII字符
    if not skill_name.isascii():
        issues.append(f"❌ 文件夹名称 '{skill_name}' 包含非ASCII字符，应使用英文")

    # 检查 SKILL.md 中的 name 字段
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_path):
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        name_match = re.search(r'^name:\s*(.+)', content, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if not name_value.isascii():
                issues.append(f"❌ frontmatter name '{name_value}' 包含非ASCII字符")

    return issues, len(issues) == 0

def check_content(skill_path):
    """检查内容质量"""
    issues = []

    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否有标题在 frontmatter 之前
    frontmatter_end = content.find('---', 3) + 3
    before_frontmatter = content[:content.find('\n', 4)]

    if '#' in before_frontmatter:
        issues.append("❌ frontmatter 之前不能有 markdown 标题")

    # 检查核心章节
    required_sections = ['核心能力', '工作流程', '输出要求']
    for section in required_sections:
        if section not in content:
            issues.append(f"⚠️ 建议包含章节: {section}")

    # 检查是否有空话术模板或placeholder
    if '### 2.1' in content or '{占位符}' in content:
        issues.append("⚠️ 内容中可能存在未填充的占位符")

    return issues, len(issues) == 0

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(skill_dir)  # 回到 skill 根目录

    log(f"\n🔍 验证技能: {os.path.basename(skill_dir)}", Colors.BLUE)
    log("=" * 50)

    all_passed = True
    issues_list = []

    # 1. Frontmatter 验证
    log("\n📋 Frontmatter 验证:", Colors.BLUE)
    skill_path = os.path.join(skill_dir, 'SKILL.md')
    fm_issues, fm_passed = check_frontmatter(skill_path)
    for issue in fm_issues:
        log(f"   {issue}")
        all_passed = False
    log(f"   {'✅ 通过' if fm_passed else '❌ 失败'}")

    # 2. 目录结构验证
    log("\n📁 目录结构验证:", Colors.BLUE)
    struct_issues, struct_passed = check_structure(skill_dir)
    for issue in struct_issues:
        log(f"   {issue}")
        all_passed = False
    log(f"   {'✅ 通过' if struct_passed else '❌ 失败'}")

    # 3. 命名规范验证
    log("\n🏷️ 命名规范验证:", Colors.BLUE)
    name_issues, name_passed = check_naming(skill_dir)
    for issue in name_issues:
        log(f"   {issue}")
        all_passed = False
    log(f"   {'✅ 通过' if name_passed else '❌ 失败'}")

    # 4. 内容质量验证
    log("\n📝 内容质量验证:", Colors.BLUE)
    content_issues, content_passed = check_content(skill_path)
    for issue in content_issues:
        log(f"   {issue}")
        all_passed = False
    log(f"   {'✅ 通过' if content_passed else '⚠️ 有建议'}")

    # 最终结果
    log("\n" + "=" * 50)
    if all_passed:
        log("✅ 所有验证通过！技能已准备就绪。", Colors.GREEN)
        return 0
    else:
        log("❌ 存在需要修复的问题。", Colors.RED)
        return 1

if __name__ == '__main__':
    sys.exit(main())
