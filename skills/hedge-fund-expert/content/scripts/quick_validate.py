#!/usr/bin/env python3
"""Quick validation script for hedge-fund-expert skill"""

import sys
import json
import os
from pathlib import Path

def validate_skill(path: str) -> bool:
    skill_path = Path(path)
    passed = True
    
    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print("❌ SKILL.md not found")
        return False
    
    # Read SKILL.md
    with open(skill_md, "r") as f:
        content = f.read()
    
    # Check frontmatter starts at line 1
    if not content.startswith("---"):
        print("❌ SKILL.md must start with --- (frontmatter)")
        passed = False
    
    # Check frontmatter fields
    if "name:" not in content:
        print("❌ Missing 'name:' in frontmatter")
        passed = False
    
    if "description:" not in content:
        print("❌ Missing 'description:' in frontmatter")
        passed = False
    
    # Check _meta.json
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        print("❌ _meta.json not found")
        passed = False
    else:
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            if "id" not in meta or "version" not in meta:
                print("❌ _meta.json must have 'id' and 'version'")
                passed = False
        except json.JSONDecodeError:
            print("❌ _meta.json is not valid JSON")
            passed = False
    
    # Check references directory
    refs_path = skill_path / "references"
    if not refs_path.exists():
        print("⚠️  references/ directory not found")
    else:
        ref_files = list(refs_path.glob("*.md"))
        print(f"📚 Found {len(ref_files)} reference files")
    
    if passed:
        print("✅ All validations passed")
    else:
        print("❌ Validation failed")
    
    return passed

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
