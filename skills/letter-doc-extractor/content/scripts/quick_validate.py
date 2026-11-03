#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证脚本 - 验证技能结构和内容
"""

import os
import sys
import json
import re


def validate_frontmatter(skill_md_path: str) -> bool:
    """验证 SKILL.md frontmatter"""
    errors = []

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 frontmatter 开头
    if not content.startswith('---'):
        errors.append("❌ SKILL.md 必须以 YAML frontmatter 开头（---）")
        return False, errors

    # 提取 frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # 检查必需字段
    if 'name:' not in frontmatter_text:
        errors.append("❌ 缺少 'name:' 字段")
    else:
        name_match = re.search(r'name:\s*(.+)', frontmatter_text)
        if name_match:
            name = name_match.group(1).strip()
            if not name:
                errors.append("❌ 'name:' 字段不能为空")
            elif ' ' in name:
                errors.append("❌ 'name:' 必须使用连字符格式（如：skill-name）")

    if 'description:' not in frontmatter_text:
        errors.append("❌ 缺少 'description:' 字段")
    else:
        desc_match = re.search(r'description:\s*(.+)', frontmatter_text)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 10:
                errors.append("⚠️ 'description:' 建议至少10个字符")

    # 检查 frontmatter 位置
    if content.index('---') > 0:
        errors.append("❌ frontmatter 前不能有任何内容（不能以标题开头）")

    return len(errors) == 0, errors


def validate_meta(meta_path: str) -> bool:
    """验证 _meta.json"""
    errors = []

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except Exception as e:
        errors.append(f"❌ _meta.json 解析错误: {e}")
        return False, errors

    if 'id' not in meta:
        errors.append("❌ _meta.json 缺少 'id' 字段")
    elif not isinstance(meta['id'], (str, int)):
        errors.append("❌ 'id' 必须为数字或字符串")

    if 'version' not in meta:
        errors.append("❌ _meta.json 缺少 'version' 字段")
    elif not re.match(r'^\d+\.\d+\.\d+$', meta.get('version', '')):
        errors.append("⚠️ 'version' 建议使用语义化版本（如：1.0.0）")

    return len(errors) == 0, errors


def validate_structure(skill_path: str) -> bool:
    """验证目录结构"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        path = os.path.join(skill_path, f)
        if not os.path.exists(path):
            errors.append(f"❌ 缺少必需文件: {f}")

    return len(errors) == 0, errors


def main():
    skill_path = os.path.dirname(os.path.abspath(__file__))
    skill_path = os.path.dirname(skill_path)  # 返回技能根目录

    print("=" * 50)
    print("技能验证报告")
    print("=" * 50)
    print(f"技能路径: {skill_path}\n")

    all_passed = True

    # 验证结构
    print("1. 目录结构验证:")
    passed, errors = validate_structure(skill_path)
    if passed:
        print("   ✅ 通过")
    else:
        all_passed = False
        for err in errors:
            print(f"   {err}")

    # 验证 _meta.json
    print("\n2. _meta.json 验证:")
    meta_path = os.path.join(skill_path, "_meta.json")
    passed, errors = validate_meta(meta_path)
    if passed:
        print("   ✅ 通过")
    else:
        all_passed = False
        for err in errors:
            print(f"   {err}")

    # 验证 SKILL.md
    print("\n3. SKILL.md 验证:")
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    passed, errors = validate_frontmatter(skill_md_path)
    if passed:
        print("   ✅ 通过")
    else:
        all_passed = False
        for err in errors:
            print(f"   {err}")

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有验证通过!")
        sys.exit(0)
    else:
        print("❌ 存在错误，请修复后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
