#!/usr/bin/env python3
"""
Quick validation script for web-novel-writer skill.
Validates frontmatter, structure, and naming conventions.
"""

import os
import re
import json
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def validate_frontmatter(skill_dir):
    """Validate SKILL.md frontmatter format."""
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        print_error("SKILL.md not found")
        return False

    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with ---
    if not content.startswith('---'):
        print_error("SKILL.md must start with frontmatter (---)")
        return False

    # Extract frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        print_error("Invalid frontmatter format")
        return False

    frontmatter_content = frontmatter_match.group(1)

    # Check required fields
    required_fields = ['name', 'description']
    missing_fields = []

    for field in required_fields:
        if not re.search(rf'^{field}:', frontmatter_content, re.MULTILINE):
            missing_fields.append(field)

    if missing_fields:
        print_error(f"Missing required frontmatter fields: {', '.join(missing_fields)}")
        return False

    # Validate name format (hyphen-case)
    name_match = re.search(r'^name:\s*(.+)', frontmatter_content, re.MULTILINE)
    if name_match:
        name = name_match.group(1).strip()
        if not re.match(r'^[a-z0-9-]+$', name):
            print_warning(f"Name '{name}' should be lowercase with hyphens only")

    print_success("Frontmatter validation passed")
    return True

def validate_meta_json(skill_dir):
    """Validate _meta.json exists and has required fields."""
    meta_file = skill_dir / "_meta.json"

    if not meta_file.exists():
        print_error("_meta.json not found")
        return False

    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)

        required_fields = ['id', 'version']
        missing_fields = []

        for field in required_fields:
            if field not in meta:
                missing_fields.append(field)

        if missing_fields:
            print_error(f"Missing required _meta.json fields: {', '.join(missing_fields)}")
            return False

        # Validate ID is an integer
        if not isinstance(meta['id'], int):
            print_error("Field 'id' must be an integer")
            return False

        # Validate version format
        version = meta.get('version', '')
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            print_warning(f"Version '{version}' should follow semantic versioning (e.g., 1.0.0)")

        print_success("_meta.json validation passed")
        return True

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in _meta.json: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading _meta.json: {e}")
        return False

def validate_naming(skill_dir):
    """Validate all paths use English names only."""
    folder_name = skill_dir.name

    # Check folder name
    if not re.match(r'^[a-z0-9-]+$', folder_name):
        print_error(f"Folder name '{folder_name}' contains non-English characters")
        return False

    # Standard skill files that are allowed with any case
    standard_files = {'SKILL.md', '_meta.json', 'README.md', 'readme.md'}

    # Check all files and subdirectories - only validate the name, not the path
    invalid_names = []
    for root, dirs, files in os.walk(skill_dir):
        for d in dirs:
            if not re.match(r'^[a-z0-9-_]+$', d):
                invalid_names.append(d)
        for f in files:
            # Allow standard skill files with any case, check others strictly
            if f not in standard_files and not re.match(r'^[a-z0-9-_.]+$', f):
                invalid_names.append(f)

    if invalid_names:
        print_error(f"Found non-English names: {', '.join(invalid_names)}")
        return False

    print_success("Naming validation passed")
    return True

def validate_structure(skill_dir):
    """Validate skill directory structure."""
    # Check required files
    required_files = ['SKILL.md', '_meta.json']

    for filename in required_files:
        filepath = skill_dir / filename
        if not filepath.exists():
            print_error(f"Required file '{filename}' not found")
            return False

    # Check for optional directories
    optional_dirs = ['references', 'scripts', 'assets']
    existing_dirs = [d.name for d in skill_dir.iterdir() if d.is_dir()]

    print_success(f"Structure validation passed (found: {', '.join(existing_dirs) if existing_dirs else 'base files only'})")
    return True

def validate_readme_not_proactive(skill_dir):
    """Check that README files are not proactively created."""
    readme_files = list(skill_dir.glob("README.md")) + list(skill_dir.glob("readme.md"))

    # Exclude references and other subdirectories
    for rf in readme_files:
        if rf.parent == skill_dir:
            print_warning("Proactive README.md found in root - should only be created when explicitly requested")

    return True

def main():
    """Run all validations."""
    skill_dir = Path(__file__).parent.parent

    print(f"\n{'='*50}")
    print(f"Validating skill: {skill_dir.name}")
    print(f"{'='*50}\n")

    results = []

    print("1. Checking frontmatter...")
    results.append(validate_frontmatter(skill_dir))

    print("\n2. Checking _meta.json...")
    results.append(validate_meta_json(skill_dir))

    print("\n3. Checking naming conventions...")
    results.append(validate_naming(skill_dir))

    print("\n4. Checking structure...")
    results.append(validate_structure(skill_dir))

    print("\n5. Checking for unnecessary files...")
    validate_readme_not_proactive(skill_dir)

    print(f"\n{'='*50}")
    if all(results):
        print_success("All validations passed!")
        return 0
    else:
        print_error("Some validations failed")
        return 1

if __name__ == "__main__":
    exit(main())
