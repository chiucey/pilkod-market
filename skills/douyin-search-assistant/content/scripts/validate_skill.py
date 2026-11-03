#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能验证脚本 - 检查SKILL.md的frontmatter和结构
"""

import os
import re
import json
import sys


def validate_frontmatter(skill_path: str) -> tuple[bool, list]:
    """
    验证SKILL.md的frontmatter

    Returns:
        (是否通过, 错误列表)
    """
    errors = []

    skill_md_path = os.path.join(skill_path, 'SKILL.md')

    if not os.path.exists(skill_md_path):
        return False, [f"SKILL.md 文件不存在: {skill_md_path}"]

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter是否在文件开头
    if content.startswith('#'):
        errors.append("SKILL.md 不能以 markdown 标题 (#) 开头，必须以 YAML frontmatter 开头")

    # 提取frontmatter
    frontmatter_pattern = r'^---\s*\n(.*?)\n---'
    match = re.search(frontmatter_pattern, content, re.DOTALL)

    if not match:
        errors.append("未找到有效的 YAML frontmatter (需要 --- 包裹)")
        return False, errors

    frontmatter_content = match.group(1)

    # 验证必需字段
    if 'name:' not in frontmatter_content:
        errors.append("frontmatter 缺少 'name' 字段")

    if 'description:' not in frontmatter_content:
        errors.append("frontmatter 缺少 'description' 字段")

    # 验证description包含触发短语
    desc_pattern = r"description:\s*(.+)"
    desc_match = re.search(desc_pattern, frontmatter_content)
    if desc_match:
        description = desc_match.group(1)
        trigger_keywords = ['抖音', '搜索', '统计', 'Excel', '关键词']
        has_trigger = any(kw in description for kw in trigger_keywords)
        if not has_trigger:
            errors.append("description 应包含触发短语，如'抖音搜索'、'关键词统计'等")

    # 检查name格式（连字符）
    name_pattern = r"name:\s*([^\n]+)"
    name_match = re.search(name_pattern, frontmatter_content)
    if name_match:
        name = name_match.group(1).strip()
        if ' ' in name:
            errors.append(f"name 应使用连字符格式(如 my-skill)，当前: {name}")
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 应只包含小写字母、数字和连字符，当前: {name}")

    return len(errors) == 0, errors


def validate_meta_json(skill_path: str) -> tuple[bool, list]:
    """
    验证 _meta.json 文件

    Returns:
        (是否通过, 错误列表)
    """
    errors = []

    meta_path = os.path.join(skill_path, '_meta.json')

    if not os.path.exists(meta_path):
        return False, [f"_meta.json 文件不存在: {meta_path}"]

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"_meta.json JSON格式错误: {e}"]

    # 验证必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必需字段: {field}")

    # 验证version格式
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"version 应为语义化版本格式(如 1.0.0)，当前: {version}")

    # 验证id是数字
    if 'id' in meta:
        try:
            int(meta['id'])
        except ValueError:
            errors.append(f"id 应为数字，当前: {meta['id']}")

    return len(errors) == 0, errors


def validate_directory_structure(skill_path: str) -> tuple[bool, list]:
    """
    验证目录结构

    Returns:
        (是否通过, 错误列表)
    """
    errors = []

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = os.path.join(skill_path, filename)
        if not os.path.exists(filepath):
            errors.append(f"缺少必需文件: {filename}")

    # 检查scripts目录
    scripts_dir = os.path.join(skill_path, 'scripts')
    if os.path.exists(scripts_dir):
        py_files = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
        if not py_files:
            errors.append("scripts/ 目录为空，应包含核心功能脚本")

    return len(errors) == 0, errors


def validate_all(skill_path: str) -> bool:
    """
    执行所有验证

    Returns:
        是否全部通过
    """
    print("=" * 50)
    print("技能验证")
    print("=" * 50)
    print(f"路径: {skill_path}\n")

    all_passed = True

    # 1. 验证frontmatter
    print("[1/3] 验证 frontmatter...")
    passed, errors = validate_frontmatter(skill_path)
    if passed:
        print("      ✓ 通过")
    else:
        print("      ✗ 失败:")
        for err in errors:
            print(f"        - {err}")
        all_passed = False

    # 2. 验证_meta.json
    print("\n[2/3] 验证 _meta.json...")
    passed, errors = validate_meta_json(skill_path)
    if passed:
        print("      ✓ 通过")
    else:
        print("      ✗ 失败:")
        for err in errors:
            print(f"        - {err}")
        all_passed = False

    # 3. 验证目录结构
    print("\n[3/3] 验证目录结构...")
    passed, errors = validate_directory_structure(skill_path)
    if passed:
        print("      ✓ 通过")
    else:
        print("      ✗ 失败:")
        for err in errors:
            print(f"        - {err}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("验证结果: 全部通过 ✓")
    else:
        print("验证结果: 存在错误 ✗")
    print("=" * 50)

    return all_passed


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/douyin-search-assistant"
    success = validate_all(skill_path)
    sys.exit(0 if success else 1)
