#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构完整性
"""

import os
import json
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头"

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not any(line.strip().startswith(f'{field}:') for line in frontmatter_lines):
            return False, f"缺少必填字段: {field}"

    return True, "Frontmatter 验证通过"

def validate_meta_json(meta_path):
    """验证 _meta.json"""
    if not os.path.exists(meta_path):
        return False, "_meta.json 不存在"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 检查必填字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"_meta.json 缺少必填字段: {field}"

    # 验证版本格式
    version = meta['version']
    if not all(part.isdigit() for part in version.split('.')):
        return False, "version 必须符合语义化版本格式 (如 1.0.0)"

    return True, "_meta.json 验证通过"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = os.path.join(skill_dir, file)
        if not os.path.exists(file_path):
            return False, f"缺少必需文件: {file}"

    return True, "目录结构验证通过"

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)

    print("=" * 50)
    print("技能验证工具")
    print("=" * 50)
    print(f"验证目录: {skill_dir}\n")

    all_passed = True

    # 验证目录结构
    success, msg = validate_directory_structure(skill_dir)
    print(f"[{'✓' if success else '✗'}] {msg}")
    all_passed = all_passed and success

    # 验证 SKILL.md
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    success, msg = validate_frontmatter(skill_md_path)
    print(f"[{'✓' if success else '✗'}] {msg}")
    all_passed = all_passed and success

    # 验证 _meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    success, msg = validate_meta_json(meta_path)
    print(f"[{'✓' if success else '✗'}] {msg}")
    all_passed = all_passed and success

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        sys.exit(0)
    else:
        print("✗ 存在验证失败项")
        sys.exit(1)

if __name__ == "__main__":
    main()
