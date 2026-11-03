#!/usr/bin/env python3
"""Validate game-idea-dev skill structure and content"""

import sys
import os

def validate_frontmatter(skill_path):
    """Validate SKILL.md frontmatter"""
    skill_md = os.path.join(skill_path, "SKILL.md")

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter at start
    if not content.startswith('---'):
        return False, "SKILL.md must start with frontmatter (---)"

    # Parse frontmatter
    lines = content.split('\n')
    frontmatter_end = None
    for i, line in enumerate(lines):
        if line == '---' and i > 0:
            frontmatter_end = i
            break

    if frontmatter_end is None:
        return False, "Frontmatter closing --- not found"

    frontmatter = '\n'.join(lines[1:frontmatter_end])

    # Check required fields
    if 'name:' not in frontmatter:
        return False, "Missing 'name:' in frontmatter"
    if 'description:' not in frontmatter:
        return False, "Missing 'description:' in frontmatter"

    return True, "Frontmatter valid"

def validate_meta(skill_path):
    """Validate _meta.json"""
    import json

    meta_path = os.path.join(skill_path, "_meta.json")

    if not os.path.exists(meta_path):
        return False, "_meta.json not found"

    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    if 'id' not in meta and 'skill_id' not in meta:
        return False, "Missing 'id' or 'skill_id' in _meta.json"
    if 'version' not in meta:
        return False, "Missing 'version' in _meta.json"

    return True, "_meta.json valid"

def main():
    skill_path = "/workspace/temp-skills/game-idea-dev"

    results = []

    # Validate frontmatter
    ok, msg = validate_frontmatter(skill_path)
    results.append(("Frontmatter", ok, msg))
    print(f"{'✓' if ok else '✗'} {msg}")

    # Validate meta
    ok, msg = validate_meta(skill_path)
    results.append(("Meta JSON", ok, msg))
    print(f"{'✓' if ok else '✗'} {msg}")

    # Check references exist
    refs_path = os.path.join(skill_path, "tags-reference.md")
    if os.path.exists(refs_path):
        results.append(("References", True, "tags-reference.md exists"))
        print("✓ tags-reference.md exists")
    else:
        results.append(("References", False, "tags-reference.md not found"))
        print("✗ tags-reference.md not found")

    all_ok = all(r[1] for r in results)

    print()
    if all_ok:
        print("✓ All validations passed")
        return 0
    else:
        print("✗ Some validations failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())