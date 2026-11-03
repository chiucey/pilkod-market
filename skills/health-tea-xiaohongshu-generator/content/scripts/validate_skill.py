#!/usr/bin/env python3
"""
养生茶电商生图技能验证脚本
验证 SKILL.md 和 _meta.json 的格式和内容
"""

import json
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 frontmatter '---' 开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 解析 YAML 简版 (name 和 description)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)

    errors = []

    if not name_match:
        errors.append("缺少 'name' 字段")
    else:
        name = name_match.group(1).strip()
        if not name:
            errors.append("'name' 字段不能为空")
        elif ' ' in name:
            errors.append("'name' 应使用连字符格式，不包含空格")

    if not desc_match:
        errors.append("缺少 'description' 字段")
    else:
        desc = desc_match.group(1).strip()
        if len(desc) < 10:
            errors.append("'description' 长度应至少10个字符")

    if not content.startswith('#'):
        pass  # 不以 # 开头是正确的
    else:
        # 检查是否有 # 在 --- 之前
        lines = content.split('\n')
        for i, line in enumerate(lines[:5]):
            if line.startswith('#'):
                return False, "frontmatter 之后才能有 markdown 标题"

    if errors:
        return False, "; ".join(errors)

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError:
            return False, "_meta.json 格式错误，不是有效的 JSON"

    errors = []

    if 'id' not in meta:
        errors.append("缺少 'id' 字段")

    if 'version' not in meta:
        errors.append("缺少 'version' 字段")
    else:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append("'version' 应符合语义化版本格式 (如 1.0.0)")

    if errors:
        return False, "; ".join(errors)

    return True, "_meta.json 验证通过"

def validate_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    optional_dirs = ['references', 'scripts', 'assets']

    errors = []

    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"缺少必需文件: {file}")

    return len(errors) == 0, "; ".join(errors) if errors else "目录结构验证通过"

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(skill_dir)

    skill_md_path = os.path.join(parent_dir, 'SKILL.md')
    meta_path = os.path.join(parent_dir, '_meta.json')

    print("=" * 50)
    print("养生茶电商生图技能验证")
    print("=" * 50)

    # 1. 验证 frontmatter
    print("\n[1/3] 验证 SKILL.md frontmatter...")
    result, msg = validate_frontmatter(skill_md_path)
    print(f"  {'✅' if result else '❌'} {msg}")
    if not result:
        sys.exit(1)

    # 2. 验证 _meta.json
    print("\n[2/3] 验证 _meta.json...")
    result, msg = validate_meta_json(meta_path)
    print(f"  {'✅' if result else '❌'} {msg}")
    if not result:
        sys.exit(1)

    # 3. 验证目录结构
    print("\n[3/3] 验证目录结构...")
    result, msg = validate_structure(parent_dir)
    print(f"  {'✅' if result else '❌'} {msg}")
    if not result:
        sys.exit(1)

    print("\n" + "=" * 50)
    print("✅ 所有验证通过！")
    print("=" * 50)

if __name__ == '__main__':
    main()
