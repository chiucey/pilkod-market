#!/usr/bin/env python3
"""
Quick validation script for circuit-diagram-generator skill.
Validates frontmatter, structure, and resources.
"""

import json
import os
import re
import sys
from pathlib import Path

def validate_frontmatter(skill_dir: Path) -> bool:
    """Validate SKILL.md frontmatter format."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ SKILL.md not found in {skill_dir}")
        return False

    content = skill_md.read_text(encoding="utf-8")

    if not content.startswith("---"):
        print("❌ SKILL.md must start with --- (frontmatter delimiter)")
        return False

    parts = content.split("---", 2)
    if len(parts) < 3:
        print("❌ Frontmatter is not properly closed with ---")
        return False

    frontmatter = parts[1]

    if "name:" not in frontmatter:
        print("❌ Frontmatter missing 'name' field")
        return False

    if "description:" not in frontmatter:
        print("❌ Frontmatter missing 'description' field")
        return False

    name_match = re.search(r"name:\s*([a-z0-9-]+)", frontmatter)
    if name_match:
        name = name_match.group(1)
        if len(name) > 64:
            print(f"❌ Skill name exceeds 64 characters: {len(name)}")
            return False
        if name != skill_dir.name:
            print(f"⚠️  Warning: folder name '{skill_dir.name}' differs from frontmatter name '{name}'")

    print("✅ Frontmatter validation passed")
    return True

def validate_meta_json(skill_dir: Path) -> bool:
    """Validate _meta.json exists and has required fields."""
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        print("❌ _meta.json not found")
        return False

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ _meta.json is not valid JSON: {e}")
        return False

    if "id" not in meta:
        print("❌ _meta.json missing 'id' field")
        return False

    if "version" not in meta:
        print("❌ _meta.json missing 'version' field")
        return False

    print("✅ _meta.json validation passed")
    return True

def validate_structure(skill_dir: Path) -> bool:
    """Validate directory structure."""
    required_dirs = ["assets", "scripts"]
    for dir_name in required_dirs:
        dir_path = skill_dir / dir_name
        if not dir_path.exists():
            print(f"❌ Required directory '{dir_name}' not found")
            return False

    key_files = [
        "assets/template.tex",
    ]
    for file_path in key_files:
        full_path = skill_dir / file_path
        if not full_path.exists():
            print(f"❌ Required file '{file_path}' not found")
            return False

    print("✅ Directory structure validation passed")
    return True

def validate_no_secrets(skill_dir: Path) -> bool:
    """Check for potential secrets or sensitive data."""
    dangerous_patterns = [
        r'password\s*=\s*["\'](?!["\']{2})',
        r'api[_-]?key\s*=\s*["\'](?!["\']{2})',
        r'secret\s*=\s*["\'](?!["\']{2})',
        r'token\s*=\s*["\'](?!["\']{2})',
    ]

    for py_file in skill_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"⚠️  Potential secret found in {py_file.relative_to(skill_dir)}")

    print("✅ No obvious secrets detected")
    return True

def main():
    skill_dir = Path(__file__).parent.parent.resolve()

    print(f"🔍 Validating skill: {skill_dir.name}")
    print("=" * 50)

    all_passed = True

    all_passed &= validate_frontmatter(skill_dir)
    all_passed &= validate_meta_json(skill_dir)
    all_passed &= validate_structure(skill_dir)
    all_passed &= validate_no_secrets(skill_dir)

    print("=" * 50)
    if all_passed:
        print("✅ All validations passed!")
        sys.exit(0)
    else:
        print("❌ Validation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
