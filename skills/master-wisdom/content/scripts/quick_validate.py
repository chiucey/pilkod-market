#!/usr/bin/env python3
"""Quick validation script for skill structure."""

import json
import os
import sys

def validate_skill(skill_path):
    """Validate skill structure and frontmatter."""
    errors = []
    warnings = []

    # Check SKILL.md exists
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("SKILL.md not found")
        return errors, warnings

    # Read and check frontmatter
    with open(skill_md, "r", encoding="utf-8") as f:
        content = f.read()

    # Check frontmatter format
    if not content.startswith("---"):
        errors.append("SKILL.md must start with frontmatter (---)")

    # Parse frontmatter
    try:
        frontmatter_end = content.index("---", 3)
        frontmatter_text = content[3:frontmatter_end].strip()
        frontmatter = {}
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()
    except:
        errors.append("Invalid frontmatter format")
        return errors, warnings

    # Check required fields
    if "name" not in frontmatter:
        errors.append("Missing required field: name")
    if "description" not in frontmatter:
        errors.append("Missing required field: description")

    # Check _meta.json
    meta_path = os.path.join(skill_path, "_meta.json")
    if not os.path.exists(meta_path):
        errors.append("_meta.json not found")
    else:
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if "id" not in meta:
                errors.append("Missing required field in _meta.json: id")
            if "version" not in meta:
                errors.append("Missing required field in _meta.json: version")
        except json.JSONDecodeError:
            errors.append("Invalid JSON in _meta.json")

    # Check references
    references_dir = os.path.join(skill_path, "references")
    if os.path.exists(references_dir):
        for file in os.listdir(references_dir):
            if not file.endswith((".json", ".md", ".txt")):
                warnings.append(f"Unusual file in references: {file}")

    return errors, warnings

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    errors, warnings = validate_skill(skill_path)

    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print(f"  - {w}")

    print("Validation passed!")
    sys.exit(0)
