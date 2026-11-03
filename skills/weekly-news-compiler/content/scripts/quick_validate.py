#!/usr/bin/env python3
"""
Quick validator for weekly-news-compiler skill
Checks frontmatter, structure, and naming conventions
"""
import os
import re
import sys
from pathlib import Path

def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """Validate skill structure and return (success, errors)"""
    errors = []
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md not found")
        return False, errors

    # Read content
    content = skill_md.read_text(encoding="utf-8")

    # Check frontmatter is at the very beginning
    if not content.startswith("---"):
        errors.append("SKILL.md must start with YAML frontmatter (---)")
        return False, errors

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        errors.append("Invalid frontmatter format")
        return False, errors

    frontmatter = frontmatter_match.group(1)

    # Check required fields
    if not re.search(r'^name:\s*.+$', frontmatter, re.MULTILINE):
        errors.append("Missing 'name' field in frontmatter")

    if not re.search(r'^description:\s*.+$', frontmatter, re.MULTILINE):
        errors.append("Missing 'description' field in frontmatter")

    # Check name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', name):
            errors.append(f"Name '{name}' should use hyphen-case (e.g., 'skill-name')")

    # Check _meta.json exists
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        errors.append("_meta.json not found")
    else:
        import json
        try:
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            if "id" not in meta:
                errors.append("_meta.json missing 'id' field")
            if "version" not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"_meta.json is not valid JSON: {e}")

    # Check for markdown heading BEFORE frontmatter (lines 0 to frontmatter_start)
    lines = content.split('\n')
    frontmatter_start = -1
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if frontmatter_start == -1:
                frontmatter_start = i
            else:
                frontmatter_end = i
                break

    # Check lines BEFORE frontmatter starts for markdown headings
    if frontmatter_start > 0:
        for i in range(0, frontmatter_start):
            if lines[i].strip().startswith('#'):
                errors.append(f"Markdown heading found at line {i+1}, should be after frontmatter")
                break

    return len(errors) == 0, errors


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success, errors = validate_skill(skill_path)

    print(f"Validating skill at: {skill_path}")
    print("-" * 50)

    if success:
        print("✓ All validations passed!")
        sys.exit(0)
    else:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
