#!/usr/bin/env python3
"""
Quick Validate Script
Validates skill structure and frontmatter.
"""

import json
import sys
from pathlib import Path


def validate_skill(skill_path: Path) -> bool:
    """Validate skill structure and frontmatter."""
    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    all_passed = True

    # Check required files
    print("\n1. Checking required files...")
    required_files = ["SKILL.md", "_meta.json"]
    for file in required_files:
        file_path = skill_path / file
        if file_path.exists():
            print(f"   ✓ {file} exists")
        else:
            print(f"   ✗ {file} MISSING")
            all_passed = False

    # Check SKILL.md frontmatter
    print("\n2. Checking SKILL.md frontmatter...")
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")

        if content.startswith("---"):
            print("   ✓ Frontmatter starts with ---")
        else:
            print("   ✗ SKILL.md must start with frontmatter (---)")
            all_passed = False

        # Extract frontmatter
        lines = content.split("\n")
        frontmatter_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                else:
                    break
            if in_frontmatter and line.strip():
                frontmatter_lines.append(line.strip())

        frontmatter_str = "\n".join(frontmatter_lines)

        if "name:" in frontmatter_str:
            print("   ✓ 'name:' field present")
        else:
            print("   ✗ 'name:' field MISSING")
            all_passed = False

        if "description:" in frontmatter_str:
            print("   ✓ 'description:' field present")
        else:
            print("   ✗ 'description:' field MISSING")
            all_passed = False

    # Check _meta.json
    print("\n3. Checking _meta.json...")
    meta_json = skill_path / "_meta.json"
    if meta_json.exists():
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))

            if "id" in meta:
                print(f"   ✓ 'id' field present: {meta['id']}")
            else:
                print("   ✗ 'id' field MISSING")
                all_passed = False

            if "version" in meta:
                print(f"   ✓ 'version' field present: {meta['version']}")
            else:
                print("   ✗ 'version' field MISSING")
                all_passed = False

        except json.JSONDecodeError as e:
            print(f"   ✗ _meta.json is invalid JSON: {e}")
            all_passed = False

    # Check directory structure
    print("\n4. Checking directory structure...")
    expected_dirs = ["scripts", "references", "assets"]
    for dir_name in expected_dirs:
        dir_path = skill_path / dir_name
        if dir_path.exists():
            files = list(dir_path.rglob("*"))
            print(f"   ✓ {dir_name}/ exists ({len([f for f in files if f.is_file()])} files)")
        else:
            print(f"   ℹ {dir_name}/ not found (optional)")

    # Summary
    print("\n" + "-" * 50)
    if all_passed:
        print("✓ All validation checks passed!")
        return True
    else:
        print("✗ Some validation checks failed.")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <skill_path>")
        sys.exit(1)

    skill_path = Path(sys.argv[1])
    success = validate_skill(skill_path)
    sys.exit(0 if success else 1)
