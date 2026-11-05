#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能验证器 - 验证公司信息Excel处理技能的结构和内容
"""

import json
import os
from pathlib import Path
import re


def validate_frontmatter(skill_dir):
    """验证SKILL.md的frontmatter格式"""
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False, "SKILL.md 文件不存在"

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        return False, "SKILL.md 必须以 YAML frontmatter 开头（---）"

    # 提取 frontmatter
    frontmatter_pattern = r'^---\n(.*?)\n---'
    match = re.search(frontmatter_pattern, content, re.DOTALL)

    if not match:
        return False, "无法解析 YAML frontmatter"

    try:
        frontmatter = match.group(1)
        # 简单验证必需字段
        if 'name:' not in frontmatter:
            return False, "frontmatter 缺少 name 字段"

        if 'description:' not in frontmatter:
            return False, "frontmatter 缺少 description 字段"

    except Exception as e:
        return False, f"YAML 解析错误: {e}"

    return True, "frontmatter 格式正确"


def validate_meta_json(skill_dir):
    """验证_meta.json文件"""
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        return False, "_meta.json 文件不存在"

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # 验证必需字段
        if 'id' not in meta:
            return False, "_meta.json 缺少 id 字段"

        if 'version' not in meta:
            return False, "_meta.json 缺少 version 字段"

        # 验证 id 是整数
        if not isinstance(meta['id'], int):
            return False, "_meta.json 的 id 必须是整数"

        # 验证 version 格式
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, meta['version']):
            return False, "_meta.json 的 version 格式不正确（应为 x.y.z）"

    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON 解析错误: {e}"

    return True, "_meta.json 格式正确"


def validate_scripts(skill_dir):
    """验证scripts目录"""
    scripts_dir = skill_dir / "scripts"

    if not scripts_dir.exists():
        return False, "scripts 目录不存在"

    # 检查主处理脚本
    processor_script = scripts_dir / "process_company_info.py"
    if not processor_script.exists():
        return False, "缺少主处理脚本 process_company_info.py"

    return True, "scripts 目录结构正确"


def validate_skill_structure():
    """验证整个技能目录结构"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent
    skill_dir = current_dir.parent

    if not skill_dir.exists():
        return False, None, f"技能目录不存在: {skill_dir}"

    print("验证技能结构")
    print("=" * 60)

    validations = [
        ("Frontmatter 验证", validate_frontmatter(skill_dir)),
        ("Meta JSON 验证", validate_meta_json(skill_dir)),
        ("Scripts 验证", validate_scripts(skill_dir)),
    ]

    all_passed = True
    results = []

    for name, (passed, message) in validations:
        status = "✓" if passed else "✗"
        print(f"{status} {name}: {message}")
        results.append((name, passed, message))
        if not passed:
            all_passed = False

    print("=" * 60)

    if all_passed:
        print("✓ 所有验证通过!")
        return True, results, None
    else:
        print("✗ 验证失败，请修复上述问题")
        return False, results, "验证失败"


def main():
    """主函数"""
    success, results, error = validate_skill_structure()

    if error:
        print(f"\n错误: {error}")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
