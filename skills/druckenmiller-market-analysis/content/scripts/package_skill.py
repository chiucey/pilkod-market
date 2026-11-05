#!/usr/bin/env python3
"""Package Druckenmiller Market Analysis Skill for Distribution"""

import json
import os
import shutil
import sys
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime

def package_skill(skill_path: str, output_dir: str = None) -> str:
    """Package skill into a .skill archive"""
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name

    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"Error: {skill_path} is not a valid skill directory")
        sys.exit(1)

    # Check required files
    if not (skill_dir / "SKILL.md").exists():
        print("Error: SKILL.md not found")
        sys.exit(1)

    if not (skill_dir / "_meta.json").exists():
        print("Error: _meta.json not found")
        sys.exit(1)

    # Read metadata
    with open(skill_dir / "_meta.json", 'r') as f:
        meta = json.load(f)

    skill_id = meta.get('id', 'unknown')
    version = meta.get('version', '1.0.0')

    # Determine output path
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = Path.cwd()

    output_path.mkdir(parents=True, exist_ok=True)

    # Create archive name
    archive_name = f"{skill_name}-{version}.skill"
    archive_path = output_path / archive_name

    # Create temporary directory for packaging
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_skill = Path(temp_dir) / skill_name
        temp_skill.mkdir()

        # Copy files (excluding unnecessary files)
        exclude_patterns = [
            '__pycache__', '*.pyc', '.git', '.DS_Store',
            'node_modules', '.venv', '*.log', 'dist', 'build'
        ]

        def should_exclude(path: str) -> bool:
            path_lower = path.lower()
            for pattern in exclude_patterns:
                if pattern.lower() in path_lower:
                    return True
            return False

        for item in skill_dir.rglob('*'):
            if item.is_file() and not should_exclude(str(item)):
                rel_path = item.relative_to(skill_dir)
                dest = temp_skill / rel_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)

        # Create archive
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(temp_skill, arcname=skill_name)

    print(f"\n=== Skill Package Created ===")
    print(f"Skill: {skill_name}")
    print(f"Version: {version}")
    print(f"ID: {skill_id}")
    print(f"Archive: {archive_path}")
    print(f"Size: {archive_path.stat().st_size / 1024:.2f} KB")

    return str(archive_path)

if __name__ == "__main__":
    skill_path = sys.argv[1] if len(sys.argv) > 1 else "/workspace/temp-skills/druckenmiller-market-analysis"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/workspace/temp-skills"

    package_skill(skill_path, output_dir)
