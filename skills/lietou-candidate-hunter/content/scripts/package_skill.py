#!/usr/bin/env python3
"""
Package skill into a distributable .skill file.
Creates a ZIP archive of the skill folder.
"""

import os
import json
import zipfile
import re
from pathlib import Path
from datetime import datetime

def sanitize_for_json(text):
    """Remove or escape non-JSON-safe characters."""
    if text is None:
        return ""
    # Convert to string if not already
    text = str(text)
    # Remove BOM if present
    text = text.replace('\ufeff', '')
    return text

def validate_skill(skill_path):
    """Validate skill before packaging."""
    errors = []

    # Check required files exist
    required_files = ['SKILL.md', '_meta.json']
    for filename in required_files:
        filepath = skill_path / filename
        if not filepath.exists():
            errors.append(f"Missing required file: {filename}")

    # Validate _meta.json
    meta_path = skill_path / "_meta.json"
    if meta_path.exists():
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Sanitize content
            content = sanitize_for_json(content)
            meta = json.loads(content)

            if 'id' not in meta:
                errors.append("Missing 'id' in _meta.json")
            if 'version' not in meta:
                errors.append("Missing 'version' in _meta.json")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in _meta.json: {e}")

    # Validate SKILL.md frontmatter
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        with open(skill_md, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.strip().startswith('---'):
            errors.append("SKILL.md must start with YAML frontmatter (---)")

        fm_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            errors.append("Cannot parse YAML frontmatter in SKILL.md")

    # Check for non-ASCII characters in file/folder names
    if not skill_path.name.isascii():
        errors.append(f"Folder name contains non-ASCII: {skill_path.name}")

    for item in skill_path.rglob('*'):
        if item.is_file() and not item.name.isascii():
            errors.append(f"File name contains non-ASCII: {item.relative_to(skill_path)}")

    return errors

def package_skill(skill_path, output_dir=None):
    """Package skill folder into a .skill file."""
    skill_path = Path(skill_path)
    skill_name = skill_path.name

    if output_dir is None:
        output_dir = skill_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Validate first
    errors = validate_skill(skill_path)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return None

    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{skill_name}_{timestamp}.skill"

    # Create ZIP archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Successfully packaged skill to: {output_file}")
    return output_file

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Package skill into .skill file')
    parser.add_argument('skill_path', nargs='?', default='.',
                        help='Path to skill folder (default: current directory)')
    parser.add_argument('--output', '-o', default=None,
                        help='Output directory (default: same as skill folder)')

    args = parser.parse_args()

    skill_path = Path(args.skill_path).resolve()
    if not skill_path.is_dir():
        print(f"Error: {skill_path} is not a directory")
        return 1

    output_file = package_skill(skill_path, args.output)

    if output_file:
        print(f"\nPackage created successfully!")
        return 0
    else:
        print("\nPackage creation failed.")
        return 1

if __name__ == "__main__":
    exit(main())
