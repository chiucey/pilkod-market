#!/usr/bin/env python3
"""
Package skill script for ziweidoushu-analyst-report.
Creates a distributable .skill package file.
"""

import os
import json
import zipfile
from pathlib import Path

def package_skill(skill_dir, output_dir):
    """Package the skill into a .skill file."""
    skill_path = Path(skill_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    meta_path = skill_path / "_meta.json"
    with open(meta_path, 'r', encoding='utf-8') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')
    skill_name = skill_path.name

    package_name = f"{skill_name}-{version}.skill"
    package_path = output_path / package_name

    with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(skill_path):
            dirs[:] = [d for d in dirs if d not in ['outputs', '__pycache__', '.git']]
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(skill_path)
                zipf.write(file_path, arcname)

    print(f"✓ Package created: {package_path}")
    print(f"  Skill ID: {skill_id}")
    print(f"  Version: {version}")

    return str(package_path)

if __name__ == "__main__":
    import sys

    skill_dir = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/ziweidoushu-analyst-report"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/workspace/temp-skills/packages"

    result = package_skill(skill_dir, output_dir)
    print(f"\nPackage saved to: {result}")