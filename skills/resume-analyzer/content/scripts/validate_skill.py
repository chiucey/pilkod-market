#!/usr/bin/env python3
"""验证技能结构和frontmatter格式"""

import os
import json
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter格式"""
    skill_md = Path(skill_path) / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding='utf-8')

    # 检查frontmatter是否在文件开头
    if not content.startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Invalid frontmatter format"

    frontmatter_content = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_content, re.MULTILINE):
            return False, f"Missing required frontmatter field: {field}"

    return True, "Valid frontmatter"

def validate_meta(skill_path):
    """验证_meta.json格式"""
    meta_file = Path(skill_path) / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))

        # 检查必需字段
        if 'id' not in meta:
            return False, "Missing required field: id"
        if 'version' not in meta:
            return False, "Missing required field: version"

        # 验证ID是整数
        if not isinstance(meta['id'], int):
            return False, "Field 'id' must be an integer"

        return True, "Valid meta"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

def validate_naming(skill_path):
    """验证命名规范"""
    skill_name = Path(skill_path).name

    # 检查是否使用连字符格式
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        return False, "Skill name must use hyphen-case (lowercase with hyphens)"

    # 检查长度
    if len(skill_name) > 64:
        return False, "Skill name must be <= 64 characters"

    return True, "Valid naming"

def validate_skill(skill_path):
    """执行所有验证"""
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("Meta", validate_meta),
        ("Naming", validate_naming),
    ]

    all_passed = True
    results = []

    for name, validator in validations:
        passed, message = validator(skill_path)
        results.append(f"[{'✅' if passed else '❌'}] {name}: {message}")
        if not passed:
            all_passed = False

    return all_passed, "\n".join(results)

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    passed, results = validate_skill(skill_path)
    print(results)
    print(f"\n{'✅ All validations passed!' if passed else '❌ Validation failed'}")
    sys.exit(0 if passed else 1)
