#!/usr/bin/env python3
"""
快速验证脚本 - 检查SKILL.md和_meta.json的结构
"""

import os
import json
import sys


def validate_skill(path: str) -> tuple[bool, list]:
    """验证技能文件结构"""
    errors = []

    # 检查SKILL.md是否存在
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md 文件不存在")
        return False, errors

    # 检查SKILL.md第一行是否是frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        errors.append("SKILL.md 文件为空")
        return False, errors

    if not lines[0].strip().startswith('---'):
        errors.append("SKILL.md 第一行必须是 YAML frontmatter (---)")
        errors.append(f"  实际第一行: {lines[0].strip()}")

    # 检查frontmatter内容
    frontmatter_valid = False
    has_name = False
    has_description = False

    in_frontmatter = False
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_valid = True
                break
        if in_frontmatter and line.startswith('name:'):
            has_name = True
        if in_frontmatter and line.startswith('description:'):
            has_description = True

    if not frontmatter_valid:
        errors.append("SKILL.md 缺少正确的 YAML frontmatter 结束标记 (---)")

    if not has_name:
        errors.append("Frontmatter 缺少 'name' 字段")

    if not has_description:
        errors.append("Frontmatter 缺少 'description' 字段")

    # 检查_meta.json
    meta_json = os.path.join(path, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if "id" not in meta:
            errors.append("_meta.json 缺少 'id' 字段")
        if "version" not in meta:
            errors.append("_meta.json 缺少 'version' 字段")
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON格式错误: {e}")

    return len(errors) == 0, errors


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success, errors = validate_skill(skill_path)

    if success:
        print("✓ 验证通过")
        sys.exit(0)
    else:
        print("✗ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)