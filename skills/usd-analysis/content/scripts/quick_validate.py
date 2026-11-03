#!/usr/bin/env python3
"""
USD Analysis Skill - Quick Validation Script
验证技能结构和内容是否符合规范
"""

import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """验证技能结构和内容"""
    errors = []
    warnings = []

    # 检查目录结构
    if not os.path.exists(skill_path):
        errors.append(f"技能目录不存在: {skill_path}")
        return False

    # 检查必需文件
    required_files = ['SKILL.md', '_meta.json']
    for file in required_files:
        file_path = os.path.join(skill_path, file)
        if not os.path.exists(file_path):
            errors.append(f"缺少必需文件: {file}")

    # 验证 SKILL.md
    skill_md_path = os.path.join(skill_path, 'SKILL.md')
    if os.path.exists(skill_md_path):
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查 frontmatter
        if not content.startswith('---'):
            errors.append("SKILL.md 必须以 frontmatter (---) 开头")

        # 检查必需字段
        if 'name:' not in content:
            errors.append("SKILL.md 缺少 name 字段")

        if 'description:' not in content:
            errors.append("SKILL.md 缺少 description 字段")

        # 检查 description 内容
        desc_match = re.search(r'description:\s*(.+)', content)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) < 20:
                warnings.append("description 内容可能过于简短")
            if '美元' not in desc and 'USD' not in desc and 'dollar' not in desc.lower():
                warnings.append("description 应包含美元相关关键词")

    # 验证 _meta.json
    meta_path = os.path.join(skill_path, '_meta.json')
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            import json
            try:
                meta = json.load(f)
                if 'id' not in meta:
                    errors.append("_meta.json 缺少 id 字段")
                if 'version' not in meta:
                    errors.append("_meta.json 缺少 version 字段")
            except json.JSONDecodeError as e:
                errors.append(f"_meta.json JSON 解析错误: {e}")

    # 输出结果
    print("=" * 50)
    print("USD Analysis Skill - 验证结果")
    print("=" * 50)

    if errors:
        print("\n❌ 错误:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️  警告:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("\n✅ 验证通过！技能结构完整。")
        return True
    elif not errors:
        print("\n✅ 验证通过（有警告）。")
        return True

    return False

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/usd-analysis"
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
