#!/usr/bin/env python3
"""Quick validation script for cross-border-ecommerce-agent skill."""

import os
import sys
import json
import re
from pathlib import Path

def validate_skill(skill_path: str) -> bool:
    """Validate skill structure and frontmatter."""
    skill_dir = Path(skill_path)
    results = []

    # Check SKILL.md exists
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print("❌ SKILL.md not found")
        return False
    print("✓ SKILL.md exists")

    # Read SKILL.md content
    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter is at the start
    if not content.startswith("---"):
        print("❌ SKILL.md must start with frontmatter (---)")
        return False
    print("✓ Frontmatter starts correctly")

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print("❌ Cannot parse frontmatter")
        return False

    frontmatter = frontmatter_match.group(1)
    print("✓ Frontmatter parsed")

    # Check required fields
    if not re.search(r'^name:', frontmatter, re.MULTILINE):
        print("❌ Missing 'name' field in frontmatter")
        return False
    print("✓ 'name' field exists")

    if not re.search(r'^description:', frontmatter, re.MULTILINE):
        print("❌ Missing 'description' field in frontmatter")
        return False
    print("✓ 'description' field exists")

    # Check _meta.json exists
    meta_json = skill_dir / "_meta.json"
    if not meta_json.exists():
        print("❌ _meta.json not found")
        return False
    print("✓ _meta.json exists")

    # Validate _meta.json content
    try:
        meta = json.loads(meta_json.read_text(encoding="utf-8"))
        if "id" not in meta:
            print("❌ _meta.json missing 'id' field")
            return False
        if "version" not in meta:
            print("❌ _meta.json missing 'version' field")
            return False
        print(f"✓ _meta.json valid (id={meta['id']}, version={meta['version']})")
    except json.JSONDecodeError as e:
        print(f"❌ _meta.json is not valid JSON: {e}")
        return False

    # Check references directory exists
    refs_dir = skill_dir / "references"
    if refs_dir.exists():
        ref_files = list(refs_dir.glob("*.md"))
        print(f"✓ references/ directory exists with {len(ref_files)} file(s)")

    # Check no markdown title before frontmatter
    lines_before_frontmatter = content.split("---")[0].strip()
    if lines_before_frontmatter and not lines_before_frontmatter.startswith("---"):
        print("❌ Content found before frontmatter")
        return False
    print("✓ No content before frontmatter")

    # Check name matches folder
    name_match = re.search(r'^name:\s*(.+)', frontmatter, re.MULTILINE)
    if name_match:
        skill_name = name_match.group(1).strip()
        if skill_name != skill_dir.name:
            print(f"⚠️  Warning: name '{skill_name}' != folder '{skill_dir.name}'")
        else:
            print(f"✓ name matches folder: {skill_name}")

    print("\n✅ All validations passed!")
    return True

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
