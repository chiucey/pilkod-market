#!/usr/bin/env python3
"""Validate knowledge-base-manager skill structure."""

import json
import sys
from pathlib import Path

def validate_skill(path: str) -> bool:
    """Validate skill structure and frontmatter."""
    skill_path = Path(path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print("❌ SKILL.md not found")
        return False

    # Check frontmatter
    content = skill_md.read_text()
    if not content.startswith("---"):
        print("❌ SKILL.md must start with frontmatter (---)")
        return False

    frontmatter_end = content.find("---", 3)
    if frontmatter_end == -1:
        print("❌ Frontmatter not closed")
        return False

    frontmatter_text = content[3:frontmatter_end].strip()

    # Parse frontmatter
    lines = frontmatter_text.split("\n")
    fields = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()

    # Check required fields
    if "name" not in fields:
        print("❌ Missing 'name' field in frontmatter")
        return False

    if "description" not in fields:
        print("❌ Missing 'description' field in frontmatter")
        return False

    # Check _meta.json
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if "id" not in meta or "version" not in meta:
            print("❌ _meta.json must contain 'id' and 'version'")
            return False
    else:
        print("❌ _meta.json not found")
        return False

    print("✅ Validation passed")
    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/knowledge-base-manager"
    success = validate_skill(path)
    sys.exit(0 if success else 1)
