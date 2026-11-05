#!/usr/bin/env python3
"""验证 OpenClaw 自我进化引擎技能结构"""

import os
import json
import re
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 frontmatter --- 开头"

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析 frontmatter"

    frontmatter_text = frontmatter_match.group(1)
    lines = frontmatter_text.split('\n')

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not any(line.strip().startswith(f'{field}:') for line in lines):
            return False, f"缺少必需字段: {field}"

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name_value):
            return False, f"name 必须使用小写字母、数字和连字符: {name_value}"

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少字段: {field}"

    if not isinstance(meta['id'], int):
        return False, "_meta.json 中 id 必须是整数"

    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, "_meta.json 中 version 必须符合语义化版本格式 (x.y.z)"

    return True, "_meta.json 验证通过"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_dirs = ['scripts', 'references', 'assets']
    for dir_name in required_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if not os.path.exists(dir_path):
            return False, f"缺少目录: {dir_name}"

    return True, "目录结构验证通过"

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    meta_path = os.path.join(skill_dir, '_meta.json')

    all_passed = True
    results = []

    # 验证 frontmatter
    passed, msg = validate_frontmatter(skill_md_path)
    results.append((passed, msg))
    if not passed:
        all_passed = False

    # 验证 meta.json
    passed, msg = validate_meta_json(meta_path)
    results.append((passed, msg))
    if not passed:
        all_passed = False

    # 验证目录结构
    passed, msg = validate_directory_structure(skill_dir)
    results.append((passed, msg))
    if not passed:
        all_passed = False

    # 输出结果
    print("=" * 50)
    print("OpenClaw 自我进化引擎 - 技能验证结果")
    print("=" * 50)
    for passed, msg in results:
        status = "✅" if passed else "❌"
        print(f"{status} {msg}")
    print("=" * 50)

    if all_passed:
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 存在验证失败项")
        return 1

if __name__ == '__main__':
    exit(main())
