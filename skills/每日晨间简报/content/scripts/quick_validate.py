#!/usr/bin/env python3
"""
快速验证脚本 - 验证 daily-morning-briefing 技能的结构完整性
"""

import os
import sys
import re
import json
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """验证 SKILL.md frontmatter 格式"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []

    # 检查是否以 --- 开头
    if not content.strip().startswith('---'):
        errors.append("❌ SKILL.md 必须以 YAML frontmatter (---) 开头")
        return errors

    # 提取 frontmatter
    lines = content.split('\n')
    in_frontmatter = False
    frontmatter_lines = []

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

    # 验证必填字段
    if not re.search(r'^name:', frontmatter_text, re.MULTILINE):
        errors.append("❌ frontmatter 缺少 'name' 字段")

    if not re.search(r'^description:', frontmatter_text, re.MULTILINE):
        errors.append("❌ frontmatter 缺少 'description' 字段")

    return errors

def validate_meta_json(meta_path):
    """验证 _meta.json 格式"""
    errors = []

    if not os.path.exists(meta_path):
        errors.append("❌ _meta.json 不存在")
        return errors

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        if 'id' not in meta:
            errors.append("❌ _meta.json 缺少 'id' 字段")
        if 'version' not in meta:
            errors.append("❌ _meta.json 缺少 'version' 字段")

    except json.JSONDecodeError as e:
        errors.append(f"❌ _meta.json 格式错误: {e}")

    return errors

def validate_file_structure(skill_dir):
    """验证目录结构"""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        path = os.path.join(skill_dir, f)
        if not os.path.exists(path):
            errors.append(f"❌ 缺少必需文件: {f}")

    # 检查 references 目录
    refs_dir = os.path.join(skill_dir, 'references')
    if os.path.exists(refs_dir):
        sources_md = os.path.join(refs_dir, 'sources.md')
        if not os.path.exists(sources_md):
            errors.append("⚠️ references/sources.md 不存在（建议添加）")

    return errors

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_dir = os.path.dirname(script_dir)  # 回到技能根目录

    print("=" * 50)
    print("🔍 验证 daily-morning-briefing 技能")
    print("=" * 50)

    all_errors = []

    # 1. 验证 frontmatter
    print("\n📋 检查 frontmatter...")
    errors = validate_frontmatter(os.path.join(skill_dir, 'SKILL.md'))
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(e)
    else:
        print("✅ frontmatter 格式正确")

    # 2. 验证 _meta.json
    print("\n📋 检查 _meta.json...")
    errors = validate_meta_json(os.path.join(skill_dir, '_meta.json'))
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(e)
    else:
        print("✅ _meta.json 格式正确")

    # 3. 验证文件结构
    print("\n📋 检查文件结构...")
    errors = validate_file_structure(skill_dir)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(e)
    else:
        print("✅ 文件结构完整")

    # 结果汇总
    print("\n" + "=" * 50)
    if all_errors:
        print(f"❌ 验证失败，发现 {len(all_errors)} 个错误")
        return 1
    else:
        print("✅ 所有验证通过！")
        return 0

if __name__ == '__main__':
    sys.exit(main())