#!/usr/bin/env python3
"""
Quick validation script for strict-academic-critic skill.
Validates frontmatter, structure, and prohibited behavior patterns.
"""

import sys
import re
from pathlib import Path

def validate_frontmatter(content: str) -> tuple[bool, list[str]]:
    """Validate frontmatter format and required fields."""
    errors = []
    lines = content.split('\n')

    # Check if file starts with ---
    if not content.strip().startswith('---'):
        errors.append("Frontmatter must start with '---' at line 1")
        return False, errors

    # Find frontmatter bounds
    frontmatter_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_end = i
            break

    if frontmatter_end == -1:
        errors.append("Missing closing '---' for frontmatter")
        return False, errors

    # Parse frontmatter
    frontmatter_lines = lines[1:frontmatter_end]
    frontmatter = {}
    for line in frontmatter_lines:
        if ':' in line:
            key = line.split(':')[0].strip()
            frontmatter[key] = True

    # Check required fields
    required = ['name', 'description']
    for field in required:
        if field not in frontmatter:
            errors.append(f"Missing required frontmatter field: {field}")

    # Check name format
    if 'name' in frontmatter:
        # Extract name value - look for 'name:' and get the value until next key or ---
        name_match = re.search(r'^name:\s*(.+?)\s*$', content, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if not re.match(r'^[a-z0-9-]+$', name):
                errors.append(f"Name must be lowercase with hyphens only: got '{name}'")
            if len(name) > 64:
                errors.append(f"Name must be <= 64 characters: got {len(name)}")

    return len(errors) == 0, errors


def validate_content_structure(content: str) -> tuple[bool, list[str]]:
    """Validate content has required sections."""
    errors = []

    # Check for markdown title after frontmatter
    lines = content.split('\n')
    frontmatter_end = -1
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            frontmatter_end = i
            break

    # Find first markdown heading
    found_heading = False
    for line in lines[frontmatter_end+1:]:
        if line.startswith('# '):
            found_heading = True
            break

    if not found_heading:
        errors.append("Content must have a # heading after frontmatter")

    # Check for key sections
    required_sections = [
        (r'禁止行为|禁止项', 'Missing prohibited behaviors section'),
        (r'执行流程|阶段', 'Missing execution workflow'),
    ]

    for pattern, error_msg in required_sections:
        if not re.search(pattern, content):
            errors.append(error_msg)

    return len(errors) == 0, errors


def validate_no_problematic_patterns(content: str) -> tuple[bool, list[str]]:
    """Check for problematic patterns that violate the skill's principles."""
    errors = []
    lines = content.split('\n')

    # Check for emoji usage (forbidden by style guide)
    for i, line in enumerate(lines):
        if re.search(r'[\U0001F300-\U0001F9FF]', line):
            errors.append(f"Line {i+1}: Contains emoji (forbidden in files)")

    return len(errors) == 0, errors


def main():
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / 'SKILL.md'

    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found")
        sys.exit(1)

    content = skill_md.read_text(encoding='utf-8')

    all_errors = []

    # Run all validations
    checks = [
        ("Frontmatter", validate_frontmatter),
        ("Content Structure", validate_content_structure),
        ("Problematic Patterns", validate_no_problematic_patterns),
    ]

    for name, validator in checks:
        valid, errors = validator(content)
        if not valid:
            all_errors.append(f"[{name}] " + "\n  ".join(errors))

    if all_errors:
        print("VALIDATION FAILED:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()