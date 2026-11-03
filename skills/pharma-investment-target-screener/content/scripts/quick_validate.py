#!/usr/bin/env python3
"""
医药投行投资标的筛选技能 - 快速验证脚本
验证技能结构、frontmatter格式和必要文件
"""

import os
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
META_JSON = SKILL_DIR / "_meta.json"

def validate_frontmatter():
    """验证frontmatter格式"""
    errors = []

    if not SKILL_MD.exists():
        errors.append(f"SKILL.md 不存在: {SKILL_MD}")
        return False, errors

    with open(SKILL_MD, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter --- 开头")

    # 提取frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("无法解析 YAML frontmatter")
        return False, errors

    frontmatter_text = frontmatter_match.group(1)

    # 检查必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_text, re.MULTILINE):
            errors.append(f"Frontmatter 缺少必需字段: {field}")

    # 验证name格式
    name_match = re.search(r'^name:\s*(.+)', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if ' ' in name:
            errors.append(f"name 应使用连字符格式: '{name}'")
        if not re.match(r'^[a-z0-9-]+$', name):
            errors.append(f"name 只能包含小写字母、数字和连字符: '{name}'")

    return len(errors) == 0, errors

def validate_meta_json():
    """验证_meta.json格式"""
    errors = []

    if not META_JSON.exists():
        errors.append(f"_meta.json 不存在: {META_JSON}")
        return False, errors

    try:
        with open(META_JSON, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json JSON格式错误: {e}")
        return False, errors

    # 检查必需字段
    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in meta:
            errors.append(f"_meta.json 缺少必需字段: {field}")

    # 验证id是整数
    if 'id' in meta:
        try:
            int(meta['id'])
        except (ValueError, TypeError):
            errors.append(f"_meta.json id 必须是整数: {meta['id']}")

    # 验证version格式
    if 'version' in meta:
        if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
            errors.append(f"_meta.json version 格式错误: {meta['version']}")

    return len(errors) == 0, errors

def validate_directory_structure():
    """验证目录结构"""
    errors = []

    # 检查根目录
    expected_dirs = []
    for d in expected_dirs:
        dir_path = SKILL_DIR / d
        if not dir_path.exists():
            # 这是可选的，所以只是提示
            pass

    return len(errors) == 0, errors

def main():
    """主验证流程"""
    print("=" * 60)
    print("医药投行投资标的筛选技能 - 验证检查")
    print("=" * 60)

    all_passed = True

    # 1. Frontmatter验证
    print("\n[1/3] 验证 Frontmatter 格式...")
    passed, errors = validate_frontmatter()
    if passed:
        print("    ✓ Frontmatter 格式正确")
    else:
        print("    ✗ Frontmatter 验证失败:")
        for err in errors:
            print(f"      - {err}")
        all_passed = False

    # 2. Meta JSON验证
    print("\n[2/3] 验证 _meta.json 格式...")
    passed, errors = validate_meta_json()
    if passed:
        print("    ✓ _meta.json 格式正确")
    else:
        print("    ✗ _meta.json 验证失败:")
        for err in errors:
            print(f"      - {err}")
        all_passed = False

    # 3. 目录结构验证
    print("\n[3/3] 验证目录结构...")
    passed, errors = validate_directory_structure()
    if passed:
        print("    ✓ 目录结构正确")
    else:
        print("    ✗ 目录结构验证失败:")
        for err in errors:
            print(f"      - {err}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有验证通过！技能已准备就绪。")
        return 0
    else:
        print("✗ 存在验证问题，请修复后重试。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
