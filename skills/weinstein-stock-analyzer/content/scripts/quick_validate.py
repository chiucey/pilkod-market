#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能验证脚本
"""

import os
import sys
import json
from pathlib import Path


def validate_skill(skill_path: str) -> bool:
    """验证技能结构"""
    print("=" * 60)
    print("笑傲牛熊技能验证")
    print("=" * 60)

    errors = []
    warnings = []

    # 检查目录结构
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        filepath = os.path.join(skill_path, f)
        if not os.path.exists(filepath):
            errors.append(f"缺少必需文件: {f}")

    # 检查SKILL.md
    skill_md = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter
        if not content.startswith('---'):
            errors.append("SKILL.md必须以frontmatter (---) 开头")

        # 检查必需字段
        if 'name:' not in content:
            errors.append("SKILL.md缺少name字段")
        if 'description:' not in content:
            errors.append("SKILL.md缺少description字段")

        # 检查标题位置
        lines = content.split('\n')
        frontmatter_end = -1
        for i, line in enumerate(lines):
            if line.strip() == '---' and i > 0:
                frontmatter_end = i
                break

        if frontmatter_end > 0:
            for i in range(frontmatter_end + 1, min(frontmatter_end + 5, len(lines))):
                if lines[i].startswith('#'):
                    # 这是允许的，标题可以在frontmatter之后
                    break
                if lines[i].strip() and not lines[i].startswith('#'):
                    # 发现了非标题内容在frontmatter之后
                    break

    # 检查_meta.json
    meta_json = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_json):
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")

            if 'id' in meta and not isinstance(meta['id'], int):
                errors.append("_meta.json的id必须是整数")

        except json.JSONDecodeError as e:
            errors.append(f"_meta.json格式错误: {e}")

    # 检查references目录
    refs_dir = os.path.join(skill_path, 'references')
    if not os.path.exists(refs_dir):
        warnings.append("建议添加references目录包含详细文档")
    else:
        print(f"✓ references目录存在")

    # 检查scripts目录
    scripts_dir = os.path.join(skill_path, 'scripts')
    if os.path.exists(scripts_dir):
        print(f"✓ scripts目录存在")
        for f in os.listdir(scripts_dir):
            if f.endswith('.py'):
                print(f"  - {f}")

    # 输出结果
    print()
    print("=" * 60)
    print("验证结果")
    print("=" * 60)

    if errors:
        print("\n❌ 错误:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("\n⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("\n✓ 验证通过！")

    return len(errors) == 0


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
