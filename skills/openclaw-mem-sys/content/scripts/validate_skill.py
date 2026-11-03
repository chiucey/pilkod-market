#!/usr/bin/env python3
"""
OpenClaw Memory System Skill Validation Script
验证 SKILL.md 和 _meta.json 的结构和内容
"""

import os
import re
import sys
import json
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter"""
    errors = []
    warnings = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md must start with frontmatter (---)")
        return errors, warnings

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Cannot parse frontmatter")
        return errors, warnings

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    if not re.search(r'^name:', frontmatter_text, re.MULTILINE):
        errors.append("Missing 'name' field in frontmatter")

    if not re.search(r'^description:', frontmatter_text, re.MULTILINE):
        errors.append("Missing 'description' field in frontmatter")

    # 检查 description 是否包含触发短语
    desc_match = re.search(r'description:\s*["\'](.*?)["\']', frontmatter_text, re.DOTALL)
    if desc_match:
        desc = desc_match.group(1)
        # 检查是否包含中文触发短语
        trigger_keywords = ['触发', '使用', '当用户', '询问', '搜索', '查询', '记忆']
        has_triggers = any(kw in desc for kw in trigger_keywords)
        if not has_triggers:
            warnings.append("Description should include trigger phrases in Chinese")

    # 检查 frontmatter 长度
    if len(frontmatter_text) > 500:
        warnings.append("Frontmatter is quite long, consider simplifying")

    return errors, warnings


def validate_meta_json(meta_path):
    """验证 _meta.json"""
    errors = []
    warnings = []

    if not os.path.exists(meta_path):
        errors.append("_meta.json does not exist")
        return errors, warnings

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in _meta.json: {e}")
        return errors, warnings

    # 检查必需字段
    required_fields = ['id', 'name', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"Missing required field '{field}' in _meta.json")

    # 检查 id 是否为整数
    if 'id' in meta:
        if not isinstance(meta['id'], int):
            errors.append("'id' must be an integer")

    # 检查 version 格式
    if 'version' in meta:
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, meta['version']):
            errors.append(f"Version should follow semver format (e.g., 1.0.0), got: {meta['version']}")

    return errors, warnings


def validate_directory_structure(skill_dir):
    """验证目录结构"""
    errors = []
    warnings = []

    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        path = os.path.join(skill_dir, file)
        if not os.path.exists(path):
            errors.append(f"Missing required file: {file}")

    return errors, warnings


def main():
    skill_dir = Path(__file__).parent.parent
    skill_md_path = skill_dir / 'SKILL.md'
    meta_path = skill_dir / '_meta.json'

    print(f"Validating skill at: {skill_dir}")
    print("=" * 50)

    all_errors = []
    all_warnings = []

    # 验证 frontmatter
    print("\n[1/3] Validating frontmatter...")
    errors, warnings = validate_frontmatter(skill_md_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    if not errors and not warnings:
        print("  OK - Frontmatter is valid")

    # 验证 _meta.json
    print("\n[2/3] Validating _meta.json...")
    errors, warnings = validate_meta_json(meta_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    if not errors and not warnings:
        print("  OK - _meta.json is valid")

    # 验证目录结构
    print("\n[3/3] Validating directory structure...")
    errors, warnings = validate_directory_structure(skill_dir)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    if warnings:
        for w in warnings:
            print(f"  WARNING: {w}")
    if not errors and not warnings:
        print("  OK - Directory structure is valid")

    # 输出总结
    print("\n" + "=" * 50)
    if all_errors:
        print(f"VALIDATION FAILED: {len(all_errors)} error(s)")
        return 1
    elif all_warnings:
        print(f"VALIDATION PASSED with {len(all_warnings)} warning(s)")
        return 0
    else:
        print("VALIDATION PASSED")
        return 0


if __name__ == '__main__':
    sys.exit(main())
