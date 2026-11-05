#!/usr/bin/env python3
"""
XMind Generator Skill - Quick Validation Script
Validates the skill structure and frontmatter compliance.
"""

import json
import os
import sys
from pathlib import Path


def validate_frontmatter(file_path: Path) -> tuple[bool, list[str]]:
    """Validate SKILL.md frontmatter format."""
    errors = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for BOM
    if content.startswith('\ufeff'):
        errors.append("File contains BOM - remove it")
        content = content[1:]

    # Check first character is ---
    if not content.strip().startswith('---'):
        errors.append("Frontmatter must start with '---' on the first line")
        return False, errors

    # Parse frontmatter
    lines = content.split('\n')
    frontmatter_lines = []
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            frontmatter_lines.append((i, line))

    if not frontmatter_lines:
        errors.append("Frontmatter not found or empty")
        return False, errors

    # Extract frontmatter content
    frontmatter_content = '\n'.join(line for _, line in frontmatter_lines)

    # Check required fields
    if 'name:' not in frontmatter_content:
        errors.append("Frontmatter missing 'name' field")

    if 'description:' not in frontmatter_content:
        errors.append("Frontmatter missing 'description' field")

    # Check for markdown heading BEFORE frontmatter starts
    frontmatter_started = False
    for i, line in enumerate(lines[:10]):
        if line.strip() == '---':
            if not frontmatter_started:
                frontmatter_started = True
                continue
            else:
                break  # Frontmatter closed
        if line.strip().startswith('#'):
            errors.append(f"Markdown heading found at line {i+1} before frontmatter")
            break

    return len(errors) == 0, errors


def validate_meta(file_path: Path) -> tuple[bool, list[str]]:
    """Validate _meta.json structure."""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"_meta.json is not valid JSON: {e}")
        return False, errors

    if 'id' not in meta:
        errors.append("_meta.json missing 'id' field")

    if 'version' not in meta:
        errors.append("_meta.json missing 'version' field")

    if 'id' in meta and not isinstance(meta['id'], (int, str)):
        errors.append("_meta.json 'id' must be int or string")

    if 'version' in meta and not isinstance(meta['version'], str):
        errors.append("_meta.json 'version' must be string")

    return len(errors) == 0, errors


def validate_structure(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate skill directory structure."""
    errors = []

    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        file_path = skill_dir / filename
        if not file_path.exists():
            errors.append(f"Required file missing: {filename}")

    # Check scripts directory exists
    scripts_dir = skill_dir / 'scripts'
    if not scripts_dir.exists():
        errors.append("scripts/ directory not found")

    return len(errors) == 0, errors


def validate_generator_script(script_path: Path) -> tuple[bool, list[str]]:
    """Validate the generator script."""
    errors = []

    if not script_path.exists():
        errors.append(f"Generator script not found: {script_path}")
        return False, errors

    # Check for required classes
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_classes = ['XMindGenerator', 'Topic', 'TopicStyle', 'TextStyle']
    for cls in required_classes:
        if f'class {cls}' not in content:
            errors.append(f"Missing class: {cls}")

    # Check for required methods
    required_methods = ['set_root', 'add_relationship', 'add_summary', 'save']
    for method in required_methods:
        if f'def {method}' not in content:
            errors.append(f"Missing method: {method}")

    return len(errors) == 0, errors


def main():
    skill_dir = Path(__file__).parent.parent
    print(f"Validating skill at: {skill_dir}\n")

    all_errors = []

    # Validate frontmatter
    print("Checking SKILL.md frontmatter...")
    valid, errors = validate_frontmatter(skill_dir / 'SKILL.md')
    if valid:
        print("  OK - Frontmatter format correct")
    else:
        for err in errors:
            print(f"  ERROR: {err}")
        all_errors.extend(errors)

    # Validate meta
    print("\nChecking _meta.json...")
    valid, errors = validate_meta(skill_dir / '_meta.json')
    if valid:
        print("  OK - Meta structure valid")
        with open(skill_dir / '_meta.json', 'r') as f:
            meta = json.load(f)
            print(f"  ID: {meta.get('id')}")
            print(f"  Version: {meta.get('version')}")
    else:
        for err in errors:
            print(f"  ERROR: {err}")
        all_errors.extend(errors)

    # Validate structure
    print("\nChecking directory structure...")
    valid, errors = validate_structure(skill_dir)
    if valid:
        print("  OK - Required files present")
    else:
        for err in errors:
            print(f"  ERROR: {err}")
        all_errors.extend(errors)

    # Validate generator
    print("\nChecking generator script...")
    valid, errors = validate_generator_script(skill_dir / 'scripts' / 'xmind_generator.py')
    if valid:
        print("  OK - Generator script valid")
    else:
        for err in errors:
            print(f"  ERROR: {err}")
        all_errors.extend(errors)

    # Summary
    print("\n" + "=" * 50)
    if all_errors:
        print(f"VALIDATION FAILED - {len(all_errors)} error(s) found")
        return 1
    else:
        print("VALIDATION PASSED - All checks successful")
        return 0


if __name__ == "__main__":
    sys.exit(main())
