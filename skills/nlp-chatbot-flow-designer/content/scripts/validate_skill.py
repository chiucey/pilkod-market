#!/usr/bin/env python3
"""
NLP Chatbot Flow Designer - Skill Validator
验证技能的frontmatter、结构完整性和命名规范
"""

import os
import re
import sys
import json
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """验证SKILL.md的frontmatter格式"""
    errors = []
    skill_file = skill_path / "SKILL.md"

    if not skill_file.exists():
        return False, ["SKILL.md file not found"]

    content = skill_file.read_text(encoding='utf-8')

    # 检查frontmatter位置 - 必须在第一行
    if not content.startswith('---'):
        errors.append("Frontmatter must start at the very beginning (before any # headings)")
        return False, errors

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if i == 0:
            continue  # 跳过第一个 ---
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Frontmatter closing '---' not found")
        return False, errors

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必填字段
    if 'name:' not in frontmatter_text and 'name :' not in frontmatter_text:
        errors.append("Missing required field: 'name' in frontmatter")

    if 'description:' not in frontmatter_text and 'description :' not in frontmatter_text:
        errors.append("Missing required field: 'description' in frontmatter")

    # 检查name格式
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Name '{name}' must be lowercase with hyphens only (hyphen-case)")
        if len(name) > 64:
            errors.append(f"Name '{name}' exceeds 64 character limit")

    return len(errors) == 0, errors

def validate_meta_json(skill_path: Path) -> tuple[bool, list[str]]:
    """验证_meta.json的有效性"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json file not found"]

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, [f"_meta.json is not valid JSON: {e}"]

    # 检查必填字段
    if 'id' not in meta:
        errors.append("Missing required field: 'id' in _meta.json")

    if 'version' not in meta:
        errors.append("Missing required field: 'version' in _meta.json")

    return len(errors) == 0, errors

def validate_directory_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """验证目录结构"""
    errors = []

    # 检查顶层结构
    required_dirs = []
    optional_dirs = ['scripts', 'references', 'assets']

    for dir_name in required_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            errors.append(f"Missing required directory: {dir_name}")

    for dir_name in optional_dirs:
        dir_path = skill_path / dir_name
        if not dir_path.exists():
            print(f"[INFO] Optional directory '{dir_name}' not found (optional)")

    return len(errors) == 0, errors

def validate_file_paths(skill_path: Path) -> tuple[bool, list[str]]:
    """验证文件路径不包含非ASCII字符"""
    errors = []

    for root, dirs, files in os.walk(skill_path):
        for d in dirs:
            if not re.match(r'^[a-zA-Z0-9_-]+$', d):
                errors.append(f"Non-ASCII/non-compliant directory name: {d}")

        for f in files:
            if not re.match(r'^[a-zA-Z0-9_.-]+$', f):
                errors.append(f"Non-ASCII/non-compliant file name: {f}")

    return len(errors) == 0, errors

def main():
    skill_path = Path(__file__).parent.parent.resolve()

    print(f"Validating skill at: {skill_path}")
    print("=" * 50)

    all_errors = []

    # 执行各项验证
    checks = [
        ("Frontmatter & Structure", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
        ("Directory Structure", validate_directory_structure),
        ("File Path Naming", validate_file_paths),
    ]

    for check_name, check_func in checks:
        print(f"\n[{check_name}]")
        passed, errors = check_func(skill_path)

        if passed:
            print(f"  ✓ Passed")
        else:
            print(f"  ✗ Failed")
            for err in errors:
                print(f"    - {err}")
            all_errors.extend(errors)

    print("\n" + "=" * 50)

    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s) found")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED: All checks successful")
        sys.exit(0)

if __name__ == "__main__":
    main()