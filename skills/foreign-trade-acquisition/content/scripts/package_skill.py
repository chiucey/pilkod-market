#!/usr/bin/env python3
"""
Package Skill Script
Packages the foreign-trade-acquisition skill for distribution
"""

import os
import json
import shutil
import zipfile
from pathlib import Path

def validate_skill_structure(skill_path):
    """Validate the skill structure"""
    required_files = ['SKILL.md', '_meta.json']
    required_dirs = ['references']

    errors = []
    warnings = []

    # Check required files
    for file in required_files:
        file_path = Path(skill_path) / file
        if not file_path.exists():
            errors.append(f"Missing required file: {file}")
        elif file_path.stat().st_size == 0:
            errors.append(f"Empty file: {file}")

    # Check required directories
    for dir_name in required_dirs:
        dir_path = Path(skill_path) / dir_name
        if not dir_path.exists():
            errors.append(f"Missing required directory: {dir_name}")
        elif not dir_path.is_dir():
            errors.append(f"{dir_name} is not a directory")

    # Check _meta.json content
    meta_path = Path(skill_path) / '_meta.json'
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            if 'id' not in meta:
                errors.append("_meta.json missing 'id' field")
            if 'version' not in meta:
                errors.append("_meta.json missing 'version' field")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in _meta.json: {e}")

    # Check SKILL.md frontmatter
    skill_path_file = Path(skill_path) / 'SKILL.md'
    if skill_path_file.exists():
        with open(skill_path_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        if 'name:' not in content or 'description:' not in content:
            errors.append("SKILL.md frontmatter must contain 'name' and 'description'")

    return errors, warnings

def package_skill(skill_path, output_dir):
    """Package the skill into a .skill file"""
    skill_name = Path(skill_path).name
    output_file = Path(output_dir) / f"{skill_name}.skill"

    # Create zip file
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    return output_file

def main():
    skill_path = Path(__file__).parent.parent
    output_dir = Path(__file__).parent.parent / 'dist'

    print("=" * 50)
    print("Foreign Trade Acquisition Skill - Package Tool")
    print("=" * 50)

    # Validate
    print("\n[1/3] Validating skill structure...")
    errors, warnings = validate_skill_structure(skill_path)

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e}")
        print("\n❌ Validation failed!")
        return 1

    print("✅ Validation passed!")

    # Package
    print("\n[2/3] Packaging skill...")
    output_dir.mkdir(exist_ok=True)
    output_file = package_skill(skill_path, output_dir)
    print(f"✅ Skill packaged: {output_file}")

    # Summary
    print("\n[3/3] Package Summary")
    print("-" * 50)
    print(f"Skill Name: foreign-trade-acquisition")
    print(f"Output File: {output_file}")
    print(f"File Size: {output_file.stat().st_size / 1024:.2f} KB")
    print("-" * 50)

    print("\n✅ Package complete!")
    return 0

if __name__ == '__main__':
    exit(main())
