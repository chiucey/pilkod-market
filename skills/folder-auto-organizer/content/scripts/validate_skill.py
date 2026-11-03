#!/usr/bin/env python3
"""
技能验证脚本 - 检查 SKILL.md 和 _meta.json 的格式规范
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_md_path: str) -> tuple[bool, list[str]]:
    """验证 SKILL.md 的 frontmatter 格式"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查文件开头是否为 frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头 (---)")
        return False, errors

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("SKILL.md 缺少结束的 ---")
        return False, errors

    frontmatter_lines = lines[1:frontmatter_end]

    # 检查必需的字段
    required_fields = ['name', 'description']
    for field in required_fields:
        found = any(line.strip().startswith(f'{field}:') for line in frontmatter_lines)
        if not found:
            errors.append(f"Frontmatter 缺少必需字段: {field}")

    # 检查 name 字段格式
    name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
    if name_match:
        name_value = name_match.group(1).strip()
        # name 应使用连字符格式
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name_value):
            errors.append(f"name 字段格式不正确，应使用连字符格式: '{name_value}'")
        # name 不应包含空格或特殊字符
        if ' ' in name_value:
            errors.append(f"name 字段不应包含空格: '{name_value}'")

    # 检查是否有 markdown 标题在 frontmatter 之前
    markdown_start = content.find('\n---', 3)
    next_content = content[frontmatter_end+1:].strip()
    if next_content.startswith('#'):
        errors.append("Frontmatter 之后不应直接以 markdown 标题 (#) 开头")

    return len(errors) == 0, errors


def validate_meta_json(meta_json_path: str) -> tuple[bool, list[str]]:
    """验证 _meta.json 的格式"""
    errors = []

    if not os.path.exists(meta_json_path):
        errors.append("_meta.json 文件不存在")
        return False, errors

    import json
    try:
        with open(meta_json_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON 格式错误: {e}")
        return False, errors

    # 检查必需的字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必需字段: {field}")

    # 验证 id 是数字
    if 'id' in meta:
        try:
            int(meta['id'])
        except (ValueError, TypeError):
            errors.append(f"_meta.json 'id' 应为数字: {meta['id']}")

    # 验证 version 格式
    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append(f"_meta.json 'version' 格式不正确，应为 x.y.z: {meta['version']}")

    return len(errors) == 0, errors


def validate_structure(skill_dir: str) -> tuple[bool, list[str]]:
    """验证技能目录结构"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = os.path.join(skill_dir, filename)
        if not os.path.exists(filepath):
            errors.append(f"缺少必需文件: {filename}")

    # 检查 SKILL.md 中的路径引用
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否有相对路径引用
        path_patterns = [
            r'\(scripts/[^)]+\)',
            r'\(references/[^)]+\)',
            r'`[^`]*scripts/[^`]*`',
        ]

        for pattern in path_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # 提取路径并验证
                path_match = re.search(r'(scripts|references)/(.+)', match)
                if path_match:
                    dir_name, filename = path_match.groups()
                    referenced_path = os.path.join(skill_dir, dir_name, filename)
                    # 移除末尾的括号或反引号
                    filename = re.sub(r'[)`\]]+$', '', filename)
                    if filename and not os.path.exists(os.path.join(skill_dir, dir_name, filename)):
                        errors.append(f"SKILL.md 引用了不存在的文件: {dir_name}/{filename}")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        skill_dir = os.getcwd()
    else:
        skill_dir = sys.argv[1]

    print(f"验证技能: {skill_dir}")
    print("=" * 50)

    all_passed = True

    # 验证结构
    print("\n[1/3] 检查目录结构...")
    passed, errors = validate_structure(skill_dir)
    if passed:
        print("  ✓ 目录结构验证通过")
    else:
        print("  ✗ 目录结构验证失败:")
        for error in errors:
            print(f"    - {error}")
        all_passed = False

    # 验证 _meta.json
    print("\n[2/3] 检查 _meta.json...")
    meta_path = os.path.join(skill_dir, '_meta.json')
    passed, errors = validate_meta_json(meta_path)
    if passed:
        print("  ✓ _meta.json 验证通过")
    else:
        print("  ✗ _meta.json 验证失败:")
        for error in errors:
            print(f"    - {error}")
        all_passed = False

    # 验证 SKILL.md
    print("\n[3/3] 检查 SKILL.md...")
    skill_md_path = os.path.join(skill_dir, 'SKILL.md')
    passed, errors = validate_frontmatter(skill_md_path)
    if passed:
        print("  ✓ SKILL.md 验证通过")
    else:
        print("  ✗ SKILL.md 验证失败:")
        for error in errors:
            print(f"    - {error}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("✓ 所有验证通过！")
        return 0
    else:
        print("✗ 存在验证错误，请修复后重试")
        return 1


if __name__ == '__main__':
    sys.exit(main())
