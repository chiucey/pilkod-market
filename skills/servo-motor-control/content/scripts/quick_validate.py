"""
Skill Validation Script

Validates SKILL.md structure and frontmatter format
"""

import os
import re
import sys
from pathlib import Path


def validate_frontmatter(skill_path: Path) -> dict:
    """Validate SKILL.md frontmatter"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    skill_file = skill_path / 'SKILL.md'
    if not skill_file.exists():
        result['valid'] = False
        result['errors'].append("SKILL.md not found")
        return result

    content = skill_file.read_text(encoding='utf-8')

    # Check frontmatter at first line
    if not content.startswith('---'):
        result['valid'] = False
        result['errors'].append("SKILL.md must start with YAML frontmatter (---)")
        return result

    # Extract frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_lines = lines[1:i]
                break

    if not frontmatter_lines:
        result['valid'] = False
        result['errors'].append("Invalid frontmatter structure")
        return result

    # Check required fields
    frontmatter_text = '\n'.join(frontmatter_lines)
    required_fields = ['name:', 'description:']
    for field in required_fields:
        if field not in frontmatter_text:
            result['valid'] = False
            result['errors'].append(f"Missing required field: {field}")

    # Check name format
    name_match = re.search(r'^name:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            result['warnings'].append(f"name '{name}' should use hyphen-case format (lowercase)")

    # Check description trigger phrases
    desc_match = re.search(r'^description:\s*(.+)$', frontmatter_text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip()
        if len(desc) < 20:
            result['warnings'].append("description should be descriptive (>20 chars)")
        if 'when' not in desc.lower() and 'use' not in desc.lower():
            result['warnings'].append("description should include trigger phrases like 'Use when...'")

    return result


def validate_meta(skill_path: Path) -> dict:
    """Validate _meta.json"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    meta_file = skill_path / '_meta.json'
    if not meta_file.exists():
        result['valid'] = False
        result['errors'].append("_meta.json not found")
        return result

    try:
        import json
        meta = json.loads(meta_file.read_text(encoding='utf-8'))

        # Check required fields
        if 'id' not in meta:
            result['valid'] = False
            result['errors'].append("_meta.json missing 'id' field")
        if 'version' not in meta:
            result['valid'] = False
            result['errors'].append("_meta.json missing 'version' field")

        # Check id type
        if 'id' in meta and not isinstance(meta['id'], int):
            result['valid'] = False
            result['errors'].append("_meta.json 'id' must be an integer")

        # Check version format
        if 'version' in meta:
            if not re.match(r'^\d+\.\d+\.\d+$', meta['version']):
                result['warnings'].append("version should follow semantic versioning (x.y.z)")

    except json.JSONDecodeError as e:
        result['valid'] = False
        result['errors'].append(f"Invalid JSON in _meta.json: {e}")

    return result


def validate_structure(skill_path: Path, skill_name: str) -> dict:
    """Validate directory structure"""
    result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }

    expected_dirs = ['references']
    for d in expected_dirs:
        dir_path = skill_path / d
        if not dir_path.exists():
            result['warnings'].append(f"Expected directory '{d}' not found")

    # Check folder name matches name
    if skill_path.name != skill_name:
        result['warnings'].append(f"Folder name '{skill_path.name}' differs from frontmatter name '{skill_name}'")

    return result


def validate_skill(skill_path: str) -> dict:
    """Complete validation"""
    path = Path(skill_path)
    results = {
        'path': str(path),
        'overall_valid': True,
        'frontmatter': {},
        'meta': {},
        'structure': {}
    }

    # Validate frontmatter
    fm_result = validate_frontmatter(path)
    results['frontmatter'] = fm_result
    if not fm_result['valid']:
        results['overall_valid'] = False

    # Validate meta
    meta_result = validate_meta(path)
    results['meta'] = meta_result
    if not meta_result['valid']:
        results['overall_valid'] = False

    # Extract skill name
    skill_name = 'unknown'
    if fm_result.get('valid', False):
        skill_file = path / 'SKILL.md'
        content = skill_file.read_text(encoding='utf-8')
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()

    # Validate structure
    struct_result = validate_structure(path, skill_name)
    results['structure'] = struct_result

    return results


def print_results(results: dict):
    """Print validation results"""
    print("\n" + "=" * 60)
    print("Skill Validation Results")
    print("=" * 60)

    print(f"\nPath: {results['path']}")
    print(f"Overall Valid: {results['overall_valid']}")

    # Frontmatter
    print("\n--- Frontmatter ---")
    fm = results['frontmatter']
    print(f"Valid: {fm.get('valid', False)}")
    for err in fm.get('errors', []):
        print(f"  ERROR: {err}")
    for warn in fm.get('warnings', []):
        print(f"  WARNING: {warn}")

    # Meta
    print("\n--- _meta.json ---")
    meta = results['meta']
    print(f"Valid: {meta.get('valid', False)}")
    for err in meta.get('errors', []):
        print(f"  ERROR: {err}")
    for warn in meta.get('warnings', []):
        print(f"  WARNING: {warn}")

    # Structure
    print("\n--- Structure ---")
    struct = results['structure']
    print(f"Valid: {struct.get('valid', False)}")
    for err in struct.get('errors', []):
        print(f"  ERROR: {err}")
    for warn in struct.get('warnings', []):
        print(f"  WARNING: {warn}")

    print("\n" + "=" * 60)
    return results['overall_valid']


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python quick_validate.py <skill_path>")
        sys.exit(1)

    results = validate_skill(sys.argv[1])
    valid = print_results(results)
    sys.exit(0 if valid else 1)
