#!/usr/bin/env python3
"""
快速验证脚本 - 检查技能结构和Frontmatter格式
"""

import os
import re
import json
import sys

def validate_skill(skill_path: str) -> Tuple[bool, List[str]]:
    """
    验证技能文件结构

    Returns:
        (is_valid, error_messages)
    """
    errors = []
    warnings = []

    # 检查SKILL.md是否存在
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md not found")
        return False, errors

    # 读取SKILL.md内容
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查Frontmatter格式
    frontmatter_pattern = r'^---\n(.*?)\n---'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("Frontmatter not found or invalid format. Must start with '---' at line 1")
        return False, errors

    frontmatter_content = match.group(1)

    # 解析YAML
    try:
        import yaml
        fm_dict = yaml.safe_load(frontmatter_content)
    except:
        errors.append("Frontmatter YAML parsing failed")
        return False, errors

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in fm_dict:
            errors.append(f"Missing required field: {field}")

    # 检查name格式
    if 'name' in fm_dict:
        name = fm_dict['name']
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"Invalid name format: '{name}'. Must be lowercase with hyphens only")

        # 检查name与文件夹名称是否匹配
        folder_name = os.path.basename(skill_path)
        if name != folder_name:
            errors.append(f"Name mismatch: folder is '{folder_name}', frontmatter name is '{name}'")

    # 检查description是否包含触发短语
    if 'description' in fm_dict:
        desc = fm_dict['description']
        if len(desc) < 20:
            warnings.append("Description is too short, should include trigger phrases")
        if 'Use when' not in desc and '当用户' not in desc:
            warnings.append("Description should contain trigger phrases like 'Use when...' or '当用户...'")

    # 检查_meta.json是否存在
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("_meta.json not found")
    else:
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError:
            errors.append("_meta.json is not valid JSON")

    # 检查文件结构
    expected_dirs = []
    for dir_name in expected_dirs:
        dir_path = os.path.join(skill_path, dir_name)
        if os.path.exists(dir_path):
            warnings.append(f"Unnecessary directory found: {dir_name}")

    return len(errors) == 0, errors + warnings

def main():
    import argparse
    from typing import Tuple

    parser = argparse.ArgumentParser(description='Validate skill structure')
    parser.add_argument('skill_path', help='Path to skill directory')
    args = parser.parse_args()

    is_valid, messages = validate_skill(args.skill_path)

    print(f"Validation {'PASSED' if is_valid else 'FAILED'}")
    print("-" * 50)

    for msg in messages:
        prefix = "ERROR" if msg.startswith("ERROR") or "not found" in msg or "missing" in msg or "Invalid" in msg else "WARNING"
        print(f"[{prefix}] {msg}")

    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
