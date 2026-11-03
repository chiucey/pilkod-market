#!/usr/bin/env python3
"""快速验证书籍层级整理技能的结构和内容"""

import json
import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能结构和内容"""
    errors = []
    warnings = []

    # 检查目录存在
    if not os.path.isdir(skill_path):
        errors.append(f"技能目录不存在: {skill_path}")
        return False

    # 检查 SKILL.md
    skill_md = Path(skill_path) / "SKILL.md"
    if not skill_md.exists():
        errors.append("缺少 SKILL.md 文件")
        return False

    # 读取并验证 frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查 frontmatter 格式
    if not content.startswith('---'):
        errors.append("SKILL.md 必须以 YAML frontmatter 开头（---）")

    # 提取 frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # 验证必需字段
        if 'name:' not in frontmatter:
            errors.append("frontmatter 缺少 name 字段")
        if 'description:' not in frontmatter:
            errors.append("frontmatter 缺少 description 字段")

        # 验证 name 格式
        name_match = re.search(r'name:\s*(.+)', frontmatter)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"name 必须使用小写字母、数字和连字符: {name}")
            if name != skill_path.split('/')[-1]:
                warnings.append(f"name '{name}' 应与文件夹名称一致")
    else:
        errors.append("无法解析 YAML frontmatter")

    # 检查 _meta.json
    meta_json = Path(skill_path) / "_meta.json"
    if not meta_json.exists():
        errors.append("缺少 _meta.json 文件")
    else:
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json 缺少 id 字段")
            if 'version' not in meta:
                errors.append("_meta.json 缺少 version 字段")
            if 'version' in meta and not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                errors.append(f"version 应遵循语义化版本格式: {meta['version']}")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json 格式错误: {e}")

    # 检查描述内容
    desc_match = re.search(r'description:\s*(.+)', frontmatter) if frontmatter_match else None
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            warnings.append("description 可能过于简短")
        if '当用户' not in desc and 'Use when' not in desc:
            warnings.append("description 应包含触发场景说明")

    # 验证工作流程内容
    if '工作流程' not in content and 'workflow' not in content.lower():
        warnings.append("SKILL.md 应包含工作流程说明")

    # 输出结果
    print("=" * 50)
    print("技能验证结果")
    print("=" * 50)

    if errors:
        print(f"\n❌ 错误 ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")

    if warnings:
        print(f"\n⚠️ 警告 ({len(warnings)}):")
        for warn in warnings:
            print(f"  - {warn}")

    if not errors and not warnings:
        print("\n✅ 验证通过！")
    elif not errors:
        print("\n✅ 基本验证通过（有警告）")
    else:
        print("\n❌ 验证失败")

    return len(errors) == 0

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
