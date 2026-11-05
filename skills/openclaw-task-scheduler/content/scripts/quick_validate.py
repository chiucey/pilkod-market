#!/usr/bin/env python3
"""快速验证脚本 - 检查技能结构和frontmatter"""

import os
import sys
import json
import re
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """验证技能结构"""
    errors = []
    skill_path = Path(skill_path)

    # 检查目录是否存在
    if not skill_path.exists():
        return False, [f"技能目录不存在: {skill_path}"]

    # 检查SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("缺少SKILL.md文件")
        return False, errors

    # 读取SKILL.md内容
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 验证1: frontmatter必须在第一行
    if not content.startswith('---'):
        errors.append("SKILL.md必须以frontmatter(---)开头，不能有markdown标题在前")

    # 验证2: 解析frontmatter
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析frontmatter，请检查格式")
    else:
        fm_content = frontmatter_match.group(1)

        # 验证必填字段
        if 'name:' not in fm_content:
            errors.append("frontmatter缺少name字段")
        if 'description:' not in fm_content:
            errors.append("frontmatter缺少description字段")

        # 提取name
        name_match = re.search(r'^name:\s*(.+)$', fm_content, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            # 验证name格式
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"name字段格式错误，应使用连字符格式: {name}")
            # 验证name与目录名匹配
            dir_name = skill_path.name
            if name != dir_name:
                errors.append(f"name({name})与目录名({dir_name})不匹配")

    # 验证3: _meta.json
    meta_file = skill_path / "_meta.json"
    if not meta_file.exists():
        errors.append("缺少_meta.json文件")
    else:
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json格式错误: {e}")

    return len(errors) == 0, errors

def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."

    print(f"验证技能: {skill_path}")
    print("-" * 50)

    valid, errors = validate_skill(skill_path)

    if valid:
        print("✅ 验证通过")
        return 0
    else:
        print("❌ 验证失败:")
        for error in errors:
            print(f"  - {error}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
