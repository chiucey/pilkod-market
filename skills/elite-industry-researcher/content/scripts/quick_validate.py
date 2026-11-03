#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和格式
"""
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter格式"""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在文件开头
    if not content.startswith('---'):
        return False, "SKILL.md must start with --- (frontmatter)"

    # 提取frontmatter (第一行是 ---, 找到第二个 --- 结束)
    lines = content.split('\n')

    # 找到第一个 --- (应该在第0行)
    if len(lines) < 1 or lines[0].strip() != '---':
        return False, "SKILL.md must start with ---"

    # 找到第二个 --- (结束frontmatter)
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "Frontmatter missing closing ---"

    frontmatter_text = '\n'.join(lines[1:end_idx])

    # 检查必需字段
    if 'name:' not in frontmatter_text:
        return False, "Frontmatter missing 'name' field"

    if 'description:' not in frontmatter_text:
        return False, "Frontmatter missing 'description' field"

    # 检查name格式
    name_match = re.search(r'name:\s*(.+)', frontmatter_text)
    if name_match:
        name = name_match.group(1).strip()
        if not name or len(name) > 64:
            return False, f"name must be 1-64 chars, got: {name}"
        if ' ' in name:
            return False, f"name must be hyphen-case, got spaces in: {name}"

    return True, "Frontmatter validation passed"


def validate_meta_json(skill_path):
    """验证_meta.json格式"""
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json not found"

    import json
    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"

    if 'id' not in meta:
        return False, "_meta.json missing 'id'"

    if 'version' not in meta:
        return False, "_meta.json missing 'version'"

    return True, "Meta JSON validation passed"


def validate_structure(skill_path):
    """验证目录结构"""
    required = ['SKILL.md', '_meta.json']
    for item in required:
        if not (skill_path / item).exists():
            return False, f"Missing required file: {item}"

    return True, "Structure validation passed"


def main():
    if len(sys.argv) < 2:
        skill_path = Path(__file__).parent.parent
    else:
        skill_path = Path(sys.argv[1])

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 结构验证
    passed, msg = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] Structure: {msg}")
    all_passed = all_passed and passed

    # frontmatter验证
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] Frontmatter: {msg}")
    all_passed = all_passed and passed

    # meta.json验证
    passed, msg = validate_meta_json(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta JSON: {msg}")
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
