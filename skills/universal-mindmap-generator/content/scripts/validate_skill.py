#!/usr/bin/env python3
"""
Skill Validation Script
验证技能结构和内容完整性
"""

import os
import json
import re
from pathlib import Path


def validate_skill(skill_path: str) -> dict:
    """验证技能完整性"""
    results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'checks': []
    }

    skill_path = Path(skill_path)

    # Check 1: SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        results['valid'] = False
        results['errors'].append('SKILL.md not found')
    else:
        results['checks'].append(('SKILL.md exists', True))

        # Check frontmatter
        content = skill_md.read_text(encoding='utf-8')
        if not content.startswith('---'):
            results['valid'] = False
            results['errors'].append('SKILL.md must start with YAML frontmatter (---)')
        else:
            results['checks'].append(('Frontmatter starts correctly', True))

            # Parse frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                fm_content = frontmatter_match.group(1)
                if 'name:' not in fm_content:
                    results['errors'].append('Frontmatter missing "name" field')
                    results['valid'] = False
                if 'description:' not in fm_content:
                    results['errors'].append('Frontmatter missing "description" field')
                    results['valid'] = False

    # Check 2: _meta.json exists
    meta_json = skill_path / '_meta.json'
    if not meta_json.exists():
        results['valid'] = False
        results['errors'].append('_meta.json not found')
    else:
        results['checks'].append(('_meta.json exists', True))
        try:
            meta = json.loads(meta_json.read_text(encoding='utf-8'))
            if 'id' not in meta:
                results['errors'].append('_meta.json missing "id" field')
                results['valid'] = False
            if 'version' not in meta:
                results['errors'].append('_meta.json missing "version" field')
                results['valid'] = False
            results['checks'].append(('_meta.json valid JSON', True))
        except json.JSONDecodeError as e:
            results['errors'].append(f'_meta.json is not valid JSON: {e}')
            results['valid'] = False

    # Check 3: Scripts directory
    scripts_dir = skill_path / 'scripts'
    if scripts_dir.exists():
        results['checks'].append(('scripts/ directory exists', True))
        py_files = list(scripts_dir.glob('*.py'))
        if py_files:
            results['warnings'].append(f'Found {len(py_files)} Python scripts')
    else:
        results['warnings'].append('No scripts/ directory (optional)')

    # Check 4: Name format
    skill_name = skill_path.name
    if not re.match(r'^[a-z0-9-]+$', skill_name):
        results['warnings'].append(f'Skill name "{skill_name}" should use lowercase with hyphens')

    return results


if __name__ == '__main__':
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    result = validate_skill(skill_path)

    print("=" * 50)
    print("Skill Validation Results")
    print("=" * 50)

    print(f"\nValid: {'✅' if result['valid'] else '❌'}")

    if result['checks']:
        print("\nPassed Checks:")
        for check, passed in result['checks']:
            print(f"  {'✅' if passed else '❌'} {check}")

    if result['warnings']:
        print("\nWarnings:")
        for warning in result['warnings']:
            print(f"  ⚠️ {warning}")

    if result['errors']:
        print("\nErrors:")
        for error in result['errors']:
            print(f"  ❌ {error}")

    sys.exit(0 if result['valid'] else 1)
