#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill archive from the skill directory.
"""
import os
import json
import zipfile
import sys
from pathlib import Path

def validate_skill(skill_dir: Path) -> bool:
    """Validate skill structure."""
    # Check required files
    required_files = ['SKILL.md', '_meta.json']
    for f in required_files:
        if not (skill_dir / f).exists():
            print(f"ERROR: Missing required file: {f}")
            return False

    # Validate _meta.json
    meta_path = skill_dir / '_meta.json'
    with open(meta_path, 'r') as f:
        meta = json.load(f)
    if 'id' not in meta or 'version' not in meta:
        print("ERROR: _meta.json must contain 'id' and 'version'")
        return False

    # Validate SKILL.md frontmatter
    skill_path = skill_dir / 'SKILL.md'
    with open(skill_path, 'r') as f:
        content = f.read()

    if not content.startswith('---'):
        print("ERROR: SKILL.md must start with --- frontmatter")
        return False

    frontmatter_end = content.find('---', 3)
    if frontmatter_end == -1:
        print("ERROR: Invalid frontmatter format")
        return False

    frontmatter = content[3:frontmatter_end].strip()
    if 'name:' not in frontmatter or 'description:' not in frontmatter:
        print("ERROR: Frontmatter must contain 'name' and 'description'")
        return False

    print(f"✓ Validation passed for {skill_dir.name}")
    return True

def package_skill(skill_dir: Path, output_dir: Path) -> Path:
    """Create .skill archive."""
    if not validate_skill(skill_dir):
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    skill_name = skill_dir.name
    output_file = output_dir / f"{skill_name}.skill"

    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir.parent)
                zf.write(file_path, arcname)

    print(f"✓ Packaged: {output_file}")
    return output_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python package_skill.py <skill_dir>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    output_dir = skill_dir.parent

    package_skill(skill_dir, output_dir)