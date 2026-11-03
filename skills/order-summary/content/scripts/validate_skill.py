#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能文件结构和Frontmatter格式
"""

import os
import json
import re
import sys

def validate_skill_structure(skill_path):
    """验证技能目录结构"""
    errors = []
    warnings = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        path = os.path.join(skill_path, f)
        if not os.path.exists(path):
            errors.append(f"缺少必需文件: {f}")

    # 检查SKILL.md的frontmatter
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以---开头
        if not content.startswith('---'):
            errors.append("SKILL.md必须以YAML frontmatter开头（---）")

        # 检查frontmatter必填字段
        if 'name:' not in content:
            errors.append("frontmatter缺少name字段")
        if 'description:' not in content:
            errors.append("frontmatter缺少description字段")

        # 检查description是否包含触发短语
        if '触发词' not in content and '当用户' not in content:
            warnings.append("description建议包含触发短语")

        # 检查是否有markdown标题在frontmatter之前
        frontmatter_end = content.find('---', 3)
        if frontmatter_end > 0:
            after_frontmatter = content[frontmatter_end:].strip()
            if after_frontmatter.startswith('#'):
                errors.append("markdown标题不能出现在frontmatter之前")

    # 检查_meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json缺少id字段")
        if 'version' not in meta:
            errors.append("_meta.json缺少version字段")

    # 检查目录结构
    if os.path.exists(os.path.join(skill_path, 'scripts')):
        scripts = os.listdir(os.path.join(skill_path, 'scripts'))
        if not any(f.endswith('.py') for f in scripts):
            warnings.append("scripts目录存在但没有Python文件")

    return errors, warnings


def main():
    if len(sys.argv) < 2:
        skill_path = '.'
    else:
        skill_path = sys.argv[1]

    errors, warnings = validate_skill_structure(skill_path)

    print("=" * 50)
    print("技能结构验证报告")
    print("=" * 50)

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✅ 验证通过！")
    elif not errors:
        print("\n✅ 基本验证通过（有警告）")
    else:
        print("\n❌ 验证失败")

    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
