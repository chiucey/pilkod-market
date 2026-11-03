# -*- coding: utf-8 -*-
"""
技能验证脚本 - 检查技能结构和frontmatter
"""

import os
import sys
import json
import re


def validate_skill(skill_dir: str) -> tuple[bool, list]:
    """
    验证技能结构和frontmatter

    Returns:
        (是否通过, 错误列表)
    """
    errors = []

    # 检查SKILL.md是否存在
    skill_md_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("缺少 SKILL.md 文件")
        return False, errors

    # 读取SKILL.md内容
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在文件开头
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")

    # 解析frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 frontmatter，请检查格式")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)
    frontmatter = {}

    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # 检查必填字段
    if 'name' not in frontmatter:
        errors.append("frontmatter 缺少 'name' 字段")

    if 'description' not in frontmatter:
        errors.append("frontmatter 缺少 'description' 字段")

    # 检查name格式
    name = frontmatter.get('name', '')
    if name and not re.match(r'^[a-z0-9-]+$', name):
        errors.append(f"name 格式不正确，应为小写字母、数字、连字符: '{name}'")

    # 检查_meta.json是否存在
    meta_path = os.path.join(skill_dir, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 'id' 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 'version' 字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查目录结构
    skills_dir = os.path.join(skill_dir, "skills")
    if not os.path.exists(skills_dir):
        errors.append("缺少 skills 目录")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_dir>")
        sys.exit(1)

    skill_dir = sys.argv[1]

    if not os.path.exists(skill_dir):
        print(f"错误: 目录不存在: {skill_dir}")
        sys.exit(1)

    success, errors = validate_skill(skill_dir)

    if success:
        print("✓ 技能验证通过")
        sys.exit(0)
    else:
        print("✗ 技能验证失败:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()