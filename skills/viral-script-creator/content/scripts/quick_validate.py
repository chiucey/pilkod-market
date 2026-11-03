#!/usr/bin/env python3
"""
Viral Script Creator - Skill Validator
验证 SKILL.md 格式和结构
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> tuple[bool, str]:
    """验证 frontmatter 格式"""
    sk_path = skill_path / "SKILL.md"
    if not sk_path.exists():
        return False, f"{sk_path} not found"

    content = sk_path.read_text(encoding='utf-8')

    # 检查是否以 --- 开头
    if not content.startswith('---'):
        return False, "SKILL.md must start with frontmatter (---)"

    # 提取 frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter = match.group(1)

    # 检查必填字段
    if 'name:' not in frontmatter:
        return False, "Missing 'name:' field in frontmatter"

    if 'description:' not in frontmatter:
        return False, "Missing 'description:' field in frontmatter"

    # 验证 name 格式（连字符）
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' must use hyphen-case"

    # 验证 description 包含触发短语
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if 'Use when' not in desc and '当用户' not in desc:
            return False, "Description must include trigger phrase"

    return True, "Frontmatter validation passed"


def validate_meta(skill_path: Path) -> tuple[bool, str]:
    """验证 _meta.json 格式"""
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        return False, "_meta.json not found"

    import json
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in _meta.json: {e}"

    if 'id' not in meta:
        return False, "Missing 'id' field in _meta.json"
    if 'version' not in meta:
        return False, "Missing 'version' field in _meta.json"

    return True, "Meta validation passed"


def validate_structure(skill_path: Path) -> tuple[bool, str]:
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_path / f).exists():
            return False, f"Missing required file: {f}"
    return True, "Structure validation passed"


def main():
    skill_path = Path(__file__).parent.parent.resolve()
    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    passed, msg = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] Structure: {msg}")
    all_passed = all_passed and passed

    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] Frontmatter: {msg}")
    all_passed = all_passed and passed

    passed, msg = validate_meta(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta: {msg}")
    all_passed = all_passed and passed

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
