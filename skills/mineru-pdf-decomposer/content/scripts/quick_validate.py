#!/usr/bin/env python3
"""MinerU PDF 分解技能快速验证脚本"""

import os
import re
import sys

def validate_frontmatter(skill_path):
    """验证 frontmatter 格式"""
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        return False, "SKILL.md not found"

    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查第一行必须是 ---
    lines = content.split("\n")
    if not lines[0].strip() == "---":
        return False, "SKILL.md must start with --- (frontmatter delimiter)"

    # 检查 frontmatter 结构
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return False, "Invalid frontmatter format"

    frontmatter = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ["name", "description"]
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
            return False, f"Missing required field: {field}"

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, "name must be lowercase with hyphens only"

    return True, "Frontmatter validation passed"

def validate_meta(skill_path):
    """验证 _meta.json 格式"""
    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    import json
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    required_fields = ["id", "version"]
    for field in required_fields:
        if field not in meta:
            return False, f"Missing required field in _meta.json: {field}"

    return True, "_meta.json validation passed"

def validate_directory_structure(skill_path):
    """验证目录结构"""
    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        if not os.path.exists(os.path.join(skill_path, file)):
            return False, f"Missing required file: {file}"

    return True, "Directory structure valid"

def main():
    skill_path = os.path.dirname(os.path.abspath(__file__)).replace("/scripts", "")

    validations = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta),
        ("Directory Structure", validate_directory_structure),
    ]

    all_passed = True
    for name, validator in validations:
        passed, message = validator(skill_path)
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nAll validations passed!")
        sys.exit(0)
    else:
        print("\nValidation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()