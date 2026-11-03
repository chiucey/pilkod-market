#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和Frontmatter
"""

import os
import sys
import re
from pathlib import Path

def validate_frontmatter(skill_path: str) -> tuple[bool, str]:
    """验证SKILL.md的Frontmatter"""
    skill_md = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md):
        return False, "SKILL.md not found"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查Frontmatter是否存在
    if not content.startswith('---'):
        return False, "Frontmatter must start with '---' at the first line"

    # 提取Frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter not closed with '---'"

    frontmatter = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        pattern = rf'^{field}:\s*.+$'
        if not re.search(pattern, frontmatter, re.MULTILINE):
            return False, f"Missing required field: {field}"

    # 提取name值
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        # 检查name格式（连字符）
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
            return False, f"Invalid name format: '{name}'. Use hyphen-case (e.g., 'video-face-replacer')"

        # 检查name与文件夹名称是否匹配
        folder_name = os.path.basename(skill_path)
        if name != folder_name:
            return False, f"Name '{name}' does not match folder name '{folder_name}'"

    # 检查description是否包含触发短语
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        description = desc_match.group(1).strip()
        if len(description) < 20:
            return False, "Description too short (should be descriptive)"

    return True, "Frontmatter valid"


def validate_meta_json(skill_path: str) -> tuple[bool, str]:
    """验证_meta.json"""
    import json

    meta_path = os.path.join(skill_path, '_meta.json')
    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field: {field}"

    # 验证version格式
    version = meta.get('version', '')
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        return False, f"Invalid version format: '{version}'. Use semver (e.g., '1.0.0')"

    return True, "Meta JSON valid"


def validate_structure(skill_path: str) -> tuple[bool, list]:
    """验证目录结构"""
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        if not os.path.exists(os.path.join(skill_path, file)):
            errors.append(f"Missing required file: {file}")

    # 建议的目录结构
    suggested_dirs = ['scripts', 'references', 'assets']
    for dir_name in suggested_dirs:
        dir_path = os.path.join(skill_path, dir_name)
        if os.path.exists(dir_path):
            # 检查目录是否为空
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                errors.append(f"Empty directory: {dir_name}/")

    return len(errors) == 0, errors


def validate_path_names(skill_path: str) -> tuple[bool, list]:
    """验证路径和名称不包含非英文字符"""
    errors = []

    # 检查所有文件名和目录名
    for root, dirs, files in os.walk(skill_path):
        for name in dirs:
            if not all(ord(c) < 128 for c in name):
                errors.append(f"Non-ASCII directory name: {name}")
        for name in files:
            if not all(ord(c) < 128 for c in name):
                errors.append(f"Non-ASCII file name: {name}")

    return len(errors) == 0, errors


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f"Validating skill: {skill_path}")
    print("=" * 50)

    all_passed = True

    # 1. 验证Frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] Frontmatter: {msg}")
    all_passed = all_passed and passed

    # 2. 验证_meta.json
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta JSON: {msg}")
    all_passed = all_passed and passed

    # 3. 验证结构
    passed, errors = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] Structure: {'Valid' if passed else ', '.join(errors)}")
    all_passed = all_passed and passed

    # 4. 验证路径名称
    passed, errors = validate_path_names(skill_path)
    print(f"[{'✓' if passed else '✗'}] Path Names: {'All ASCII' if passed else ', '.join(errors)}")
    all_passed = all_passed and passed

    print("=" * 50)
    print(f"Result: {'ALL PASSED ✓' if all_passed else 'VALIDATION FAILED ✗'}")

    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
