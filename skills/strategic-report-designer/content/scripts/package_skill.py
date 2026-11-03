#!/usr/bin/env python3
"""
Package skill for distribution.
Creates a .skill bundle from the skill directory.
"""

import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime


def package_skill(skill_path: str, output_dir: str = ".") -> bool:
    """Package skill directory into a .skill file."""
    skill_path = Path(skill_path)
    output_dir = Path(output_dir)

    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}")
        return False

    # Read skill ID and version from _meta.json
    meta_path = skill_path / "_meta.json"
    if not meta_path.exists():
        print(f"Error: _meta.json not found in {skill_path}")
        return False

    import json
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # Get skill name from SKILL.md frontmatter
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding='utf-8')
        import re
        name_match = re.search(r'^name:\s*(.+)$', content, re.MULTILINE)
        if name_match:
            skill_name = name_match.group(1).strip()
        else:
            skill_name = skill_path.name
    else:
        skill_name = skill_path.name

    # Create output filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_file = output_dir / f"{skill_name}_{skill_id}_{version}.skill"

    # Files to include (no secrets, no build artifacts)
    exclude_patterns = {
        '__pycache__', '.git', '.DS_Store', '*.pyc', '.venv', 'node_modules'
    }

    # Create zip archive
    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(skill_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not any(
                    pattern in d for pattern in exclude_patterns
                )]

                for file in files:
                    # Skip excluded files
                    if any(file.endswith(pattern.lstrip('*')) for pattern in exclude_patterns):
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(skill_path)
                    zf.write(file_path, arcname)

        print(f"✓ Skill packaged successfully!")
        print(f"  Name: {skill_name}")
        print(f"  ID: {skill_id}")
        print(f"  Version: {version}")
        print(f"  Output: {output_file}")
        return True

    except Exception as e:
        print(f"Error packaging skill: {e}")
        return False


if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    success = package_skill(skill_path, output_dir)
    sys.exit(0 if success else 1)
