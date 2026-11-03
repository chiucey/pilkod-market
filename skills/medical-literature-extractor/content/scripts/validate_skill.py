#!/usr/bin/env python3
"""
医学文献提取器 - 技能验证脚本
验证SKILL.md格式和元数据的正确性
"""

import json
import os
from pathlib import Path

def validate_frontmatter(content: str) -> tuple[bool, str]:
    """验证frontmatter格式"""
    if not content.startswith('---'):
        return False, "SKILL.md必须以---开头"

    lines = content.split('\n')
    if len(lines) < 4:
        return False, "frontmatter不完整"

    # 找到第二个---
    second_dash = content.find('---', 3)
    if second_dash == -1:
        return False, "frontmatter未正确闭合"

    frontmatter_str = content[3:second_dash].strip()

    # 解析YAML简单检查
    required_fields = ['name:', 'description:']
    for field in required_fields:
        if field not in frontmatter_str:
            return False, f"缺少必需字段: {field}"

    return True, "frontmatter验证通过"


def validate_meta(meta_path: Path) -> tuple[bool, str]:
    """验证_meta.json"""
    if not meta_path.exists():
        return False, "_meta.json不存在"

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            return False, "_meta.json缺少id字段"
        if 'version' not in meta:
            return False, "_meta.json缺少version字段"

        return True, "_meta.json验证通过"
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"


def validate_structure(skill_dir: Path) -> tuple[bool, str]:
    """验证目录结构"""
    required_files = ['SKILL.md', '_meta.json']
    for fname in required_files:
        fpath = skill_dir / fname
        if not fpath.exists():
            return False, f"缺少必需文件: {fname}"

    return True, "目录结构验证通过"


def main():
    skill_dir = Path(__file__).parent.parent

    print(f"验证技能目录: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # 1. 验证目录结构
    passed, msg = validate_structure(skill_dir)
    print(f"✓ {msg}" if passed else f"✗ {msg}")
    all_passed = all_passed and passed

    # 2. 验证_meta.json
    passed, msg = validate_meta(skill_dir / '_meta.json')
    print(f"✓ {msg}" if passed else f"✗ {msg}")
    all_passed = all_passed and passed

    # 3. 验证SKILL.md
    skill_md = skill_dir / 'SKILL.md'
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    passed, msg = validate_frontmatter(content)
    print(f"✓ {msg}" if passed else f"✗ {msg}")
    all_passed = all_passed and passed

    # 4. 检查name字段与目录名一致性
    lines = content.split('\n')
    for line in lines:
        if line.startswith('name:'):
            skill_name = line.split(':', 1)[1].strip()
            dir_name = skill_dir.name
            if skill_name != dir_name:
                print(f"⚠ name字段('{skill_name}')与目录名('{dir_name}')不一致")
            else:
                print(f"✓ name字段与目录名一致")
            break

    print("-" * 50)
    if all_passed:
        print("✅ 所有验证通过！")
        return 0
    else:
        print("❌ 存在验证失败项")
        return 1


if __name__ == '__main__':
    exit(main())
