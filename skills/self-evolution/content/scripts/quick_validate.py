#!/usr/bin/env python3
"""
自我进化技能 - 快速验证脚本
验证技能结构和frontmatter是否符合规范
"""

import os
import re
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter"""
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头(frontmatter)"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析frontmatter"

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(f'^{field}:', frontmatter_text, re.MULTILINE):
            return False, f"缺少必需字段: {field}"

    # 检查name字段格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name必须使用小写字母、数字和连字符: {name}"

    return True, "frontmatter验证通过"

def validate_meta_json(skill_path):
    """验证_meta.json"""
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON解析失败: {e}"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"缺少必需字段: {field}"

    # 检查version格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, f"version格式错误，应为x.y.z: {meta['version']}"

    return True, "_meta.json验证通过"

def validate_structure(skill_path):
    """验证目录结构"""
    name = skill_path.name

    # 检查name与目录名一致
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if frontmatter_match:
            name_match = re.search(r'^name:\s*(.+)', frontmatter_match.group(1), re.MULTILINE)
            if name_match:
                frontmatter_name = name_match.group(1).strip()
                if frontmatter_name != name:
                    return False, f"name不匹配: 目录为{name}, frontmatter为{frontmatter_name}"

    return True, "结构验证通过"

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    skill_path = script_dir.parent

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证_meta.json
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    # 验证结构
    passed, msg = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过!")
        sys.exit(0)
    else:
        print("✗ 存在验证失败项")
        sys.exit(1)

if __name__ == "__main__":
    main()
