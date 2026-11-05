#!/usr/bin/env python3
"""
验证Word文档美化技能的结构和内容
"""
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Cannot parse YAML frontmatter"

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"Missing required frontmatter field: {field}"

    # 检查name格式（连字符）
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should use hyphen-case (lowercase with hyphens)"

    # 检查description包含触发短语
    desc_match = re.search(r'^description:\s*(.+)', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if '当用户' not in desc and 'when' not in desc.lower():
            return False, "Description should contain trigger phrases like '当用户'"

    return True, "Frontmatter validated successfully"

def validate_meta_json(meta_path):
    """验证_meta.json的格式"""
    import json

    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field in _meta.json: {field}"

    # 检查id是否为数字
    if not isinstance(meta['id'], int):
        return False, f"id should be an integer, got {type(meta['id'])}"

    # 检查version格式
    if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
        return False, f"version should follow semantic versioning (x.y.z), got {meta['version']}"

    return True, "_meta.json validated successfully"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            return False, f"Missing required file: {file}"

    # 检查可选目录
    optional_dirs = ['references', 'scripts', 'assets']
    for dir_name in optional_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path):
            if not os.listdir(dir_path):
                print(f"  Warning: {dir_name}/ directory is empty")

    return True, "Directory structure validated successfully"

def validate_skill_name_match(skill_md_path, folder_name):
    """验证技能名称与文件夹名称匹配"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()
            expected_name = folder_name.replace('_', '-')
            if skill_name != expected_name:
                return False, f"Name mismatch: SKILL.md has '{skill_name}', folder is '{folder_name}'"

    return True, "Skill name matches folder"

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f"Validating skill at: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 验证目录结构
    result, msg = validate_directory_structure(skill_dir)
    print(f"[{'PASS' if result else 'FAIL'}] {msg}")
    all_passed = all_passed and result

    # 验证_meta.json
    meta_path = os.path.join(skill_dir, '_meta.json')
    result, msg = validate_meta_json(meta_path)
    print(f"[{'PASS' if result else 'FAIL'}] {msg}")
    all_passed = all_passed and result

    # 验证frontmatter
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    result, msg = validate_frontmatter(skill_md_path)
    print(f"[{'PASS' if result else 'FAIL'}] {msg}")
    all_passed = all_passed and result

    # 验证名称匹配
    folder_name = os.path.basename(os.path.abspath(skill_dir))
    result, msg = validate_skill_name_match(skill_md_path, folder_name)
    print(f"[{'PASS' if result else 'FAIL'}] {msg}")
    all_passed = all_passed and result

    print("-" * 50)
    if all_passed:
        print("All validations passed!")
        return 0
    else:
        print("Some validations failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
