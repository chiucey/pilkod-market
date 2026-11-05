#!/usr/bin/env python3
"""
试卷分析技能验证脚本
验证 SKILL.md 的 frontmatter 和结构完整性
"""

import os
import sys
import re

def validate_skill(skill_path):
    """验证技能文件的完整性和格式规范"""

    errors = []
    warnings = []

    # 检查目录结构
    if not os.path.exists(skill_path):
        errors.append(f"技能目录不存在: {skill_path}")
        return errors, warnings

    skill_name = os.path.basename(skill_path)

    # 检查 SKILL.md
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md 文件不存在")
    else:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            errors.append("SKILL.md 缺少 frontmatter 或格式不正确")
        else:
            frontmatter = frontmatter_match.group(1)

            # 检查必需字段
            if not re.search(r'^name:', frontmatter, re.MULTILINE):
                errors.append("frontmatter 缺少 'name' 字段")

            if not re.search(r'^description:', frontmatter, re.MULTILINE):
                errors.append("frontmatter 缺少 'description' 字段")

        # 检查文件开头
        first_line = content.split('\n')[0]
        if first_line.startswith('#'):
            errors.append("SKILL.md 第一行不能是 markdown 标题（#），必须是 ---")

    # 检查 _meta.json
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
    else:
        import json
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")

            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查目录名称
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        warnings.append(f"目录名称 '{skill_name}' 应使用小写字母、数字和连字符")

    return errors, warnings


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/chinese-exam-analysis"

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    errors, warnings = validate_skill(skill_path)

    if errors:
        print("❌ 错误:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("⚠️ 警告:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("✅ 验证通过")
        return 0
    elif not errors:
        print("✅ 验证通过（有警告）")
        return 0
    else:
        print("❌ 验证失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())