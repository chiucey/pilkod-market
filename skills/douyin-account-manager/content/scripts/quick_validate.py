#!/usr/bin/env python3
"""
技能验证脚本
验证抖音账号管理技能的文件结构和frontmatter格式
"""

import os
import sys
import json
import re
from pathlib import Path


def validate_frontmatter(skill_path: str) -> tuple[bool, list]:
    """
    验证 SKILL.md 的 frontmatter 格式

    Returns:
        (是否通过, 错误列表)
    """
    errors = []
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.exists(skill_md):
        errors.append("SKILL.md 文件不存在")
        return False, errors

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查文件开头是否为 frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 frontmatter (---) 开头")

    # 提取 frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        errors.append("无法解析 frontmatter")
        return False, errors

    fm_content = match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', fm_content, re.MULTILINE):
            errors.append(f"frontmatter 缺少必需字段: {field}")

    # 检查 name 格式
    name_match = re.search(r'^name:\s*(.+)', fm_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 必须使用小写字母、数字和连字符: {name}")

    return len(errors) == 0, errors


def validate_meta(skill_path: str) -> tuple[bool, list]:
    """
    验证 _meta.json 格式

    Returns:
        (是否通过, 错误列表)
    """
    errors = []
    meta_file = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_file):
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("_meta.json 缺少 id 字段")
        if 'version' not in meta:
            errors.append("_meta.json 缺少 version 字段")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json 格式错误: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> tuple[bool, list]:
    """
    验证目录结构

    Returns:
        (是否通过, 错误列表)
    """
    errors = []
    required_dirs = ['scripts', 'references']

    for dir_name in required_dirs:
        dir_path = os.path.join(skill_path, dir_name)
        if not os.path.exists(dir_path):
            errors.append(f"缺少目录: {dir_name}")

    # 检查脚本文件
    scripts_dir = os.path.join(skill_path, "scripts")
    if os.path.exists(scripts_dir):
        py_files = list(Path(scripts_dir).glob("*.py"))
        if len(py_files) == 0:
            errors.append("scripts 目录中缺少 Python 脚本文件")

    return len(errors) == 0, errors


def main():
    skill_path = os.path.dirname(os.path.abspath(__file__)).replace('/scripts', '')

    print("=" * 50)
    print("抖音账号管理技能 - 验证工具")
    print("=" * 50)
    print(f"技能路径: {skill_path}")
    print("-" * 50)

    all_passed = True

    # 验证 frontmatter
    passed, errors = validate_frontmatter(skill_path)
    print(f"\n[{'✓' if passed else '✗'}] Frontmatter 验证: {'通过' if passed else '失败'}")
    for err in errors:
        print(f"    - {err}")
    all_passed = all_passed and passed

    # 验证 meta
    passed, errors = validate_meta(skill_path)
    print(f"[{'✓' if passed else '✗'}] Meta 验证: {'通过' if passed else '失败'}")
    for err in errors:
        print(f"    - {err}")
    all_passed = all_passed and passed

    # 验证结构
    passed, errors = validate_structure(skill_path)
    print(f"[{'✓' if passed else '✗'}] 结构验证: {'通过' if passed else '失败'}")
    for err in errors:
        print(f"    - {err}")
    all_passed = all_passed and passed

    print("\n" + "=" * 50)
    print(f"验证结果: {'✓ 全部通过' if all_passed else '✗ 存在错误'}")
    print("=" * 50)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
