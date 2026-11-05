#!/usr/bin/env python3
"""
进销存技能验证脚本
验证技能文件的完整性和格式正确性
"""

import os
import sys
import json
import re

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "无法解析frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 检查必要字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"缺少必填字段: {field}"

    # 检查name格式（连字符）
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name必须使用小写字母、数字和连字符: {name}"

    return True, "frontmatter验证通过"

def validate_meta_json(meta_path):
    """验证_meta.json格式"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必填字段
        if 'id' not in meta:
            return False, "缺少id字段"
        if 'version' not in meta:
            return False, "缺少version字段"

        # 检查id类型
        if not isinstance(meta['id'], int):
            return False, "id必须是整数"

        # 检查version格式
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            return False, "version必须符合语义化版本格式"

        return True, "_meta.json验证通过"
    except json.JSONDecodeError as e:
        return False, f"JSON格式错误: {e}"
    except Exception as e:
        return False, f"验证错误: {e}"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            return False, f"缺少必要文件: {file}"
    return True, "目录结构验证通过"

def main():
    # 获取技能目录
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(skill_dir)  # 返回上一级目录

    print(f"验证技能: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 验证目录结构
    success, msg = validate_directory_structure(skill_dir)
    print(f"[{'✓' if success else '✗'}] {msg}")
    all_passed = all_passed and success

    # 验证meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    success, msg = validate_meta_json(meta_path)
    print(f"[{'✓' if success else '✗'}] {msg}")
    all_passed = all_passed and success

    # 验证SKILL.md
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    success, msg = validate_frontmatter(skill_md_path)
    print(f"[{'✓' if success else '✗'}] {msg}")
    all_passed = all_passed and success

    print("-" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 验证失败")
        return 1

if __name__ == '__main__':
    sys.exit(main())
