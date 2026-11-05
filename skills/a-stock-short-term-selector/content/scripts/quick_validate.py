#!/usr/bin/env python3
"""
A股短线选股系统 - 技能验证脚本
验证SKILL.md的frontmatter格式和结构完整性
"""

import os
import re
import json
import sys

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter格式"""
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return False, f"SKILL.md不存在于 {skill_path}"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在第一行开始
    lines = content.split('\n')
    if not lines[0].strip().startswith('---'):
        return False, "SKILL.md必须以---frontmatter块开始，不能有标题或空行在前面"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析frontmatter块，请检查格式"

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    if 'name:' not in frontmatter_text:
        return False, "frontmatter缺少name字段"
    if 'description:' not in frontmatter_text:
        return False, "frontmatter缺少description字段"

    # 验证name格式（连字符）
    name_match = re.search(r'name:\s*([a-z0-9-]+)', frontmatter_text)
    if name_match:
        name = name_match.group(1)
        if name != os.path.basename(skill_path):
            return False, f"name '{name}' 必须与文件夹名称 '{os.path.basename(skill_path)}' 一致"

    return True, "frontmatter验证通过"

def validate_meta_json(skill_path):
    """验证_meta.json的完整性"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必需字段
        if 'id' not in meta:
            return False, "_meta.json缺少id字段"
        if 'version' not in meta:
            return False, "_meta.json缺少version字段"

        return True, "_meta.json验证通过"
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

def validate_structure(skill_path):
    """验证目录结构"""
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    for d in required_dirs:
        dir_path = os.path.join(skill_path, d)
        if not os.path.exists(dir_path):
            return False, f"缺少必需目录: {d}"

    return True, "目录结构验证通过"

def main():
    # 获取技能路径
    skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"正在验证技能: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] Frontmatter验证: {msg}")
    all_passed = all_passed and passed

    # 验证meta.json
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta验证: {msg}")
    all_passed = all_passed and passed

    # 验证结构
    passed, msg = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] 结构验证: {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        sys.exit(0)
    else:
        print("✗ 存在验证失败项")
        sys.exit(1)

if __name__ == "__main__":
    main()
