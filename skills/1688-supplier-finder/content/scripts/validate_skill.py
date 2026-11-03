#!/usr/bin/env python3
"""1688供应商搜索技能验证脚本"""

import json
import os
import sys
from pathlib import Path

def validate_skill():
    """验证技能结构和完整性"""
    errors = []
    warnings = []

    skill_dir = Path("/workspace/temp-skills/1688-supplier-finder")

    # 检查必需文件
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_dir / f).exists():
            errors.append(f"Missing required file: {f}")

    # 验证 SKILL.md frontmatter
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否以 --- 开头
        if not content.strip().startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        # 检查必需字段
        if 'name:' not in content:
            errors.append("SKILL.md missing 'name' field in frontmatter")
        if 'description:' not in content:
            errors.append("SKILL.md missing 'description' field in frontmatter")

    # 验证 _meta.json
    meta_json = skill_dir / "_meta.json"
    if meta_json.exists():
        try:
            with open(meta_json, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # 检查目录结构
    expected_dirs = ["scripts", "references"]
    for d in expected_dirs:
        if not (skill_dir / d).is_dir():
            warnings.append(f"Optional directory not found: {d}")

    return errors, warnings

if __name__ == "__main__":
    errors, warnings = validate_skill()

    if errors:
        print("❌ Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if warnings:
        print("⚠️ Validation passed with warnings:")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("✅ Validation passed!")

    sys.exit(0)