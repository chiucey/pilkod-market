#!/usr/bin/env python3
"""
Skill Validation Script
Check SKILL.md and _meta.json format
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_skill(skill_path: str) -> dict:
    """Validate skill structure"""

    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    skill_path = Path(skill_path)

    # Check SKILL.md
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        results["valid"] = False
        results["errors"].append("SKILL.md does not exist")
        return results

    # Read SKILL.md content
    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter position
    lines = content.split("\n")
    if lines[0].strip() != "---":
        results["valid"] = False
        results["errors"].append("SKILL.md must start with --- (frontmatter start)")

    # Extract frontmatter
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        results["valid"] = False
        results["errors"].append("SKILL.md frontmatter not properly closed")
        return results

    frontmatter_text = "\n".join(lines[1:frontmatter_end])

    # Check required fields
    if "name:" not in frontmatter_text:
        results["valid"] = False
        results["errors"].append("frontmatter missing name field")

    if "description:" not in frontmatter_text:
        results["valid"] = False
        results["errors"].append("frontmatter missing description field")

    # Extract name value
    name_match = re.search(r"name:\s*([^\n]+)", frontmatter_text)
    if name_match:
        name = name_match.group(1).strip()
        if name != skill_path.name:
            results["warnings"].append(f"name '{name}' should match directory name '{skill_path.name}'")

    # Check _meta.json
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        results["valid"] = False
        results["errors"].append("_meta.json does not exist")
        return results

    try:
        meta = json.loads(meta_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        results["valid"] = False
        results["errors"].append(f"_meta.json JSON parse failed: {e}")
        return results

    if "id" not in meta:
        results["valid"] = False
        results["errors"].append("_meta.json missing id field")

    if "version" not in meta:
        results["valid"] = False
        results["errors"].append("_meta.json missing version field")

    # Check scripts directory
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob("*.py"))
        if len(scripts) < 2:
            results["warnings"].append(f"scripts directory has only {len(scripts)} Python files")

    return results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate skill structure")
    parser.add_argument("path", nargs="?", default=".", help="Skill path")

    args = parser.parse_args()
    results = validate_skill(args.path)

    print("=" * 50)
    print(f"Validation result: {'PASS' if results['valid'] else 'FAIL'}")
    print("=" * 50)

    if results["errors"]:
        print("\nErrors:")
        for err in results["errors"]:
            print(f"  - {err}")

    if results["warnings"]:
        print("\nWarnings:")
        for warn in results["warnings"]:
            print(f"  - {warn}")

    sys.exit(0 if results["valid"] else 1)
