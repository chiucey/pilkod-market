#!/usr/bin/env python3
"""
技能验证脚本 - 验证 SKILL.md 和目录结构
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Tuple, List


def validate_frontmatter(skill_md_path: str) -> Tuple[bool, List[str]]:
    """验证 frontmatter 格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")
        return False, errors

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    # 解析 frontmatter
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key = line.split(':')[0].strip()
            frontmatter[key] = True

    # 检查必填字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Frontmatter 缺少必填字段: {field}")

    # 检查 name 格式（连字符、小写）
    if 'name' in frontmatter:
        name = None
        for line in frontmatter_lines:
            if line.startswith('name:'):
                name = line.split(':', 1)[1].strip()
                break

        if name:
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"name 必须使用小写字母和连字符: {name}")

            # 检查与文件夹名称是否匹配
            folder_name = Path(skill_md_path).parent.name
            if name != folder_name:
                errors.append(f"name ({name}) 与文件夹名称 ({folder_name}) 不匹配")

    # 检查 description 是否包含触发短语
    if 'description' in frontmatter:
        desc = None
        for line in frontmatter_lines:
            if line.startswith('description:'):
                desc = line.split(':', 1)[1].strip()
                break

        if desc and 'Use when' not in desc and '当用户' not in desc:
            errors.append("description 应包含触发短语 (Use when... / 当用户...)")

    return len(errors) == 0, errors


def validate_meta_json(meta_path: str) -> Tuple[bool, List[str]]:
    """验证 _meta.json 格式"""
    errors = []
    import json

    if not os.path.exists(meta_path):
        errors.append("_meta.json 文件不存在")
        return False, errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 检查必填字段
        if 'id' not in meta:
            errors.append("_meta.json 缺少 id 字段")
        elif not isinstance(meta['id'], int):
            errors.append("_meta.json id 必须是整数")

        if 'version' not in meta:
            errors.append("_meta.json 缺少 version 字段")
        elif not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append("_meta.json version 必须符合语义化版本格式 (x.y.z)")

    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 解析错误: {e}")

    return len(errors) == 0, errors


def validate_structure(skill_dir: str) -> Tuple[bool, List[str]]:
    """验证目录结构"""
    errors = []
    skill_path = Path(skill_dir)

    # 检查 SKILL.md
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        errors.append("SKILL.md 文件不存在")

    # 检查 _meta.json
    meta_json = skill_path / '_meta.json'
    if not meta_json.exists():
        errors.append("_meta.json 文件不存在")

    # 检查 scripts 目录（可选但建议有）
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        # 检查脚本文件是否为有效 Python 文件
        for script in scripts_dir.glob('*.py'):
            if script.name != '__init__.py':
                # 尝试编译检查
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        compile(f.read(), script.name, 'exec')
                except SyntaxError as e:
                    errors.append(f"脚本 {script.name} 语法错误: {e}")

    return len(errors) == 0, errors


def main():
    import argparse
    from typing import Tuple, List

    parser = argparse.ArgumentParser(description='验证技能结构')
    parser.add_argument('skill_path', help='技能目录路径')

    args = parser.parse_args()

    skill_path = Path(args.skill_path)

    print(f"验证技能: {skill_path}")
    print("=" * 50)

    all_passed = True

    # 验证 frontmatter
    print("\n[1] 验证 Frontmatter...")
    skill_md = skill_path / 'SKILL.md'
    if skill_md.exists():
        passed, errors = validate_frontmatter(str(skill_md))
        if passed:
            print("    ✓ Frontmatter 格式正确")
        else:
            print("    ✗ Frontmatter 验证失败:")
            for err in errors:
                print(f"      - {err}")
            all_passed = False
    else:
        print("    ✗ SKILL.md 不存在")
        all_passed = False

    # 验证 _meta.json
    print("\n[2] 验证 _meta.json...")
    meta_json = skill_path / '_meta.json'
    passed, errors = validate_meta_json(str(meta_json))
    if passed:
        print("    ✓ _meta.json 格式正确")
    else:
        print("    ✗ _meta.json 验证失败:")
        for err in errors:
            print(f"      - {err}")
        all_passed = False

    # 验证目录结构
    print("\n[3] 验证目录结构...")
    passed, errors = validate_structure(str(skill_path))
    if passed:
        print("    ✓ 目录结构完整")
    else:
        print("    ✗ 目录结构验证失败:")
        for err in errors:
            print(f"      - {err}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过")
        return 0
    else:
        print("✗ 存在验证错误")
        return 1


if __name__ == '__main__':
    sys.exit(main())
