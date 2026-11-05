#!/usr/bin/env python3
"""
Quick validation script for Agent Browser skill.
Validates structure, frontmatter, and essential files.
"""

import os
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
REQUIRED_FILES = ['SKILL.md', '_meta.json']
REQUIRED_DIRS = ['references']
REQUIRED_REFS = ['cdp-protocol.md', 'selectors.md', 'config-reference.md']

def validate_frontmatter():
    """Validate SKILL.md frontmatter format."""
    skill_md = SKILL_DIR / 'SKILL.md'

    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text()

    # Check if file starts with ---
    if not content.strip().startswith('---'):
        return False, "SKILL.md must start with YAML frontmatter (---)"

    # Extract frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[1].strip() == '':
        return False, "Invalid frontmatter structure"

    frontmatter_lines = []
    in_frontmatter = False
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append(line)

    frontmatter_text = '\n'.join(frontmatter_lines)

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if f'{field}:' not in frontmatter_text:
            return False, f"Missing required frontmatter field: {field}"

    # Check description contains trigger keywords
    desc_match = None
    for line in frontmatter_lines:
        if line.strip().startswith('description:'):
            desc_match = line
            break

    if not desc_match:
        return False, "description field not found in frontmatter"

    return True, "Frontmatter validation passed"

def validate_meta_json():
    """Validate _meta.json structure."""
    meta_file = SKILL_DIR / '_meta.json'

    if not meta_file.exists():
        return False, "_meta.json not found"

    try:
        data = json.loads(meta_file.read_text())
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in _meta.json: {e}"

    required_fields = ['id', 'version']
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field in _meta.json: {field}"

    return True, "_meta.json validation passed"

def validate_structure():
    """Validate directory structure."""
    for file in REQUIRED_FILES:
        if not (SKILL_DIR / file).exists():
            return False, f"Missing required file: {file}"

    for dir_name in REQUIRED_DIRS:
        dir_path = SKILL_DIR / dir_name
        if not dir_path.exists():
            return False, f"Missing required directory: {dir_name}"

    for ref in REQUIRED_REFS:
        if not (SKILL_DIR / 'references' / ref).exists():
            return False, f"Missing required reference file: {ref}"

    return True, "Structure validation passed"

def validate_naming():
    """Validate naming conventions."""
    # Check folder name matches name field
    meta_file = SKILL_DIR / '_meta.json'
    data = json.loads(meta_file.read_text())

    folder_name = SKILL_DIR.name
    skill_name = data.get('name', '').lower().replace(' ', '-')

    # Allow some flexibility (e.g., "agent-browser" matches "agent browser")
    if folder_name != skill_name and folder_name.replace('-', '') != skill_name.replace('-', ''):
        return False, f"Folder name '{folder_name}' doesn't match skill name '{skill_name}'"

    return True, "Naming validation passed"

def validate_content():
    """Validate SKILL.md content quality."""
    skill_md = SKILL_DIR / 'SKILL.md'
    content = skill_md.read_text()

    # Check for markdown headings
    if '#' not in content:
        return False, "SKILL.md should contain markdown headings"

    # Check minimum content length
    if len(content) < 500:
        return False, "SKILL.md content seems too short"

    return True, "Content validation passed"

def main():
    """Run all validations."""
    validations = [
        ("Frontmatter", validate_frontmatter),
        ("Meta JSON", validate_meta_json),
        ("Structure", validate_structure),
        ("Naming", validate_naming),
        ("Content", validate_content),
    ]

    all_passed = True
    for name, validator in validations:
        passed, message = validator()
        status = "✓" if passed else "✗"
        print(f"[{status}] {name}: {message}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n✓ All validations passed!")
        return 0
    else:
        print("\n✗ Some validations failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
