#!/usr/bin/env python3
"""快速验证脚本 - 验证技能结构"""

import json
import os
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头"

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if i == 0 and line == '---':
            in_frontmatter = True
            continue
        if in_frontmatter and line == '---':
            break
        frontmatter_lines.append(line)

    # 解析frontmatter
    frontmatter_str = '\n'.join(frontmatter_lines)
    required_fields = ['name:', 'description:']

    for field in required_fields:
        if field not in frontmatter_str:
            return False, f"frontmatter缺少必需字段: {field}"

    return True, "frontmatter格式正确"

def validate_meta(meta_path):
    """验证_meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json缺少必需字段: {field}"

    return True, "_meta.json格式正确"

def validate_naming(skill_dir):
    """验证命名规范"""
    dir_name = os.path.basename(skill_dir)

    # 检查目录名是否包含非ASCII字符
    if not dir_name.isascii():
        return False, f"目录名包含非ASCII字符: {dir_name}"

    return True, "命名规范正确"

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    skill_md = os.path.join(skill_dir, 'SKILL.md')
    meta_json = os.path.join(skill_dir, '_meta.json')

    all_passed = True

    # 验证frontmatter
    result, msg = validate_frontmatter(skill_md)
    print(f"[{'✓' if result else '✗'}] SKILL.md frontmatter: {msg}")
    all_passed = all_passed and result

    # 验证_meta.json
    result, msg = validate_meta(meta_json)
    print(f"[{'✓' if result else '✗'}] _meta.json: {msg}")
    all_passed = all_passed and result

    # 验证命名
    result, msg = validate_naming(skill_dir)
    print(f"[{'✓' if result else '✗'}] 命名规范: {msg}")
    all_passed = all_passed and result

    if all_passed:
        print("\n✅ 所有验证通过!")
        return 0
    else:
        print("\n❌ 验证失败!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
