#!/usr/bin/env python3
"""
stock-analysis-pro 技能验证脚本
"""

import os
import sys
import re
import json
from pathlib import Path


def validate_frontmatter(skill_dir: str) -> tuple:
    """验证frontmatter格式"""
    errors = []
    skill_md = Path(skill_dir) / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    if not lines[0].strip().startswith('---'):
        errors.append("SKILL.md must start with --- in first line")

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

        if 'name:' not in frontmatter_text:
            errors.append("Missing 'name:' field")
        if 'description:' not in frontmatter_text:
            errors.append("Missing 'description:' field")

        name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
        if name_match:
            name_value = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name_value):
                errors.append(f"Invalid name format: '{name_value}'")

    return len(errors) == 0, errors


def validate_meta_json(skill_dir: str) -> tuple:
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

    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_dir: str) -> tuple:
    """验证目录结构"""
    errors = []
    required_dirs = ['src', 'tests', 'config', 'references', 'scripts', 'instructions', 'assets']
    required_files = ['SKILL.md', '_meta.json', 'src/main.py', 'tests/test_main.py']

    for d in required_dirs:
        if not Path(skill_dir, d).exists():
            errors.append(f"Missing directory: {d}")

    for f in required_files:
        if not Path(skill_dir, f).exists():
            errors.append(f"Missing file: {f}")

    return len(errors) == 0, errors


def main():
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    all_errors = []

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
