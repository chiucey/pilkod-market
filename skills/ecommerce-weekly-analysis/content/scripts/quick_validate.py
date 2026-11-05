#!/usr/bin/env python3
"""
Validation script for ecommerce-weekly-analysis skill
Checks frontmatter, structure, and naming conventions
"""

import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter is correct"""
    errors = []
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter at the very beginning
    if not content.startswith("---"):
        errors.append("SKILL.md must start with frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    if "name:" not in frontmatter:
        errors.append("Missing 'name' field in frontmatter")
    if "description:" not in frontmatter:
        errors.append("Missing 'description' field in frontmatter")

    # Check name matches folder
    name_match = re.search(r"name:\s*(.+)", frontmatter)
    if name_match:
        name = name_match.group(1).strip()
        if name != skill_path.name:
            errors.append(f"Frontmatter name '{name}' does not match folder name '{skill_path.name}'")

    return len(errors) == 0, errors

def validate_meta(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json exists and is valid"""
    errors = []
    meta_file = skill_path / "_meta.json"

    if not meta_file.exists():
        return False, ["_meta.json not found"]

    import json
    try:
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, [f"Invalid _meta.json: {e}"]

    if "id" not in meta:
        errors.append("Missing 'id' field in _meta.json")
    if "version" not in meta:
        errors.append("Missing 'version' field in _meta.json")

    return len(errors) == 0, errors

def validate_structure(skill_path: Path) -> tuple[bool, list[str]]:
    """Validate directory structure"""
    errors = []

    # Required files
    required_files = ["SKILL.md", "_meta.json"]
    for f in required_files:
        if not (skill_path / f).exists():
            errors.append(f"Missing required file: {f}")

    # Allowed directories
    allowed_dirs = ["scripts", "references", "assets"]
    for item in skill_path.iterdir():
        if item.is_dir() and item.name not in allowed_dirs:
            errors.append(f"Unexpected directory: {item.name}")

    return len(errors) == 0, errors

def main():
    skill_path = Path(os.environ.get("SKILL_PATH", "/workspace/temp-skills/ecommerce-weekly-analysis"))

    all_passed = True
    results = []

    # Run validations
    checks = [
        ("Frontmatter", validate_frontmatter),
        ("Meta", validate_meta),
        ("Structure", validate_structure),
    ]

    for name, check_func in checks:
        passed, errors = check_func(skill_path)
        if passed:
            results.append(f"✅ {name}: PASS")
        else:
            results.append(f"❌ {name}: FAIL")
            for err in errors:
                results.append(f"   - {err}")
            all_passed = False

    print("\n".join(results))
    print()

    if all_passed:
        print("🎉 All validations passed!")
        sys.exit(0)
    else:
        print("⚠️  Validation failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
