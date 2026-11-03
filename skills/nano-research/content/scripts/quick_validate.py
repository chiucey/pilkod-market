#!/usr/bin/env python3
"""NanoResearch 技能验证脚本"""

import json
import os
import sys
from pathlib import Path

def validate_skill(path: str) -> bool:
    """验证技能结构和 frontmatter"""
    skill_path = Path(path)
    errors = []

    # 检查 SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False

    content = skill_md.read_text()

    # 检查 frontmatter
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter")

    # 解析 frontmatter
    try:
        frontmatter_end = content.index("---", 3)
        frontmatter = content[3:frontmatter_end].strip()

        for line in frontmatter.split("\n"):
            if ":" in line:
                key = line.split(":")[0].strip()
                if key not in ["name", "description"]:
                    errors.append(f"Unexpected frontmatter key: {key}")
    except ValueError:
        errors.append("Invalid frontmatter format")

    # 检查 _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        try:
            meta = json.loads(meta_json.read_text())
            if "id" not in meta or "version" not in meta:
                errors.append("_meta.json must contain 'id' and 'version'")
        except json.JSONDecodeError:
            errors.append("Invalid JSON in _meta.json")

    if errors:
        print("Validation FAILED:")
        for e in errors:
            print(f"  - {e}")
        return False

    print("Validation PASSED")
    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
