#!/usr/bin/env python3
"""
NLP语料生成器技能验证脚本
验证SKILL.md和_meta.json的格式和内容
"""

import os
import sys
import json
from pathlib import Path

def validate_frontmatter(skill_path):
    """验证SKILL.md的frontmatter格式"""
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以---开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md必须以---开头（frontmatter开始标记）"

    # 解析frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        return False, "frontmatter格式不正确"

    # 检查name和description字段
    has_name = False
    has_desc = False
    in_frontmatter = False

    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            if line.strip().startswith('name:'):
                has_name = True
            if line.strip().startswith('description:'):
                has_desc = True

    if not has_name:
        return False, "frontmatter缺少name字段"
    if not has_desc:
        return False, "frontmatter缺少description字段"

    return True, "frontmatter验证通过"

def validate_meta(skill_path):
    """验证_meta.json格式"""
    meta_file = Path(skill_path) / "_meta.json"
    if not meta_file.exists():
        return False, "_meta.json不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            return False, "_meta.json缺少id字段"
        if 'version' not in meta:
            return False, "_meta.json缺少version字段"

        return True, "_meta.json验证通过"
    except json.JSONDecodeError as e:
        return False, f"_meta.json格式错误: {e}"

def validate_structure(skill_path):
    """验证技能目录结构"""
    skill_name = Path(skill_path).name

    # 检查name是否与文件夹名匹配
    meta_file = Path(skill_path) / "_meta.json"
    with open(meta_file, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # 读取SKILL.md获取name
    skill_md = Path(skill_path) / "SKILL.md"
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取name字段值
    lines = content.split('\n')
    in_frontmatter = False
    name_value = None
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and line.strip().startswith('name:'):
            name_value = line.split(':', 1)[1].strip()
            break

    if name_value != skill_name:
        return False, f"name字段({name_value})与文件夹名({skill_name})不匹配"

    return True, "结构验证通过"

def main():
    if len(sys.argv) < 2:
        print("用法: python quick_validate.py <skill_path>")
        sys.exit(1)

    skill_path = sys.argv[1]

    checks = [
        ("Frontmatter验证", validate_frontmatter(skill_path)),
        ("_meta.json验证", validate_meta(skill_path)),
        ("结构验证", validate_structure(skill_path)),
    ]

    all_passed = True
    for name, (passed, msg) in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {msg}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n所有验证通过！")
        sys.exit(0)
    else:
        print("\n验证失败，请修复后重试")
        sys.exit(1)

if __name__ == "__main__":
    main()