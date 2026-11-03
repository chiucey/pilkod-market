#!/usr/bin/env python3
"""
技能验证脚本
检查SKILL.md frontmatter格式、文件结构和内容完整性
"""

import os
import re
import json
from pathlib import Path

def validate_frontmatter(skill_dir):
    """验证SKILL.md的frontmatter格式"""
    skill_md = Path(skill_dir) / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md not found"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否是---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return False, f"SKILL.md must start with '---', found: {lines[0][:50]}"

    # 提取frontmatter
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        return False, "Frontmatter not properly closed with '---'"

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 检查必需字段
    if 'name:' not in frontmatter_text:
        return False, "Missing 'name:' field in frontmatter"

    if 'description:' not in frontmatter_text:
        return False, "Missing 'description:' field in frontmatter"

    # 检查name和description是否在---之前有标题
    content_after_frontmatter = '\n'.join(lines[frontmatter_end+1:])
    if content_after_frontmatter.strip().startswith('#'):
        # 允许第一个是标题
        pass

    return True, "Frontmatter validation passed"

def validate_meta_json(skill_dir):
    """验证_meta.json文件"""
    meta_file = Path(skill_dir) / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            return False, "Missing 'id' in _meta.json"

        if 'version' not in meta:
            return False, "Missing 'version' in _meta.json"

        return True, "_meta.json validation passed"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in _meta.json: {e}"

def validate_skill_name(skill_dir):
    """验证技能名称"""
    skill_md = Path(skill_dir) / "SKILL.md"
    # 使用resolve()获取绝对路径再取name，避免相对路径问题
    folder_name = Path(skill_dir).resolve().name

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取frontmatter
    lines = content.split('\n')
    frontmatter_end = 0
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            frontmatter_end = i
            break

    frontmatter_text = '\n'.join(lines[1:frontmatter_end])

    # 提取name字段
    name_match = re.search(r'name:\s*(.+)', frontmatter_text)
    if name_match:
        skill_name = name_match.group(1).strip()
        if skill_name != folder_name:
            return False, f"Skill name '{skill_name}' doesn't match folder name '{folder_name}'"

    return True, "Skill name validation passed"

def validate_folder_structure(skill_dir):
    """验证文件夹结构"""
    skill_path = Path(skill_dir)

    # 检查必需文件
    if not (skill_path / "SKILL.md").exists():
        return False, "Missing SKILL.md"

    if not (skill_path / "_meta.json").exists():
        return False, "Missing _meta.json"

    return True, "Folder structure validation passed"

def main():
    import sys

    if len(sys.argv) < 2:
        skill_dir = "."
    else:
        skill_dir = sys.argv[1]

    validations = [
        ("Folder Structure", validate_folder_structure),
        ("Frontmatter Format", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
        ("Skill Name", validate_skill_name),
    ]

    all_passed = True
    for name, func in validations:
        passed, message = func(skill_dir)
        status = "✓" if passed else "✗"
        print(f"[{status}] {name}: {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All validations passed!")
        return 0
    else:
        print("\n✗ Some validations failed")
        return 1

if __name__ == "__main__":
    exit(main())
