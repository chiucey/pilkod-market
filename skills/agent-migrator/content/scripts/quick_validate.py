#!/usr/bin/env python3
"""
Quick Validation Script for Agent Migrator Skill
Validates SKILL.md frontmatter, _meta.json, and directory structure.
"""

import json
import os
import re
import sys
from pathlib import Path

ERRORS = []
WARNINGS = []


def validate_frontmatter(skill_md_path: str) -> bool:
    """Validate SKILL.md frontmatter format."""
    global ERRORS, WARNINGS

    with open(skill_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check frontmatter starts at line 1
    if not content.startswith('---'):
        ERRORS.append(f"SKILL.md must start with --- (frontmatter delimiter)")
        return False

    # Extract frontmatter
    lines = content.split('\n')
    if len(lines) < 3:
        ERRORS.append("SKILL.md frontmatter is incomplete")
        return False

    # Parse frontmatter
    frontmatter = {}
    in_frontmatter = False
    fm_lines = []

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter and ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Validate required fields
    if 'name' not in frontmatter:
        ERRORS.append("Frontmatter missing required field: 'name'")

    if 'description' not in frontmatter:
        ERRORS.append("Frontmatter missing required field: 'description'")

    # Check name format (hyphen-case)
    if 'name' in frontmatter:
        name = frontmatter['name']
        if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
            ERRORS.append(f"Skill name '{name}' should use hyphen-case format (e.g., 'agent-migrator')")

    # Check description contains trigger phrases
    if 'description' in frontmatter:
        desc = frontmatter['description']
        trigger_keywords = ['迁移', 'migrate', 'platform', '平台']
        if not any(kw.lower() in desc.lower() for kw in trigger_keywords):
            WARNINGS.append("Description should contain trigger keywords like '迁移' or 'migrate'")

    # Check frontmatter is at the very beginning (before any markdown)
    if content.index('---') != 0:
        ERRORS.append("Frontmatter must be at the beginning of SKILL.md (before any markdown content)")

    return len(ERRORS) == 0


def validate_meta_json(meta_path: str) -> bool:
    """Validate _meta.json format."""
    global ERRORS, WARNINGS

    if not os.path.exists(meta_path):
        ERRORS.append("_meta.json not found")
        return False

    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        ERRORS.append(f"_meta.json is not valid JSON: {e}")
        return False

    # Required fields
    required_fields = ['id', 'name', 'version', 'description']
    for field in required_fields:
        if field not in meta:
            ERRORS.append(f"_meta.json missing required field: '{field}'")

    # Validate id is a number
    if 'id' in meta and not isinstance(meta['id'], int):
        ERRORS.append("_meta.json 'id' must be an integer")

    # Validate version format
    if 'version' in meta:
        version = meta['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            ERRORS.append(f"_meta.json 'version' should follow semantic versioning (e.g., '1.0.0'), got: '{version}'")

    return len(ERRORS) == 0


def validate_directory_structure(base_path: str) -> bool:
    """Validate skill directory structure."""
    global ERRORS, WARNINGS

    # Required files
    required_files = ['SKILL.md', '_meta.json']

    for fname in required_files:
        fpath = os.path.join(base_path, fname)
        if not os.path.exists(fpath):
            ERRORS.append(f"Required file missing: {fname}")

    # Optional but recommended directories
    optional_dirs = ['scripts', 'references', 'assets']
    for dname in optional_dirs:
        dpath = os.path.join(base_path, dname)
        if os.path.exists(dpath):
            if not os.path.isdir(dpath):
                ERRORS.append(f"{dname} should be a directory, not a file")

    # Check for suspicious files
    suspicious = ['.env', 'secrets.json', 'credentials.json', '*.key', '*.pem']
    for pattern in suspicious:
        if pattern.startswith('*.') and pattern.endswith('*'):
            ext = pattern[1:]
            for f in os.listdir(base_path):
                if f.endswith(ext):
                    WARNINGS.append(f"Found potentially sensitive file: {f}")
        elif os.path.exists(os.path.join(base_path, pattern)):
            WARNINGS.append(f"Found potentially sensitive file: {pattern}")

    return len(ERRORS) == 0


def validate_scripts(base_path: str) -> bool:
    """Validate scripts directory and files."""
    global ERRORS, WARNINGS

    scripts_dir = os.path.join(base_path, 'scripts')
    if not os.path.exists(scripts_dir):
        WARNINGS.append("scripts/ directory not found (recommended for complex skills)")
        return True

    if not os.path.isdir(scripts_dir):
        ERRORS.append("scripts exists but is not a directory")
        return False

    # Check scanner.py exists
    scanner_path = os.path.join(scripts_dir, 'scanner.py')
    if not os.path.exists(scanner_path):
        WARNINGS.append("scripts/scanner.py not found (recommended)")
    else:
        # Basic syntax check
        try:
            with open(scanner_path, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, scanner_path, 'exec')
        except SyntaxError as e:
            ERRORS.append(f"scanner.py has syntax error: {e}")

    return len(ERRORS) == 0


def validate_references(base_path: str) -> bool:
    """Validate references directory."""
    global WARNINGS

    refs_dir = os.path.join(base_path, 'references')
    if os.path.exists(refs_dir):
        if not os.path.isdir(refs_dir):
            print("WARNING: references exists but is not a directory")
            return False
    else:
        WARNINGS.append("references/ directory not found (recommended for detailed documentation)")

    return True


def main():
    """Main validation entry point."""
    global ERRORS, WARNINGS

    # Get skill directory from argument or use current directory
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    print(f"Validating skill at: {os.path.abspath(skill_dir)}")
    print("-" * 50)

    all_passed = True

    # Run validations
    print("Checking frontmatter...")
    if not validate_frontmatter(os.path.join(skill_dir, 'SKILL.md')):
        all_passed = False

    print("Checking _meta.json...")
    if not validate_meta_json(os.path.join(skill_dir, '_meta.json')):
        all_passed = False

    print("Checking directory structure...")
    if not validate_directory_structure(skill_dir):
        all_passed = False

    print("Checking scripts...")
    if not validate_scripts(skill_dir):
        all_passed = False

    print("Checking references...")
    if not validate_references(skill_dir):
        all_passed = False

    # Print results
    print("-" * 50)

    if ERRORS:
        print(f"\n❌ ERRORS ({len(ERRORS)}):")
        for e in ERRORS:
            print(f"  - {e}")

    if WARNINGS:
        print(f"\n⚠️  WARNINGS ({len(WARNINGS)}):")
        for w in WARNINGS:
            print(f"  - {w}")

    if all_passed:
        print("\n✅ All validations passed!")
        return 0
    else:
        print("\n❌ Validation failed. Please fix errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
