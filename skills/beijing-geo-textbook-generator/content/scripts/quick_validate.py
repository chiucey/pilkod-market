#!/usr/bin/env python3
"""
北京高中地理课本文章生成器 - 快速验证脚本
验证 SKILL.md 结构和 frontmatter 格式
"""

import os
import re
import json
import sys

def validate_frontmatter(skill_md_path):
    """验证 frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 --- 开头"

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "缺少 frontmatter 结束标记 ---"

    frontmatter = '\n'.join(lines[1:frontmatter_end])

    # 检查必填字段
    if 'name:' not in frontmatter:
        return False, "缺少 name 字段"

    if 'description:' not in frontmatter:
        return False, "缺少 description 字段"

    # 检查 description 是否包含触发短语
    if 'Use when' not in frontmatter and '当用户' not in frontmatter:
        return False, "description 应包含触发条件说明"

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 文件不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta:
        return False, "_meta.json 缺少 id 字段"

    if 'version' not in meta:
        return False, "_meta.json 缺少 version 字段"

    return True, "_meta.json 验证通过"

def validate_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for f in required_files:
        path = os.path.join(skill_dir, f)
        if not os.path.exists(path):
            return False, f"缺少必需文件: {f}"

    return True, "目录结构验证通过"

def main():
    skill_dir = os.path.dirname(os.path.abspath(__file__)).replace('/scripts', '')
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    meta_json = os.path.join(skill_dir, '_meta.json')

    all_passed = True

    # 验证结构
    result, msg = validate_structure(skill_dir)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 验证 frontmatter
    result, msg = validate_frontmatter(skill_md)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    # 验证 meta.json
    result, msg = validate_meta_json(meta_json)
    print(f"[{'✓' if result else '✗'}] {msg}")
    all_passed = all_passed and result

    if all_passed:
        print("\n✅ 所有验证通过")
        sys.exit(0)
    else:
        print("\n❌ 验证失败")
        sys.exit(1)

if __name__ == '__main__':
    main()