#!/usr/bin/env python3
"""快速验证技能结构和内容"""

import os
import sys
import json
import re

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否是---
    lines = content.strip().split('\n')
    if not lines[0].strip().startswith('---'):
        return False, "SKILL.md必须以---开头"

    # 提取frontmatter
    frontmatter_lines = []
    in_frontmatter = False
    for line in lines:
        if line.strip().startswith('---') and not in_frontmatter:
            in_frontmatter = True
            continue
        elif line.strip().startswith('---') and in_frontmatter:
            break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:\s*\S+', frontmatter_text, re.MULTILINE):
            return False, f"缺少必需字段: {field}"

    return True, "Frontmatter验证通过"

def validate_meta_json(meta_path):
    """验证_meta.json格式"""
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_keys = ['id', 'version']
    for key in required_keys:
        if key not in meta:
            return False, f"缺少必需键: {key}"

    if not isinstance(meta['id'], int):
        return False, "id必须是整数"

    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, "version必须是语义化版本格式 (x.y.z)"

    return True, "_meta.json验证通过"

def validate_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            return False, f"缺少必需文件: {file}"
    return True, "目录结构验证通过"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print(f"验证技能: {skill_dir}")
    print("-" * 40)

    # 验证结构
    valid, msg = validate_structure(skill_dir)
    print(f"{'✓' if valid else '✗'} {msg}")
    if not valid:
        sys.exit(1)

    # 验证frontmatter
    valid, msg = validate_frontmatter(os.path.join(skill_dir, 'SKILL.md'))
    print(f"{'✓' if valid else '✗'} {msg}")
    if not valid:
        sys.exit(1)

    # 验证meta.json
    valid, msg = validate_meta_json(os.path.join(skill_dir, '_meta.json'))
    print(f"{'✓' if valid else '✗'} {msg}")
    if not valid:
        sys.exit(1)

    print("-" * 40)
    print("✓ 所有验证通过！")
    return 0

if __name__ == '__main__':
    sys.exit(main())
