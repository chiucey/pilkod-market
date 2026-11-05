#!/usr/bin/env python3
"""
Package Skill Script
Creates a distributable .skill package from skill directory
"""
import os
import json
import zipfile
import shutil
from pathlib import Path

def package_skill(skill_dir: str, output_dir: str = "."):
    skill_path = Path(skill_dir)
    skill_name = skill_path.name

    # Validate SKILL.md exists
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError("SKILL.md not found in skill directory")

    # Validate _meta.json exists
    meta_json = skill_path / "_meta.json"
    if not meta_json.exists():
        raise FileNotFoundError("_meta.json not found in skill directory")

    # Validate frontmatter
    with open(skill_md, 'r', encoding='utf-8') as f:
        content = f.read()
        if not content.startswith('---'):
            raise ValueError("SKILL.md must start with frontmatter (---)")

    # Read meta
    with open(meta_json, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    # Create output package
    version = meta.get('version', '1.0.0')
    output_file = Path(output_dir) / f"{skill_name}-{version}.skill"

    # Create zip
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # Skip __pycache__ and other dev directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]

            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

    print(f"Package created: {output_file}")
    print(f"Package size: {output_file.stat().st_size} bytes")

    return str(output_file)

if __name__ == "__main__":
    import sys
    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    package_skill(skill_dir)