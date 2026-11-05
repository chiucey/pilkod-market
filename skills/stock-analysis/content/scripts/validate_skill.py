#!/usr/bin/env python3
"""
股票分析技能验证脚本
验证技能文件结构和frontmatter格式
"""

import os
import sys
import re
import json
from pathlib import Path

def validate_frontmatter(skill_dir: str) -> tuple[bool, list[str]]:
    """验证frontmatter格式"""
    errors = []
    skill_md = Path(skill_dir) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否为---
    lines = content.split('\n')
    if not lines[0].strip().startswith('---'):
        errors.append("SKILL.md must start with --- in first line")

    # 提取frontmatter
    if lines[0].strip() == '---':
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx is None:
            errors.append("Frontmatter closing --- not found")
            return False, errors

        frontmatter_text = '\n'.join(lines[1:end_idx])

        # 验证必需字段
        if 'name:' not in frontmatter_text:
            errors.append("Missing 'name:' field in frontmatter")

        if 'description:' not in frontmatter_text:
            errors.append("Missing 'description:' field in frontmatter")

        # 验证name格式
        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name_value):
                errors.append(f"Invalid name format: '{name_value}'. Use lowercase with hyphens only")
            if len(name_value) > 64:
                errors.append(f"Name too long: {len(name_value)} chars (max 64)")

    return len(errors) == 0, errors

def validate_meta_json(skill_dir: str) -> tuple[bool, list[str]]:
    """验证_meta.json"""
    errors = []
    meta_file = Path(skill_dir) / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("Missing 'id' in _meta.json")

        if 'version' not in meta:
            errors.append("Missing 'version' in _meta.json")

        # 验证version格式
        if 'version' in meta:
            version = meta['version']
            if not re.match(r'^\d+\.\d+\.\d+$', version):
                errors.append(f"Invalid version format: '{version}'. Use semver (e.g., 1.0.0)")

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")

    return len(errors) == 0, errors

def validate_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查目录名是否与skill name一致
    skill_md = Path(skill_dir) / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取name
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            expected_name = name_match.group(1).strip()
            dir_name = Path(skill_dir).name

            if dir_name != expected_name:
                errors.append(f"Directory name '{dir_name}' doesn't match skill name '{expected_name}'")

    # 验证文件名无中文和特殊字符
    for root, dirs, files in os.walk(skill_dir):
        for f in files:
            if not re.match(r'^[a-zA-Z0-9_.-]+$', f):
                errors.append(f"Invalid filename: {f} (use English only)")

    return len(errors) == 0, errors

def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    all_errors = []

    # 执行各项验证
    checks = [
        ("Frontmatter", validate_frontmatter),
        ("_meta.json", validate_meta_json),
        ("Directory Structure", validate_structure),
    ]

    all_passed = True
    for check_name, check_func in checks:
        passed, errors = check_func(skill_dir)
        if not passed:
            all_passed = False
            all_errors.append(f"\n{check_name} Errors:")
            all_errors.extend([f"  - {e}" for e in errors])

    if all_passed:
        print(f"✓ All validations passed for {skill_dir}")
        return 0
    else:
        print("✗ Validation failed:")
        for error in all_errors:
            print(error)
        return 1

if __name__ == "__main__":
    sys.exit(main())
