#!/usr/bin/env python3
"""
快速验证脚本 - 检查 SKILL.md 和 _meta.json 的基本结构
"""
import json
import os
import sys
import re

def validate_frontmatter(skill_path):
    """验证 SKILL.md frontmatter 格式"""
    skill_file = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_file):
        return False, "SKILL.md not found"

    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查第一行是否是 ---
    lines = content.split('\n')
    if not lines[0].strip() == '---':
        return False, f"SKILL.md must start with ---, found: {lines[0][:50]}"

    # 提取 frontmatter
    fm_end = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            fm_end = i
            break

    if fm_end == -1:
        return False, "Frontmatter closing --- not found"

    fm_text = '\n'.join(lines[1:fm_end])

    # 检查必需字段
    if not re.search(r'^name:', fm_text, re.MULTILINE):
        return False, "Missing 'name:' field in frontmatter"

    if not re.search(r'^description:', fm_text, re.MULTILINE):
        return False, "Missing 'description:' field in frontmatter"

    return True, "Frontmatter valid"

def validate_meta(skill_path):
    """验证 _meta.json 格式"""
    meta_file = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_file):
        return False, "_meta.json not found"

    with open(meta_file, 'r', encoding='utf-8') as f:
        try:
            meta = json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"

    if 'id' not in meta:
        return False, "Missing 'id' field in _meta.json"

    if 'version' not in meta:
        return False, "Missing 'version' field in _meta.json"

    return True, f"Meta valid (id={meta['id']}, version={meta['version']})"

def validate_directory_structure(skill_path):
    """验证目录结构"""
    name = os.path.basename(skill_path)

    # 检查文件夹名称是否与 frontmatter 中的 name 一致
    skill_file = os.path.join(skill_path, "SKILL.md")
    with open(skill_file, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if fm_match:
        frontmatter_name = fm_match.group(1).strip()
        if frontmatter_name != name:
            return False, f"Folder name '{name}' doesn't match frontmatter name '{frontmatter_name}'"

    return True, "Directory structure valid"

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证 frontmatter
    passed, msg = validate_frontmatter(skill_path)
    print(f"[{'✓' if passed else '✗'}] Frontmatter: {msg}")
    if not passed:
        all_passed = False

    # 验证 meta
    passed, msg = validate_meta(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta JSON: {msg}")
    if not passed:
        all_passed = False

    # 验证目录结构
    passed, msg = validate_directory_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] Structure: {msg}")
    if not passed:
        all_passed = False

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()