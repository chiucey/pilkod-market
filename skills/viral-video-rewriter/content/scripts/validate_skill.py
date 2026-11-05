#!/usr/bin/env python3
"""
验证脚本 - 检查 viral-video-rewriter 技能的结构和内容
"""

import os
import re
import json
import sys

def validate_frontmatter(file_path):
    """验证 SKILL.md 的 frontmatter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "Frontmatter 必须以 '---' 开头"

    # 提取 frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "Frontmatter 格式错误"

    frontmatter = parts[1]

    # 检查必需字段
    if 'name:' not in frontmatter:
        return False, "缺少 name 字段"
    if 'description:' not in frontmatter:
        return False, "缺少 description 字段"

    # 提取 name 值
    name_match = re.search(r'name:\s*(.+)', frontmatter)
    if name_match:
        name = name_match.group(1).strip()
        if not name or not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name 字段格式错误: {name}"

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "_meta.json 缺少 id 字段"
    if 'version' not in meta:
        return False, "_meta.json 缺少 version 字段"

    return True, "_meta.json 验证通过"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            return False, f"缺少必需文件: {file}"
    return True, "目录结构验证通过"

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"验证技能目录: {skill_dir}")
    print("-" * 50)

    # 验证目录结构
    valid, msg = validate_directory_structure(skill_dir)
    print(f"{'✅' if valid else '❌'} {msg}")
    if not valid:
        sys.exit(1)

    # 验证 _meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    valid, msg = validate_meta_json(meta_path)
    print(f"{'✅' if valid else '❌'} {msg}")
    if not valid:
        sys.exit(1)

    # 验证 SKILL.md
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    valid, msg = validate_frontmatter(skill_md_path)
    print(f"{'✅' if valid else '❌'} {msg}")
    if not valid:
        sys.exit(1)

    print("-" * 50)
    print("✅ 所有验证通过!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
