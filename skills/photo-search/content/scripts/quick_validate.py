#!/usr/bin/env python3
"""
Photo Search Skill - Quick Validation Script
验证技能结构和frontmatter格式
"""

import os
import re
import json
import sys

def validate_skill(path: str) -> bool:
    """验证技能结构和内容"""
    errors = []
    warnings = []

    # 1. 检查目录结构
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        fpath = os.path.join(path, f)
        if not os.path.exists(fpath):
            errors.append(f"Missing required file: {f}")

    # 2. 验证SKILL.md frontmatter
    skill_md = os.path.join(path, 'SKILL.md')
    if os.path.exists(skill_md):
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查frontmatter是否在第一行
        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        # 提取frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_content = fm_match.group(1)

            # 检查必填字段
            if 'name:' not in fm_content:
                errors.append("Missing 'name' in frontmatter")
            if 'description:' not in fm_content:
                errors.append("Missing 'description' in frontmatter")

            # 提取name验证格式
            name_match = re.search(r'name:\s*(.+)', fm_content)
            if name_match:
                name = name_match.group(1).strip()
                if not re.match(r'^[a-z0-9-]+$', name):
                    warnings.append(f"name '{name}' should be lowercase with hyphens")
        else:
            errors.append("Cannot parse YAML frontmatter")
    else:
        errors.append("SKILL.md not found")

    # 3. 验证_meta.json
    meta_json = os.path.join(path, '_meta.json')
    if os.path.exists(meta_json):
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)

            if 'id' not in meta:
                errors.append("Missing 'id' in _meta.json")
            if 'version' not in meta:
                errors.append("Missing 'version' in _meta.json")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid _meta.json: {e}")

    # 4. 路径检查（确保无中文和特殊字符）
    skill_name = os.path.basename(path)
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        errors.append(f"Directory name '{skill_name}' should be lowercase with hyphens only")

    # 输出结果
    print(f"\n{'='*50}")
    print(f"Validation for: {path}")
    print(f"{'='*50}")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n❌ Validation FAILED")
        return False
    else:
        print(f"\n✅ Validation PASSED")
        return True

if __name__ == '__main__':
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)