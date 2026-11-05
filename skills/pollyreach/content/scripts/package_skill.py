#!/usr/bin/env python3
"""
PollyReach Skill Packager
Package skill directory into a .skill file for distribution.
"""

import os
import json
import zipfile
import sys
from pathlib import Path


def validate_skill(skill_path: str) -> bool:
    """Validate skill structure before packaging."""
    skill_dir = Path(skill_path)

    # Check required files
    if not (skill_dir / "SKILL.md").exists():
        print("Error: SKILL.md not found")
        return False

    if not (skill_dir / "_meta.json").exists():
        print("Error: _meta.json not found")
        return False

    # Validate _meta.json
    try:
        with open(skill_dir / "_meta.json") as f:
            meta = json.load(f)
            if "id" not in meta or "version" not in meta:
                print("Error: _meta.json must contain 'id' and 'version'")
                return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid _meta.json: {e}")
        return False

    # Validate SKILL.md frontmatter
    with open(skill_dir / "SKILL.md") as f:
        content = f.read()
        if not content.startswith("---"):
            print("Error: SKILL.md must start with YAML frontmatter")
            return False
        if "name:" not in content or "description:" not in content:
            print("Error: SKILL.md must contain 'name' and 'description' in frontmatter")
            return False

    print("Validation passed!")
    return True


def package_skill(skill_path: str, output_dir: str = ".") -> str:
    """Package skill into a .skill file."""
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    # Read meta for version
    with open(skill_dir / "_meta.json") as f:
        meta = json.load(f)

    output_file = Path(output_dir) / f"{skill_name}.skill"

    # Create zip archive
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_dir)
                zf.write(file_path, arcname)

    print(f"Packaged: {output_file}")
    return str(output_file)


def main():
    if len(sys.argv) < 2:
        print("Usage: package_skill.py <skill_path> [output_dir]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    if not validate_skill(skill_path):
        sys.exit(1)

    output_file = package_skill(skill_path, output_dir)
    print(f"\nSuccess! Package created: {output_file}")


if __name__ == "__main__":
    main()
