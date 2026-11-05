#!/usr/bin/env python3
"""
KOL Content Streamer Skill - Quick Validation Script
Validates skill file completeness and format correctness
"""

import os
import sys
import json
import re
from pathlib import Path

def validate_frontmatter(skill_md_path):
    """Validate SKILL.md frontmatter format"""
    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if starts with ---
    if not content.strip().startswith('---'):
        return False, "SKILL.md must start with frontmatter ---"

    # Extract frontmatter
    lines = content.split('\n')
    if len(lines) < 3 or lines[0].strip() != '---':
        return False, "Frontmatter format error"

    # Find end marker
    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return False, "Frontmatter missing closing ---"

    # Parse YAML
    frontmatter_text = '\n'.join(lines[1:end_idx])

    # Check required fields
    if 'name:' not in frontmatter_text:
        return False, "Frontmatter must contain name field"
    if 'description:' not in frontmatter_text:
        return False, "Frontmatter must contain description field"

    # Check no markdown before frontmatter
    before_frontmatter = content[:content.find('---')]
    if '#' in before_frontmatter or '`' in before_frontmatter:
        return False, "No markdown content before frontmatter"

    return True, "Frontmatter format correct"

def validate_meta_json(meta_path):
    """Validate _meta.json format"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        # Check required fields
        if 'id' not in meta:
            return False, "_meta.json must contain id field"
        if 'version' not in meta:
            return False, "_meta.json must contain version field"

        # Check id type
        if not isinstance(meta['id'], int):
            return False, "_meta.json id must be integer"

        # Check version format
        version_pattern = r'^\d+\.\d+\.\d+$'
        if not re.match(version_pattern, meta['version']):
            return False, "_meta.json version must follow semantic versioning (x.y.z)"

        return True, "_meta.json format correct"
    except json.JSONDecodeError as e:
        return False, f"_meta.json JSON parse error: {e}"
    except Exception as e:
        return False, f"_meta.json validation error: {e}"

def validate_naming(path):
    """Validate all file and path names are in English"""
    issues = []

    # Check directory name
    path_parts = Path(path).parts
    for part in path_parts:
        if re.search(r'[\u4e00-\u9fff]', part):
            issues.append(f"Directory name contains Chinese: {part}")

    # Check file names
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if re.search(r'[\u4e00-\u9fff]', d):
                issues.append(f"Subdirectory contains Chinese: {os.path.join(root, d)}")
        for f in files:
            if re.search(r'[\u4e00-\u9fff]', f):
                issues.append(f"Filename contains Chinese: {os.path.join(root, f)}")

    if issues:
        return False, "; ".join(issues)
    return True, "Naming check passed"

def main():
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    print(f"Validating skill directory: {skill_dir}")
    print("-" * 50)

    all_passed = True

    # Validate SKILL.md
    skill_md = os.path.join(skill_dir, 'SKILL.md')
    if os.path.exists(skill_md):
        passed, msg = validate_frontmatter(skill_md)
        print(f"[{'✓' if passed else '✗'}] SKILL.md frontmatter: {msg}")
        all_passed = all_passed and passed
    else:
        print("[✗] SKILL.md not found")
        all_passed = False

    # Validate _meta.json
    meta_json = os.path.join(skill_dir, '_meta.json')
    if os.path.exists(meta_json):
        passed, msg = validate_meta_json(meta_json)
        print(f"[{'✓' if passed else '✗'}] _meta.json: {msg}")
        all_passed = all_passed and passed
    else:
        print("[✗] _meta.json not found")
        all_passed = False

    # Validate naming
    passed, msg = validate_naming(skill_dir)
    print(f"[{'✓' if passed else '✗'}] Path naming: {msg}")
    all_passed = all_passed and passed

    # Check required directories
    required_dirs = ['scripts', 'references', 'assets']
    for dir_name in required_dirs:
        dir_path = os.path.join(skill_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"[✓] Directory exists: {dir_name}/")
        else:
            print(f"[!] Directory not found: {dir_name}/ (optional)")

    print("-" * 50)
    if all_passed:
        print("✓ All validations passed")
        return 0
    else:
        print("✗ Some validations failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
