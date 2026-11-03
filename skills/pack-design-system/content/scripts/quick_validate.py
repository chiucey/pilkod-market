#!/usr/bin/env python3
"""
PACK Design System Skill Validation Script
验证技能结构和内容是否符合规范
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证SKILL.md的frontmatter格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.startswith('---'):
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter not properly closed with ---"

    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    required_fields = ['name', 'description']
    missing_fields = []
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        return False, f"Missing required frontmatter fields: {', '.join(missing_fields)}"

    # 验证name格式（连字符）
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"name '{name}' must use hyphen-case (lowercase with hyphens only)"

    # 检查是否有markdown标题在frontmatter之前
    for line in lines[:frontmatter_end+1]:
        if line.strip().startswith('#'):
            return False, "No markdown headings allowed before frontmatter closes"

    return True, "Frontmatter validation passed"

def validate_meta_json(meta_path):
    """验证_meta.json格式"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_keys = ['id', 'version']
        missing_keys = [k for k in required_keys if k not in meta]

        if missing_keys:
            return False, f"Missing required keys in _meta.json: {', '.join(missing_keys)}"

        # 验证version格式
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            return False, f"version '{meta['version']}' must follow semantic versioning (e.g., 1.0.0)"

        return True, "_meta.json validation passed"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in _meta.json: {e}"
    except Exception as e:
        return False, f"Error reading _meta.json: {e}"

def validate_directory_structure(skill_dir):
    """验证目录结构"""
    expected_dirs = []
    for item in ['references', 'scripts', 'assets']:
        path = Path(skill_dir) / item
        if path.exists() and path.is_dir():
            expected_dirs.append(item)

    return True, f"Directory structure valid (found: {', '.join(expected_dirs) if expected_dirs else 'core files only'})"

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md_path = skill_dir / 'SKILL.md'
    meta_path = skill_dir / '_meta.json'

    print("=" * 60)
    print("PACK Design System Skill Validation")
    print("=" * 60)

    all_passed = True

    # 验证SKILL.md frontmatter
    print("\n[1/3] Validating SKILL.md frontmatter...")
    passed, msg = validate_frontmatter(skill_md_path)
    print(f"      {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    # 验证_meta.json
    print("\n[2/3] Validating _meta.json...")
    if meta_path.exists():
        passed, msg = validate_meta_json(meta_path)
        print(f"      {'✓' if passed else '✗'} {msg}")
        all_passed = all_passed and passed
    else:
        print(f"      ✗ _meta.json not found")
        all_passed = False

    # 验证目录结构
    print("\n[3/3] Validating directory structure...")
    passed, msg = validate_directory_structure(skill_dir)
    print(f"      {'✓' if passed else '✗'} {msg}")
    all_passed = all_passed and passed

    print("\n" + "=" * 60)
    if all_passed:
        print("All validations PASSED ✓")
        return 0
    else:
        print("Some validations FAILED ✗")
        return 1

if __name__ == '__main__':
    sys.exit(main())
