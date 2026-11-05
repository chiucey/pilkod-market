#!/usr/bin/env python3
"""
技能验证脚本
验证SKILL.md的结构和frontmatter
"""

import os
import re
import sys

def validate_skill(path):
    """验证技能结构"""
    errors = []
    warnings = []

    # 检查SKILL.md是否存在
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md不存在")
        return errors, warnings

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查frontmatter
    if not content.startswith('---'):
        errors.append("SKILL.md必须以frontmatter开头（---）")
    else:
        # 提取frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append("frontmatter格式错误")
        else:
            frontmatter = parts[1]
            lines = frontmatter.strip().split('\n')

            # 检查必需字段
            has_name = False
            has_description = False

            for line in lines:
                if line.startswith('name:'):
                    has_name = True
                    name_value = line.split(':', 1)[1].strip()
                    if not name_value:
                        errors.append("name字段不能为空")
                    elif ' ' in name_value:
                        errors.append("name必须使用连字符格式（hyphen-case）")
                if line.startswith('description:'):
                    has_description = True
                    if not line.split(':', 1)[1].strip():
                        warnings.append("description字段为空")

            if not has_name:
                errors.append("缺少name字段")
            if not has_description:
                errors.append("缺少description字段")

    # 检查_meta.json
    meta_json = os.path.join(path, "_meta.json")
    if os.path.exists(meta_json):
        import json
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json缺少id字段")
            if 'version' not in meta:
                errors.append("_meta.json缺少version字段")
        except json.JSONDecodeError:
            errors.append("_meta.json格式错误")
    else:
        errors.append("_meta.json不存在")

    # 检查目录结构
    expected_dirs = ['scripts', 'references', 'assets']
    for d in expected_dirs:
        dir_path = os.path.join(path, d)
        if not os.path.exists(dir_path):
            warnings.append(f"建议添加{d}目录")

    return errors, warnings


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/auto-skill-generator"

    errors, warnings = validate_skill(skill_path)

    if errors:
        print("❌ 验证失败:")
        for e in errors:
            print(f"  - {e}")

    if warnings:
        print("⚠️ 警告:")
        for w in warnings:
            print(f"  - {w}")

    if not errors and not warnings:
        print("✅ 验证通过")
        sys.exit(0)
    elif not errors:
        sys.exit(0)
    else:
        sys.exit(1)
