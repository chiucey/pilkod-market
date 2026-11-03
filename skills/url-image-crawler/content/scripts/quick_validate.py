#!/usr/bin/env python3
"""
Quick validation script for url-image-crawler skill
Validates: frontmatter, structure, naming conventions
"""

import os
import re
import sys
import json
from pathlib import Path

class ValidationError(Exception):
    pass

def validate_frontmatter(skill_md_path: Path) -> dict:
    """Validate SKILL.md frontmatter format and content"""
    content = skill_md_path.read_text(encoding='utf-8')

    # Check frontmatter exists and is at the start
    if not content.startswith('---'):
        raise ValidationError("SKILL.md must start with YAML frontmatter (---)")

    # Extract frontmatter
    frontmatter_end = content.find('\n---', 3)
    if frontmatter_end == -1:
        raise ValidationError("Frontmatter closing --- not found")

    frontmatter_text = content[3:frontmatter_end].strip()

    # Parse frontmatter (handle multiline values like description |)
    try:
        frontmatter = {}
        lines = frontmatter_text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            # Check if this line starts a field
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Handle multiline values (| or >)
                if value in ('|', '>'):
                    # Collect multiline content
                    multiline_lines = []
                    i += 1
                    while i < len(lines):
                        next_line = lines[i]
                        # Check for blank line or next field
                        if next_line and not next_line[0].isspace():
                            break
                        if next_line.strip():
                            multiline_lines.append(next_line.strip())
                        i += 1
                    frontmatter[key] = ' '.join(multiline_lines)
                    continue
                else:
                    frontmatter[key] = value
            i += 1
    except Exception as e:
        raise ValidationError(f"Failed to parse frontmatter: {e}")

    # Check required fields
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in frontmatter:
            raise ValidationError(f"Missing required frontmatter field: {field}")

    # Validate name format (hyphen-case, alphanumeric only)
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
        raise ValidationError(f"Invalid name format '{name}': must be hyphen-case (e.g., 'my-skill')")

    if len(name) > 64:
        raise ValidationError(f"Name '{name}' exceeds 64 character limit")

    # Validate description exists and has trigger phrases
    description = frontmatter['description']
    if len(description) < 10:
        raise ValidationError("Description too short (must be descriptive)")

    return {
        'name': name,
        'description': description,
        'frontmatter_valid': True
    }

def validate_meta_json(meta_path: Path, expected_id: int = None) -> dict:
    """Validate _meta.json format and content"""
    try:
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in _meta.json: {e}")

    # Check required fields
    if 'id' not in meta:
        raise ValidationError("_meta.json missing 'id' field")
    if 'version' not in meta:
        raise ValidationError("_meta.json missing 'version' field")

    # Validate id is an integer
    if not isinstance(meta['id'], int):
        raise ValidationError(f"_meta.json 'id' must be an integer, got {type(meta['id']).__name__}")

    # Validate version format (semver)
    version = meta['version']
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        raise ValidationError(f"Invalid version format '{version}': must be semver (e.g., '1.0.0')")

    if expected_id and meta['id'] != expected_id:
        raise ValidationError(f"_meta.json id mismatch: expected {expected_id}, got {meta['id']}")

    return meta

def validate_structure(skill_dir: Path) -> dict:
    """Validate skill directory structure"""
    required_files = ['SKILL.md', '_meta.json']

    for file in required_files:
        file_path = skill_dir / file
        if not file_path.exists():
            raise ValidationError(f"Missing required file: {file}")

    # Check scripts directory exists and has content
    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists():
        scripts = list(scripts_dir.glob('*'))
        if not scripts:
            print("Warning: scripts/ directory is empty")

    return {'structure_valid': True}

def main():
    skill_dir = Path('/workspace/temp-skills/url-image-crawler')

    print("=" * 50)
    print("Skill Validation: url-image-crawler")
    print("=" * 50)

    try:
        # Validate structure
        print("\n[1/3] Validating directory structure...")
        validate_structure(skill_dir)
        print("  ✓ Structure valid")

        # Validate frontmatter
        print("\n[2/3] Validating SKILL.md frontmatter...")
        frontmatter = validate_frontmatter(skill_dir / 'SKILL.md')
        print(f"  ✓ Name: {frontmatter['name']}")
        print(f"  ✓ Description present ({len(frontmatter['description'])} chars)")
        print("  ✓ Frontmatter valid")

        # Validate meta.json
        print("\n[3/3] Validating _meta.json...")
        meta = validate_meta_json(skill_dir / '_meta.json')
        print(f"  ✓ ID: {meta['id']}")
        print(f"  ✓ Version: {meta['version']}")
        print("  ✓ _meta.json valid")

        print("\n" + "=" * 50)
        print("✓ All validations passed!")
        print("=" * 50)
        return 0

    except ValidationError as e:
        print(f"\n✗ Validation failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
