#!/usr/bin/env python3
"""
K-Dense BYOK Skill Packaging Script
Packages the skill for distribution as a .skill file
"""

import json
import os
import shutil
import sys
import zipfile
from pathlib import Path


def validate_skill(skill_path: Path) -> bool:
    """Validate skill structure before packaging"""
    required_files = ['SKILL.md', '_meta.json']
    required_meta_keys = ['id', 'version']

    # Check required files exist
    for filename in required_files:
        file_path = skill_path / filename
        if not file_path.exists():
            print(f"Error: Missing required file: {filename}")
            return False

    # Validate _meta.json
    with open(skill_path / '_meta.json', 'r') as f:
        meta = json.load(f)

    for key in required_meta_keys:
        if key not in meta:
            print(f"Error: _meta.json missing required key: {key}")
            return False

    # Validate SKILL.md frontmatter
    with open(skill_path / 'SKILL.md', 'r') as f:
        content = f.read()
        if not content.startswith('---'):
            print("Error: SKILL.md must start with YAML frontmatter")
            return False
        if 'name:' not in content or 'description:' not in content:
            print("Error: SKILL.md frontmatter must contain name and description")
            return False

    print("Validation passed!")
    return True


def package_skill(skill_path: str, output_path: str = None):
    """Package skill into a .skill file"""
    skill_path = Path(skill_path)

    if not validate_skill(skill_path):
        sys.exit(1)

    skill_name = skill_path.name
    if output_path is None:
        output_path = f"{skill_name}.skill"

    # Files to include (exclude hidden and build artifacts)
    exclude_patterns = {'.git', '__pycache__', '.DS_Store', '*.pyc', 'node_modules'}

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in exclude_patterns]

            for file in files:
                if file in exclude_patterns or file.endswith('.pyc'):
                    continue

                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Skill packaged successfully: {output_path}")
    return output_path


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Package K-Dense BYOK Skill')
    parser.add_argument('skill_path', nargs='?', default='.',
                       help='Path to skill directory')
    parser.add_argument('-o', '--output', help='Output .skill file path')
    args = parser.parse_args()

    package_skill(args.skill_path, args.output)
