#!/usr/bin/env python3
"""
Quick validation script for material-paper-assistant skill.
Validates frontmatter, structure, and naming conventions.
"""
import os
import re
import sys

def validate_skill(skill_dir):
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return errors, warnings

    # Read and validate SKILL.md
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter position (must be at very beginning)
    if not content.startswith('---'):
        errors.append("SKILL.md must start with YAML frontmatter (---)")

    # Parse frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)

        # Check required fields
        if 'name:' not in frontmatter:
            errors.append("Frontmatter missing 'name' field")
        if 'description:' not in frontmatter:
            errors.append("Frontmatter missing 'description' field")

        # Check name format
        name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"Name '{name}' should use hyphen-case (lowercase with hyphens)")

    # Check _meta.json
    meta_json = os.path.join(skill_dir, "_meta.json")
    if not os.path.exists(meta_json):
        errors.append("_meta.json not found")
    else:
        import json
        with open(meta_json, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        if 'id' not in meta:
            errors.append("_meta.json missing 'id' field")
        if 'version' not in meta:
            errors.append("_meta.json missing 'version' field")

    # Check references directory
    refs_dir = os.path.join(skill_dir, "references")
    if os.path.exists(refs_dir):
        ref_files = [f for f in os.listdir(refs_dir) if f.endswith('.md')]
        if not ref_files:
            warnings.append("references/ directory is empty")

    return errors, warnings

if __name__ == "__main__":
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    errors, warnings = validate_skill(skill_dir)

    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("Errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("Validation passed!")
        sys.exit(0)
